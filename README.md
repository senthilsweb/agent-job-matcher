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
docker compose up -d api                  # FastAPI on :8000
```

## Surfaces

| Surface | Entry | Notes |
|---|---|---|
| CLI | `jobmatch analyze`, `jobmatch jsonresume` | persists runs to disk, exit 0 for completed runs |
| REST | `POST /analyze`, `POST /resume/jsonresume`, `GET /health` | stateless; typed JSON array payload; OpenAPI spec attached to every [release](https://github.com/senthilsweb/agent-job-matcher/releases) |
| Python | `from job_matcher import run_analysis, score_job_fit, extract_jsonresume` | the embeddable core for in-process agents |
| Chat | `mcp/` — MCP server (Claude Desktop) + agent service (`/chat/stream`, `/upload`) | see [mcp/README.md](mcp/README.md) |

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
