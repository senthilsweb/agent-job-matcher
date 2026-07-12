# Spec: `docker-compose.yaml` demo-stack wiring

## Requirement: The full demo surface comes up with one command
The root `docker-compose.yaml` SHALL gain three services —
`chat-demo` (the containerized `mcp-chat-client` image),
`playground`, and `openapi-docs` — alongside the existing `api`/`cli`
services, each on a distinct published port, such that `docker compose
up -d` (with a filled `.env`) brings up the entire demo surface with no
manual steps beyond environment configuration.

## Requirement: Published images are the primary path; local build is a documented convenience
Each new service SHALL default to its published `ghcr.io/senthilsweb/...`
image (matching the existing `api`/`cli` services' pattern), with a
`build:` block as a local-override convenience for contributors who
have the relevant source checked out — documented inline as such, not
presented as the primary path (`mcp-chat-client` in particular lives in
a sibling repo, so its local `build:` context only resolves for a
side-by-side checkout).

## Requirement: Inter-service addressing uses the compose network, not localhost
`playground` and `openapi-docs` SHALL reach the backend via the
compose network service name (e.g. `http://api:8000`), not
`localhost`, by default — configurable via env var override for
running any of the three demo services against an external/non-
compose backend.

## Requirement: No secrets committed in the compose file
All new services' environment blocks SHALL follow the existing file's
convention: `${VAR:-default}` interpolation from the root `.env`, empty
defaults for anything sensitive, never a literal credential.
