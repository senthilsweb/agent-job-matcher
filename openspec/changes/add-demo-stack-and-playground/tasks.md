# Tasks — `add-demo-stack-and-playground`

Specified 2026-07-12. Owner approved 2026-07-12 ("good to go"),
implementation order set by the owner: Bolt 1 → 3 → 4 → 2 → 5. **All
five bolts implemented and verified 2026-07-12.**

## Bolt 1 — `mcp-chat-client` public Docker image ✅ (2026-07-12)

- [x] `mcp-chat-client/Dockerfile` — multi-stage: Node 20 build of the
      demo page (`npm run build` = `tsc && vite build` against the
      default `vite.config.ts`, i.e. the demo page, not the widget
      bundle) → `nginx:1.27-alpine` static runtime
- [x] `mcp-chat-client/docker/nginx.conf` + `docker/runtime-config.js.template`
      + `docker/entrypoint.sh` (installed as
      `/docker-entrypoint.d/40-runtime-config.sh`, nginx's official
      pre-start hook) — `envsubst`-generated `runtime-config.js`
      exposing `AGENT_SERVICE_URL` at container start; `.dockerignore` added
- [x] `src/lib/env.ts` — `apiEndpoint` reads
      `window.__MCP_CHAT_CONFIG__?.agentServiceUrl` first, falling
      through to `VITE_API_ENDPOINT` / the existing hardcoded default
      (dev server unaffected — the global is absent there);
      `src/vite-env.d.ts` declares the `Window` augmentation;
      `index.html` loads `/runtime-config.js` before the app bundle
- [x] `mcp-chat-client/.github/workflows/build-and-publish.yml` —
      modeled directly on `agent-job-matcher`'s existing workflow;
      publishes `ghcr.io/senthilsweb/mcp-chat-client`
- [x] `mcp-chat-client/openspec/changes/add-demo-stack-and-playground/`
      stub proposal — cross-references this spec (the driving change
      lives here since it's the "self-contained demo" requirement)
- [x] **Verification (2026-07-12, real `docker build`/`docker run`,
      not assumed):** built `mcp-chat-client:local` clean; ran it with
      `AGENT_SERVICE_URL=http://testhost:9999` — `GET
      /runtime-config.js` returned exactly
      `window.__MCP_CHAT_CONFIG__ = { agentServiceUrl:
      "http://testhost:9999" };`, `GET /` returned 200 with the
      `<script src="/runtime-config.js">` tag present in the served
      HTML, nginx access log confirmed both requests. Full chat round
      trip against a live agent-service not re-verified here (already
      proven working pre-container in `add-history-branding-and-
      release-assets`) — the container only changes how the endpoint
      URL is supplied, not the chat flow itself.

## Bolt 2 — `docker-compose.yaml` wiring (all three new services) ✅ (2026-07-12)

- [x] `chat-demo` (`:8091`), `playground` (`:3011`), `openapi-docs`
      (`:3012`) services added to the root compose file, per
      `specs/docker-compose-stack/spec.md`. Ports deliberately chosen
      to avoid this machine's many other locally-running compose
      projects (3001, 3030, 8081 etc. were all already taken by
      unrelated services) — picked free ports, not the first ones that
      came to mind
- [x] `playground`/`openapi-docs` default `API_URL` to the compose
      network hostname `http://api:8000`, not `localhost`; `chat-demo`
      defaults `AGENT_SERVICE_URL` to `http://host.docker.internal:8006`
      since no agent-service container exists yet (out of scope for
      this change) — documented inline in the compose file
- [x] `chat-demo`'s `build:` points at `../mcp-chat-client` (works only
      for a side-by-side checkout); the published `image:` is the
      primary path, matching the existing `api`/`cli` services'
      convention
- [x] **Verification (2026-07-12, real `docker compose up`/`down`, not
      assumed):** `docker compose config` validates the full resolved
      file with no errors. Brought up `playground` + `openapi-docs` via
      compose (`--no-deps`, `API_URL` overridden to
      `http://host.docker.internal:8000` to test against the
      already-running host backend without a port clash on the `api`
      service) — both returned 200; ran a real multipart `/analyze`
      request through the compose-managed playground's proxy route
      (Bain's "Expert Senior Manager, AI Engineering" JD, real score
      76/100) confirming the whole compose-networked path works, then
      tore the stack down cleanly.

