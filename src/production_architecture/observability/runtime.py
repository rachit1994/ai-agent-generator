"""Deterministic production observability derivation."""

from __future__ import annotations

from .contracts import (
    PRODUCTION_OBSERVABILITY_CONTRACT,
    PRODUCTION_OBSERVABILITY_SCHEMA_VERSION,
)


def execute_production_observability_runtime(
    *,
    trace_rows: int,
    orchestration_rows: int,
    run_log_lines: int,
) -> dict[str, int | list[str]]:
    missing_signal_sources: list[str] = []
    if trace_rows <= 0:
        missing_signal_sources.append("traces")
    if orchestration_rows <= 0:
        missing_signal_sources.append("orchestration")
    if run_log_lines <= 0:
        missing_signal_sources.append("run_log")
    return {
        "signals_processed": 3,
        "trace_rows_observed": max(0, trace_rows),
        "orchestration_rows_observed": max(0, orchestration_rows),
        "run_log_lines_observed": max(0, run_log_lines),
        "missing_signal_sources": missing_signal_sources,
    }


def build_production_observability(
    *,
    run_id: str,
    mode: str,
    trace_rows: int,
    orchestration_rows: int,
    run_log_lines: int,
) -> dict[str, object]:
    execution = execute_production_observability_runtime(
        trace_rows=trace_rows, orchestration_rows=orchestration_rows, run_log_lines=run_log_lines
    )
    has_core = trace_rows > 0 and orchestration_rows > 0
    has_log = run_log_lines > 0
    status = "missing"
    if has_core and has_log:
        status = "healthy"
    elif has_core or has_log:
        status = "degraded"
    return {
        "schema": PRODUCTION_OBSERVABILITY_CONTRACT,
        "schema_version": PRODUCTION_OBSERVABILITY_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "execution": execution,
        "metrics": {
            "trace_rows": trace_rows,
            "orchestration_rows": orchestration_rows,
            "run_log_lines": run_log_lines,
        },
        "evidence": {
            "traces_ref": "traces.jsonl",
            "orchestration_ref": "orchestration.jsonl",
            "run_log_ref": "run.log",
            "observability_ref": "observability/production_observability.json",
        },
    }
