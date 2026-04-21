"""Deterministic orchestration run-start runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    ORCHESTRATION_RUN_START_RUNTIME_CONTRACT,
    ORCHESTRATION_RUN_START_RUNTIME_SCHEMA_VERSION,
)
from .orchestration_run_start_contract import validate_orchestration_run_start_dict


def build_orchestration_run_start_runtime(
    *,
    run_id: str,
    orchestration_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    first_line = orchestration_rows[0] if orchestration_rows else {}
    line_present = bool(orchestration_rows)
    first_line_is_run_start = bool(first_line.get("type") == "run_start") if isinstance(first_line, dict) else False
    contract_valid = first_line_is_run_start and validate_orchestration_run_start_dict(first_line) == []
    status = "ready" if line_present and first_line_is_run_start and contract_valid else "degraded"
    return {
        "schema": ORCHESTRATION_RUN_START_RUNTIME_CONTRACT,
        "schema_version": ORCHESTRATION_RUN_START_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "line_present": line_present,
            "first_line_is_run_start": first_line_is_run_start,
            "contract_valid": contract_valid,
        },
        "evidence": {
            "orchestration_ref": "orchestration.jsonl",
            "runtime_ref": "orchestration/run_start_runtime.json",
        },
    }
