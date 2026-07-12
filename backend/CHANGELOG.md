# CHANGELOG


## v0.6.0 (2026-07-12)

### Features

- **compose**: Containerize the MCP Bridge, put the whole stack on one port scheme
  ([`b39560b`](https://github.com/senthilsweb/agent-job-matcher/commit/b39560b306134ff9cff3eee28d5b6dd4b324a77b))

mcp/agent-service/Dockerfile (new): the MCP server (mcp/index.js) has no network port of its own —
  it's a pure stdio bridge, spawned as a child process by the agent-service via pydantic-ai's
  StdioTransport. So there's no separate "MCP container": this one image bundles both Python
  (FastAPI/pydantic-ai, reusing job_matcher directly) and Node 20 (to actually run index.js). Wired
  into docker-compose.yaml as `agent-service`; chat-demo now points at it by compose network name
  instead of falling back to host.docker.internal.

Real bug found while picking port 6000 specifically: it's on the WHATWG Fetch spec's "bad ports"
  blocklist (the historical X11 port) — Node's native fetch() and every browser refuse to connect to
  it outright. wget from inside a container worked fine, masking the problem at first; the
  playground's own /api/health route (which uses fetch()) silently reported a healthy backend as
  offline. Root-caused via `docker exec ... node -e "fetch(...)"`, which surfaced the real "bad
  port" TypeError. Fixed by shifting the whole scheme to 6010-6014 (also clear of 6006/6007, already
  in local use by an unrelated Arize Phoenix container, and of 6665-6669/6697, also on the
  blocklist).

Verified end-to-end with real containers: agent-service's spawned MCP subprocess discovers all 3
  tools, a real /chat/stream call produces a genuine tool-called answer, and a real /analyze
  submission through the containerized playground scores a live job posting correctly — the full
  REST + MCP Bridge + playground + chat-demo stack, all containerized, all on the corrected port
  range.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


## v0.5.0 (2026-07-12)

### Documentation

- **openspec**: Demo-stack and playground-ui-parity change specs
  ([`25064fb`](https://github.com/senthilsweb/agent-job-matcher/commit/25064fbf61e3eb973f06f5d4190c8ac04ebfe3c8))

add-demo-stack-and-playground: proposal/design/tasks/specs for the containerized mcp-chat-client
  image, the playground and openapi-docs Next.js apps, and the docker-compose wiring — written and
  approved before implementation per standing AI-DLC process, all bolts now implemented and verified
  (see tasks.md evidence).

fix-playground-ui-parity: two rounds of owner UAT correction on the playground's look and feel
  (industry-standard match colors, sticky submit, missing cover letter/copy-to-clipboard, then a
  full privacyshield-template-parity pass — nav rail, fonts, contrast) — both logged and implemented
  same-day per owner direction.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

- **readme**: Document the demo stack, REST endpoints, env vars, cover-letter templates
  ([`70bac56`](https://github.com/senthilsweb/agent-job-matcher/commit/70bac563bc9a76632c6c1a43b1a374627305e05c))

- Related repos: trimmed to mcp-chat-client (runtime dependency) and ai-dlc (the methodology deck
  this repo's whole openspec workflow follows) — privacyshield/ai-agents/templrgo were
  design-lineage notes that had served their purpose and just added noise - New REST endpoints table
  (backend + agent service), Key environment variables table, and Cover letter templates section
  (default path, placeholders, and the TEMPLATES_DIR override — verified against prompts.py's actual
  render() function, not assumed) - Quick start gained the docker compose up -d demo-stack block

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

### Features

- **compose**: Wire playground, openapi-docs, and chat-demo into the demo stack
  ([`dd7515e`](https://github.com/senthilsweb/agent-job-matcher/commit/dd7515e938ffb48bd230690d8d85bd5ca89dcfed))

docker compose up -d now brings up the full self-contained demo: the backend API, the containerized
  mcp-chat-client demo page, the playground, and the branded OpenAPI docs — each on its own port,
  chosen to avoid collisions with this machine's other locally-running compose projects.

Also pins `platform: linux/amd64` and `pull_policy: missing` on every image+build service (api, cli,
  chat-demo). These images are published amd64-only; without the pin, Compose can't resolve an arm64
  manifest on Apple Silicon and silently falls back to a local build instead of saying why —
  confirmed via `docker compose pull`, which surfaces the real reason plainly (a genuine
  architecture mismatch for agent-job-matcher's own image; a still-private GHCR package, pending a
  one-time manual visibility change, for mcp-chat-client's).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

- **openapi-docs**: Add branded Next.js OpenAPI reference app
  ([`531497d`](https://github.com/senthilsweb/agent-job-matcher/commit/531497d857e5f9574ef2dbafaabdf116a796850f))

A second, separate Next.js app (its own port, not a tab inside the playground) rendering the
  backend's live OpenAPI document through Scalar, themed with the same Slack-purple accent as the
  rest of the demo suite. app/route.ts fetches /openapi.json server-side on every request and
  inlines it via Scalar's `content` field rather than `url`, so the browser never needs direct
  network access to the backend — only this app's own origin, which matters inside the compose
  network where the backend's address isn't browser-reachable. Additive to FastAPI's built-in /docs,
  not a replacement.

Also force-adds playground/.env.example and openapi-docs/.env.example, both silently dropped from
  the prior playground commit by create-next-app's default `.env*` gitignore pattern — they're plain
  non-secret templates (just API_URL) matching the root repo's own tracked .env.example convention.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

- **playground**: Add Next.js playground for visual, evidence-grounded fit reports
  ([`624dcba`](https://github.com/senthilsweb/agent-job-matcher/commit/624dcba1e9e7925f19ee7f249fd0c3b18fda9104))

Resume upload + one-to-many job links on the left, a compact Grafana/ PowerBI-styled accordion of
  scored report cards on the right — a non-chat way to see the 40/20/20/20 breakdown and evidence
  quotes this project's whole scoring model produces. Server-side route handlers proxy to the
  backend's existing POST /analyze and GET /health, keeping API_URL out of client-side code
  entirely.

Layout, colors, and chrome are a deliberate port of privacyshield's Sidebar/App structure (colored
  collapsible nav rail, header with a live backend-status pill, Card/Label form composition) rather
  than a new design, per owner direction during UAT. Match-status colors follow the standard
  green-to-red grading scale, not the brand purple used elsewhere for chrome. Cover letters render
  in a collapsible section with copy-to-clipboard.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


## v0.4.2 (2026-07-12)

### Bug Fixes

- **agent-service**: Tool-call notices as a distinct field, not concatenated text
  ([`373434c`](https://github.com/senthilsweb/agent-job-matcher/commit/373434c68834644b4ba934c02a855a301dfdcb95))

Owner-reported bug: the progress notice ("🔧 analyze_job_fit...") was literally prepended into the
  answer text, with no distinct visual treatment - the chat just showed one concatenated blob.

- app.py: tool notices now emit a distinct {"action": "<label>"} SSE field (with a friendly per-tool
  label map) instead of folding "🔧 {name}...\n" into content. Additive to the ctms wire contract - a
  client ignoring the field behaves exactly as before. - test_app.py updated: asserts no "🔧" ever
  appears in content, and that an "action" event carries the tool notice instead.

README: added Tech Stack and Related Repos sections, including an

honest answer to "are we using Pydantic AI Gateway" - we're not: model ids resolve directly to each
  provider via pydantic-ai's own provider integrations, not through Pydantic's hosted
  gateway/routing product (a real, separate thing, now part of Pydantic Logfire). Noted as an
  additive future option, not a current gap.

A second, deeper issue was found while verifying this fix (the action label isn't yet genuinely live
  - it arrives alongside the first content chunk rather than while the tool call is in flight,
  confirmed via Playwright instrumentation on both fast and ~11s tool calls) and is logged as a
  defect spec in mcp-chat-client's openspec, not fixed here - it needs a real async-generator
  concurrency change.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>


## v0.4.1 (2026-07-12)

### Bug Fixes

- **observability**: Configure() must load .env itself, not rely on call order
  ([`6aa788c`](https://github.com/senthilsweb/agent-job-matcher/commit/6aa788ce480f7b8962a8826cc696fca1103a27a0))

Owner configured ARIZE_SPACE_ID/ARIZE_API_KEY for real and got zero telemetry. Root cause:
  configure() read env vars directly, depending on resolve_model() having already called
  load_dotenv() earlier in the process - true in the CLI/pipeline path (resolve_model runs before
  the root span opens), false in the agent service's /chat/stream handler, where start_span() fires
  before any model-resolving code runs. configure()'s result is cached for the process's lifetime,
  so reading a pre-.env environment once meant Arize/OpenObserve were silently dead for that entire
  server process, however long it ran.

Reproduced directly (a clean subprocess calling configure() before anything else resolved False for
  sink activation despite correct .env values on disk) and fixed: configure() now calls the same
  ensure_env_loaded() config.py already exposes (renamed from _ensure_env_loaded, now a shared
  utility instead of module-private).

Verified via the real root_span/traced API in a clean process, not a hand-rolled OTel script: spans
  now reach otlp.arize.com with HTTP 200.

New regression test pins the exact failure mode. Fixing it surfaced a second issue in the existing
  telemetry test fixture: it deleted Arize env vars to simulate a clean environment, but
  configure()'s new .env load faithfully repopulated them from the real .env on disk (deleting a var
  just makes it "unset" from load_dotenv's perspective) - fixed by also freezing config's _loaded
  flag during those tests.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

### Testing

- **agent-service**: Cover conversation-history threading
  ([`7aaf0cd`](https://github.com/senthilsweb/agent-job-matcher/commit/7aaf0cd44f975040abc25d746b5019be4912f10e))

Existing stub fixtures needed the new history parameter added to run_chat()'s signature (from the
  prior commit, bundled in with the CI race fix by an add -A - the code change was correct, this
  fills in its test coverage): history-threaded-through, missing-history-is-empty-list, and
  _to_model_history's dict-to-pydantic-ai-message conversion.

Live-verified end to end (not just unit tested): a follow-up question in the same session answered
  correctly from conversation memory alone (59/100 + the specific gap, no re-invoked tool call); the
  identical question with no history in a fresh session correctly said it hadn't given a score,
  ruling out a lucky guess.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>


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
