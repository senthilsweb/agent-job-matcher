# Design — `add-demo-stack-and-playground`

## 1. `mcp-chat-client` Docker image

**Model:** this repo's own `Dockerfile` (single-stage Python) is not the
right template — `mcp-chat-client` has no backend of its own, it's a
static site once built. The closer model is `privacyshield`'s **first
stage** (Node build → static output), paired with an `nginx:alpine`
runtime stage instead of privacyshield's Python runtime stage (it has
no second-stage backend to serve).

```dockerfile
# Stage 1: build the demo page (Vite)
FROM node:20-alpine AS builder
WORKDIR /web
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build            # existing script; builds src/main.tsx (demo) to dist/

# Stage 2: static runtime
FROM nginx:alpine
COPY --from=builder /web/dist /usr/share/nginx/html
COPY docker/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY docker/entrypoint.sh /docker-entrypoint.d/40-runtime-config.sh
```

**Runtime-configurable agent-service URL, without rebuilding the
image.** Vite's `import.meta.env.VITE_*` is baked in at build time,
which would tie the published image to one hardcoded agent-service
URL — wrong for a demo image meant to be pointed at whatever agent-
service is running in the same compose stack (or a remote one). Fix:
a tiny runtime-config script, the standard static-SPA pattern:

- `docker/entrypoint.sh` (runs via nginx's official
  `/docker-entrypoint.d/` hook, which already supports shell scripts
  before nginx starts) writes `/usr/share/nginx/html/runtime-config.js`:
  ```js
  window.__MCP_CHAT_CONFIG__ = { agentServiceUrl: "${AGENT_SERVICE_URL}" };
  ```
  using `envsubst`, reading the container's `AGENT_SERVICE_URL` env var
  (default `http://localhost:8006`, overridable per compose service).
- `index.html` gains one `<script src="/runtime-config.js"></script>`
  tag before the app bundle.
- `src/demo/constants.ts` (already the single source of the demo's
  config) reads `window.__MCP_CHAT_CONFIG__?.agentServiceUrl ??
  import.meta.env.VITE_AGENT_SERVICE_URL ?? 'http://localhost:8006'` —
  local `npm run dev` is unaffected (no `window.__MCP_CHAT_CONFIG__` in
  dev, falls through to the existing Vite env var / default), the
  container path is additive.

**GHCR workflow:** copy `agent-job-matcher/.github/workflows/build-and-
publish.yml`'s shape (checkout → buildx → GHCR login using
`GITHUB_TOKEN` → build+push tagged `ghcr.io/senthilsweb/mcp-chat-
client`, amd64 minimum, GHA layer cache) into `mcp-chat-client/.github/
workflows/`, triggered the same way (tag push / release, matching that
repo's existing `release.yml` semantic-release flow so the image tag
tracks the same version).

## 2. `playground/` (Next.js)

