# Tasks — `add-job-matcher-cli`

Bolts follow AI-DLC: evals pinned before or alongside the code they gate.
Nothing starts until the proposal's open questions are resolved and status
moves to **approved**.

## Bolt 0 — Inception gate ✅ (passed 2026-07-11)

- [x] Resolve open question 1 — **resolved by owner (2026-07-11):**
      pydantic-ai
- [x] Resolve open question 2 — **resolved by owner (2026-07-11):**
      Typer
- [x] Resolve open question 3 — **resolved by owner (2026-07-11):**
      synthetic resume committed; real resume local-only, gitignored
- [x] Resolve open question 4 — **resolved by owner (2026-07-11):**
      JS rounding semantics via `floor(x + 0.5)`
- [x] Resolve open question 5 — **resolved by owner (2026-07-11):**
      JSON logs + OpenObserve REST sink; no OTel SDK in v1
- [x] Resolve open question 6 — **resolved by owner (2026-07-11):**
      synchronous API returning the typed JSON array; no /runs endpoints,
      no workflow layer
- [x] Codify logger + file-header conventions in `AGENTS.md` and
      `backend/AGENTS.md` (done with revision 3)
- [x] Proposal status → **APPROVED** (2026-07-11)

## Bolt 1 — Package skeleton + deterministic core (no LLM)

- [ ] `backend/pyproject.toml` — package `job_matcher`, console script
      `jobmatch`, deps pinned (incl. `fastapi`, `uvicorn`, `structlog`,
      `httpx`); optional `[otel]` extra declared (`opentelemetry-sdk`,
      `opentelemetry-exporter-otlp-proto-http`,
      `openinference-semantic-conventions`); old prototype files removed
- [ ] `logging.py` — the structlog factory per `backend/AGENTS.md`
      (JSON lines, ISO timestamps, `./logs/<entry>_<ts>.log` + stdout)
- [ ] `observability/` facade — `@traced`/`@timed` decorators,
      contextvars propagation, env-driven sink registry, json/none sinks
      only in this bolt (remote backends arrive in Bolt 5);
      `test_observability.py` core cases green — built first so every
      later module lands already decorated
- [ ] `schemas.py` — Pydantic port of the Eve schemas incl. the
      SkillMatch matched⇔evidence validator
- [ ] `scoring.py` — behaviour-identical port (formula, reallocation,
      bands, recommendations, js_round)
- [ ] `report.py` — slugify + filename contract + report assembly
- [ ] Copy JD/failure/adversarial fixtures verbatim from
      `ai-agents/agents/job-matcher/evals/data/`; author the
      **synthetic resume** fixture (realistic, fictional identity);
      gitignore a local path for the owner's real resume; port
      `evals/rubrics.md` (SOFT band table marked "recalibrate against
      synthetic profile at verification")
- [ ] Offline tests green: `test_scoring_determinism`,
      `test_match_banding`, `test_slug_naming`,
      `test_schema_conformance` (recorded fixtures)

## Bolt 2 — Inputs and fetch guards (no LLM)

- [ ] `resume.py` — pypdf/python-docx/txt/md extraction, normalized +
      wrapped output, scanned-PDF and `.doc` rejection
- [ ] `fetch.py` — guards, one-attempt log, local-file mode
- [ ] `test_fetch_guards.py` green against the committed JS-shell
      captures, incl. mixed-run and all-failed behaviour

## Bolt 3 — Generative step + pipeline + CLI

- [ ] `config.py` — `.env` discovery, `MODEL_ANALYST` → `MODEL` → error
- [ ] `prompts.py` + `prompts/` — ported analysis prompt frame (data,
      not instructions); review old talent-align prompts for reuse
- [ ] `analyze.py` — typed extraction call
- [ ] `pipeline.py` — the service layer: per-job end-to-end asyncio
      tasks (semaphore-bounded, context-propagating, per-task graceful
      failure) gathered into the typed `list[JobOutcome]`; CLI-side
      persistence (`results.json`, per-job files, `ranking.md`,
      `summary.json`); stable core API re-exported from `__init__.py`
- [ ] `cli.py` — `jobmatch analyze` per spec, exit-code contract, root
      span per command
- [ ] `test_embeddable_core.py` — offline fixture run through direct
      import only
- [ ] `.env.example` at repo root updated (model vars,
      `OBSERVABILITY_SINK`, `JOB_FANOUT_CONCURRENCY`, and every
      telemetry-backend block commented out: OpenObserve REST, generic
      OTLP, Phoenix, Arize, `TELEMETRY_RECORD_IO`)

## Bolt 4 — FastAPI surface

- [ ] `api.py` — `POST /analyze` (multipart + server-path) returning the
      typed JSON array + `run_id`, `GET /health`; no `/runs` endpoints,
      no server-side persistence, no `/score` endpoint; localhost default
      bind; root-span middleware
- [ ] `test_api.py` — TestClient over fixtures with the analyze step
      stubbed; asserts the response array is schema-identical to what
      the CLI writes to `results.json` for the same inputs, and that the
      API run leaves nothing under `runs/`; verify `/score` does not exist
- [ ] Verify decorator-only instrumentation: no trace/span calls inside
      core function bodies (grep gate from acceptance criterion 10)

## Bolt 5 — Telemetry backends (env-activated)

- [ ] `observability/sinks.py` — OpenObserve REST sink: batched POSTs to
      `{url}/api/{org}/{stream}/_json`, basic auth, fire-and-forget,
      one warning per run on failure
- [ ] `observability/otel_bridge.py` — the only OTel import site: facade
      spans → OTel spans (one-to-one nesting), OpenInference attrs on the
      analyze span, `TELEMETRY_RECORD_IO` gate; OTLP exporters for
      generic endpoint / Phoenix / Arize AX
- [ ] Env registry wiring: each backend activates by its own vars alone;
      multiple backends fan out; OTLP env without `[otel]` installed →
      clear startup error naming the extra
- [ ] Tests: registry activation matrix (each backend solo + two
      together), unreachable-backend resilience, missing-extra error,
      no vendor/OTel import outside `otel_bridge.py` (grep gate)
- [ ] Manual smoke: one fixture run visible in a local Phoenix
      (`docker run arizephoenix/phoenix`) and a local OpenObserve, via
      env-only switches — record evidence in this file

## Bolt 6 — Live evals + verification

- [ ] Live suites under `tests/live/` behind `-m live`: grounding,
      injection, single/multi-job, mixed-failure run
- [ ] Full HARD sweep passes; SOFT observations recorded in rubrics.md
- [ ] README rewritten for this repo (quick start, CLI usage, eval howto)
- [ ] Status → **implemented**, then **verified** after the rubric review
      ceremony; corrections logged in design.md as encountered
