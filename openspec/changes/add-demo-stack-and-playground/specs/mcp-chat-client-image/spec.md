# Spec: `mcp-chat-client` public Docker image

## Requirement: A public GHCR image serves the demo page as a static site
The `mcp-chat-client` repo SHALL gain a multi-stage `Dockerfile`
(Node build stage → `nginx:alpine` runtime stage) that builds and
serves the existing demo page (`src/demo/DemoApp.tsx` + the embedded
widget) — not the embeddable npm/UMD library bundle, which remains a
GitHub Release asset only. The image SHALL be published to
`ghcr.io/senthilsweb/mcp-chat-client` by a GitHub Actions workflow
modeled directly on `agent-job-matcher`'s existing build-and-publish
workflow (same trigger shape, same amd64-minimum build, same GHA layer
caching).

## Requirement: The agent-service URL is runtime-configurable, not baked in
The container SHALL read an `AGENT_SERVICE_URL` environment variable at
**container start** (not image build time) and expose it to the
already-built static bundle via a generated `runtime-config.js` (an
nginx-entrypoint script using `envsubst`), so one published image can
be pointed at any agent-service instance without a rebuild. Local
`npm run dev` SHALL be unaffected — the demo's config resolution falls
through to the existing Vite env var / hardcoded default when no
`window.__MCP_CHAT_CONFIG__` is present.

## Requirement: No secrets in the image or its build context
The Dockerfile and workflow SHALL contain no credentials, API keys, or
placeholder secrets of any kind — consistent with this repo's existing
"verified clean, keep it that way" standing rule (`openspec/project.md`).
