# Proposal: Add `job-matcher` backend (CLI + REST + embeddable core)

> Status: **IMPLEMENTED** — 2026-07-11. All nine bolts built; HARD eval
> sweep green (96 offline + 11 live on the mini model); SOFT
> observations reviewed and the band table recalibrated (rubrics.md §3).
> → VERIFIED awaits two owner manual evidence items (Claude Desktop
> mount, neutral-chatbot UI run), then archive.
> (APPROVED 2026-07-11: inception gate passed, all six questions resolved)
> Owner: @senthilsweb
> Revision: 6 (owner, 2026-07-11: **agent service added to `mcp/`** —
> the ctms-style REST/SSE chat bridge (`/chat/stream`, `/upload`) that
> lets the owner's existing neutral chatbot drive the MCP tools, while
> Claude Desktop mounts the same MCP server over stdio. Reverses
> revision 5's "MCP code only" — evaluation showed a thin REST→MCP
> passthrough is worthless (our REST API already exists) but an LLM
> orchestration loop is genuinely new capability. The system now has
> exactly TWO LLM operations: typed extraction (backend) and chat
> orchestration (agent service). See ADR
> `openspec/adr/0001-agent-service-chat-bridge.md`)
> Revision: 5 (owner, 2026-07-11: two scope additions — a **JSON Resume
> extraction** capability (`POST /resume/jsonresume` + CLI + core:
> resume in → strongly-typed https://jsonresume.org document out) as
> new Bolt 6, and the **MCP server pulled from roadmap into scope** as
> a root `mcp/` folder (Node, stdio, modelled on ctms-mcp-server — its
> MCP part only, not its REST/agent service) as new Bolt 7; live evals
> + verification renumbered to Bolt 8 so verification stays last)
> Revision: 4 (owner, 2026-07-11: telemetry must support **Arize AX,
> Arize Phoenix, and OpenObserve (with or without OTel)** selected
> purely by env vars — this reverses revision 3's "no OTel SDK"
> decision: Arize/Phoenix only ingest OTLP, so an OTel bridge ships as
> an optional extra, confined to the sink layer)
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
     array of per-job outcomes as the response payload), convert a
     resume to a standard JSON Resume document
     (`POST /resume/jsonresume`, revision 5), and health
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
  leave behaviour identical.
