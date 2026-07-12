# Spec: `openapi-docs/` Next.js app

## Requirement: A separate, independently-routed Next.js app renders the API reference
`openapi-docs/` SHALL be its own Next.js app (own `package.json`, own
container/port) — not a route or tab within `playground/` — serving a
browsable, branded reference for the backend's OpenAPI document,
fetched server-side from `API_URL`'s `/openapi.json` at request time
so the rendered docs always reflect whichever backend the container
points at.

## Requirement: Reuse an existing OpenAPI renderer, don't hand-build one
The app SHALL render the spec using an existing, maintained OpenAPI UI
library with Next.js support (e.g. Scalar's `@scalar/nextjs-api-
reference`) rather than a hand-rolled Swagger-UI clone — consistent
with this repo's standing "reuse, don't reimplement" principle
(`AGENTS.md`).

## Requirement: Branded consistently with the rest of the demo suite
The renderer's theme SHALL be configured with the same Slack-purple
(`#4A154B`) accent used elsewhere in this change, so `playground/` and
`openapi-docs/` read as one coherent demo suite.

## Requirement: Additive to, not a replacement for, FastAPI's built-in docs
The backend's existing `/docs` (Swagger UI, generated natively by
FastAPI) SHALL remain unchanged and continue to work standalone;
`openapi-docs/` is an additional, branded, standalone experience for
the demo stack, not a migration away from the built-in docs.
