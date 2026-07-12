"""
File Name: app.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
The agent service — the conversational REST bridge (ADR 0001, Bolt 8).
Hosts the system's second and final LLM operation (LLM-2: chat
orchestration); the only other one is the backend's typed extraction.

This service bridges chat to MCP by:
1. POST /chat/stream — SSE in the ctms-compatible shape the owner's
   neutral chatbot already speaks: data:{"content": ...} chunks,
   data:{"done": true}, data:{"error": ...}. Tool invocations surface
   as content notices ("🔧 tool..."). The request body's optional
   `history` field (an array of {role, content} prior turns, additive
   and backward compatible) is threaded into the model call every turn
   — the service holds no server-side session state (see
   openspec/changes/add-history-branding-and-release-assets in
   mcp-chat-client for the design and its rationale).
2. The loop is pydantic-ai's MCP client (MCPToolset over stdio to
   ../index.js) — no hand-rolled function-calling loop. The system
   prompt (job_matcher package data: chat_system.txt) forbids invented
   scores; numbers come only from tool results.
3. POST /upload — multipart file → AGENT_UPLOAD_DIR (a configured temp
   directory; share it with the backend when containerized), returning
   the server-side path the conversation then references.
4. GET /health — service liveness + the discovered MCP tool list.
5. Max reuse: logging, observability, config, and prompts all come from
   the installed job_matcher package — nothing re-implemented here.

Environment Variables (.env at repo root):
- MODEL_CHAT → MODEL_ANALYST → MODEL: the orchestration model (mini tier default)
- JOBMATCHER_API_URL: backend REST base for the MCP server (default http://localhost:8000)
- AGENT_UPLOAD_DIR: upload landing directory (default: <system temp>/job-matcher-uploads)
"""

# Import necessary libraries
from __future__ import annotations

import asyncio
import json
import os
import re
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset, StdioTransport
from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart

from job_matcher.config import resolve_model
from job_matcher.logging import get_logger
from job_matcher.observability import start_span
from job_matcher.prompts import load_prompt
from job_matcher.resume import SUPPORTED_EXTENSIONS

log = get_logger("jobmatch-agent")

MCP_INDEX = Path(__file__).parent.parent / "index.js"

app = FastAPI(title="agent-job-matcher agent service", version="1.0.0")
# The neutral chatbot is a browser client on another origin
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def build_agent() -> Agent:
    """LLM-2: pydantic-ai agent with the MCP server as its only toolset."""
    toolset = MCPToolset(
        StdioTransport(
            "node",
            [str(MCP_INDEX)],
            env={**os.environ, "JOBMATCHER_API_URL": os.getenv("JOBMATCHER_API_URL", "http://localhost:8000")},
        )
    )
    return Agent(
        resolve_model("CHAT", "ANALYST"),
        toolsets=[toolset],
        system_prompt=load_prompt("chat_system"),
    )


def upload_dir() -> Path:
    configured = os.getenv("AGENT_UPLOAD_DIR", "").strip()
    d = Path(configured) if configured else Path(tempfile.gettempdir()) / "job-matcher-uploads"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


# Friendly labels for the live "current action" indicator — kept here since
# this service owns the tool semantics; the widget stays generic (spec:
# add-history-branding-and-release-assets).
TOOL_ACTION_LABELS = {
    "analyze_job_fit": "Analyzing job fit…",
    "extract_jsonresume": "Converting resume to JSON Resume…",
    "health": "Checking backend status…",
}


def _action_label(tool_name: str) -> str:
    return TOOL_ACTION_LABELS.get(tool_name, f"Running {tool_name}…")


def _to_model_history(history: list[dict] | None) -> list:
    """Convert the wire-format {role, content} turns into pydantic-ai's
    native message history. The agent service stays stateless: history is
    threaded by the caller every turn, never held in server-side session
    state (see openspec/changes/add-history-branding-and-release-assets)."""
    if not history:
        return []
    messages: list = []
    for turn in history:
        if turn.get("role") == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=turn.get("content", ""))]))
        else:
            messages.append(ModelResponse(parts=[TextPart(content=turn.get("content", ""))]))
    return messages


async def run_chat(
    message: str, tool_notices: asyncio.Queue, history: list[dict] | None = None
) -> "asyncio.Iterator[str]":
    """The one LLM-2 invocation per chat turn; wrapped so tests can stub it."""
    agent = build_agent()

    async def notice(ctx, call_tool, name, tool_args):  # MCPToolset process_tool_call shape
        await tool_notices.put(name)
        return await call_tool(name, tool_args)

    # Surface tool invocations as ctms-style content notices
    for toolset in agent.toolsets:
        if isinstance(toolset, MCPToolset):
            toolset.process_tool_call = notice

    async with agent:
        async with agent.run_stream(message, message_history=_to_model_history(history)) as stream:
            async for delta in stream.stream_text(delta=True):
                yield delta


@app.post("/chat/stream")
async def chat_stream(request: Request):
    """Stream a chat answer over SSE (ctms contract: content / done / error)."""
    body = await request.json()
    message = (body.get("message") or "").strip()
    history = body.get("history") or []

    async def event_stream():
        with start_span("chat_turn", session_id=body.get("session_id", "default"), history_turns=len(history)):
            if not message:
                yield _sse({"error": "empty message"})
                return
            tool_notices: asyncio.Queue = asyncio.Queue()
            try:
                async for delta in run_chat(message, tool_notices, history):
                    while not tool_notices.empty():
                        # A distinct "action" field, not folded into content — the
                        # widget renders this as a live progress indicator (three
                        # dots + label), replaced once real content starts
                        # streaming, instead of literal text concatenated into
                        # the answer (the original ctms-inherited approach).
                        yield _sse({"action": _action_label(tool_notices.get_nowait())})
                    yield _sse({"content": delta})
                while not tool_notices.empty():
                    yield _sse({"action": _action_label(tool_notices.get_nowait())})
                yield _sse({"done": True})
            except Exception as exc:
                log.error("chat_failed", error=f"{type(exc).__name__}: {exc}")
                yield _sse({"error": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Store an uploaded resume in the configured temp dir; return its path."""
    suffix = Path(file.filename or "resume.pdf").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        return {"error": f"unsupported resume format {suffix!r}", "supported": sorted(SUPPORTED_EXTENSIONS)}
    safe_stem = re.sub(r"[^a-z0-9-]+", "-", Path(file.filename or "resume").stem.lower()).strip("-") or "resume"
    target = upload_dir() / f"{safe_stem}-{uuid.uuid4().hex[:8]}{suffix}"
    target.write_bytes(await file.read())
    log.info("upload_stored", path=str(target))
    return {
        "path": str(target),
        "filename": file.filename,
        # `content` is the field the mcp-chat-client widget (and any client
        # following its UploadResponse contract) folds into the next chat
        # message — it must carry the server path or the model never learns
        # where the file landed.
        "content": f"Resume uploaded — server path: {target}",
        "message": "Uploaded. Reference this path in chat.",
    }


@app.get("/health")
async def health():
    """Liveness + the MCP tool list discovered over stdio."""
    tools: list[str] = []
    try:
        toolset = MCPToolset(StdioTransport("node", [str(MCP_INDEX)], env=dict(os.environ)))
        async with toolset:
            tools = sorted(t.name for t in await toolset.list_tools())
    except Exception as exc:  # health must answer even when the MCP server can't start
        log.warning("health_tools_unavailable", error=str(exc))
    return {"status": "ok", "service": "agent-service", "tools": tools}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("AGENT_PORT", "8006")))
