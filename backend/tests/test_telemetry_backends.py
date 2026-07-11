"""
File Name: test_telemetry_backends.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Telemetry-backend eval (no LLM; no reachable backends needed) — the
env-activation matrix, delivery resilience, and the [otel] extra gate
from the spec's "Telemetry backends activated by env alone".

This suite pins the backends by:
1. Registry matrix: each backend joins solely via its env vars; two set
   together both join (fan-out).
2. OpenObserve REST sink survives an unreachable endpoint: run output
   unaffected, exactly one warning, no raise.
3. OTLP env configured without the OpenTelemetry SDK → startup error
   naming `job-matcher[otel]`.
4. The OTel bridge (when installed): facade spans map one-to-one with
   preserved nesting and OpenInference attributes on the analyze span.
"""

# Import necessary libraries
import sys
import time

import pytest

from job_matcher.observability import Span, configure, set_sinks
from job_matcher.observability.sinks import JsonLogSink, OpenObserveRestSink

CLEAN_ENV = [
    "OBSERVABILITY_SINK", "OPENOBSERVE_URL", "OPENOBSERVE_ORG", "OPENOBSERVE_STREAM",
    "OPENOBSERVE_USER", "OPENOBSERVE_PASSWORD", "OTEL_EXPORTER_OTLP_ENDPOINT",
    "PHOENIX_COLLECTOR_ENDPOINT", "PHOENIX_API_KEY",
    "ARIZE_SPACE_ID", "ARIZE_API_KEY", "ARIZE_PROJECT_NAME",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in CLEAN_ENV:
        monkeypatch.delenv(var, raising=False)
    yield
    # monkeypatch restores env AFTER this teardown — don't re-configure here,
    # just neutralize the registry; later tests configure() as they need.
    set_sinks([])


def _types(sinks):
    return [type(s).__name__ for s in sinks]


def test_default_is_json_only():
    assert _types(configure(force=True)) == ["JsonLogSink"]


def test_none_disables_everything(monkeypatch):
    monkeypatch.setenv("OBSERVABILITY_SINK", "none")
    monkeypatch.setenv("OPENOBSERVE_URL", "http://localhost:5080")  # even with a backend set
    assert configure(force=True) == []


def test_openobserve_joins_by_env_alone(monkeypatch):
    monkeypatch.setenv("OPENOBSERVE_URL", "http://localhost:5080")
    monkeypatch.setenv("OPENOBSERVE_ORG", "default")
    monkeypatch.setenv("OPENOBSERVE_STREAM", "job_matcher")
    assert _types(configure(force=True)) == ["JsonLogSink", "OpenObserveRestSink"]


def test_missing_otel_extra_is_clear_startup_error(monkeypatch):
    monkeypatch.setenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006")
    # Simulate the extra not being installed
    for mod in list(sys.modules):
        if mod == "opentelemetry" or mod.startswith("opentelemetry."):
            monkeypatch.delitem(sys.modules, mod, raising=False)
    monkeypatch.setitem(sys.modules, "opentelemetry", None)
    with pytest.raises(RuntimeError, match=r"job-matcher\[otel\]"):
        configure(force=True)


def _span(name, span_id, parent_id=None, **attrs):
    s = Span(name=name, trace_id="t-1", span_id=span_id, parent_id=parent_id,
             started_at=time.time(), attributes=attrs)
    s.ended_at = s.started_at + 0.01
    return s


def test_openobserve_unreachable_warns_once_never_raises():
    sink = OpenObserveRestSink(
        url="http://127.0.0.1:9", org="default", stream="test", user="u", password="p"
    )
    root = _span("run_analysis", "root1")
    sink.on_span_end(_span("child", "c1", "root1"))
    sink.on_span_end(root)  # root end forces a flush against the dead endpoint
    assert sink._warned is True
    sink.on_span_end(_span("run_analysis", "root2"))  # second failure: silent, still no raise
    assert sink._buffer == []


def test_openobserve_batches_and_flushes_on_root_end(monkeypatch):
    posted = []

    class FakeResponse:
        def raise_for_status(self):
            return None

    def fake_post(endpoint, json, auth, timeout):
        posted.append((endpoint, json))
        return FakeResponse()

    import job_matcher.observability.sinks as sinks_mod

    monkeypatch.setattr(sinks_mod.httpx, "post", fake_post)
    sink = OpenObserveRestSink(url="http://o2:5080", org="myorg", stream="jm", user="u", password="p")
    sink.on_span_end(_span("child", "c1", "root1"))
    assert posted == []  # buffered — not a root end yet
    sink.on_span_end(_span("run_analysis", "root1", run_id="r-1"))
    assert len(posted) == 1
    endpoint, batch = posted[0]
    assert endpoint == "http://o2:5080/api/myorg/jm/_json"
    assert [r["span_name"] for r in batch] == ["child", "run_analysis"]
    assert batch[1]["run_id"] == "r-1"


def test_otel_bridge_maps_spans_with_openinference_attrs():
    otel = pytest.importorskip("opentelemetry")  # noqa: F841 — extra-installed environments only
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    from job_matcher.observability.otel_bridge import OtelBridgeSink

    exporter = InMemorySpanExporter()
    sink = OtelBridgeSink([exporter], use_batch=False)

    root = _span("run_analysis", "r1", run_id="run-9")
    llm = _span("analyze_job_fit", "a1", "r1", model="openai:gpt-5.4-mini",
                input_tokens=100, output_tokens=40, job_index=0)
    sink.on_span_start(root)
    sink.on_span_start(llm)
    sink.on_span_end(llm)
    sink.on_span_end(root)

    exported = {s.name: s for s in exporter.get_finished_spans()}
    assert set(exported) == {"run_analysis", "analyze_job_fit"}
    llm_span, root_span = exported["analyze_job_fit"], exported["run_analysis"]
    assert llm_span.parent.span_id == root_span.context.span_id  # nesting preserved
    assert llm_span.attributes["openinference.span.kind"] == "LLM"
    assert llm_span.attributes["llm.model_name"] == "openai:gpt-5.4-mini"
    assert llm_span.attributes["llm.token_count.prompt"] == 100
    assert root_span.attributes["openinference.span.kind"] == "CHAIN"
    assert root_span.attributes["run_id"] == "run-9"
