# syntax=docker/dockerfile:1.6
# =====================================================================
# agent-service — the MCP Bridge (ADR 0001, Bolt 8), containerized.
#
# Hosts LLM-2 (chat orchestration) and the MCP client loop. The MCP
# server itself (mcp/index.js) has no network interface of its own —
# it's a pure stdio bridge, spawned as a child process by this service
# via pydantic-ai's StdioTransport (see app.py's build_agent()). So this
# one image needs BOTH Python (FastAPI/pydantic-ai) and Node (to run
# index.js) — there is no separate "MCP container": the MCP server lives
# inside this container's process tree, not on its own port.
#
# Build context is the repo root (not mcp/), same as the root
# Dockerfile, so this can COPY both backend/ and mcp/ freely.
# =====================================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OPENSSL_armcap=0

# Node.js, to run mcp/index.js as a stdio subprocess.
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl gnupg ca-certificates \
 && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# job_matcher (config/logging/prompts/observability reuse — app.py
# imports these directly rather than re-implementing them).
COPY backend/ ./backend/
RUN pip install --upgrade pip \
 && pip install ./backend "cryptography<49"

# The MCP server + its one dependency.
COPY mcp/package.json mcp/package-lock.json ./mcp/
RUN cd mcp && npm ci --omit=dev --no-audit --no-fund
COPY mcp/index.js ./mcp/index.js

# The agent service itself.
COPY mcp/agent-service/app.py ./mcp/agent-service/app.py

RUN useradd --system --create-home --uid 1001 app \
 && mkdir -p /work/uploads && chown -R app:app /app /work
USER app

WORKDIR /app/mcp/agent-service
EXPOSE 6011
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "6011"]
