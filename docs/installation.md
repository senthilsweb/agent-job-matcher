# Installation

At the end you will have your preferred way to run agent-job-matcher:
a local pip install, the published Docker image, or the fully
containerized demo stack. Every path starts with the same `.env`
bootstrap:

```bash
git clone https://github.com/senthilsweb/agent-job-matcher && cd agent-job-matcher
cp .env.example .env      # then fill in the values you need
```

No configuration or credential ever ships in source — a missing
required value is a clear startup error, on purpose (AGENTS.md rule 5).

## Option A — pip (CLI, Python package, local dev)

Python 3.11+:

```bash
pip install -e "backend[dev]"
jobmatch --help
pytest backend -m "not live"    # offline suite proves the install, no API key needed
```

This gives you the `jobmatch` CLI and the embeddable core
(`from job_matcher import run_analysis, score_job_fit,
extract_jsonresume`). Add the `[otel]` extra if you plan to use an
OTLP-shaped telemetry backend
([Configuration](configuration.md#telemetry-activates-by-env-alone)).

## Option B — the Docker image

Published to GHCR by CI on every push to main and on version tags:

```bash
docker pull ghcr.io/senthilsweb/agent-job-matcher:latest
docker run --rm --env-file .env ghcr.io/senthilsweb/agent-job-matcher:latest --help
```

Or through compose, backend only:

```bash
docker compose up -d api                 # FastAPI on :6010
docker compose run --rm cli version      # the CLI through the same image
```

## Option C — the full demo stack

Every piece containerized, one consistent 6010-series port each:

```bash
docker compose up -d
# api            http://localhost:6010  — REST backend
# agent-service  http://localhost:6011  — chat bridge (LLM-2 + the MCP server inside)
# playground     http://localhost:6012  — resume + job links -> visual fit reports
# openapi-docs   http://localhost:6013  — browsable, branded API reference
# chat-demo      http://localhost:6014  — the mcp-chat-client chatbot demo page
```

The chat demo uses the
[mcp-chat-client](https://github.com/senthilsweb/mcp-chat-client)
widget — a runtime dependency, already baked into its container.

## Claude Desktop (MCP)

The MCP server (`mcp/`) is a pure stdio bridge to the REST API — point
Claude Desktop at it and the backend must be reachable. Setup and the
tool list:
[mcp/README.md](https://github.com/senthilsweb/agent-job-matcher/blob/main/mcp/README.md).

Next: [Configuration](configuration.md).
