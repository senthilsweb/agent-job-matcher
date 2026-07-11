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
- [ ] Resolve open question 5: observability sink strategy (recommended:
      pluggable facade — JSON logs default, OTel as optional extra)
- [ ] Resolve open question 6: API execution model (recommended:
      synchronous v1)
- [ ] Proposal status → **APPROVED** with date

## Bolt 1 — Package skeleton + deterministic core (no LLM)

- [ ] `backend/pyproject.toml` — package `job_matcher`, console script
      `jobmatch`, deps pinned (incl. `fastapi`, `uvicorn`; `[otel]`
      extra); old prototype files removed
- [ ] `observability.py` — `@traced`/`@timed` facade, contextvars
      propagation, json/none sinks (otel sink stubbed behind the extra);
      `test_observability.py` green — built first so every later module
      lands already decorated
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
- [ ] `pipeline.py` — the service layer: run dir, bounded worker pool
      (context-propagating), scoring, reports, `ranking.md`,
      `summary.json`; stable core API re-exported from `__init__.py`
- [ ] `cli.py` — `jobmatch analyze` per spec, exit-code contract, root
      span per command
- [ ] `test_embeddable_core.py` — offline fixture run through direct
      import only
- [ ] `.env.example` at repo root updated (model vars +
      `OBSERVABILITY_SINK`, `JOB_FANOUT_CONCURRENCY`)

## Bolt 4 — FastAPI surface

- [ ] `api.py` — `POST /analyze` (multipart + server-path), `GET /runs`,
      `GET /runs/{run_id}`, `GET /runs/{run_id}/reports`, `POST /score`,
      `GET /health`; localhost default bind; root-span middleware
- [ ] `test_api.py` — TestClient over fixtures with the analyze step
      stubbed; asserts response report ≡ persisted report ≡ CLI schema
- [ ] Verify decorator-only instrumentation: no trace/span calls inside
      core function bodies (grep gate from acceptance criterion 10)

## Bolt 5 — Live evals + verification

- [ ] Live suites under `tests/live/` behind `-m live`: grounding,
      injection, single/multi-job, mixed-failure run
- [ ] Full HARD sweep passes; SOFT observations recorded in rubrics.md
- [ ] README rewritten for this repo (quick start, CLI usage, eval howto)
- [ ] Status → **implemented**, then **verified** after the rubric review
      ceremony; corrections logged in design.md as encountered
