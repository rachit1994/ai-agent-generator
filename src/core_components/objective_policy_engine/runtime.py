"""Deterministic objective policy engine derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    OBJECTIVE_POLICY_ENGINE_CONTRACT,
    OBJECTIVE_POLICY_ENGINE_SCHEMA_VERSION,
)

_COMPOSITE_RELEASE_FLOOR = 70.0


def _to_float_or_zero(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _clamp_score(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 100.0:
        return 100.0
    return round(value, 2)


def _passed(value: Any) -> bool:
    return value is True


def build_objective_policy_engine(
    *,
    run_id: str,
    mode: str,
    summary: dict[str, Any],
    review: dict[str, Any],
    cto: dict[str, Any],
    policy_bundle_rollback_errors: list[str],
) -> dict[str, Any]:
    balanced = summary.get("balanced_gates") if isinstance(summary, dict) else {}
    if not isinstance(balanced, dict):
        balanced = {}
    scores = {
        "reliability": _clamp_score(_to_float_or_zero(balanced.get("reliability"))),
        "delivery": _clamp_score(_to_float_or_zero(balanced.get("delivery"))),
        "governance": _clamp_score(_to_float_or_zero(balanced.get("governance"))),
        "composite": _clamp_score(_to_float_or_zero(balanced.get("composite"))),
    }
    review_status = str(review.get("status", ""))
    hard_stop_rows = cto.get("hard_stops") if isinstance(cto, dict) else []
    if not isinstance(hard_stop_rows, list):
        hard_stop_rows = []
    failed_hard_stops = sum(1 for row in hard_stop_rows if isinstance(row, dict) and not _passed(row.get("passed")))
    rollback_ok = len(policy_bundle_rollback_errors) == 0
    score_floor_ok = scores["composite"] >= _COMPOSITE_RELEASE_FLOOR
    decision = "deny"
    reason = "hard_stop_failure"
    next_step = "resolve_hard_stops"
    if failed_hard_stops == 0 and not score_floor_ok:
        reason = "score_floor_failure"
        next_step = "improve_balanced_scores"
    elif failed_hard_stops == 0 and not rollback_ok:
        reason = "rollback_validation_failure"
        next_step = "fix_policy_bundle_rollback"
    elif failed_hard_stops == 0 and review_status == "completed_review_pass" and rollback_ok:
        decision = "allow"
        reason = "policy_checks_passed"
        next_step = "proceed_with_release"
    elif failed_hard_stops == 0 and rollback_ok:
        decision = "defer"
        reason = "review_not_passed"
        next_step = "address_review_findings"
    return {
        "schema": OBJECTIVE_POLICY_ENGINE_CONTRACT,
        "schema_version": OBJECTIVE_POLICY_ENGINE_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "scores": scores,
        "policy": {
            "decision": decision,
            "reason": reason,
            "next_step": next_step,
        },
        "context": {
            "review_status": review_status,
            "failed_hard_stop_count": failed_hard_stops,
            "score_floor_ok": score_floor_ok,
            "rollback_errors": sorted(policy_bundle_rollback_errors),
        },
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "policy_bundle_ref": "program/policy_bundle_rollback.json",
            "objective_policy_ref": "strategy/objective_policy_engine.json",
        },
    }
