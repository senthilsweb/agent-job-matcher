# Tasks — `add-graphify-and-ci`

Owner-directed change: specified and implemented together (2026-07-11).

## Implementation (done with this change's commit)

- [x] Copy `scripts/graphify-build.py` from templrgo (repo-generic, verbatim)
- [x] Adapt `scripts/graphify-index.py` (module roots for this repo, RBAC
      cross-referencing removed)
- [x] `.github/workflows/graphify.yml` — root-of-main storage divergence,
      `[skip graphify]` loop guard, failure tracking issue, optional
      `OPENAI_API_KEY`
- [x] `.github/workflows/build-and-publish.yml` — GHCR publish via
      `GITHUB_TOKEN`, privacyshield tag strategy
- [x] Interim root `Dockerfile` + `.dockerignore` (prototype CLI image)
- [x] Secrets audit: privacyshield has none to copy (GHCR uses
      `GITHUB_TOKEN`); templrgo's `OPENAI_API_KEY` value is not
      recoverable (write-only) and no local `.env` holds one — left unset,
      workflow degrades to AST-only

## Verification (after first push)

- [ ] Graphify run green; root `graph.json`/`graph-index.json`/
      `graph-manifest.json` committed by the bot; no retrigger loop
- [ ] Build & publish run green; `ghcr.io/senthilsweb/agent-job-matcher`
      exists with `latest` + sha tags
- [ ] `docker run ghcr.io/senthilsweb/agent-job-matcher:latest` prints CLI
      usage
- [ ] **Manual, owner:** flip GHCR package visibility to public (package
      settings — no API for this)
- [ ] **Optional, owner:** `gh secret set OPENAI_API_KEY -R
      senthilsweb/agent-job-matcher` to enable graphify's semantic pass
- [ ] Status → **verified**; then archive per openspec convention
