"""Deterministic safety-controller runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import SAFETY_CONTROLLER_CONTRACT, SAFETY_CONTROLLER_SCHEMA_VERSION


def execute_safety_controller_runtime(*, cto: dict[str, Any]) -> dict[str, Any]:
    hard_stops = cto.get("hard_stops") if isinstance(cto.get("hard_stops"), list) else []
    evaluated_hard_stops = [row for row in hard_stops if isinstance(row, dict)]
    malformed_hard_stop_rows = len(hard_stops) - len(evaluated_hard_stops)
    non_boolean_hard_stop_passed_ids: list[str] = []
    for row in evaluated_hard_stops:
        passed = row.get("passed")
        if passed is True or passed is False:
            continue
        hs_id = row.get("id")
        non_boolean_hard_stop_passed_ids.append(str(hs_id) if isinstance(hs_id, str) and hs_id.strip() else "unknown")
    return {
        "hard_stops_processed": len(hard_stops),
        "evaluated_hard_stops": len(evaluated_hard_stops),
        "malformed_hard_stop_rows": malformed_hard_stop_rows,
        "non_boolean_hard_stop_passed_ids": non_boolean_hard_stop_passed_ids,
    }


def build_safety_controller(
    *,
    run_id: str,
    cto: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_safety_controller_runtime(cto=cto)
    hard_stops = cto.get("hard_stops") if isinstance(cto.get("hard_stops"), list) else []
    hard_stop_failures = any(row.get("passed") is not True for row in hard_stops if isinstance(row, dict))
    validation_ready = cto.get("validation_ready") is True
    policy_bundle_valid = not hard_stop_failures
    status = "allow" if validation_ready and policy_bundle_valid else "block"
    return {
        "schema": SAFETY_CONTROLLER_CONTRACT,
        "schema_version": SAFETY_CONTROLLER_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "execution": execution,
        "metrics": {
            "hard_stop_failures": hard_stop_failures,
            "validation_ready": validation_ready,
            "policy_bundle_valid": policy_bundle_valid,
        },
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "safety_controller_ref": "safety/controller_runtime.json",
        },
    }
