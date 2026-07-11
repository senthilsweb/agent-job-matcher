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

## Bolt 1 — Package skeleton + deterministic core (no LLM) ✅ (2026-07-11)

- [x] `backend/pyproject.toml` — package `job_matcher`, console script
      `jobmatch` (Typer, `version` command live), deps pinned, `[otel]`
      + `[dev]` extras, pytest markers, python-semantic-release config.
      **Correction (2026-07-11, Construction):** "old prototype files
      removed" is deferred to Bolt 3 — the interim Docker image's
      entrypoint is the prototype `cli.py`, so removal waits until the
      `jobmatch` CLI can replace it in the same commit
- [x] `logging.py` — the structlog factory per `backend/AGENTS.md`
      (JSON lines, ISO timestamps, `./logs/<entry>_<ts>.log` + stdout,
      configure-once guard)
- [x] `observability/` facade — `@traced`/`@timed`, contextvars
      propagation (verified across asyncio.gather), allowlist capture,
      env registry with json/none sinks; `test_observability.py` green
- [x] `schemas.py` — Pydantic port incl. the SkillMatch
      matched⇔evidence validator and the fetch_status-discriminated
      JobOutcome union
- [x] `scoring.py` — behaviour-identical port (formula, reallocation,
      bands, recommendations verbatim, js_round pinning 2.5→3)
- [x] `report.py` — slugify + filename contract + report assembly +
      path-confined artifact writes
- [x] Fixtures: JD/failure/adversarial + manifest copied verbatim;
      synthetic resume authored (fictional "Jordan Rivera" profile,
      generator committed); `backend/evals/data/resume/local/`
      gitignored for the real resume; `evals/rubrics.md` ported with
      the SOFT band table marked provisional
- [x] Offline suite green: **36 passed** (`pytest -m "not live"`) —
      scoring determinism, banding, slug/naming, schema conformance,
      observability; `jobmatch version` + embeddable-core import
      smoke-tested (span emitted via decorator, zero calls in core)

## Bolt 2 — Inputs and fetch guards (no LLM) ✅ (2026-07-11)

- [x] `resume.py` — pypdf/python-docx/txt/md extraction, normalized +
      120-col wrapped output, scanned-PDF (min-words) and `.doc`
      rejection, byte cap; `test_resume_extraction.py` green
- [x] `fetch.py` — one attempt code-enforced (no retry loop exists),
      scheme allowlist, SSRF hostname blocklist (pre-connect +
      post-redirect), byte cap, min-words JS-shell guard, local-file
      mode; DNS-rebinding residual documented as in the Eve baseline
- [x] `test_fetch_guards.py` green against the committed JS-shell
      captures; all guards verified to trip pre-connect (suite is
      network-free)

## Bolt 3 — Generative step + pipeline + CLI ✅ (2026-07-11)

- [x] `config.py` — `.env` discovery (walk up from cwd), `MODEL_ANALYST`
      → `MODEL` → ConfigError; typed knob accessors
- [x] `prompts.py` + package-data `prompts/` — Eve's extraction
      discipline ported verbatim (data-not-instructions frame, no-score
      rule, quote-grounded evidence); override order `$PROMPTS_DIR` →
      `./prompts/` → package default. Old talent-align prompts reviewed
      and **rejected** (they instruct the LLM to compute the score and
      hard-code candidate bio — both banned); deleted with the prototype
- [x] `analyze.py` — the one generative call: pydantic-ai
      `Agent(output_type=JobAnalysis)`, token-usage capture
- [x] `pipeline.py` — per-job end-to-end asyncio tasks
      (semaphore-bounded, per-task graceful failure incl. analysis
      exceptions), typed `list[JobOutcome]`, CLI persistence contract,
      API mode persists nothing; `run_analysis` re-exported
- [x] `cli.py` — `jobmatch analyze` per spec; operator errors exit 2
      with a clear message; completed runs exit 0 (verified all-failed)
- [x] `test_pipeline_offline.py` (7 cases: mixed, all-failed, fan-out
      call counts, exception isolation, persistence contract, API mode)
      + `test_embeddable_core.py`; **offline suite now 66 passed**
- [x] Prototype removed (`app.py`, old `cli.py`,
      `job_fit_from_files.py`, `requirements-job-fit.txt`, old
      prompts/templates incl. embedded candidate PII); Dockerfile now
      installs the package with `jobmatch` as entrypoint
- [x] **Live smoke (2026-07-11, `openai:gpt-5.4-mini`):** synthetic
      resume vs Anthropic JD + 1 failure fixture → 79/good_match
      (inside the provisional band range), failure isolated, exit 0;
      recomputed score == reported (79), recommendation byte-identical.
      **Observation for Bolt 8:** 9/14 matched-evidence strings were
      exact substrings of resume.txt — the model paraphrased the rest;
      tighten the prompt to "exact quote only" (or normalize harder)
      before the HARD grounding eval lands
