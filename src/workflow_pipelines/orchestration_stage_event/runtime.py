"""Deterministic orchestration stage-event runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    ORCHESTRATION_STAGE_EVENT_RUNTIME_CONTRACT,
    ORCHESTRATION_STAGE_EVENT_RUNTIME_SCHEMA_VERSION,
)
from .orchestration_stage_event_contract import validate_orchestration_stage_event_line_dict


def build_orchestration_stage_event_runtime(
    *,
    run_id: str,
    orchestration_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    stage_event_rows = [row for row in orchestration_rows if row.get("type") == "stage_event"]
    has_stage_event_lines = len(stage_event_rows) > 0
    all_stage_event_lines_valid = all(
        validate_orchestration_stage_event_line_dict(row) == [] for row in stage_event_rows
    )
    status = "ready" if has_stage_event_lines and all_stage_event_lines_valid else "degraded"
    return {
        "schema": ORCHESTRATION_STAGE_EVENT_RUNTIME_CONTRACT,
        "schema_version": ORCHESTRATION_STAGE_EVENT_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "has_stage_event_lines": has_stage_event_lines,
            "all_stage_event_lines_valid": all_stage_event_lines_valid,
        },
        "counts": {"stage_event_count": len(stage_event_rows)},
        "evidence": {
            "orchestration_ref": "orchestration.jsonl",
            "runtime_ref": "orchestration/stage_event_runtime.json",
        },
    }
