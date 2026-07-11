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

## Gated on add-job-matcher-cli Bolt 4 (the API)

- [ ] `api.py` app metadata: project description, version from
      `__version__`, license/contact, `externalDocs` → repo URL, tag
      descriptions
- [ ] Every endpoint: summary + Markdown description + fixture-sourced
      request/response examples (Pydantic `Field(examples=...)` /
      `openapi_extra`)
- [ ] Offline test `test_openapi_docs.py`: every path+method has
      summary, description, and examples; `info`/`externalDocs` fields
      present; spec passes openapi-spec-validator
- [ ] Add `openapi-spec-validator` + `pyyaml` to backend `[dev]` extra

## Verification (first release after Bolt 4)

- [ ] Release run attaches valid `openapi.json` + `openapi.yaml` to the
      GitHub Release; version matches the tag; assets import cleanly
      into Postman — record evidence here
- [ ] Status → **verified**, then archive
