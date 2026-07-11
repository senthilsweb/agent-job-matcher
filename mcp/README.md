# jobmatcher-mcp

MCP access to agent-job-matcher (see `openspec/adr/0001` for the architecture).

Two pieces, one tool surface:

- **`index.js`** — the MCP server (stdio, Node ≥18). A pure bridge: three
  tools (`analyze_job_fit`, `extract_jsonresume`, `health`) that pass
  through to the backend REST API. No business logic, no REST endpoints,
  no secrets.
- **`agent-service/`** — the chat REST bridge (FastAPI). Hosts the LLM
  orchestration loop (pydantic-ai + this MCP server) behind the
  ctms-compatible contract: `POST /chat/stream` (SSE), `POST /upload`,
  `GET /health`. This is what the neutral chatbot connects to.

## Run

```bash
# 1. Backend API (from repo root; needs .env configured)
uvicorn job_matcher.api:app --port 8000

# 2a. Claude Desktop — paste configs/claude-desktop.json (fix the path)
# 2b. Chatbot — start the agent service:
uvicorn app:app --app-dir mcp/agent-service --port 8006
#     then point the chatbot at it: VITE_API_ENDPOINT=http://127.0.0.1:8006

# smoke test the MCP server (stub backend, no LLM):
cd mcp && npm install && npm test
```

## Env

| Var | Used by | Default |
|---|---|---|
| `JOBMATCHER_API_URL` | index.js, agent-service | `http://localhost:8000` |
| `MODEL_CHAT` → `MODEL_ANALYST` → `MODEL` | agent-service (LLM-2) | — (required) |
| `AGENT_UPLOAD_DIR` | agent-service `/upload` | system temp dir |
| `AGENT_PORT` | agent-service | 8006 |
