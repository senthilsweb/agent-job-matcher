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
2. OpenObserveRestSink — batched POSTs of span records straight to
   OpenObserve's `/api/{org}/{stream}/_json` ingestion API (no OTel, no
   extra dependencies). Fire-and-forget: batches flush on size and when
   a root span ends; an unreachable instance logs ONE warning per
   process and never fails or slows a run.
3. The OTel bridge (Phoenix / Arize / generic OTLP) lives in
   otel_bridge.py — the only module allowed to import vendor SDKs.

Environment Variables (.env at repo root):
- OPENOBSERVE_URL / OPENOBSERVE_ORG / OPENOBSERVE_STREAM /
  OPENOBSERVE_USER / OPENOBSERVE_PASSWORD (presence of URL activates)
"""

# Import necessary libraries
from __future__ import annotations

import os

import httpx
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


def _span_record(span: Span) -> dict:
    return {
        "span_name": span.name,
        "trace_id": span.trace_id,
        "span_id": span.span_id,
        "parent_id": span.parent_id,
        "started_at": span.started_at,
        "duration_ms": span.duration_ms,
        "status": span.status,
        "error": span.error,
        **span.attributes,
    }


class OpenObserveRestSink:
    """Ship spans to OpenObserve's REST JSON-ingestion API — no OTel involved."""

    def __init__(
        self, url: str, org: str, stream: str, user: str, password: str, batch_size: int = 50
    ) -> None:
        self._endpoint = f"{url.rstrip('/')}/api/{org}/{stream}/_json"
        self._auth = (user, password)
        self._batch_size = batch_size
        self._buffer: list[dict] = []
        self._warned = False

    @classmethod
    def from_env(cls) -> "OpenObserveRestSink":
        return cls(
            url=os.getenv("OPENOBSERVE_URL", "").strip(),
            org=os.getenv("OPENOBSERVE_ORG", "default").strip() or "default",
            stream=os.getenv("OPENOBSERVE_STREAM", "job_matcher").strip() or "job_matcher",
            user=os.getenv("OPENOBSERVE_USER", ""),
            password=os.getenv("OPENOBSERVE_PASSWORD", ""),
        )

    def on_span_start(self, span: Span) -> None:
        return None

    def on_span_end(self, span: Span) -> None:
        self._buffer.append(_span_record(span))
        # Flush on batch size, and always when a trace root ends (end of run)
        if len(self._buffer) >= self._batch_size or span.parent_id is None:
            self.flush()

    def flush(self) -> None:
        """Fire-and-forget delivery: one warning per process, never a raise."""
        if not self._buffer:
            return
        batch, self._buffer = self._buffer, []
        try:
            httpx.post(self._endpoint, json=batch, auth=self._auth, timeout=3.0).raise_for_status()
        except Exception as exc:
            if not self._warned:
                log.warning("telemetry_delivery_failed", backend="openobserve", error=str(exc))
                self._warned = True
