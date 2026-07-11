# Proposal: Add `job-matcher` backend (CLI + REST + embeddable core)

> Status: **PROPOSED** — awaiting inception-gate approval
> Owner: @senthilsweb
> Revision: 3 (owner corrections 2026-07-11: run-browsing endpoints
> dropped as an Eve-ism — no workflow layer, each request is simply a
> unique run; telemetry ships to OpenObserve over REST with OTel as a
> future insert; custom structlog logger + file-header convention made
> mandatory via AGENTS.md; fan-out is per-job end-to-end async; results
> are a typed JSON array — disk for CLI, payload for API; MCP REST
> bridge noted as roadmap)
> Revision: 2 (adds: FastAPI surface for key operations; AOP-style
> decorator instrumentation for observability)
> Reference implementation: `ai-agents/agents/job-matcher/` (Eve, TypeScript)

## Why

The Eve rebuild of the job matcher (`ai-agents/agents/job-matcher/`) got the
*design* right — deterministic scoring in code, evidence-grounded extraction,
fetch guards, evals-first — but the Eve runtime itself is not the platform we
want to keep building on. This project takes the proven core of that design
and rebuilds it as a plain, CLI-triggered **Python** GenAI backend, in this
standalone repo, modelled structurally on `privacyshield` (backend now,
frontend later).

The current `backend/` contents are the moved talent-align prototype: it
works, but the LLM computes the score inside the prompt, candidate identity
is hard-coded in source, there are no run artifacts, no fetch guards, and no
evals. It is the "before" picture and will be replaced by this change.

## What changes

- Rebuild `backend/` as a proper Python package (`job_matcher/`) whose
  **core is an interface-agnostic library**, exposed through three access
  surfaces over the same use case (feature depth may vary per surface —
  parity is explicitly not required):
  1. **CLI** — `jobmatch analyze --resume <file> --job <url-or-file>
     [--job ...] [--out runs/]`; the primary surface for this change.
  2. **REST API (FastAPI)** — the *key operations only*: submit an
     analysis (`POST /analyze`, synchronous, returns the typed JSON
     array of per-job outcomes as the response payload) and health
     (`GET /health`); served by
     uvicorn; the surface the later frontend change and the roadmap MCP
     bridge will consume. **No run-browsing endpoints** (`GET /runs...`
     was an Eve-ism) — there is no workflow/run-management layer; each
     request simply carries its own unique `run_id` in the response.
  3. **Embeddable core** — the pipeline, analysis, and scoring functions
     importable directly (`from job_matcher import ...`) so a GenAI
     agent/orchestrator can call them as tools in-process, no CLI or
     HTTP hop.

  All three surfaces are thin adapters over one service layer — no
  business logic lives in a CLI command or route handler.
- **Observability as aspects (AOP).** Cross-cutting instrumentation —
  trace/span creation, timing, success/error capture — SHALL attach to
  key methods via Python decorators (`@traced`, `@timed`), never as
  inline calls woven through core logic; removing the decorators must
  leave behaviour identical. Sinks: local structured JSON logs (always
  on) and **OpenObserve via its REST JSON-ingestion API** when
  configured — batched, fire-and-forget, never failing a run. OTel is
  *not* part of v1: if needed later it is inserted between the sink
  interface and OpenObserve as its own change (the ai-agents monorepo's
  OTLP-to-OpenObserve setup is the reference for that future step).
- **Custom logger + file-header convention, repo-wide.** All Python code
  logs through one structlog-based factory (JSON lines, ISO timestamps,
  per-invocation `./logs/<entry>_<ts>.log` + stdout) and every file opens
  with the owner's header-docstring convention. Both are codified in
  `AGENTS.md` (repo level) and `backend/AGENTS.md` (workspace level) as
  part of this change, with the canonical snippet taken from the owner's
  established pipeline-script style.
- **Async, per-job, end-to-end fan-out.** Given multiple job sources,
  each spawns one end-to-end asyncio task (fetch → analyze → score →
  report), bounded by `JOB_FANOUT_CONCURRENCY`. Any job's failure is
  logged gracefully and recorded as a failed outcome without disturbing
  the other jobs; an all-failed run still completes cleanly.
- **Typed JSON array as the result contract.** Every surface produces
  the same `list[JobOutcome]` (Pydantic union of report | fetch-failure).
  CLI: stored on disk under `runs/<ts>/` (per-job files plus an
  aggregated `results.json`). API: returned as the response payload —
  not persisted server-side.

