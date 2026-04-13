"""Phase 0: prove OTLP HTTP exporter dependency is present for future agentevals trace uploads."""

from __future__ import annotations

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


def test_otlp_http_exporter_constructible() -> None:
    exporter = OTLPSpanExporter(endpoint="http://127.0.0.1:4318/v1/traces")
    assert exporter.shutdown() is None
