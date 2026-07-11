# Tasks — `add-job-matcher-cli`

Bolts follow AI-DLC: evals pinned before or alongside the code they gate.
Nothing starts until the proposal's open questions are resolved and status
moves to **approved**.

## Bolt 0 — Inception gate

- [ ] Resolve open question 1: LLM library (recommended: pydantic-ai)
- [ ] Resolve open question 2: CLI framework (recommended: Typer)
- [ ] Resolve open question 3: commit the real resume fixture to this
      public repo, or substitute a synthetic one (owner decision)
- [ ] Resolve open question 4: rounding convention (recommended: JS
      semantics, `floor(x + 0.5)`)
- [x] Resolve open question 5 — **resolved by owner (2026-07-11):**
      JSON logs + OpenObserve REST sink; no OTel SDK in v1
- [x] Resolve open question 6 — **resolved by owner (2026-07-11):**
      synchronous API returning the typed JSON array; no /runs endpoints,
      no workflow layer
- [x] Codify logger + file-header conventions in `AGENTS.md` and
      `backend/AGENTS.md` (done with revision 3)
- [ ] Proposal status → **APPROVED** with date

## Bolt 1 — Package skeleton + deterministic core (no LLM)

- [ ] `backend/pyproject.toml` — package `job_matcher`, console script
      `jobmatch`, deps pinned (incl. `fastapi`, `uvicorn`, `structlog`,
      `httpx`); old prototype files removed
- [ ] `logging.py` — the structlog factory per `backend/AGENTS.md`
      (JSON lines, ISO timestamps, `./logs/<entry>_<ts>.log` + stdout)
- [ ] `observability.py` — `@traced`/`@timed` facade, contextvars
      propagation, sinks json/none/openobserve (REST `_json` ingestion,
      batched, fire-and-forget); `test_observability.py` green — built
      first so every later module lands already decorated
- [ ] `schemas.py` — Pydantic port of the Eve schemas incl. the
      SkillMatch matched⇔evidence validator
- [ ] `scoring.py` — behaviour-identical port (formula, reallocation,
      bands, recommendations, js_round)
- [ ] `report.py` — slugify + filename contract + report assembly
- [ ] Copy eval fixtures from
      `ai-agents/agents/job-matcher/evals/data/` (per Bolt 0 decision on
      the resume) and port `evals/rubrics.md`
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
      `OBSERVABILITY_SINK`, `JOB_FANOUT_CONCURRENCY`, and the
      `OPENOBSERVE_URL/ORG/STREAM/USER/PASSWORD` set)

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

## Bolt 5 — Live evals + verification

- [ ] Live suites under `tests/live/` behind `-m live`: grounding,
      injection, single/multi-job, mixed-failure run
- [ ] Full HARD sweep passes; SOFT observations recorded in rubrics.md
- [ ] README rewritten for this repo (quick start, CLI usage, eval howto)
- [ ] Status → **implemented**, then **verified** after the rubric review
      ceremony; corrections logged in design.md as encountered
