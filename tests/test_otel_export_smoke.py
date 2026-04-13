"""Phase 0: capture OpenTelemetry spans in-process (CI-safe) to prove the export pipeline is wired."""

from __future__ import annotations

from collections.abc import Sequence

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)


class _ListSpanExporter(SpanExporter):
    """Minimal exporter that retains spans for assertions (no network)."""

    def __init__(self) -> None:
        self._finished: list[ReadableSpan] = []

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        self._finished.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        return None


def test_otel_spans_reachable_for_agentevals_hooks() -> None:
    exporter = _ListSpanExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": "phase0-ci-smoke"}))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)
    with tracer.start_as_current_span("plan"):
        with tracer.start_as_current_span("action"):
            with tracer.start_as_current_span("output"):
                pass
    finished = exporter._finished
    assert len(finished) == 3
    names = {span.name for span in finished}
    assert names == {"plan", "action", "output"}
