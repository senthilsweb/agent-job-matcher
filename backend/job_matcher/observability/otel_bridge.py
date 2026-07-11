"""
File Name: observability/otel_bridge.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
The OTel bridge — THE ONLY MODULE in this codebase allowed to import the
OpenTelemetry SDK (backend/AGENTS.md). Installed via the optional
`pip install job-matcher[otel]` extra; configuring an OTLP backend
without it is a clear startup error naming the extra.

This module bridges telemetry by:
1. Mapping facade spans onto OTel spans one-to-one (same nesting, real
   start/end times) via the Sink protocol — core code never sees OTel.
2. Building one OTLP/HTTP exporter per env-activated backend:
   generic collector (OTEL_EXPORTER_OTLP_ENDPOINT — also how
   OpenObserve-via-OTel works), Arize Phoenix
   (PHOENIX_COLLECTOR_ENDPOINT + optional PHOENIX_API_KEY), and
   Arize AX (ARIZE_SPACE_ID + ARIZE_API_KEY → otlp.arize.com).
3. Decorating LLM analysis spans with OpenInference semantic attributes
   (span kind, model, token counts) so Phoenix/Arize render them
   natively; prompt/completion payloads ride only when
   TELEMETRY_RECORD_IO=true (attached upstream in analyze.py).

Environment Variables (.env at repo root):
- OTEL_EXPORTER_OTLP_ENDPOINT / OTEL_EXPORTER_OTLP_HEADERS
- PHOENIX_COLLECTOR_ENDPOINT / PHOENIX_API_KEY
- ARIZE_SPACE_ID / ARIZE_API_KEY / ARIZE_PROJECT_NAME (default job-matcher)
"""

# Import necessary libraries
from __future__ import annotations

import os

from job_matcher.observability import Span

INSTALL_HINT = (
    "an OTLP telemetry backend is configured but the OpenTelemetry SDK is not "
    "installed — run: pip install 'job-matcher[otel]'"
)


def _require_otel():
    try:
        from opentelemetry import trace  # noqa: F401
        from opentelemetry.sdk.resources import Resource  # noqa: F401
        from opentelemetry.sdk.trace import TracerProvider  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(INSTALL_HINT) from exc


class OtelBridgeSink:
    """Facade spans → OTel spans, fanned out to every configured OTLP exporter."""

    def __init__(self, exporters: list, use_batch: bool = True) -> None:
        _require_otel()
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor

        resource = Resource.create(
            {
                "service.name": "job-matcher",
                # Arize keys traces by model_id; harmless elsewhere
                "model_id": os.getenv("ARIZE_PROJECT_NAME", "job-matcher").strip() or "job-matcher",
            }
        )
        self._provider = TracerProvider(resource=resource)
        processor_cls = BatchSpanProcessor if use_batch else SimpleSpanProcessor
        for exporter in exporters:
            self._provider.add_span_processor(processor_cls(exporter))
        self._tracer = self._provider.get_tracer("job_matcher.observability")
        self._trace_api = trace
        self._live: dict[str, object] = {}

    def on_span_start(self, span: Span) -> None:
        parent = self._live.get(span.parent_id) if span.parent_id else None
        context = self._trace_api.set_span_in_context(parent) if parent else None
        otel_span = self._tracer.start_span(
            span.name, context=context, start_time=int(span.started_at * 1e9)
        )
        self._live[span.span_id] = otel_span

    def on_span_end(self, span: Span) -> None:
        otel_span = self._live.pop(span.span_id, None)
        if otel_span is None:
            return
        for key, value in span.attributes.items():
            if value is not None:
                otel_span.set_attribute(str(key), value)
        otel_span.set_attribute("facade.trace_id", span.trace_id)
        # OpenInference semantics: the analysis span is the LLM call, the rest are chain steps
        if span.name == "analyze_job_fit":
            otel_span.set_attribute("openinference.span.kind", "LLM")
            if model := span.attributes.get("model"):
                otel_span.set_attribute("llm.model_name", str(model))
            if (v := span.attributes.get("input_tokens")) is not None:
                otel_span.set_attribute("llm.token_count.prompt", int(v))
            if (v := span.attributes.get("output_tokens")) is not None:
                otel_span.set_attribute("llm.token_count.completion", int(v))
        else:
            otel_span.set_attribute("openinference.span.kind", "CHAIN")
        if span.status == "error":
            from opentelemetry.trace import Status, StatusCode

            otel_span.set_status(Status(StatusCode.ERROR, span.error or ""))
        otel_span.end(end_time=int(span.ended_at * 1e9) if span.ended_at else None)
        if span.parent_id is None:  # end of a trace — push batches out
            self._provider.force_flush(timeout_millis=3000)


def _build_exporters() -> list:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    exporters: list = []
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip():
        # Generic collector — endpoint/headers read from the standard env vars
        exporters.append(OTLPSpanExporter())
    if phoenix := os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "").strip():
        headers = {}
        if key := os.getenv("PHOENIX_API_KEY", "").strip():
            headers["authorization"] = f"Bearer {key}"
        exporters.append(OTLPSpanExporter(endpoint=f"{phoenix.rstrip('/')}/v1/traces", headers=headers))
    space_id = os.getenv("ARIZE_SPACE_ID", "").strip()
    api_key = os.getenv("ARIZE_API_KEY", "").strip()
    if space_id and api_key:
        exporters.append(
            OTLPSpanExporter(
                endpoint="https://otlp.arize.com/v1/traces",
                headers={"space_id": space_id, "api_key": api_key},
            )
        )
    return exporters


def otlp_env_configured() -> bool:
    """True when any OTLP-shaped backend's activation env is present."""
    return bool(
        os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
        or os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "").strip()
        or (os.getenv("ARIZE_SPACE_ID", "").strip() and os.getenv("ARIZE_API_KEY", "").strip())
    )


def build_otel_sink() -> OtelBridgeSink | None:
    """Construct the bridge for whatever OTLP backends the env activates."""
    if not otlp_env_configured():
        return None
    _require_otel()
    exporters = _build_exporters()
    return OtelBridgeSink(exporters) if exporters else None
