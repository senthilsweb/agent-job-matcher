# Tasks — `add-openapi-release-artifact`

Owner-directed change (2026-07-11). Wiring lands now; activation rides
`add-job-matcher-cli` Bolt 4.

## Implemented with this change

- [x] `scripts/export-openapi.py` — app import (no server), json + yaml
      dump, graceful "API not present yet" skip
- [x] `.github/workflows/openapi-spec.yml` — separate action: on
      release published + dispatch; generate → validate
      (openapi-spec-validator) → `gh release upload`
- [x] AGENTS.md — API-documentation convention (rule 9)

## Gated on add-job-matcher-cli Bolt 4 (the API) — done with Bolt 4 (2026-07-11)

- [x] `api.py` app metadata: project description, version from
      `__version__`, license/contact, `externalDocs` → repo URL
- [x] Every endpoint: summary + Markdown description + fixture-sourced
      request/response examples (`openapi_extra`)
- [x] Offline test `test_openapi_docs.py`: summary/description/example
      coverage per path+method, `info`/`externalDocs` present, spec
      passes openapi-spec-validator
- [x] `openapi-spec-validator` + `pyyaml` added to backend `[dev]`;
      `scripts/export-openapi.py` verified producing openapi.json+yaml
      locally (title/version/externalDocs/paths correct)

## Verification (first release after Bolt 4)

- [x] **Evidence (2026-07-11):** release v0.2.1 carries `openapi.json` +
      `openapi.yaml`, attached automatically by the workflow_run-chained
      OpenAPI workflow after semantic-release cut the tag; spec passed
      openapi-spec-validator in the run; document version matches the
      tag. **Correction:** the original `release: published` trigger
      never fired — GITHUB_TOKEN-created releases don't emit events to
      other workflows; fixed by chaining on the Release workflow's
      completion (still a separate action). v0.2.0 predates the fix and
      has no assets (superseded by v0.2.1 as latest).
- [ ] Owner: confirm a Postman import of the attached spec, then
      status → **verified** and archive