## Bolt 3 — `playground/` Next.js app ✅ (2026-07-12)

- [x] Scaffold (`create-next-app` App Router + Tailwind v4 + shadcn/ui
      `init --defaults`) under `agent-job-matcher/playground/`. shadcn's
      current CLI defaults to the **Base UI** component library, not
      Radix (a "Select a component library" prompt now precedes the old
      Radix-only flow) — used as offered rather than forcing Radix
- [x] Slack-purple theme: Tailwind v4 is CSS-first (no
      `tailwind.config.js`) — the brand ramp and `--primary`/`--ring`
      overrides live in `app/globals.css`'s `@theme` block instead,
      same hex values as `privacyshield`
- [x] Left sidebar: `components/playground/resume-dropzone.tsx`
      (drag/drop + click, matches `SUPPORTED_EXTENSIONS`),
      `job-link-list.tsx` (dynamic add/remove rows), `sidebar-form.tsx`
      (disabled until resume + ≥1 non-empty link)
- [x] `app/api/analyze/route.ts` — server-side proxy, `API_URL` never
      reaches the browser; passes the backend's typed response through
      unmodified
- [x] `lib/types.ts` — hand-mirrors `job_matcher/schemas.py`'s
      `JobOutcome` union exactly (verified field-by-field against the
      real schema and a real API response, not assumed)