- **Telemetry backends selected purely by env** *(revision 4)*. Local
  structured JSON logs are always on; remote backends activate by
  setting nothing more than the env vars each vendor documents:

  | Backend | Enabled by | Transport | Extra deps? |
  |---|---|---|---|
  | OpenObserve (no OTel) | `OPENOBSERVE_URL` (+ org/stream/user/password) | its REST `_json` ingestion API | none |
  | OpenObserve (via OTel) | `OTEL_EXPORTER_OTLP_ENDPOINT` (+ `OTEL_EXPORTER_OTLP_HEADERS`) | OTLP/HTTP | `[otel]` |
  | Arize Phoenix | `PHOENIX_COLLECTOR_ENDPOINT` (+ `PHOENIX_API_KEY`) | OTLP/HTTP | `[otel]` |
  | Arize AX | `ARIZE_SPACE_ID` + `ARIZE_API_KEY` (+ `ARIZE_PROJECT_NAME`) | OTLP to otlp.arize.com | `[otel]` |

  Multiple backends may be active at once (fan-out, like the ai-agents
  monorepo's Phoenix + OpenObserve dual export). The three OTLP-shaped
  backends share **one OTel bridge module** living inside the
  observability package — an optional `pip install job-matcher[otel]`
  extra; application/core code still never imports a vendor SDK. LLM
  analysis spans carry OpenInference semantic attributes so Phoenix and
  Arize render model/token/prompt data natively (prompt/completion
  capture gated by `TELEMETRY_RECORD_IO`, default off). All delivery is
  batched and fire-and-forget — an unreachable backend logs one warning
  and never fails a run.
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
  - `evals/data/` fixtures from the Eve project: the four real JD
    snapshots, the two genuine JS-shell fetch-failure captures,
    `manifest.json`, and the adversarial prompt-injection JD — all
    verbatim. The resume fixture is the exception (resolved question 3):
    a **synthetic resume** is authored and committed instead of the
    owner's real PDF; the real one stays local-only and gitignored.
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
- **JSON Resume extraction** *(revision 5)*: given a resume file, return
  it as a **strongly-typed [JSON Resume](https://jsonresume.org)
  document** (schema v1.0.0 — basics/work/education/skills/projects/…),
  available on all three surfaces: `POST /resume/jsonresume`,
  `jobmatch jsonresume --resume <file>`, and
  `extract_jsonresume()` in the embeddable core. One typed LLM
  extraction call (same pattern and model resolution as the analysis
  call); Pydantic models mirror the standard field-for-field, so the
  output is schema-valid by construction or the request fails loudly.
- **Agent service in `mcp/agent-service/`** *(revision 6)*: the
  conversational REST bridge modelled on the owner's ctms
  `agent_service_mcp_client.py` — a small FastAPI app exposing
  `POST /chat/stream` (SSE, ctms-compatible contract so the existing
  neutral chatbot connects with config only), `POST /upload` (multipart
  → a **configured temp directory**, returning the server-side path the
  chat then references), and `GET /health` (with the discovered tool
  list). It hosts the system's **second and final LLM operation**: an
  orchestration loop that receives natural language and picks MCP tools.
  Max-reuse rules: the loop is **pydantic-ai's MCP client** (stdio
  toolset over `mcp/index.js` — no hand-rolled function-calling loop);
  being Python, it imports the `job_matcher` package's existing
  `logging`, `observability`, and `config` modules rather than
  duplicating them; model resolution `MODEL_CHAT` → `MODEL_ANALYST` →
  `MODEL` (mini tier per the cost policy). It contains no business
  logic — it orchestrates, never scores, parses, or fetches.
- **MCP server at root `mcp/`** *(revision 5 — promoted from roadmap)*:
  a Node (≥18, ES module) server on the official
  `@modelcontextprotocol/sdk` over **stdio**, modelled on the owner's
  `ctms-mcp-server` — **its MCP part only** (the reference's REST/agent
  service is explicitly not copied; our REST layer is the backend
  itself). It bridges MCP tools → the backend REST API
  (`JOBMATCHER_API_URL`, default `http://localhost:8000`): tools
  `analyze_job_fit`, `extract_jsonresume`, `health`. Ships with
  `configs/claude-desktop.json` + `configs/vscode-mcp.json` samples so
  the owner's existing chatbot can mount it.
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
- Running/operating any telemetry backend (Phoenix, Arize account,
  OpenObserve instance) — this change ships the client-side sinks and
  bridge only.
- ~~MCP REST bridge (roadmap)~~ — **pulled into scope by revision 5**
  as the root `mcp/` folder (Bolt 7), and **revision 6 added the agent
  service** (Bolt 8) as the chat-facing REST/SSE layer. Still out of
  scope: HTTP/SSE transports on the MCP server itself (stdio only —
  the agent service is the HTTP face), auth on either, chat
  sessions/memory beyond a single conversation buffer, and a thin
  no-LLM REST→MCP passthrough (evaluated and rejected: our REST API
  already exists; see ADR 0001).
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
   `jobmatch analyze --resume evals/data/resume/synthetic-resume.pdf
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
11. Telemetry backends activate by env alone: setting only
    `OPENOBSERVE_URL...` lands span records in the stream via REST;
    setting only `PHOENIX_COLLECTOR_ENDPOINT` lands OTLP traces in
    Phoenix; setting only `ARIZE_SPACE_ID`/`ARIZE_API_KEY` exports to
    Arize; setting only `OTEL_EXPORTER_OTLP_ENDPOINT` exports generic
    OTLP (OpenObserve-with-OTel). Two backends set together both
    receive the run (fan-out). With any backend down, the run still
    succeeds and logs exactly one delivery warning per backend. OTLP
    backends configured without the `[otel]` extra installed produce a
    clear startup error naming the missing extra.
12. Every Python file carries the AGENTS.md header docstring; all
    diagnostics flow through the shared structlog factory (a run
    produces `./logs/<entry>_<ts>.log` with JSON lines); `grep` finds no
    `print(` diagnostics and no per-module `logging.basicConfig` outside
    `job_matcher/logging.py`.
13. A CLI run writes `results.json` (the typed array) alongside the
    per-job files under `runs/<ts>/`; an API run writes nothing under
    `runs/`.
14. `POST /resume/jsonresume` with the synthetic resume fixture returns
    a document that validates against the JSON Resume v1.0.0 schema
    (typed Pydantic mirror), with `basics.name`/`basics.email` matching
    the fixture's fictional identity; `jobmatch jsonresume` produces the
    identical document for the same input.
15. `node mcp/index.js` (with the API running) answers an MCP
    `tools/list` with `analyze_job_fit`, `extract_jsonresume`, and
    `health`, and a `tools/call` of `analyze_job_fit` against a local
    JD fixture returns the same typed JSON array as `POST /analyze`.
    The MCP server itself contains no REST endpoints (the agent
    service is the only HTTP face inside `mcp/`).
16. With the backend API and agent service running: `POST /upload`
    stores a resume into the configured temp directory and returns its
    server-side path; `POST /chat/stream` with a natural-language
    message referencing that path streams SSE events in the
    ctms-compatible shape, and the answer's scores are grounded in a
    real `analyze_job_fit` MCP tool call (verified via the tool-call
    events in the stream). `GET /health` lists the discovered MCP
    tools. The agent service imports `job_matcher`'s logging/
    observability/config modules — a grep gate shows no duplicated
    logging or sink configuration inside `mcp/agent-service/`.

## Open questions for the inception gate

1. ~~LLM integration library~~ — **Resolved (owner, 2026-07-11):**
   **pydantic-ai** — typed output (`output_type=JobAnalysis`),
   model-agnostic id strings, env-driven provider routing.
2. ~~CLI framework~~ — **Resolved (owner, 2026-07-11):** **Typer**.
3. ~~Committing the real resume fixture~~ — **Resolved (owner,
   2026-07-11):** **synthetic resume in the repo.** A realistic but
   fictional resume is authored and committed as the eval fixture; the
   owner's real resume stays local-only at a gitignored path for
   personal smoke runs. The rubric's SOFT band-range expectations are
   recalibrated once against the synthetic profile at verification.
4. ~~Rounding convention~~ — **Resolved (owner, 2026-07-11):** **JS
   `Math.round` semantics** via a `floor(x + 0.5)` helper, keeping the
   ported eval fixtures byte-identical to the Eve reference.
7. ~~Resume-into-chat mechanism (revision 6)~~ — **Resolved (owner,
   2026-07-11):** the chatbot uses an **upload option**: the agent
   service's `POST /upload` stores the file into a configured temp
   directory (`AGENT_UPLOAD_DIR`; a shared volume when containerized)
   and returns the server-side path, which the conversation then
   references — from there the existing analyze flow continues
   unchanged (the MCP tool's `resume_path` input).
5. ~~Observability backend behind the decorators~~ — **Resolved (owner,
   2026-07-11):** JSON logs always on; OpenObserve via its REST
   JSON-ingestion API when configured. **Correction (owner, revision
   4, same day):** the "no OTel SDK in v1" clause is reversed — Arize
   AX, Arize Phoenix, and OpenObserve-via-OTLP must all work by env
   alone, which requires an OTel bridge; it ships as the optional
   `[otel]` extra, confined to the sink layer.
6. ~~API execution model~~ — **Resolved (owner, 2026-07-11):**
   synchronous; `POST /analyze` returns the typed JSON array as the
   response payload. No workflow layer, no run-browsing endpoints —
   each request is its own unique run.
