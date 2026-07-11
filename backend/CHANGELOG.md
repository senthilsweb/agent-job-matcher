# CHANGELOG


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
