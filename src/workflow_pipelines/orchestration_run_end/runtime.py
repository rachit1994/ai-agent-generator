"""Deterministic orchestration run-end runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    ORCHESTRATION_RUN_END_RUNTIME_CONTRACT,
    ORCHESTRATION_RUN_END_RUNTIME_SCHEMA_VERSION,
)
from .orchestration_run_end_contract import validate_orchestration_run_end_dict


def build_orchestration_run_end_runtime(
    *,
    run_id: str,
    orchestration_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    run_end_rows = [row for row in orchestration_rows if row.get("type") == "run_end"]
    has_run_end_line = len(run_end_rows) > 0
    all_run_end_lines_valid = all(validate_orchestration_run_end_dict(row) == [] for row in run_end_rows)
    status = "ready" if has_run_end_line and all_run_end_lines_valid else "degraded"
    return {
        "schema": ORCHESTRATION_RUN_END_RUNTIME_CONTRACT,
        "schema_version": ORCHESTRATION_RUN_END_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "has_run_end_line": has_run_end_line,
            "all_run_end_lines_valid": all_run_end_lines_valid,
        },
        "counts": {"run_end_count": len(run_end_rows)},
        "evidence": {
            "orchestration_ref": "orchestration.jsonl",
            "runtime_ref": "orchestration/run_end_runtime.json",
        },
    }