- [x] `.env.example` at repo root (done early with Bolt 1,
      2026-07-11): model vars, `JOB_FANOUT_CONCURRENCY`,
      `OBSERVABILITY_SINK`, `TELEMETRY_RECORD_IO`, and every
      telemetry-backend block — kept concise per owner direction

## Bolt 4 — FastAPI surface ✅ (2026-07-11)

- [x] `api.py` — `POST /analyze` (multipart + server-path) returning the
      typed JSON array (every element carries `run_id`), `GET /health`;
      no `/runs`, no `/score`, no server-side persistence; per-request
      span middleware; full OpenAPI metadata (project description,
      version, license, contact, externalDocs repo link,
      fixture-sourced examples) per the add-openapi-release-artifact spec
- [x] `test_api.py` (7 cases: health, server-path + multipart analyze,
      exactly-one-resume-input rule, operator errors → 422, format
      rejection, statelessness, absent workflow endpoints) +
      `test_openapi_docs.py` (5 cases: summary/description/example
      coverage, info/externalDocs, spec validates) — **offline suite 86
      passed**
- [x] Decorator-only grep gate clean; `@traced` gained `enrich=` so even
      post-call span attributes (LLM token usage, gated IO capture) are
      declared at the decorator, not in function bodies
- [x] **Live server smoke (2026-07-11):** uvicorn boot, `GET /health` ok,
      real `POST /analyze` (mini model) → Bain JD 74/good_match, typed
      array payload, nothing persisted

## Bolt 5 — Telemetry backends (env-activated) ✅ core (2026-07-11)

- [x] `observability/sinks.py` — OpenObserveRestSink: batched POSTs to
      `{url}/api/{org}/{stream}/_json`, basic auth, flush on batch size
      and root-span end, one warning per process on failure, never raises
- [x] `observability/otel_bridge.py` — the only OTel import site: facade
      spans → OTel spans (nesting + real timestamps preserved),
      OpenInference attrs on the analyze span (kind=LLM, model, token
      counts; `TELEMETRY_RECORD_IO` gates payloads), OTLP exporters for
      generic endpoint / Phoenix / Arize AX; `[otel]` extra
- [x] Env registry wiring in `configure()`: backends join purely by
      their env vars; fan-out; OTLP env without the extra → startup
      error naming `job-matcher[otel]`
- [x] Tests (`test_telemetry_backends.py`, 7 cases): activation matrix,
      none-override, unreachable-OpenObserve resilience (one warning,
      run unaffected), batching/flush contract, missing-extra error,
      OTel bridge span mapping with OpenInference attrs (InMemory
      exporter)
- [ ] Manual smoke: one fixture run visible in a local Phoenix
      (`docker run arizephoenix/phoenix`) and a local OpenObserve, via
      env-only switches — record evidence here (deferred: needs the
      containers running; unit suite covers the contracts)

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

## Bolt 6 — JSON Resume extraction (revision 5)

- [ ] `jsonresume.py` — Pydantic mirror of JSON Resume v1.0.0
      (basics/location/profiles, work, volunteer, education, awards,
      certificates, publications, skills, languages, interests,
      references, projects, meta); unknown fields rejected
- [ ] `extract_jsonresume()` — one typed LLM call, analysis-call
      pattern (fenced resume text, MODEL_ANALYST resolution), grounding
      rule on contact fields; re-exported from the package root
- [ ] `POST /resume/jsonresume` (multipart + server-path, returns the
      document, persists nothing) + `jobmatch jsonresume --resume
      <file> [--out <file>]`
- [ ] Offline test: schema mirror validates/rejects fixture documents;
      live eval: synthetic resume → schema-valid document with the
      fixture's fictional identity in `basics`

## Bolt 7 — MCP server (`mcp/`, revision 5)

- [ ] `mcp/package.json` + `mcp/index.js` — single-file server on
      `@modelcontextprotocol/sdk`, stdio transport, modelled on
      ctms-mcp-server (MCP part only); tools `analyze_job_fit`,
      `extract_jsonresume`, `health` → fetch() to `JOBMATCHER_API_URL`
- [ ] `mcp/configs/claude-desktop.json` + `mcp/configs/vscode-mcp.json`
      client samples; `mcp/.env.example`; `mcp/README.md`
- [ ] Node smoke test: `tools/list` + one `tools/call` against a
      stubbed backend fetch; verify no REST endpoints exist in `mcp/`
- [ ] Manual: mount in the owner's chatbot via the claude-desktop
      config and run one end-to-end analyze — record evidence here

## Bolt 8 — Live evals + verification

- [ ] Live suites under `tests/live/` behind `-m live`: grounding,
      injection, single/multi-job, mixed-failure run
- [ ] Full HARD sweep passes; SOFT observations recorded in rubrics.md
- [ ] README rewritten for this repo (quick start, CLI usage, eval howto)
- [ ] Status → **implemented**, then **verified** after the rubric review
      ceremony; corrections logged in design.md as encountered
