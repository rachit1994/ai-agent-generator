"""Deterministic orchestration run-error runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    ORCHESTRATION_RUN_ERROR_RUNTIME_CONTRACT,
    ORCHESTRATION_RUN_ERROR_RUNTIME_SCHEMA_VERSION,
)
from .orchestration_run_error_contract import validate_orchestration_run_error_dict


def build_orchestration_run_error_runtime(
    *,
    run_id: str,
    orchestration_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    run_error_rows = [row for row in orchestration_rows if row.get("type") == "run_error"]
    orchestration_present = len(orchestration_rows) > 0
    all_run_error_lines_valid = all(validate_orchestration_run_error_dict(row) == [] for row in run_error_rows)
    if not orchestration_present:
        status = "degraded"
    elif run_error_rows and all_run_error_lines_valid:
        status = "has_error"
    elif run_error_rows and not all_run_error_lines_valid:
        status = "degraded"
    else:
        status = "no_error"
    return {
        "schema": ORCHESTRATION_RUN_ERROR_RUNTIME_CONTRACT,
        "schema_version": ORCHESTRATION_RUN_ERROR_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "orchestration_present": orchestration_present,
            "all_run_error_lines_valid": all_run_error_lines_valid,
        },
        "counts": {"run_error_count": len(run_error_rows)},
        "evidence": {
            "orchestration_ref": "orchestration.jsonl",
            "runtime_ref": "orchestration/run_error_runtime.json",
        },
    }
