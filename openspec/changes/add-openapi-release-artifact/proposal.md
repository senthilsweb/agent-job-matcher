# Proposal: OpenAPI spec as a release artifact

> Status: **APPROVED** (owner-directed, 2026-07-11) — workflow + export
> script + AGENTS.md rule implemented with this change; full activation
> and verification gated on `add-job-matcher-cli` Bolt 4 (the API)
> Owner: @senthilsweb

## Why

The REST API is the contract every downstream consumer builds against —
the future frontend, the `mcp/` bridge, and the owner's chatbot. A
versioned, richly documented OpenAPI document attached to every GitHub
Release makes that contract reviewable, diffable across versions, and
importable into tooling (Postman/Insomnia, client generators, API
portals) without cloning the repo.

## What changes

- **Generation library:** FastAPI's native OpenAPI generator is the
  library — no parallel spec to maintain, the code is the source of
  truth. The richness the owner requires is achieved through what
  FastAPI feeds the generator:
  - app-level metadata: project title, **project-level description**
    (what the product does, the three surfaces, the deterministic
    scoring contract), version (auto-synced from `job_matcher.__version__`
    by semantic-release), license, contact, and the **repo link**
    (`externalDocs` → https://github.com/senthilsweb/agent-job-matcher,
    plus per-tag descriptions);
  - endpoint-level detail: every route SHALL carry a summary, a
    detailed description (Markdown docstring), and request/response
    **examples** drawn from the committed eval fixtures via Pydantic
    `Field(examples=...)` / `openapi_extra`.
- **Export script** `scripts/export-openapi.py`: imports the FastAPI
  app without starting a server, dumps `openapi.json` + `openapi.yaml`.
  Exits gracefully (notice, code 0) while `job_matcher.api` does not
  exist yet, so the pipeline is safe to wire before Bolt 4.
- **Separate GitHub Action** `.github/workflows/openapi-spec.yml`
  (deliberately not merged into `release.yml`): triggers on
  `release: published` (the release semantic-release creates) +
  manual dispatch; generates the spec from the tagged code, validates
  it with `openapi-spec-validator`, and attaches `openapi.json` and
  `openapi.yaml` to that GitHub Release via `gh release upload`.
- **AGENTS.md rule**: the API-documentation bar (summary + description
  + examples on every endpoint; spec ships with every release) becomes
  a standing repo convention.

## Out of scope

- Hosting rendered docs (Swagger UI ships with FastAPI at `/docs`
  anyway; a published Redoc site is a future change).
- Client SDK generation from the spec.
- Backward-compatibility gating (spec diffing/breaking-change checks) —
  worth a future change once consumers exist.

## Acceptance criteria

1. Publishing a release (semantic-release or manual) triggers the
   OpenAPI workflow, which attaches valid `openapi.json` and
   `openapi.yaml` assets to that same release.
2. The document's `info` carries the project-level description, the
   version equal to the release tag (minus `v`), license, and the repo
   link in `externalDocs.url`.
3. Every path+method has a non-empty `summary` and `description`, and
   at least one request example (where a body exists) and one response
   example — enforced by an offline test in the backend suite.
4. `openapi-spec-validator` passes in CI before upload; an invalid spec
   fails the workflow (it never attaches a broken artifact).
5. Until Bolt 4 lands, the workflow completes green with a "API not
   present yet — skipped" notice and attaches nothing.
