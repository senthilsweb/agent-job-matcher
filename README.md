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

## I want to… → run this

```bash
git clone https://github.com/senthilsweb/agent-job-matcher && cd agent-job-matcher
cp .env.example .env                      # set MODEL_ANALYST + your provider key
```

| I want to… | Run this |
|---|---|
| See a visual fit report in 5 minutes | `docker compose up -d` → http://localhost:6012 — [Getting Started](docs/getting-started.md) |
| Analyze from the terminal | `pip install -e "backend[dev]"` then `jobmatch analyze --resume my-resume.pdf --job <url>` |
| Call the REST API | `docker compose up -d api` → `POST :6010/analyze` — [Surfaces](docs/surfaces.md) |
| Use it from Claude Desktop | the MCP server — [mcp/README.md](mcp/README.md) |
| Embed it in Python | `from job_matcher import run_analysis` — [Surfaces](docs/surfaces.md) |
| Configure models, telemetry, templates | [Configuration](docs/configuration.md) |
| Operate it (secrets, releases, CI) | [Runbook](docs/runbook.md) |

## Documentation

The wiki lives in [docs/](docs/) and is published at
<https://senthilsweb.github.io/agent-job-matcher/>:

- [Home](docs/index.md) — how the pieces fit, tech stack, related repos
- [Getting Started](docs/getting-started.md) — three 5-minute paths in
- [Installation](docs/installation.md) — pip, Docker image, or the full demo stack
- [Configuration](docs/configuration.md) — every env var, model resolution, template overrides
- [Surfaces](docs/surfaces.md) — CLI, REST (both services' endpoints), Python, chat/MCP
- [Runbook](docs/runbook.md) — workflows, secrets, releases, tests, graphify
- [FAQ](docs/faq.md) — why the LLM never scores, and more, linked to specs

Docs follow the shared
[documentation style guide](https://senthilsweb.github.io/ai-agents/style-guide/).
Engineering conventions for contributors: [AGENTS.md](AGENTS.md).
Specs: [openspec/](openspec/) (AI-DLC — this repo is the
[ai-dlc](https://github.com/senthilsweb/ai-dlc) running example).

## Layout

    .env              all secrets/config — never committed
    backend/          Python GenAI backend (CLI + FastAPI + embeddable core)
    mcp/              Node MCP server + agent-service (chat bridge, LLM-2)
    playground/       visual demo form (resume + job links -> fit reports)
    openapi-docs/     branded, browsable API reference
    docs/             the wiki (see Documentation above)
    openspec/         AI-DLC change specs and ADRs
    graph*.json       CI-generated knowledge graph — never edit by hand

## License

MIT
