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

- [x] Graphify run green (2026-07-11, dispatch run): bot committed
      `344b6eb` with all three root graph files; the push-triggered run
      was correctly skipped by the loop guard
- [x] Build & publish run green (2026-07-11, push run for `c619f2e`)
- [x] Image behaviour verified locally pre-push on the identical
      Dockerfile (usage prints with an API key set; SIGILL fixes baked
      in — see proposal acceptance criterion 5)
- [ ] **Manual, owner:** flip GHCR package visibility to public (package
      settings — no API for this)
- [x] **Owner set the `OPENAI_API_KEY` repo secret (2026-07-11);**
      suggested Actions variable `OPENAI_MODEL=gpt-5-mini` (bulk
      extraction workload — mini tier suffices; unset falls back to
      gpt-5). Note: currently dormant — the CI build step runs AST-only
      extraction because graphify's semantic pass can't run inside
      Actions (needs an LLM orchestrator; run locally and push instead).
      The key/model activate automatically if that changes
- [ ] Status → **verified**; then archive per openspec convention
