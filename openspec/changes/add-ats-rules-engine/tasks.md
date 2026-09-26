# Tasks — `add-ats-rules-engine`

- [x] `backend/pyproject.toml` — `zen-engine` dependency; package-data for `ats_rules/*/*.json`
- [x] `backend/job_matcher/ats.py` — rule loading, `resolve`, `extract`, Pydantic contracts
- [x] `backend/job_matcher/ats_rules/{ashby,greenhouse,lever}/{resolve,extract}.json`
- [x] `backend/job_matcher/fetch.py` — ATS branch before the HTML path
- [x] `backend/tests/fixtures/ats/` — trimmed real API responses
- [x] `backend/tests/test_ats_rules.py` — offline (httpx MockTransport)
- [x] `.env.example`, `docs/configuration.md`, `docs/ats-rules.md`, `mkdocs.yml`
- [x] Wheel contains the rule files (built and inspected)
- [x] Both Docker images built locally and resolve an Ashby URL
- [x] CI: `build-and-publish.yml` path filters confirmed to trigger on `backend/**`
- [x] Verified live against the UAT Ashby URL

## Verified locally (2026-09-26), nothing pushed

- Offline suite: 114 passed. The 19 failures are pre-existing and unrelated
  (`backend/evals/data/` fixtures were never committed).
- Live fetch of Ashby (UAT URL, 2084 words), Greenhouse, and Lever.
- Full `/analyze` run on the UAT Ashby URL: report produced, salary range read.
- Wheel contains all six rule files and requires `zen-engine`.
- Both backend-based images (root `Dockerfile`, `mcp/agent-service/Dockerfile`)
  built for `linux/amd64`, the platform CI uses, and resolve ATS URLs in-container.
- **Correction:** the first Greenhouse fixture was fetched with `pay_transparency=true`
  while the rule URL was not, so the fixture hid a live failure. Fixed in the rule,
  and a "field absent" regression test added for Greenhouse and Lever.