- **Port the core features of the Eve job-matcher** (and only the core —
  no Eve sessions, subagents, sandboxes, or OTel pipeline):
  1. **Deterministic scoring in code, never in the LLM.** Port
     `agent/lib/scoring.ts` to `job_matcher/scoring.py`: the 40/20/20/20
     formula, empty-preferred reallocation (required scales to 60), match
     bands (≥80 / 65–79 / 50–64 / 35–49 / <35), and the deterministic
     per-band recommendation strings. Behaviour-identical, including the
     rounding convention (see design.md — Python's `round()` differs from
     JS `Math.round()` on exact .5).
  2. **Typed, evidence-grounded extraction as the only generative step.**
     Port the Zod schemas to Pydantic (`JobAnalysis`, `SkillMatch`,
     `ScoreBreakdown`, `JobReport`, `JobFetchFailure`). The analysis schema
     carries counts and resume-quoted evidence, never a score — no field
     exists for an injected score to land in.
  3. **Fetch guards.** One attempt per job source, no retry; http/https
     allowlist; SSRF hostname blocklist; byte cap; minimum-extractable-words
     guard; per-job failure records instead of fabricated analyses; a mixed
     run completes the healthy jobs.
  4. **Per-job JSON reports** under `runs/<timestamp>/`, named
     `slug(<job title>)_<timestamp>.json` (or `....failed.json`), plus
     `ranking.md` for multi-job runs, `resume.txt` and `jobs/<n>.txt`
     referenced, not embedded.
  5. **Prompt-injection defense** carried over architecturally: job text
     delivered as fenced, labeled data; scores structurally impossible to
     inject; adversarial eval retained.
  6. **Model-agnostic env configuration**, no hard-coded model or candidate
     identity; config read from the repo-root `.env`.
- **Copy the eval assets into this repo, re-expressed pythonically:**
  - `evals/data/` fixtures verbatim from the Eve project: the resume PDF,
    the four real JD snapshots, the two genuine JS-shell fetch-failure
    captures, `manifest.json`, and the adversarial prompt-injection JD.
  - `evals/rubrics.md` adapted: same canonical scoring formula, same
    HARD/SOFT contract, criteria that referenced Eve internals (child
    session ids, subagent counts) restated in CLI terms.
  - The eight evals become **pytest** suites under `backend/evals/`:
    deterministic ones (scoring, banding) run with no LLM and no network;
    live ones (extraction, grounding, injection, fetch guards) are opt-in
    via a pytest marker so CI stays cheap and offline-safe.
- Multi-job fan-out becomes **code-bounded concurrency in-process**
  (a worker pool over the analysis call) — an upgrade over Eve, where
  subagent pacing could only be instruction-paced.
- Root `.env.example` documenting every variable, per privacyshield
  convention.

## Out of scope

