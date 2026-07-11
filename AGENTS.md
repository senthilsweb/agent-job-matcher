# AGENTS — agent-job-matcher

Repo-level conventions. Every coding agent (and human) working anywhere in
this repo follows these; `backend/AGENTS.md` adds the Python-workspace
specifics. Every non-trivial change goes through `openspec/changes/<name>/`
first — see `openspec/project.md` for the AI-DLC lifecycle.

## Layout

```
agent-job-matcher/
├── .env              # all secrets/config — never committed (.gitignore enforces)
├── openspec/         # AI-DLC change specs; check status with /openspec-status
├── backend/          # Python GenAI backend (CLI + FastAPI + embeddable core)
├── frontend/         # later phase
├── scripts/          # repo automation (graphify)
└── graph*.json       # CI-generated knowledge graph — never edit by hand
```

## Common engineering requirements (all code, all languages)

1. **Custom structured logger everywhere.** No bare `print()` for
   diagnostics and no ad-hoc `logging.basicConfig` scattered per module.
   One shared logger factory produces structlog-style JSON lines (ISO
   timestamps, level, logger name) written to both stdout and a
   per-invocation file `./logs/<entry_point>_<YYYYmmdd_HHMMSS>.log`.
   Python specifics and the canonical snippet: `backend/AGENTS.md`.
2. **File-header comment convention.** Every source file opens with a
   header docstring/comment block: File Name, Author, Date, Description
   (with a numbered list of what the file does), and — for entry points —
   environment setup, requirements, and the environment variables it
   reads. Template in `backend/AGENTS.md`.
3. **Telemetry backends are env-activated, never code-selected.** Local
   JSON logs are always on. Setting a backend's own documented env vars
   is all it takes to add it to the fan-out: OpenObserve via REST
   (`OPENOBSERVE_URL...`, no extra deps), OpenObserve via OTLP or any
   collector (`OTEL_EXPORTER_OTLP_ENDPOINT`), Arize Phoenix
   (`PHOENIX_COLLECTOR_ENDPOINT`), Arize AX (`ARIZE_SPACE_ID` +
   `ARIZE_API_KEY`). The OTLP-shaped backends require the
   `job-matcher[otel]` extra. Vendor/OTel SDK imports are allowed **only
   inside the observability sink layer** — core and application code
   depend on the sink interface, nothing else. Telemetry delivery
   failures are logged and swallowed; they never fail a run.
4. **Instrumentation is aspect-oriented.** Trace/span/timing attach to
   methods only via decorators (`@traced`, `@timed`); core function
   bodies contain no instrumentation calls.
5. **No secrets or config in source.** All configuration, especially
   credentials (API keys, database passwords, service endpoints,
   authentication tokens) MUST come from the root `.env`, never as
   source defaults, placeholders, or fallback values. Missing required
   secrets/config is a clear startup error — this is the intended
   behaviour. Never commit a credential in code, comments, examples, or
   fallback defaults, not even marked as "example" or "placeholder".
6. **Typed contracts.** Data crossing any boundary (LLM output, API
   response, disk artifact) is a Pydantic-validated schema; API/CLI
   results are typed JSON arrays of those schemas.
7. **Per-request run identity, no workflow engine.** Each CLI or API
   request is its own unique run (`run_id`), but there is no workflow /
   run-management layer: no queues, no state machines, no run-browsing
   endpoints. CLI runs persist artifacts to disk; API runs return the
   payload.
