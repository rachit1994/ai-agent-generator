"""Deterministic production-readiness derivation for local runs."""

from __future__ import annotations

from typing import Any

from .contracts import PRODUCTION_READINESS_PROGRAM_CONTRACT, PRODUCTION_READINESS_PROGRAM_SCHEMA_VERSION


def build_production_readiness_program(
    *,
    run_id: str,
    mode: str,
    summary: dict[str, Any],
    review: dict[str, Any],
    hard_stops: list[dict[str, Any]],
    artifact_paths: list[dict[str, Any]],
) -> dict[str, Any]:
    manifest_valid = bool(
        summary.get("runId") == run_id
        and isinstance(summary.get("mode"), str)
        and summary.get("mode") == mode
    )
    review_status = str(review.get("status", ""))
    review_gate_passed = review_status == "completed_review_pass"
    hard_stop_rows = [row for row in hard_stops if isinstance(row, dict)]
    hard_stops_passed = bool(hard_stop_rows) and all(row.get("passed") is True for row in hard_stop_rows)
    balanced = summary.get("balanced_gates")
    balanced_ready = bool(isinstance(balanced, dict) and balanced.get("validation_ready") is True)
    artifact_rows = [row for row in artifact_paths if isinstance(row, dict)]
    required_present = bool(artifact_rows) and all(row.get("present") is True for row in artifact_rows)
    policy_bundle_valid = required_present
    checks = {
        "run_manifest_valid": manifest_valid,
        "review_gate_passed": review_gate_passed,
        "hard_stops_passed": hard_stops_passed,
        "balanced_gates_ready": balanced_ready,
        "required_artifacts_present": required_present,
        "policy_bundle_valid": policy_bundle_valid,
    }
    status = "ready" if all(checks.values()) else "not_ready"
    return {
        "schema": PRODUCTION_READINESS_PROGRAM_CONTRACT,
        "schema_version": PRODUCTION_READINESS_PROGRAM_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "checks": checks,
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "readiness_ref": "program/production_readiness.json",
        },
    }

