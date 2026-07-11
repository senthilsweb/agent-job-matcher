"""
File Name: observability/sinks.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Zero-dependency telemetry sinks behind the observability facade's Sink
protocol.

This module ships spans by:
1. JsonLogSink — one structured JSON log line per completed span through
   the shared structlog pipeline (the always-on default).
2. Bolt 5 adds OpenObserveRestSink (batched POSTs to the _json ingestion
   API) here, and the OTel bridge (Phoenix / Arize / generic OTLP) in
   otel_bridge.py — the only module allowed to import vendor SDKs.
"""

# Import necessary libraries
from __future__ import annotations

import structlog

from job_matcher.observability import Span

log = structlog.get_logger("observability")


class JsonLogSink:
    """Emit each completed span as one structured JSON log event."""

    def on_span_start(self, span: Span) -> None:
        # Start events are debug-level noise; the end event carries everything
        return None

    def on_span_end(self, span: Span) -> None:
        log.info(
            "span",
            span_name=span.name,
            trace_id=span.trace_id,
            span_id=span.span_id,
            parent_id=span.parent_id,
            duration_ms=span.duration_ms,
            status=span.status,
            error=span.error,
            **span.attributes,
        )
