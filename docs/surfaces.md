# Surfaces

At the end you will know all four ways into the same service layer and
which endpoints each one exposes. Whatever the surface, the result is
the same typed report: evidence quotes from the resume, a
code-computed 40/20/20/20 score, and a match band.

| Surface | Entry | Notes |
|---|---|---|
| CLI | `jobmatch analyze`, `jobmatch jsonresume` | persists runs to disk, exit 0 for completed runs |
| REST | `POST /analyze`, `POST /resume/jsonresume`, `GET /health` | stateless; typed JSON array payload |
| Python | `from job_matcher import run_analysis, score_job_fit, extract_jsonresume` | the embeddable core for in-process agents |
| Chat | MCP server (Claude Desktop, stdio) + agent service (REST/SSE) | see below |

## CLI

```bash
jobmatch analyze --resume my-resume.pdf --job <url-or-file> [--job ...]
jobmatch jsonresume --resume my-resume.pdf
```

Each invocation is its own run (`run_id`); artifacts persist under
`runs/<timestamp>/`. There is deliberately no run-management layer —
no queues, no state machines (AGENTS.md rule 7).

## REST — backend API

Default `:8000` natively, `:6010` in the compose stack.

| Method | Path | Purpose |
|---|---|---|
| POST | `/analyze` | analyze a resume against one or more job sources → typed `JobReport`/`JobFetchFailure` array |
| POST | `/resume/jsonresume` | convert a resume to a JSON Resume v1.0.0 document |
| GET | `/health` | liveness and package version |

The OpenAPI document is generated from the FastAPI app — never
hand-maintained — and attached to every
[GitHub Release](https://github.com/senthilsweb/agent-job-matcher/releases)
as `openapi.json`/`openapi.yaml`. Every endpoint ships with a summary,
a Markdown description, and request/response examples sourced from the
committed eval fixtures; an offline test fails the build if an
endpoint is undocumented (AGENTS.md rule 9). Browse it live at `/docs`
(Swagger UI) or the branded reference on `:6013`.

## REST — agent service (the chat bridge)

Default `:8006` natively, `:6011` in the compose stack. This is LLM-2:
it orchestrates chat and calls the backend through MCP tools — it
never scores
([ADR 0001](https://github.com/senthilsweb/agent-job-matcher/blob/main/openspec/adr/0001-agent-service-chat-bridge.md)).

| Method | Path | Purpose |
|---|---|---|
| POST | `/chat/stream` | stream a chat answer over SSE (`content`/`action`/`done`/`error` events) |
| POST | `/upload` | store an uploaded resume, return the server-side path for the conversation |
| GET | `/health` | liveness and the discovered MCP tool list |

The compatible chat widget is
[mcp-chat-client](https://github.com/senthilsweb/mcp-chat-client) — a
separate repo and a runtime dependency of the chat surface.

## Python

```python
from job_matcher import run_analysis, score_job_fit, extract_jsonresume
```

The embeddable core, for in-process agents. Data crossing every
boundary is a Pydantic-validated schema (`JobAnalysis`,
`ScoreBreakdown`, `JobReport`, the full JSON Resume v1.0.0 mirror) —
never a loose dict.

## Chat via Claude Desktop

The MCP server
([mcp/](https://github.com/senthilsweb/agent-job-matcher/tree/main/mcp))
is a pure stdio bridge: it exposes the REST API as MCP tools and holds
no logic of its own. Setup:
[mcp/README.md](https://github.com/senthilsweb/agent-job-matcher/blob/main/mcp/README.md).

Next: [Runbook](runbook.md).