**Stack decision:** plain Next.js (App Router) + Tailwind + **shadcn/ui
this time** — unlike `mcp-chat-client`'s widget, this is a normal
compiled React app with no runtime HTML-injection constraint (that
constraint was specific to rendering LLM-generated HTML strings via
`dangerouslySetInnerHTML` inside a Shadow-DOM-free widget bundle), so
shadcn's copy-in component source compiles normally. Use `Card`,
`Accordion`, `Button`, `Input`, `Progress`/`Badge` primitives from
shadcn as the base, themed with the Slack-purple ramp (same values as
`privacyshield`'s `tailwind.config.ts`).

**Layout** (privacyshield pattern — collapsible left sidebar, main
content area):

- Left sidebar: file drop-zone (`resume`, accepts pdf/docx/txt/md —
  mirrors `SUPPORTED_EXTENSIONS` from the backend), a dynamic list of
  job-link text inputs with add/remove row controls (at least one
  required), Submit button (disabled until resume + ≥1 job present).
- On submit: builds a `FormData` with `resume` (file) and repeated
  `jobs` fields, `POST`s directly to the backend's existing `/analyze`
  (`NEXT_PUBLIC_API_URL`, default `http://localhost:8000` — same
  runtime-config-vs-build-time consideration as above, but Next.js
  server-rendering makes this simpler: read `process.env.API_URL` in a
  server action/route handler that proxies the multipart POST, so the
  browser never needs to know the backend's container-network address
  — avoids a second runtime-config shim).
- Right pane: results as a **carousel of compact cards**, one per job
  in the response array — each card shows: job title (from the job
  source, truncated), match-band badge (color-coded 1:1 from
  `job_matcher.schemas.MatchStatus`'s five literal values —
  `strong_match`=brand-700, `good_match`=emerald, `moderate_match`=amber,
  `weak_match`=orange, `no_match`=red — never invented bands or colors),
  total score as a large number + a compact horizontal bar for the
  four sub-scores (`required_skills_score` [0-60, reallocates the
  preferred budget when a job has no preferred skills — render the bar
  against its actual scale, not a fixed 40], `preferred_skills_score`,
  `experience_score`, `domain_score` [each 0-20] — the exact breakdown
  the backend computes in `ScoreBreakdown`, never re-derived client-side).
  Clicking a card (or its header, in accordion mode) expands in place
  to show the full report: evidence quotes per matched skill, gaps,
  and the raw score breakdown — collapsing any other expanded card
  (single-expand accordion behavior, like the reference "Grafana
  panel" pattern: dense collapsed grid, one focused expanded view).
- Empty/loading/error states: skeleton cards while the request is in
  flight (this can be tens of seconds — job fetch + LLM extraction per
  job), a clear error card per job that individually failed (the
  backend's response is a typed array; a single job's fetch failure
  must not blank out the others).

**Why a client-side-only static consumer of `/analyze` and not the
chat/MCP path:** the ask is explicitly a form-and-report UI, not a
chat UI (that already exists via `mcp-chat-client`) — this reuses the
plain REST surface, zero new backend code, per "Out of scope."

## 3. `openapi-docs/` (Next.js) — separate "virtual directory"

A second, independent Next.js app (own `package.json`, own container),
not a route inside `playground/` — the "virtual directories" phrasing
means: served at its own path/port, so it can be reverse-proxied or
linked independently of the playground. Renders the backend's
`/openapi.json` (fetched server-side at request time from
`API_URL`, so it always reflects whatever backend the docs container
points at) through **Scalar's `@scalar/nextjs-api-reference`** (a
themeable, MIT-licensed OpenAPI renderer with first-class Next.js
support) rather than hand-building a Swagger UI clone — same
"reuse, don't reimplement" principle as the rest of this repo
(AGENTS.md preamble). Themed with the same Slack-purple accent color
via Scalar's config `theme`/custom CSS variables, so the two new apps
read as one demo suite rather than visually unrelated tools. This is
in addition to, not a replacement for, FastAPI's built-in `/docs` —
that stays as the zero-setup Swagger UI for anyone hitting the API
directly; `openapi-docs/` is the branded, standalone experience for the
demo stack.

## 4. `docker-compose.yaml` wiring

Extends the existing root compose (already has `api`, `cli`). New
services, each built from its own subfolder's Dockerfile:

```yaml
  chat-demo:
    image: ghcr.io/senthilsweb/mcp-chat-client:latest
    build: { context: ../mcp-chat-client }   # local override path; see note below
    environment:
      AGENT_SERVICE_URL: ${AGENT_SERVICE_URL:-http://localhost:8006}
    ports: ["8081:80"]

  playground:
    build: { context: ./playground }
    environment:
      API_URL: ${API_URL:-http://api:8000}   # container-network name, not localhost
    ports: ["3001:3000"]
    depends_on: [api]

  openapi-docs:
    build: { context: ./openapi-docs }
    environment:
      API_URL: ${API_URL:-http://api:8000}
    ports: ["3002:3000"]
    depends_on: [api]
```

**Open question flagged, not blocking:** `mcp-chat-client` lives in a
sibling repo, not a subfolder of this one, so `build: {context:
../mcp-chat-client}` only works for a co-located local checkout. The
compose file's primary path is the **published `image:`** (matching
this repo's existing `api`/`cli` services, which already default to
the GHCR image with `build: .` as a local-override convenience) — the
same pattern applies here, `build:` is best-effort/documented as
"only if you have both repos checked out side by side," not the
demo's primary path.

## 5. README additions

- **REST endpoints table**: one row per route already implemented in
  `api.py`/`app.py` (`POST /analyze`, `POST /resume/jsonresume`, `GET
  /health` on the backend; `POST /chat/stream`, `POST /upload`, `GET
  /health` on the agent service) — method, path, one-line purpose,
  link to the fuller OpenAPI description. Generated by hand from the
  current routes (small, stable set), not scripted — matches the
  existing "Surfaces" table's style already in the README.
- **Key environment variables**: a grouped table (model/keys,
  pipeline, telemetry, agent-service/upload) — a curated subset of
  `.env.example`, not a restatement of every line; links to
  `.env.example` for the full list.
- **Cover letter templates**: documents the package-default
  `job_matcher/templates/cover_letter.txt`, its placeholders
  (`{{candidate_name}}`, `{{candidate_contact_line}}`, `{{date}}`,
  `{{re_line}}`, `{{cover_letter_body}}`), and the actual override
  mechanism confirmed in `prompts.py`: the `TEMPLATES_DIR` env var
  (checked before the package default; same resolution order used for
  prompts) — drop a `cover_letter.txt` there to override without
  touching source.
