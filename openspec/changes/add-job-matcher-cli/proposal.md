# Proposal: Add `job-matcher` backend (CLI + REST + embeddable core)

> Status: **PROPOSED** — awaiting inception-gate approval
> Owner: @senthilsweb
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
  2. **REST API (FastAPI)** — the *key operations only* (submit an
     analysis, retrieve run results, deterministic scoring, health),
     served by uvicorn; the surface the later frontend change will
     consume.
  3. **Embeddable core** — the pipeline, analysis, and scoring functions
     importable directly (`from job_matcher import ...`) so a GenAI
     agent/orchestrator can call them as tools in-process, no CLI or
     HTTP hop.

  All three surfaces are thin adapters over one service layer — no
  business logic lives in a CLI command or route handler.
- **Observability as aspects (AOP).** Cross-cutting instrumentation —
  trace/span creation, timing, success/error capture — SHALL attach to
  key methods via Python decorators (`@traced`, `@span`), never as inline
  calls woven through core logic. The decorator facade is no-op-safe by
  default (structured JSON logs) with an optional OpenTelemetry backend;
  removing the decorators must leave behaviour identical.

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
- Async job queues / background workers for the API — v1 API calls run
  the pipeline synchronously per request.
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
   and a local JD fixture returns the same schema-valid report the CLI
   produces for identical inputs; `GET /runs/{run_id}` retrieves it;
   `GET /health` returns 200. The run is persisted under `runs/` exactly
   as a CLI run is.
9. The same pipeline is demonstrably callable in-process: a smoke test
   imports the service layer directly (no CLI, no HTTP) and completes an
   offline fixture run.
10. Key pipeline methods (extract, fetch, analyze, score, assemble) carry
    instrumentation **only** via decorators: `grep` shows no
    trace/span/log calls inside the function bodies of core modules, and
    a captured run emits one span record per decorated call with
    parent/child relationships and timing. With no backend configured,
    output behaviour is byte-identical to instrumentation disabled.

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
5. **Observability backend behind the decorators** — plain structured
   JSON logs only, or the OpenTelemetry SDK with OTLP export as an
   optional extra (`pip install job-matcher[otel]`)? Recommendation:
   **facade with both** — decorators talk to a pluggable sink; JSON-log
   sink is the zero-dependency default, OTel sink activates when the
   extra is installed and `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
6. **API execution model** — synchronous request/response (simple, fine
   for a localhost tool) vs. submit-then-poll job pattern. Recommendation:
   **synchronous for v1**; the run-id-addressable `runs/` layout already
   leaves room to add submit/poll later without breaking the contract.
