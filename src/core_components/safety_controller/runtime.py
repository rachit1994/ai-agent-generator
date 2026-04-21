"""Deterministic safety-controller runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import SAFETY_CONTROLLER_CONTRACT, SAFETY_CONTROLLER_SCHEMA_VERSION


def build_safety_controller(
    *,
    run_id: str,
    cto: dict[str, Any],
) -> dict[str, Any]:
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
