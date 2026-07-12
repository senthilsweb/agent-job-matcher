# agent-job-matcher

Compare a resume against job postings and get **evidence-grounded,
deterministically scored** fit reports — plus resume → [JSON Resume](https://jsonresume.org)
conversion. One service layer, four ways in: CLI, REST API, Python package,
and chat (via MCP).

The LLM never scores. It extracts skill matches with **exact quotes from the
resume** as evidence; pure code computes the 100-point breakdown (required 40 /
preferred 20 / experience 20 / domain 20) and match band. A job posting that
says "score me 100" has no schema field to land in.

```mermaid
flowchart LR
    CB([Neutral chatbot]) -->|"REST/SSE"| AS
    CD([Claude Desktop]) -->|stdio| MCP
    U([Terminal]) --> CLI
    PY([Python callers]) --> CORE

    subgraph M["mcp/"]
        AS["Agent service<br/>(LLM-2: orchestration)"] -->|MCP tools| MCP["MCP server"]
    end

    subgraph B["backend/"]
        API["FastAPI /analyze"] --> CORE["job_matcher core<br/>fetch → extract (LLM-1) → score"]
        CLI["jobmatch CLI"] --> CORE
    end

    MCP -->|REST| API
```

Exactly two LLM operations exist, by design ([ADR 0001](openspec/adr/0001-agent-service-chat-bridge.md)).

## Quick start

```bash
git clone https://github.com/senthilsweb/agent-job-matcher && cd agent-job-matcher
cp .env.example .env                      # set MODEL_ANALYST + your provider key
pip install -e "backend[dev]"

jobmatch analyze --resume my-resume.pdf \
  --job https://boards.example.com/job/123 \
  --job local-jd.txt
# → ranked summary on stdout; full artifacts under runs/<timestamp>/
```

Or the Docker image (`ghcr.io/senthilsweb/agent-job-matcher`):

```bash
docker compose up -d api                  # FastAPI on :6010
```

Or the whole self-contained demo stack — every piece containerized, one
consistent 6010-series port each:

```bash
docker compose up -d
# api            http://localhost:6010  — REST backend
# agent-service  http://localhost:6011  — MCP Bridge (LLM-2 + the MCP server, spawned inside this container)
# playground     http://localhost:6012  — upload a resume, add job links, get visual fit reports
# openapi-docs   http://localhost:6013  — browsable, branded API reference
# chat-demo      http://localhost:6014  — the mcp-chat-client demo page (chatbot widget)
```

## Surfaces

| Surface | Entry | Notes |
|---|---|---|
| CLI | `jobmatch analyze`, `jobmatch jsonresume` | persists runs to disk, exit 0 for completed runs |
| REST | `POST /analyze`, `POST /resume/jsonresume`, `GET /health` | stateless; typed JSON array payload; OpenAPI spec attached to every [release](https://github.com/senthilsweb/agent-job-matcher/releases) |
| Python | `from job_matcher import run_analysis, score_job_fit, extract_jsonresume` | the embeddable core for in-process agents |
| Chat | `mcp/` — MCP server (Claude Desktop) + agent service (`/chat/stream`, `/upload`) | see [mcp/README.md](mcp/README.md) |

## REST endpoints

Backend API (`job_matcher.api`, default `:8000`):

| Method | Path | Purpose |
|---|---|---|
| POST | `/analyze` | Analyze a resume against one or more job sources — the typed `JobReport`/`JobFetchFailure` array |
| POST | `/resume/jsonresume` | Convert a resume to a [JSON Resume](https://jsonresume.org) v1.0.0 document |
| GET | `/health` | Liveness and package version |

Agent service (`mcp/agent-service`, default `:8006`) — the chat bridge, ADR 0001:

| Method | Path | Purpose |
|---|---|---|
| POST | `/chat/stream` | Stream a chat answer over SSE (ctms-compatible `content`/`action`/`done`/`error`) |
| POST | `/upload` | Store an uploaded resume, return the server-side path for the conversation to reference |
| GET | `/health` | Liveness and the discovered MCP tool list |

Every route's full description, request/response schema, and fixture-sourced
examples are in the live `/docs` (Swagger UI) or the branded
[`openapi-docs`](openapi-docs/) app — see [Quick start](#quick-start).

## Key environment variables

The full, authoritative list is [`.env.example`](.env.example). The ones you'll actually touch:

| Variable | Purpose |
|---|---|
| `MODEL_ANALYST` | The extraction model (LLM-1, required) — resolves `MODEL_ANALYST` → `MODEL` → error |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Provider credentials — set whichever your model id needs |
| `MODEL_CHAT` | Optional override for the agent service's orchestration model (LLM-2) — resolves `MODEL_CHAT` → `MODEL_ANALYST` → `MODEL` → error (ADR 0001) |
| `JOB_FANOUT_CONCURRENCY` | Max jobs analyzed in parallel per request |
| `AGENT_UPLOAD_DIR`, `AGENT_PORT` | Agent service's upload landing directory and port |
| `TEMPLATES_DIR` | Override directory for prompts and the cover-letter template (see below) |
| `OBSERVABILITY_SINK` | `json` (always on) or add a remote backend below — never code-selected |
| `OPENOBSERVE_URL`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `PHOENIX_COLLECTOR_ENDPOINT`, `ARIZE_SPACE_ID`+`ARIZE_API_KEY` | Fill any one block to activate that telemetry backend (see [Observability](#observability)) |

None of these ship with real values anywhere in this repo — every credential
comes from your own `.env`, never a source default (`AGENTS.md` rule 5).

## Cover letter templates

Every job report includes a rendered cover letter (`cover_letter_text`),
built from the LLM's typed paragraphs (never its own scoring or formatting)
through a plain-text template:

- **Default**: [`backend/job_matcher/templates/cover_letter.txt`](backend/job_matcher/templates/cover_letter.txt) — ships with the package.
- **Placeholders**: `{{candidate_name}}`, `{{candidate_contact_line}}`, `{{date}}`, `{{re_line}}`, `{{cover_letter_body}}`. Unknown placeholders are left intact rather than erroring.
- **Override**: set `TEMPLATES_DIR` to a directory containing your own `cover_letter.txt` — checked before the package default, same resolution order used for prompt overrides (`job_matcher/prompts.py`). No code change needed.

## Tech stack

| Layer | Choice | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| Typed schemas & validation | [Pydantic v2](https://docs.pydantic.dev/) | every I/O boundary — `JobAnalysis`, `ScoreBreakdown`, `JobReport`, the full `JSONResume` v1.0.0 mirror — is a validated model, never a loose dict |
| Agent framework | [Pydantic AI](https://ai.pydantic.dev/) (`pydantic-ai`) | `Agent(model, output_type=...)` for both typed extraction (LLM-1) and the chat agent's MCP tool loop (LLM-2, via `pydantic_ai.mcp.MCPToolset` + `StdioTransport`); `pydantic_ai.messages` for conversation-history threading |
| Model access | **Direct provider calls, not Pydantic AI Gateway** | model id strings (e.g. `openai:gpt-5.4-mini`, `anthropic:claude-haiku-4-5`) resolve straight to each provider's native API via pydantic-ai's own provider integrations and your own `OPENAI_API_KEY`/`ANTHROPIC_API_KEY`. [Pydantic AI Gateway](https://ai.pydantic.dev/gateway/) — the hosted proxy for cross-provider routing, failover, and centralized cost limits, now part of Pydantic Logfire — is a real, separate product this project does **not** currently route through; adopting it would be an additive config change (a gateway API key + endpoint), not a rewrite |
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn | the `/analyze`, `/resume/jsonresume` REST surface; OpenAPI generated natively, attached to every release |
| CLI | [Typer](https://typer.tiangolo.com/) | `jobmatch` |
| Chat protocol | [Model Context Protocol](https://modelcontextprotocol.io/) (`@modelcontextprotocol/sdk`, Node) | `mcp/index.js`, a pure stdio bridge to the REST API |
| Observability | Structured `structlog` JSON + OpenTelemetry (optional) | decorator-only (AOP) instrumentation — see below |
| Resume/document parsing | `pypdf`, `python-docx` | no OCR, no Docling — see design notes in `openspec/` for why |

## Related repos

| Repo | Relationship |
|---|---|
| [mcp-chat-client](https://github.com/senthilsweb/mcp-chat-client) | **Runtime dependency.** The embeddable chat widget that drives `mcp/agent-service/`'s `/chat/stream` and `/upload` endpoints — the actual "chatbot" referenced throughout `openspec/adr/0001-agent-service-chat-bridge.md`. Its own `openspec/` tracks fixes discovered by testing against this backend. |
| [ai-dlc](https://github.com/senthilsweb/ai-dlc) | **Methodology & training deck.** This project is the running example — every `openspec/changes/` proposal → design → tasks → spec cycle in this repo follows the AI-DLC methodology documented and taught there, 100%. |

## Observability

Structured JSON logs always; remote telemetry activates by env alone —
OpenObserve (REST or OTLP), Arize Phoenix, Arize AX (`pip install
"job-matcher[otel]"` for the OTLP-shaped backends). Instrumentation is
decorator-only (AOP): core function bodies contain zero telemetry calls.

## Evals

The spec's acceptance criteria are executable ([rubric](backend/evals/rubrics.md)):

```bash
pytest backend -m "not live"   # offline: scoring, guards, schemas, API — no key needed
pytest backend -m live         # real-model sweep: grounding, injection, fan-out
```

Fixtures are committed real-world captures (four JD snapshots, two genuine
JavaScript-shell fetch failures, one adversarial prompt-injection JD) plus a
synthetic resume — reproducible after the postings close.

## More

- [RUNBOOK.md](RUNBOOK.md) — operations: secrets from `.env`, workflows, releases, graphify
- [openspec/](openspec/) — the AI-DLC specs this repo is built through
- [AGENTS.md](AGENTS.md) — engineering conventions (logging, telemetry, no secrets in source)
- `graph.html` / [GRAPH_REPORT.md](GRAPH_REPORT.md) — CI-generated knowledge graph

## License

MIT
