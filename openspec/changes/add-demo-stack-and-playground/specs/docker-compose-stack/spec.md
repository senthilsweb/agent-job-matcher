# Spec: `docker-compose.yaml` demo-stack wiring

## Requirement: The full demo surface comes up with one command
The root `docker-compose.yaml` SHALL gain four services — `agent-service`
(the containerized MCP Bridge, hosting the MCP server as a stdio
subprocess — it has no port of its own), `chat-demo` (the containerized
`mcp-chat-client` image), `playground`, and `openapi-docs` — alongside
the existing `api`/`cli` services, each on a distinct published port,
such that `docker compose up -d` (with a filled `.env`) brings up the
entire demo surface with no manual steps beyond environment
configuration.

## Requirement: Published ports are a single, verified-safe consistent range
Every service's published port SHALL come from one contiguous range,
chosen to avoid both this machine's other locally-running services and
any port on the WHATWG Fetch "bad ports" blocklist (which Node's
native `fetch()` and every browser silently refuse to connect to —
6000 and 6665-6669/6697 are blocked; verified via `docker exec ...
node -e "fetch(...)"` after picking a bad port broke a real health
check). Currently: `api` 6010, `agent-service` 6011, `playground` 6012,
`openapi-docs` 6013, `chat-demo` 6014.

## Requirement: Published images are the primary path; local build is a documented convenience
Each new service SHALL default to its published `ghcr.io/senthilsweb/...`
image (matching the existing `api`/`cli` services' pattern), with a
`build:` block as a local-override convenience for contributors who
have the relevant source checked out — documented inline as such, not
presented as the primary path (`mcp-chat-client` in particular lives in
a sibling repo, so its local `build:` context only resolves for a
side-by-side checkout).

## Requirement: Inter-service addressing uses the compose network, not localhost
`playground`, `openapi-docs`, and `agent-service` SHALL reach the
backend via the compose network service name (e.g. `http://api:6010`),
not `localhost`, by default; `chat-demo` SHALL reach `agent-service`
the same way (`http://agent-service:6011`) rather than
`host.docker.internal`. All SHALL be configurable via env var override
for running any demo service against an external/non-compose backend.

## Requirement: No secrets committed in the compose file
All new services' environment blocks SHALL follow the existing file's
convention: `${VAR:-default}` interpolation from the root `.env`, empty
defaults for anything sensitive, never a literal credential.
