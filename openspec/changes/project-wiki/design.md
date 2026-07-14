# Design: project-wiki

## D1 — Same pattern as ai-agents, independent publishing
Owner chose one independent Pages site per repo (no cross-repo
imports). This repo copies the proven setup: `docs/` + `mkdocs.yml`
(Material, explicit nav) + a workflow running `mkdocs build --strict`
and `actions/deploy-pages`. Only `site_name`, `site_url`, and `nav`
differ from the ai-agents instance. mkdocs pinned `<2` (the 2.0
rewrite drops the plugin system Material 9.x needs).

## D2 — Page map (task-organized)
- **index** — what it is, the two-LLM diagram, start-here table.
- **getting-started** — three 5-minute paths: docker compose demo
  stack (no clone of anything else), CLI analyze, plain REST call.
- **installation** — pip editable install, Docker image, the full
  demo stack, `.env` bootstrap.
- **configuration** — env var reference grouped by concern (model
  resolution chain, fan-out, agent service, telemetry activation,
  template overrides); `.env.example` stays authoritative and is
  linked.
- **surfaces** — CLI / REST / Python / Chat-MCP, with both services'
  endpoint tables and where the OpenAPI contract lives.
- **runbook** — relocated RUNBOOK.md content: workflows table, gh
  secrets recipe, release flow, Docker ops, graphify, test suites.
- **faq** — design decisions linked to specs: LLM-never-scores,
  exactly-two-LLM-ops (ADR 0001), direct provider vs gateway, pypdf
  over Docling, fixture-based evals, OpenAPI-contract-per-release.

## D3 — Relocation, not rewriting
README and RUNBOOK content moves verbatim where it is already good;
only organization and connective prose change. Root RUNBOOK.md becomes
a two-line pointer (kept — links elsewhere reference it). AGENTS.md is
untouched (behavior-defining; out of scope).

## D4 — Link rules (from the shared style guide)
Relative links between docs pages; absolute GitHub URLs to anything
outside `docs/` (mcp/README, .env.example, openspec, workflows).
Linked headings avoid punctuation that anchors differently on GitHub
vs MkDocs. The style guide itself is linked, not copied:
https://senthilsweb.github.io/ai-agents/style-guide/

## D5 — Workflow safety
`docs.yml` triggers only on `docs/**`, `mkdocs.yml`, and itself — it
cannot fire the image build. `docs:` commits release nothing under the
existing semantic-release rules, so publishing docs never bumps a
version. Graphify ignores docs paths (it watches code/spec paths).
