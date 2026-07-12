# Proposal: Self-contained demo stack — playground UI, OpenAPI docs UI, containerized chat widget

> Status: **IMPLEMENTED** (2026-07-12) — owner approved 2026-07-12
> ("good to go"), Bolts 1-5 built and individually verified in owner-
> specified order (1 → 3 → 4 → 2 → 5). See `tasks.md` for evidence.
> Pending: owner final review, then **verified** + archive.
> Owner: @senthilsweb

## Why

Today, trying this project end-to-end means: run the backend locally,
run the agent-service locally, clone `mcp-chat-client` separately and
run its dev server, and hit the API with `curl` to see a report. There
is no one-command way to demo the product, and no visual, non-chat way
to see what a fit report actually looks like — the compact, evidence-
grounded 40/20/20/20 breakdown that is this project's whole reason to
exist is currently only visible as raw JSON or buried in chat prose.

This change makes the whole product demoable with `docker compose up`:
a resume-and-job-links form that renders the fit report as a proper
visual report (not a chat transcript), a browsable OpenAPI reference
for the REST contract, and the existing chat widget, all as containers
in the same compose stack — plus the README updates needed for someone
new to actually use any of it (endpoints, env vars, cover-letter
templates).

## What changes

1. **`mcp-chat-client` gets a public Docker image**, built the same way
   `agent-job-matcher`'s image is (multi-stage Dockerfile, GHCR publish
   workflow modeled directly on this repo's `.github/workflows/` build-
   and-publish pattern). The image serves the existing demo page (the
   privacyshield-pattern sidebar + header + embedded widget rebuilt in
   `add-history-branding-and-release-assets`) as a static site, not the
   embeddable npm/UMD bundle — the bundle stays release-asset-only.
2. **A new `playground/` Next.js app** in this repo: a privacyshield-
   style two-pane page — left sidebar with resume upload (drag/drop or
   picker) and one-to-many job link inputs (add/remove rows) and a
   Submit button, calling the backend's existing `POST /analyze`
   directly (browser → API, no new backend code); right pane renders
   each returned job report as a compact, elegant, Grafana/PowerBI-
   styled card in an accordion/carousel — job title as the accordion
   header, click to expand the full score breakdown, evidence quotes,
   and match band for that job. Slack-purple (`#4A154B`) brand theme,
   matching `privacyshield` and `mcp-chat-client`'s demo page.
3. **A second, separate Next.js app, `openapi-docs/`**, serving a
   browsable, branded API reference UI over the backend's live
   `/openapi.json` (or the release-attached spec) — a distinct "virtual
   directory" alongside the playground, not a tab inside it.
4. **`docker-compose.yaml` (root)** gains services for all three: the
   containerized `mcp-chat-client` demo, `playground`, and
   `openapi-docs` — so `docker compose up` brings up the entire demo
   surface (API + chat widget + playground + API docs) alongside the
   existing `api`/`cli` services.
5. **README additions**: a compact Markdown table of REST endpoints, a
   "Key environment variables" section, and a "Cover letter templates"
   section documenting Bolt 10's default template and override
   mechanism.

## Out of scope

- Any change to the backend's API surface or scoring logic — the
  playground and docs apps are pure consumers of what already exists
  (`POST /analyze`, `GET /openapi.json`).
- Authentication/multi-tenant concerns for the playground or docs UI —
  this is a demo stack, not a hosted product; no login, no persistence
  beyond the single request/response in the browser.
- Editing `mcp-chat-client`'s embeddable widget itself (`src/`) — only
  a new Dockerfile + publish workflow are added there, packaging the
  demo page that already exists.
- Mobile-responsive layout polish beyond a reasonable desktop-first
  pass — this is a demo tool, not a production frontend.
- The two previously-logged `mcp-chat-client` defects (history losing
  the uploaded-file reference; the action indicator not being
  genuinely live) — unrelated to this change, still deliberately
  unimplemented per prior owner direction.

## Acceptance criteria

1. `docker compose up -d` from `agent-job-matcher`'s root, with a
   filled `.env`, brings up: the backend API, the containerized
   `mcp-chat-client` demo, `playground`, and `openapi-docs` — all
   reachable on distinct localhost ports, no manual steps beyond
   `.env` configuration.
2. In the playground: uploading a resume file + one or more job links
   and clicking Submit returns, for each job, a compact report card
   (job title, match band, total score, 40/20/20/20 sub-scores) in a
   carousel; clicking a card (or its accordion header) expands the
   full report (evidence quotes, gaps) for that job only — collapsed
   state shows all job titles at a glance.
3. The playground's visual style uses the `#4A154B` Slack-purple ramp
   consistently (headers, accents, active states) and reads as compact
   and information-dense (Grafana/PowerBI card density), not a plain
   list of paragraphs.
4. `openapi-docs` renders the backend's OpenAPI document as a browsable
   reference (endpoints grouped, expandable request/response schemas
   and examples) at its own route, independent of the playground.
5. The `mcp-chat-client` GHCR image builds and runs identically to how
   `agent-job-matcher`'s image does today (same workflow shape, same
   `ghcr.io/senthilsweb/...` naming, amd64 build minimum).
6. README has: a REST endpoints table (method, path, purpose — one row
   each, linking to the fuller OpenAPI description), a "Key environment
   variables" section (model/API keys, telemetry toggles, upload/agent
   ports — grouped, not exhaustive), and a "Cover letter templates"
   section (default template location, override mechanism, the
   template placeholders).
7. No secrets, hardcoded credentials, or candidate identity anywhere in
   any new file (Dockerfiles, compose, Next.js apps, README) — same
   standing rule as the rest of the repo (`AGENTS.md` rule 5).
