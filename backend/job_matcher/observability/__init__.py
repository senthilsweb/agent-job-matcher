"""
File Name: observability/__init__.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
The AOP observability facade — the only vocabulary core code uses for
instrumentation. Cross-cutting trace/span/timing attach to functions via
the decorators here; core function bodies contain zero instrumentation
calls, and stripping every decorator changes no behaviour.

This module provides instrumentation by:
1. @traced(name, capture=...) — wraps sync and async callables in a span;
   captures only an explicit allowlist of arguments (never raw args, so
   resume/JD content cannot leak into telemetry).
2. Context propagation via contextvars: a per-invocation root span
   (run_id as the trace/correlation id) parents nested decorated calls,
   including across asyncio tasks in the fan-out.
3. An env-driven sink registry: the JSON-log sink is always on;
   OBSERVABILITY_SINK=none disables everything; remote backends
   (OpenObserve REST, OTLP/Phoenix/Arize) join in Bolt 5.

Environment Variables (.env at repo root):
- OBSERVABILITY_SINK: json (default) | none
"""

# Import necessary libraries
from __future__ import annotations

import functools
import inspect
import os
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Iterable, Protocol


@dataclass
class Span:
    """One recorded unit of work — what every sink receives."""

    name: str
    trace_id: str
    span_id: str
    parent_id: str | None
    started_at: float
    ended_at: float | None = None
    status: str = "ok"
    error: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float | None:
        if self.ended_at is None:
            return None
        return round((self.ended_at - self.started_at) * 1000, 3)


class Sink(Protocol):
    """The contract every telemetry backend implements."""

    def on_span_start(self, span: Span) -> None: ...

    def on_span_end(self, span: Span) -> None: ...


# The active span for the current execution context (copied into asyncio tasks)
_current_span: ContextVar[Span | None] = ContextVar("job_matcher_current_span", default=None)
_sinks: list[Sink] | None = None


def configure(force: bool = False) -> list[Sink]:
    """Resolve the sink fan-out from env, once at startup (idempotent).

    The JSON-log sink is always on (OBSERVABILITY_SINK=none disables all
    telemetry); every remote backend joins purely by its own env vars:
    OpenObserve REST (OPENOBSERVE_URL...), and the OTLP-shaped trio —
    generic collector / Phoenix / Arize — through the otel bridge, which
    requires the job-matcher[otel] extra (a clear startup error names it
    when missing).
    """
    global _sinks
    if _sinks is not None and not force:
        return _sinks
    mode = os.getenv("OBSERVABILITY_SINK", "json").strip().lower()
    if mode == "none":
        _sinks = []
        return _sinks

    from job_matcher.observability.sinks import JsonLogSink, OpenObserveRestSink

    sinks: list[Sink] = [JsonLogSink()]
    if os.getenv("OPENOBSERVE_URL", "").strip():
        sinks.append(OpenObserveRestSink.from_env())

    from job_matcher.observability.otel_bridge import build_otel_sink, otlp_env_configured

    if otlp_env_configured():
        otel_sink = build_otel_sink()  # raises with the [otel] install hint if the SDK is absent
        if otel_sink is not None:
            sinks.append(otel_sink)

    _sinks = sinks
    return _sinks


def set_sinks(sinks: list[Sink]) -> None:
    """Test/advanced hook: replace the sink fan-out explicitly."""
    global _sinks
    _sinks = list(sinks)


def current_span() -> Span | None:
    """The span active in this execution context, if any."""
    return _current_span.get()


@contextmanager
def start_span(name: str, *, trace_id: str | None = None, **attributes: Any):
    """Open a span nested under the context's active span (or a new trace root)."""
    parent = _current_span.get()
    span = Span(
        name=name,
        trace_id=trace_id or (parent.trace_id if parent else uuid.uuid4().hex),
        span_id=uuid.uuid4().hex[:16],
        parent_id=parent.span_id if parent else None,
        started_at=time.time(),
        attributes=dict(attributes),
    )
    sinks = configure()
    for s in sinks:
        s.on_span_start(span)
    token = _current_span.set(span)
    try:
        yield span
    except BaseException as exc:
        span.status = "error"
        span.error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        span.ended_at = time.time()
        _current_span.reset(token)
        for s in sinks:
            s.on_span_end(span)


@contextmanager
def root_span(name: str, run_id: str, **attributes: Any):
    """Open the per-invocation root span; the run id becomes the trace id.

    When already inside a span (e.g. the API's per-request middleware span),
    the existing trace is kept — run_id stays queryable as an attribute.
    """
    trace_id = None if _current_span.get() else run_id
    with start_span(name, trace_id=trace_id, run_id=run_id, **attributes) as span:
        yield span


def add_span_attributes(**attributes: Any) -> None:
    """Attach attributes to the active span from inside a decorated call.

    The sanctioned way for a function to enrich its own span (e.g. token
    usage after an LLM call) without touching sink or span plumbing.
    """
    span = _current_span.get()
    if span is not None:
        span.attributes.update(attributes)


def _allowlisted(fn, capture: Iterable[str], args: tuple, kwargs: dict) -> dict[str, Any]:
    """Extract only allowlisted argument values — never raw args by default."""
    names = set(capture)
    if not names:
        return {}
    try:
        bound = inspect.signature(fn).bind_partial(*args, **kwargs)
        return {k: v for k, v in bound.arguments.items() if k in names}
    except TypeError:
        return {}


def traced(name: str | None = None, capture: Iterable[str] = (), enrich=None):
    """Decorator: run the wrapped sync/async callable inside a span.

    Signature-preserving; exceptions are recorded as an error outcome and
    re-raised untouched. `enrich(result, arguments) -> dict` lets a caller
    declare post-call span attributes (e.g. token usage from an LLM result)
    AT THE DECORATOR — keeping instrumentation out of function bodies.
    """

    def decorator(fn):
        span_name = name or fn.__qualname__

        def _arguments(args, kwargs) -> dict[str, Any]:
            try:
                return dict(inspect.signature(fn).bind_partial(*args, **kwargs).arguments)
            except TypeError:
                return {}

        def _apply_enrich(span: Span, result, args, kwargs) -> None:
            if enrich is not None:
                span.attributes.update(enrich(result, _arguments(args, kwargs)) or {})

        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                with start_span(span_name, **_allowlisted(fn, capture, args, kwargs)) as span:
                    result = await fn(*args, **kwargs)
                    _apply_enrich(span, result, args, kwargs)
                    return result

            return async_wrapper

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with start_span(span_name, **_allowlisted(fn, capture, args, kwargs)) as span:
                result = fn(*args, **kwargs)
                _apply_enrich(span, result, args, kwargs)
                return result

        return wrapper

    return decorator


def timed(name: str | None = None):
    """Decorator: duration-only span, for hot spots where full tracing is noise."""
    return traced(name=name, capture=())
