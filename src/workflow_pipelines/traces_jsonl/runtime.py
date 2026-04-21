"""Deterministic traces JSONL event-row runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    TRACES_JSONL_EVENT_ROW_RUNTIME_CONTRACT,
    TRACES_JSONL_EVENT_ROW_RUNTIME_SCHEMA_VERSION,
)
from .traces_jsonl_event_contract import validate_traces_jsonl_event_dict


def build_traces_jsonl_event_row_runtime(
    *,
    run_id: str,
    trace_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    row_count = len(trace_rows)
    row_errors = [validate_traces_jsonl_event_dict(row) for row in trace_rows]
    all_rows_valid = row_count > 0 and all(len(errs) == 0 for errs in row_errors)
    run_id_consistent = row_count > 0 and all(str(row.get("run_id")) == run_id for row in trace_rows)
    status = "ready" if all_rows_valid and run_id_consistent and row_count > 0 else "degraded"
    return {
        "schema": TRACES_JSONL_EVENT_ROW_RUNTIME_CONTRACT,
        "schema_version": TRACES_JSONL_EVENT_ROW_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "all_rows_valid": all_rows_valid,
            "run_id_consistent": run_id_consistent,
        },
        "counts": {"row_count": row_count},
        "evidence": {
            "traces_ref": "traces.jsonl",
            "runtime_ref": "traces/event_row_runtime.json",
        },
    }
