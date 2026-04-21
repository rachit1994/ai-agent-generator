"""Deterministic production observability derivation."""

from __future__ import annotations

from .contracts import (
    PRODUCTION_OBSERVABILITY_CONTRACT,
    PRODUCTION_OBSERVABILITY_SCHEMA_VERSION,
)


def build_production_observability(
    *,
    run_id: str,
    mode: str,
    trace_rows: int,
    orchestration_rows: int,
    run_log_lines: int,
) -> dict[str, object]:
    has_core = trace_rows > 0 and orchestration_rows > 0
    has_log = run_log_lines > 0
    status = "healthy" if has_core and has_log else "degraded" if (has_core or has_log) else "missing"
    return {
        "schema": PRODUCTION_OBSERVABILITY_CONTRACT,
        "schema_version": PRODUCTION_OBSERVABILITY_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
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