- Frontend (`frontend/` arrives in a later change, modelled on
  privacyshield's Vite SPA). The FastAPI surface in this change is the
  contract that frontend will consume, but no UI work happens here.
- API auth, rate limiting, multi-tenancy — the API binds to localhost by
  default; hardening arrives with the frontend/deployment change.
- Any workflow / run-management layer: no job queues, no background
  workers, no run state machine, no run-browsing endpoints. Each request
  is a unique, self-contained run.
- OTel SDK integration — telemetry goes straight to OpenObserve over
  REST in v1; an OTel layer in between is a possible future change.
- **MCP REST bridge (roadmap, design must not block it):** an MCP tool
  server wrapping this REST API so the owner's existing chatbot can call
  it (chatbot → MCP tool → `POST /analyze`). The stable typed JSON array
  contract is what makes this a thin future addition; it lands as its own
  `openspec/changes/<name>/`.
- DOCX/PDF/HTML rendering — cover-letter content stays text inside the
  JSON, same v1 boundary as the Eve project.
- OCR / scanned-PDF support, legacy `.doc`.
- LinkedIn profile analysis, salary benchmarking, interview questions,
  ATS-score simulation (roadmap in both ancestors — stays roadmap).
- Headless-browser rendering of JS-heavy job boards (local JD files are
  the documented workaround; the failure fixtures prove the guard).
- Running/operating a telemetry backend (collector, Phoenix,
  OpenObserve). In scope: the decorator instrumentation facade and an
  optional OTLP exporter. Out of scope: deploying anything to receive it.

## Acceptance criteria

1. `pip install -e backend/` (or `uv sync`) then
   `jobmatch analyze --resume evals/data/resume/sk-resume-june-2026.pdf
   --job evals/data/jobs/data-engineering-manager-product-anthropic.txt`
   produces a schema-valid per-job JSON report under `runs/<ts>/`.
2. `pytest -m "not live"` passes offline with no API key: scoring
   determinism, match banding, schema conformance on recorded fixtures,
   fetch-guard behaviour against the committed JS-shell captures.
3. `pytest -m live` (with a configured model) passes every HARD criterion
   in `evals/rubrics.md`, including evidence grounding and prompt-injection
   integrity (score recomputable from counts, recommendation byte-identical
   to the deterministic string).
4. `grep -ri "CANDIDATE_INFO" backend/` returns 0 hits — candidate identity
   comes only from the resume.
5. No model id appears in source; removing `MODEL_ANALYST`/`MODEL_*` from
   the environment produces a clear startup error, not a fallback.
6. A run mixing one good JD snapshot and the two failure fixtures yields
   1 analysis JSON + 2 `.failed.json` records + `ranking.md`, exit code 0.
7. The old prototype files (`app.py`, `cli.py`, `job_fit_from_files.py`)
   are gone from `backend/` — fully superseded, not wrapped.
8. `uvicorn job_matcher.api:app` starts; `POST /analyze` with a resume
   and a local JD fixture synchronously returns a typed JSON array of
   per-job outcomes (schema-identical to what the CLI writes to disk for
   the same inputs) with a unique `run_id`; `GET /health` returns 200;
   no `/runs` endpoints exist.
9. The same pipeline is demonstrably callable in-process: a smoke test
   imports the service layer directly (no CLI, no HTTP) and completes an
   offline fixture run.
10. Key pipeline methods (extract, fetch, analyze, score, assemble) carry
    instrumentation **only** via decorators: `grep` shows no
    trace/span calls inside the function bodies of core modules, and
    a captured run emits one span record per decorated call with
    parent/child relationships and timing. With no backend configured,
    output behaviour is byte-identical to instrumentation disabled.
11. With `OBSERVABILITY_SINK=openobserve` and a reachable instance, a
    fixture run lands span records in the configured stream via the REST
    ingestion API; with the instance down, the run still succeeds and
    logs exactly one delivery warning.
12. Every Python file carries the AGENTS.md header docstring; all
    diagnostics flow through the shared structlog factory (a run
    produces `./logs/<entry>_<ts>.log` with JSON lines); `grep` finds no
    `print(` diagnostics and no per-module `logging.basicConfig` outside
    `job_matcher/logging.py`.
13. A CLI run writes `results.json` (the typed array) alongside the
    per-job files under `runs/<ts>/`; an API run writes nothing under
    `runs/`.

## Open questions for the inception gate

1. **LLM integration library** — pydantic-ai (what the prototype used;
   typed output, model-agnostic id strings) vs. the provider SDK directly.
   Recommendation: **pydantic-ai**, it matches the "typed extraction only"
   design and keeps model routing env-driven.
2. **CLI framework** — Typer (rich help, subcommands, matches "add more
   commands later") vs. stdlib argparse. Recommendation: **Typer**.
3. **Committing the real resume fixture** — the Eve repo committed the
   owner's real resume deliberately. This repo is public
   (github.com/senthilsweb/agent-job-matcher). Copy as-is, or substitute a
   synthetic resume and keep the real one local-only? Needs an owner call.
4. **Rounding convention** — keep JS `Math.round` semantics (2.5 → 3, the
   value pinned by the Eve eval fixtures) or adopt Python banker's rounding
   (2.5 → 2)? Recommendation: **keep JS semantics** via
   `math.floor(x + 0.5)` so the ported eval fixtures stay byte-identical.
5. ~~Observability backend behind the decorators~~ — **Resolved (owner,
   2026-07-11):** JSON logs always on; OpenObserve via its REST
   JSON-ingestion API when configured; **no OTel SDK in v1** — OTel may
   be inserted between the sink interface and OpenObserve later as its
   own change.
6. ~~API execution model~~ — **Resolved (owner, 2026-07-11):**
   synchronous; `POST /analyze` returns the typed JSON array as the
   response payload. No workflow layer, no run-browsing endpoints —
   each request is its own unique run.
