"""
File Name: test_observability.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Observability facade eval (no LLM) — the AOP contract from the spec:
span nesting mirrors the call tree, context propagates across asyncio
tasks, errors re-raise untouched, capture is allowlist-only, and
disabling telemetry changes nothing about behaviour.

This suite pins the facade by:
1. Recorder-sink assertions on nesting/trace ids (incl. asyncio.gather).
2. @traced error path: status=error recorded, exception unchanged.
3. capture= allowlist: only named arguments land in span attributes.
4. OBSERVABILITY_SINK=none → zero records, identical return values.
"""

# Import necessary libraries
import asyncio

import pytest

from job_matcher.observability import Span, configure, root_span, set_sinks, traced


class RecorderSink:
    def __init__(self) -> None:
        self.started: list[Span] = []
        self.ended: list[Span] = []

    def on_span_start(self, span: Span) -> None:
        self.started.append(span)

    def on_span_end(self, span: Span) -> None:
        self.ended.append(span)


@pytest.fixture()
def recorder():
    sink = RecorderSink()
    set_sinks([sink])
    yield sink
    set_sinks([])


@traced("inner")
def inner(x: int) -> int:
    return x * 2


@traced("outer")
def outer(x: int) -> int:
    return inner(x) + 1


def test_span_nesting_matches_call_tree(recorder):
    with root_span("run", run_id="r-123"):
        assert outer(2) == 5
    by_name = {s.name: s for s in recorder.ended}
    assert set(by_name) == {"run", "outer", "inner"}
    assert by_name["outer"].parent_id == by_name["run"].span_id
    assert by_name["inner"].parent_id == by_name["outer"].span_id
    # run_id is the trace/correlation id on every span in the tree
    assert {s.trace_id for s in recorder.ended} == {"r-123"}


async def test_context_propagates_across_asyncio_tasks(recorder):
    @traced("job_task", capture={"job_index"})
    async def job_task(job_index: int) -> int:
        await asyncio.sleep(0)
        return job_index

    with root_span("run", run_id="r-async"):
        results = await asyncio.gather(*(job_task(job_index=i) for i in range(3)))
    assert results == [0, 1, 2]
    tasks = [s for s in recorder.ended if s.name == "job_task"]
    root = next(s for s in recorder.ended if s.name == "run")
    assert len(tasks) == 3
    assert all(t.parent_id == root.span_id for t in tasks)
    assert sorted(t.attributes["job_index"] for t in tasks) == [0, 1, 2]


def test_error_recorded_and_reraised_untouched(recorder):
    @traced("boom")
    def boom():
        raise ValueError("kapow")

    with pytest.raises(ValueError, match="kapow"):
        boom()
    span = recorder.ended[0]
    assert span.status == "error"
    assert "ValueError" in span.error


def test_capture_is_allowlist_only(recorder):
    @traced("fn", capture={"job_index"})
    def fn(job_index: int, resume_text: str) -> None:
        return None

    fn(job_index=7, resume_text="SENSITIVE CONTENT")
    span = recorder.ended[0]
    assert span.attributes == {"job_index": 7}
    assert "resume_text" not in span.attributes


def test_none_sink_disables_everything(monkeypatch):
    monkeypatch.setenv("OBSERVABILITY_SINK", "none")
    sinks = configure(force=True)
    assert sinks == []
    # Behaviour identical with telemetry off
    assert outer(2) == 5
    # Restore default resolution for other tests
    monkeypatch.setenv("OBSERVABILITY_SINK", "json")
    configure(force=True)
    set_sinks([])


def test_decorator_preserves_signature_metadata():
    assert inner.__name__ == "inner"
    assert outer(3) == 7


def test_enrich_declares_post_call_attributes_at_the_decorator(recorder):
    @traced("llm_call", enrich=lambda result, args: {"tokens": result[1], "model": args.get("model")})
    def llm_call(prompt: str, model: str):
        return "answer", 42

    assert llm_call("p", model="test:m") == ("answer", 42)
    span = recorder.ended[0]
    assert span.attributes == {"tokens": 42, "model": "test:m"}
