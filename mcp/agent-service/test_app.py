"""
File Name: test_app.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Agent-service eval (no LLM, no node — run_chat stubbed): the ctms SSE
contract, the upload→path round trip, and the reuse rules.

This suite pins the service by:
1. /chat/stream emits data:{"content"} chunks with tool notices, then
   data:{"done": true}; errors become data:{"error"}.
2. /upload stores into AGENT_UPLOAD_DIR and returns the server-side
   path; unsupported formats are refused.
3. The module imports job_matcher's logging/config/prompts — no
   duplicated plumbing (grep-gated in acceptance criterion 16).

Run: pytest mcp/agent-service -q  (job-matcher package must be installed)
"""

# Import necessary libraries
import asyncio
import json
from pathlib import Path

import app as agent_app
import pytest
from fastapi.testclient import TestClient

client = TestClient(agent_app.app)


def sse_events(text: str) -> list[dict]:
    return [json.loads(line[6:]) for line in text.splitlines() if line.startswith("data: ")]


@pytest.fixture()
def stubbed_chat(monkeypatch):
    async def fake_run_chat(message, tool_notices: asyncio.Queue):
        await tool_notices.put("analyze_job_fit")
        yield "Score is "
        yield "79 (good_match)."

    monkeypatch.setattr(agent_app, "run_chat", fake_run_chat)


def test_chat_stream_ctms_contract(stubbed_chat):
    response = client.post("/chat/stream", json={"message": "analyze my resume", "session_id": "s1"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    events = sse_events(response.text)
    contents = [e["content"] for e in events if "content" in e]
    assert any("🔧 analyze_job_fit" in c for c in contents)  # tool notice surfaced
    assert "".join(contents).endswith("79 (good_match).")
    assert events[-1] == {"done": True}


def test_chat_stream_empty_message_is_error():
    response = client.post("/chat/stream", json={"message": ""})
    events = sse_events(response.text)
    assert events == [{"error": "empty message"}]


def test_chat_stream_exception_becomes_error_event(monkeypatch):
    async def broken(message, tool_notices):
        raise RuntimeError("loop exploded")
        yield  # pragma: no cover — makes this an async generator

    monkeypatch.setattr(agent_app, "run_chat", broken)
    events = sse_events(client.post("/chat/stream", json={"message": "hi"}).text)
    assert any("error" in e for e in events)
    assert not any(e.get("done") for e in events)


def test_upload_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_UPLOAD_DIR", str(tmp_path))
    response = client.post(
        "/upload", files={"file": ("My Resume (v2).pdf", b"%PDF-1.4 fake", "application/pdf")}
    )
    assert response.status_code == 200
    body = response.json()
    stored = Path(body["path"])
    assert stored.parent == tmp_path          # landed in the configured dir
    assert stored.read_bytes().startswith(b"%PDF")
    assert stored.suffix == ".pdf"
    assert "/" not in stored.stem and "(" not in stored.stem  # sanitized name


def test_upload_rejects_unsupported_format(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_UPLOAD_DIR", str(tmp_path))
    body = client.post("/upload", files={"file": ("r.exe", b"MZ", "application/octet-stream")}).json()
    assert "error" in body


def test_reuse_no_duplicated_plumbing():
    # The service must import shared modules, not re-implement them
    import inspect

    source = inspect.getsource(agent_app)
    assert "from job_matcher.logging import get_logger" in source
    assert "from job_matcher.config import resolve_model" in source
    assert "from job_matcher.prompts import load_prompt" in source
    assert "logging.basicConfig" not in source
    assert "structlog.configure" not in source
