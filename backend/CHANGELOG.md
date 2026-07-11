# CHANGELOG


## v0.4.0 (2026-07-11)

### Bug Fixes

- **ci**: Re-sync to current main before semantic-release runs
  ([`23f1bc7`](https://github.com/senthilsweb/agent-job-matcher/commit/23f1bc7691c0a5fbc72f3cbc49a10810d824670a))

The shared concurrency group only serializes execution with graphify.yml - it doesn't stop that
  job's push from landing on main first while this job's checkout stays pinned to the original
  trigger SHA. Add a git fetch + reset --hard origin/main immediately before invoking
  semantic-release so it always computes/commits/pushes against the actual current tip, not a stale
  snapshot.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

- **ci**: Serialize release and graphify pushes to stop a real race
  ([`24de086`](https://github.com/senthilsweb/agent-job-matcher/commit/24de086febc2890205fd5b9117ce5443f56d56df))

release.yml's semantic-release push and graphify.yml's graph-commit push both fire on every push to
  main but lived in separate concurrency groups, so they could run in parallel and race for the same
  ref — observed twice today: the Bolt 10 feat commit's release run was rejected non-fast-forward
  because graphify's push landed on main first, mid-run, and a plain `gh run rerun` couldn't fix it
  (it replays the original stale checkout, not current main).

Both workflows now share one concurrency group (main-writers, cancel-in-progress: false) so they
  queue instead of racing.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### Features

- **backend**: Cover letter rendering with deterministic candidate identity
  ([`7163d29`](https://github.com/senthilsweb/agent-job-matcher/commit/7163d291492c54d21aeab85aa39659106bedd008))

Bolt 10 of add-job-matcher-cli (revision 7) - offline suite now 109 passed (13 new tests), live
  smoke on openai:gpt-5.4-mini renders the full header with zero operator configuration:

- candidate.py: deterministic regex extraction of name/email/phone/ github/linkedin/website from the
  already-extracted resume text - no third LLM call, no grounding guard needed (a regex match is
  definitionally a literal substring of the source). Computed once per run, reused across every job
  in the fan-out. - job_matcher/templates/cover_letter.txt ships as package data; load_template()
  gains the same package-default fallback load_prompt() already has, so cover-letter rendering
  activates with no operator setup (correction to the earlier "no package default, missing template
  degrades to plain text" design) - pipeline.py: identity + a run-level date threaded through
  _job_task -> _cover_letter_text(), which builds the Re: <title> [at <company>] line and renders
  through the template - Real bug caught and fixed during implementation: the URL scanner's
  email-exclusion lookbehind blocked matching a domain AFTER an email's @, but not the email's own
  local-part before it (e.g. "sam.lee" in "sam.lee@example.com" briefly misread as a website) -
  fixed by blanking email matches out of the text before URL scanning

Proposal status: all ten bolts now implemented; VERIFIED still awaits only the two owner manual
  evidence items (Claude Desktop mount, chatbot UI run).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>


## v0.3.2 (2026-07-11)

### Bug Fixes

- **agent-service**: Upload response includes content field for chat fold-in
  ([`b2588d0`](https://github.com/senthilsweb/agent-job-matcher/commit/b2588d0c4dcc2e1c5c07d137305da380172375fd))

Verifying the agent service's upload flow against the actual neutral chatbot
  (github.com/senthilsweb/mcp-chat-client) surfaced a real gap: its UploadResponse contract folds a
  `content` string into the next chat message and never reads `path` — our /upload only returned
  path/filename/message, so the model would never learn where an uploaded file landed even after the
  widget's own dead-code bug (fixed upstream in that repo) was corrected.

- /upload now also returns `content`: "Resume uploaded — server path: <path>", the field the
  widget's contract actually relays into chat - Full round trip verified end-to-end at the wire
  level (widget's exact request/response handling replicated): upload -> fold content into message
  -> analyze_job_fit tool call -> grounded 78/100 good_match answer -> done. Existing test asserting
  body["path"] unaffected; agent-service suite still 6/6, backend 96/96. - openspec: ADR 0001 and
  design.md/spec.md carry dated corrections (not silent rewrites) documenting the gap and the fix;
  tasks.md distinguishes this wire-level proof from the still-open manual browser-UI evidence item

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### Chores

- **compose**: Inline all env vars alongside env_file
  ([`a6cb568`](https://github.com/senthilsweb/agent-job-matcher/commit/a6cb568b31de9e1fbf6ebccfa0fe8ce8ae9ff41e))

Every variable listed in a shared x-jobmatcher-env anchor with ${VAR:-default} interpolation — .env
  stays the source of truth, the compose file documents every knob, and any value can be overridden
  per-run. Adds a named uploads volume pre-wired for the future containerized agent service (ADR
  0001 upload flow).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>


## v0.3.1 (2026-07-11)

### Bug Fixes

- **backend**: Exact-quote evidence rule; live eval suites green — change implemented
  ([`9ea96f2`](https://github.com/senthilsweb/agent-job-matcher/commit/9ea96f268e90bd90350f2c084b978f7ecb5673b4))

Bolt 9 of add-job-matcher-cli, closing construction: - analysis prompt evidence rule tightened to
  exact contiguous quote only (Eve's "close paraphrase" allowance failed HARD grounding 5/14 in the
  Bolt 3 smoke; with this rule the sweep passes) — correction logged in rubrics.md - tests/live/:
  grounding (verbatim evidence + rerun stability), prompt injection (grounded output, score
  recomputed from counts, byte-identical recommendation), single/multi fan-out (call-count spy,
  ranking order), mixed/all-failed runs (one attempt per source, failures never reach the LLM). HARD
  sweep: 11/11 live + 96 offline - rubrics band table recalibrated against the synthetic profile:
  Anthropic 84 strong, Bain 72 good, Gusto ~80 good/strong, Temporal 40 weak, adversarial 67 (not
  strong); rerun delta 1 band - README rewritten (product overview + diagram + surfaces + evals);
  slim backend README; last prototype leftovers removed (json-flows/, OpenDLC doc) - proposal
  status: APPROVED → IMPLEMENTED; VERIFIED gated only on the two owner manual evidence items

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>


## v0.3.0 (2026-07-11)

### Documentation

- **openspec**: Record OpenAPI release-artifact verification evidence (v0.2.1)
  ([`d0a7d7d`](https://github.com/senthilsweb/agent-job-matcher/commit/d0a7d7d9af29d313e20a14e335e56153973f7d39))

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

- **openspec**: Revision 6 — agent service chat bridge, ADR 0001, architecture diagram
  ([`ed0c7f3`](https://github.com/senthilsweb/agent-job-matcher/commit/ed0c7f37b5e8d26886936a0916825a67a49dab4c))

Owner-approved evaluation outcome: a thin REST→MCP passthrough is rejected (our REST API already
  exists); the ctms-style agent service is adopted as mcp/agent-service/ — POST /chat/stream (SSE),
  POST /upload (→ configured temp dir, then the existing resume_path flow), GET /health with tool
  list. LLM loop = pydantic-ai MCP client over mcp/index.js; imports job_matcher
  logging/observability/config (max reuse, grep-gated). System invariant recorded: exactly two LLM
  operations — extraction (MODEL_ANALYST) and orchestration (MODEL_CHAT). New Bolt 8; live evals
  renumbered to Bolt 9. First ADR at openspec/adr/0001; mermaid system diagram added to design.md.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### Features

- **mcp**: Json Resume extraction, MCP server, and agent service chat bridge
  ([`0df1212`](https://github.com/senthilsweb/agent-job-matcher/commit/0df12126de5dd4f2db93aa5feeea290cb3df6f6c))

Bolts 6-8 of add-job-matcher-cli (96 backend + 6 agent-service tests + 5-assertion MCP smoke, all
  green; every bolt verified live on the mini model): - jsonresume.py: strongly-typed Pydantic
  mirror of JSON Resume v1.0.0 (unknown fields rejected at every level), extract_jsonresume with a
  deterministic contact-grounding guard, POST /resume/jsonresume + jobmatch jsonresume + core
  re-export. Live: synthetic resume → correct fictional identity, meta v1.0.0 - mcp/index.js: stdio
  MCP server on @modelcontextprotocol/sdk (ctms model, MCP part only) — analyze_job_fit /
  extract_jsonresume / health passed through to the REST API untouched; client configs for Claude
  Desktop + VS Code; stub-backend smoke test - mcp/agent-service/app.py: the ADR-0001 chat bridge —
  /chat/stream (ctms SSE contract with tool notices), /upload (sanitized → AGENT_UPLOAD_DIR, returns
  server-side path), /health with MCP tool discovery; LLM-2 = pydantic-ai Agent +
  MCPToolset(StdioTransport); reuses job_matcher logging/observability/config/prompts (test-pinned).
  Full-chain live smoke: upload → chat → MCP → API → 81/100 strong_match streamed with the
  deterministic recommendation - resolve_model gains fallback chains (MODEL_CHAT → MODEL_ANALYST →
  MODEL); graphify watches mcp/**; .env.example updated

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>


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
