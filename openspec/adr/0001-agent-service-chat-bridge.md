# ADR 0001 — Agent service as the chat↔MCP bridge

> Status: **Accepted** — 2026-07-11 (owner)
> Relates to: `openspec/changes/add-job-matcher-cli/` revision 6
> Reference implementation: ctms-mcp-server `agent_service_mcp_client.py`
> (zynomi-projects)

## Context

The owner has an existing **neutral chatbot** (ctms-style web client)
that speaks REST/SSE with natural-language messages — it cannot speak
MCP and cannot form structured API calls. The repo already has:

- a **REST API** (`POST /analyze`, `POST /resume/jsonresume`,
  `GET /health`) — structured calls, no conversation;
- an **MCP server** (`mcp/index.js`, stdio) — a thin bridge exposing
  those operations as tools, mountable by Claude Desktop.

The question: what does it take for the chatbot to drive the job
matcher, and should that thing exist in this repo?

## Options considered

1. **Chatbot calls the REST API directly.** Rejected: a chat client
   sends prose, not multipart requests. Something must translate intent
   into tool calls — that is an LLM loop, which the backend deliberately
   does not contain (its only LLM call is typed extraction).
2. **Thin REST→MCP passthrough (no LLM).** Rejected: our MCP server is
   itself a thin bridge to our own REST API, so REST→MCP→REST is a
   round trip that ends where it started. A structured-REST caller
   should just call `POST /analyze`; the OpenAPI release artifact
   already documents it.
3. **Agent service (the ctms model).** Accepted: a small FastAPI app
   hosting an LLM orchestration loop — natural language in, MCP tool
   calls out, SSE answer stream back. This is genuinely new capability
   (conversational orchestration), and it justifies MCP's existence:
   **one tool-definition surface serves both Claude Desktop (stdio) and
   the neutral chatbot (via the agent service).**

## Decision

Build `mcp/agent-service/` per option 3, with these bindings:

- **Endpoints** mirror the ctms contract the chatbot already speaks:
  `POST /chat/stream` (SSE), `POST /upload`, `GET /health` (+ tool
  list). The chatbot connects through configuration alone.
- **Upload flow (owner decision):** uploads land in a configured temp
  directory (`AGENT_UPLOAD_DIR`, a shared volume when containerized);
  the returned server-side path feeds the existing `resume_path` flow
  unchanged — no new resume handling downstream.
  **Correction (2026-07-11):** verifying against the actual chatbot
  (`github.com/senthilsweb/mcp-chat-client`, confirmed to be "the
  neutral chatbot" this ADR refers to) surfaced two real gaps, both
  fixed:
  1. The widget's own `uploadFile()` was dead code — no UI ever called
     it, and `Chat.tsx` never wired the callback it exposed. Fixed
     upstream in that repo: attach + send is now one atomic
     `useChat.sendMessage(text, file)` call (uploads before streaming,
     never races), with an upload-progress state and an attachment chip
     on the sent message.
  2. The widget's `UploadResponse` contract folds a `content` string
     into the *next chat message* — it never reads `path`. Our
     `/upload` originally returned only `path`/`filename`/`message`, so
     even with the widget fixed, the model would never have learned
     where the file landed. Fixed by adding `content` (a short note
     carrying the path) alongside the existing fields.
  Verified end-to-end (not just unit-tested): upload → widget-style
  fold of `content` into the chat message → real `analyze_job_fit` MCP
  tool call → grounded, scored streamed answer. This is the first real
  proof the ADR's upload flow works as designed, not just as specified.
- **Max reuse, minimum code:** the loop is pydantic-ai's MCP client
  (`MCPServerStdio` toolset over `mcp/index.js`), not a hand-rolled
  function-calling loop; the service imports `job_matcher`'s
  `logging`, `observability`, and `config` modules instead of
  duplicating them.
- **Exactly two LLM operations system-wide, by design:**
  | # | Operation | Lives in | Model role |
  |---|---|---|---|
  | LLM-1 | Typed extraction (`JobAnalysis`, JSON Resume) | backend core | `MODEL_ANALYST` |
  | LLM-2 | Chat orchestration (tool selection, phrasing) | agent service | `MODEL_CHAT` → `MODEL_ANALYST` → `MODEL` |
  Neither may score: LLM-1's schema has no score field; LLM-2's prompt
  forbids invented numbers and its answers must trace to tool outputs.
  Both default to the mini tier (cost policy, 2026-07-11).

## Consequences

**Positive:** the existing chatbot works with zero client changes; MCP
earns its place (two AI clients, one tool surface); conversational
access without contaminating the deterministic backend; observability
spans distinguish the two LLM operations.

**Negative / accepted:** a third runtime process (compose manages the
topology); every chat turn costs tokens (mini tier); the upload
directory must be shared between agent service and backend in
containerized deployments; chat answers add an LLM layer that can
paraphrase results — mitigated by the no-invented-scores rule and the
tool-call events visible in the SSE stream.

**Explicitly out of scope now:** auth on the agent service, chat
sessions/memory beyond one conversation buffer, HTTP transports on the
MCP server itself.
