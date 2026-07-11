# CHANGELOG


## v0.2.1 (2026-07-11)

### Bug Fixes

- **ci**: Openapi artifact via workflow_run; skip image builds for bot/doc commits
  ([`cc8face`](https://github.com/senthilsweb/agent-job-matcher/commit/cc8face27a81cf530a079400597eea984f0aedbf))

GITHUB_TOKEN-created releases don't emit release:published to other workflows, so the OpenAPI
  workflow now chains off the Release workflow's completion (staying a separate action per owner
  direction) and resolves the latest tag itself; dispatch backfills any release.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>


## v0.2.0 (2026-07-11)

### Features

- **api**: Fastapi surface and env-activated telemetry backends
  ([`213c3a5`](https://github.com/senthilsweb/agent-job-matcher/commit/213c3a562bb56960d07a6b59380ea6600a9420c1))

Bolts 4-5 of add-job-matcher-cli (offline suite 86 passed; live server smoke: uvicorn + real POST
  /analyze on the mini model → 74/good_match):

- api.py: POST /analyze (multipart or server-path resume → typed JSON array, stateless, no workflow
  endpoints), GET /health; per-request span middleware; full OpenAPI metadata + fixture-sourced
  examples (test_openapi_docs.py enforces the documentation bar; export script verified producing
  valid openapi.json/yaml) - telemetry: OpenObserve REST sink (batched _json ingestion,
  fire-and-forget, one-warning resilience); OTel bridge as the only vendor-SDK import site behind
  the [otel] extra — generic OTLP, Phoenix, and Arize AX exporters, OpenInference attrs on LLM
  spans; env-only activation with fan-out; missing-extra startup error - @traced gained enrich= so
  post-call span attributes (token usage, gated IO capture) are declared at the decorator — grep
  gate clean: zero instrumentation calls in core function bodies - root docker-compose api service
  now backed by the real app

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>


## v0.1.0 (2026-07-11)

### Documentation

- Add project description to README
  ([`3a3483f`](https://github.com/senthilsweb/agent-job-matcher/commit/3a3483fafba293169284a9cf74b7a36a48683883))

### Features

- **backend**: Deterministic core, pipeline, CLI; repo automation rev 2
  ([`e43df5e`](https://github.com/senthilsweb/agent-job-matcher/commit/e43df5e652862376284a3490982bdf2a00753b1c))

Bolts 1-3 of add-job-matcher-cli (66 offline tests green + live smoke on openai:gpt-5.4-mini —
  79/good_match, recomputed score identical, failure fixture isolated, exit 0): - job_matcher
  package: structlog factory, AOP observability facade (@traced/@timed, contextvars, json/none
  sinks), Pydantic schemas, behaviour-identical scoring port (js_round pins 2.5→3), report/slug
  contract, resume extraction (pypdf/docx, scanned rejection), fetch guards (one attempt, SSRF
  blocklist, min-words JS-shell detector), pydantic-ai typed extraction, per-job async pipeline with
  typed JSON-array contract, Typer CLI (analyze/version) - prototype fully removed (incl. hard-coded
  candidate PII in old prompts); Dockerfile now ships the jobmatch package; root docker-compose.yaml
  added (api + cli services) - eval corpus: JD/failure/adversarial fixtures verbatim from the Eve
  reference; synthetic resume fixture (fictional identity) per inception decision Q3; rubrics ported
  (mini-tier model policy) - spec revisions 2-5: OpenObserve/Phoenix/Arize env-activated telemetry,
  JSON Resume + MCP bolts, /score dropped; AGENTS.md conventions (logger, headers, secrets,
  conventional commits, OpenAPI rule) - new automations: semantic-release workflow, OpenAPI
  release-artifact workflow (graceful pre-API skip), graphify full generation (graphify update:
  communities + graph.html + GRAPH_REPORT.md), RUNBOOK.md, concise .env.example

[skip graphify]

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