- [x] `components/playground/report-card.tsx` + `score-bar.tsx` +
      `results-panel.tsx`: compact cards, match-band badge colors 1:1
      from `MatchStatus`, sub-score bars scaled correctly (required's
      max is 60 only when `preferred_skills` is empty — confirmed
      against `scoring.py`'s actual reallocation rule, not guessed),
      single-expand accordion (Base UI's `Accordion` single-expands by
      **default** via `multiple: false` — its API has no Radix-style
      `type="single" collapsible` props, caught by reading the
      installed component's source before using it), per-job error
      isolation (`fetch_status: "failed"` renders a distinct disabled-
      style card, doesn't block the others)
- [x] `playground/Dockerfile` — Next.js `output: "standalone"` build,
      non-root user, `API_URL` read at request time
- [x] **Real bug found and fixed during verification (2026-07-12):**
      `ResumeDropzone`'s hidden `<input type=file>` is nested inside the
      clickable `<button>` (so the whole dropzone is one click target).
      The input's own click — triggered programmatically by the
      button's `onClick` — bubbles back up to that same button and
      re-invokes the handler a second, reentrant time on the same
      input; browsers silently drop both dialog-open attempts when that
      happens. Fixed with `onClick={(e) => e.stopPropagation()}` on the
      input.
- [x] **Environment finding (2026-07-12, not a code bug):** `next dev`
      (Turbopack) in this sandbox has a broken HMR WebSocket
      (`net::ERR_INVALID_HTTP_RESPONSE`) that also silently breaks
      React's click-event delegation for the whole page — confirmed
      with a minimal isolated counter-button reproduction (0 code, just
      `useState` + `onClick`) that also failed under `next dev` but
      worked correctly under a production `next build && next start`.
      All verification below therefore ran against the production
      build, which is also the actual Docker image's runtime mode.
- [x] **Verification (2026-07-12, real Playwright + a live backend +
      real LLM calls, not assumed):** (1) single-job submission —
      `synthetic-resume.pdf` + Gusto's Staff Software Engineer JD —
      rendered a collapsed card (80/100, "Strong match", correct
      36/9/20/15 sub-scores) and, on click, the fully expanded report
      (summary, required/preferred skill checklist, gaps,
      recommendation); (2) two-job submission, one deliberately
      pointed at a nonexistent path — rendered a distinct "Fetch
      failed" card alongside a normal successful card (76/100, "Good
      match", Anthropic's Data Engineering Manager role) with no
      cross-contamination; (3) the built Docker image, run standalone
      with `API_URL=http://host.docker.internal:8000`, correctly
      proxied a real `/analyze` call end-to-end to the host backend and
      returned the real score. Screenshots and raw responses captured
      during this session.

## Bolt 4 — `openapi-docs/` Next.js app ✅ (2026-07-12)

- [x] Scaffold under `agent-job-matcher/openapi-docs/`; installed
      `@scalar/nextjs-api-reference`. Its `ApiReference(config)` returns
      a route-handler function that renders a **complete HTML document
      itself** (not a React component) — so this app has no `page.tsx`
      at all; `app/route.ts` is a Route Handler at `/` that `fetch()`es
      `${API_URL}/openapi.json` server-side (container-network-safe,
      refetched on every request — never baked in at build time),
      passes the parsed JSON via Scalar's `content` field (not `url`,
      which would require the *browser* to reach the backend directly —
      wrong for the compose network), and returns the handler's
      Response. A 502 with a plain-text explanation renders if the
      backend fetch fails, instead of crashing
- [x] Slack-purple theme: Scalar's built-in `theme: "purple"` preset as
      a base, with a `customCss` override pinning
      `--scalar-color-accent` to the exact `#4a154b` (light) /
      `#a067a6` (dark) brand values — same hex ramp as the rest of the
      demo suite
- [x] `openapi-docs/Dockerfile` (Next.js standalone build, same shape
      as `playground/Dockerfile`)
- [x] **Verification (2026-07-12, real Playwright against the live
      backend, not assumed):** full page render confirms project
      title/description, `v0.4.0`/`OpenAPI 3.1.0` badges, all real
      routes in the sidebar with method badges; clicking into `POST
      /analyze` shows the full description, request body schema
      (`jobs`/`resume`/`resume_path`, required/nullable markers), a
      generated curl example, and a real 200 response example sourced
      from the committed eval fixtures (`run_id`, `job_title: "Senior
      Data Engineer"`, evidence quotes) plus the `422` case — matches
      what `/docs` already shows, branded distinctly. Also verified via
      the built Docker image standalone
      (`API_URL=http://host.docker.internal:8000`), title and content
      confirmed identical to the dev-server render.

## Bolt 5 — README additions ✅ (2026-07-12)

- [x] "REST endpoints" table — both backend (`/analyze`,
      `/resume/jsonresume`, `/health`) and agent-service (`/chat/stream`,
      `/upload`, `/health`) routes, confirmed against the actual
      `@app.get`/`@app.post` decorators in `api.py`/`app.py` (grepped,
      not recalled from memory)
- [x] "Key environment variables" section — grouped subset (model/keys,
      pipeline, agent-service, templates, telemetry), pointer to
      `.env.example` for the full list; `MODEL_ANALYST` vs. `MODEL_CHAT`
      fallback chains stated precisely per `config.py`'s
      `resolve_model()` (caught and fixed one drafting error: `MODEL_CHAT`'s
      chain was initially mis-attributed to the `MODEL_ANALYST` row)
- [x] "Cover letter templates" section — default template path,
      placeholders, and the `TEMPLATES_DIR` override, verified against
      `prompts.py`'s actual `load_template()`/`render()` (including the
      "unknown placeholders stay as-is" behavior, confirmed by reading
      the regex substitution function itself)
- [x] "Quick start" gained a third block for `docker compose up -d`
      (the full demo stack) with the three new services' ports and
      one-line descriptions; "Related repos" and "Surfaces" left as-is
      (already accurate — the new apps live in this repo, not as
      external related repos)

## Verification

- [x] Bolts 1-5 all implemented and individually verified with real
      builds, real containers, and real backend calls (see each bolt's
      evidence above) — no mocked or assumed behavior anywhere in this
      change
- [ ] Owner: final review pass, then status → **verified** and archive
      per convention. Two items deliberately remain outside this
      change's scope, unaffected: the agent-service is not yet
      containerized (chat-demo points at a host-run instance by
      default), and `mcp-chat-client`'s two previously-logged defects
      (history losing the uploaded-file reference; the action indicator
      not genuinely live) are still tracked separately in that repo's
      own openspec.
