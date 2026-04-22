"""Contracts for objective policy engine artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OBJECTIVE_POLICY_ENGINE_CONTRACT = "sde.objective_policy_engine.v1"
OBJECTIVE_POLICY_ENGINE_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_ALLOWED_DECISIONS = {"allow", "defer", "deny"}
_ALLOWED_DENY_REASONS = {
    "hard_stop_failure",
    "score_floor_failure",
    "rollback_validation_failure",
}
_REQUIRED_EVIDENCE = (
    "summary_ref",
    "review_ref",
    "policy_bundle_ref",
    "objective_policy_ref",
)


def _validate_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["objective_policy_engine_execution"]
    errs: list[str] = []
    for key in (
        "signals_processed",
        "hard_stop_rows_processed",
        "malformed_hard_stop_rows",
        "rollback_error_count",
    ):
        value = execution.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errs.append(f"objective_policy_engine_execution_type:{key}")
    if not isinstance(execution.get("missing_signal_sources"), list):
        errs.append("objective_policy_engine_execution_type:missing_signal_sources")
    return errs


def _validate_scores(scores: Any) -> list[str]:
    if not isinstance(scores, dict):
        return ["objective_policy_engine_scores"]
    errs: list[str] = []
    for key in ("reliability", "delivery", "governance", "composite"):
        value = scores.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"objective_policy_engine_score_type:{key}")
            continue
        numeric = float(value)
        if numeric < 0.0 or numeric > 100.0:
            errs.append(f"objective_policy_engine_score_range:{key}")
    return errs


def _validate_policy(policy: Any) -> list[str]:
    if not isinstance(policy, dict):
        return ["objective_policy_engine_policy"]
    errs: list[str] = []
    decision = policy.get("decision")
    if decision not in _ALLOWED_DECISIONS:
        errs.append("objective_policy_engine_decision")
    reason = policy.get("reason")
    if decision == "deny" and reason not in _ALLOWED_DENY_REASONS:
        errs.append("objective_policy_engine_policy_reason_deny")
    for key in ("reason", "next_step"):
        value = policy.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"objective_policy_engine_policy_{key}")
    return errs


def _validate_context(context: Any) -> list[str]:
    if not isinstance(context, dict):
        return ["objective_policy_engine_context"]
    errs: list[str] = []
    review_status = context.get("review_status")
    if not isinstance(review_status, str) or not review_status.strip():
        errs.append("objective_policy_engine_context_review_status")
    failed_hard_stop_count = context.get("failed_hard_stop_count")
    if isinstance(failed_hard_stop_count, bool) or not isinstance(failed_hard_stop_count, int):
        errs.append("objective_policy_engine_context_failed_hard_stop_count_type")
    elif failed_hard_stop_count < 0:
        errs.append("objective_policy_engine_context_failed_hard_stop_count_range")
    score_floor_ok = context.get("score_floor_ok")
    if not isinstance(score_floor_ok, bool):
        errs.append("objective_policy_engine_context_score_floor_ok")
    rollback_errors = context.get("rollback_errors")
    if not isinstance(rollback_errors, list) or any(not isinstance(row, str) for row in rollback_errors):
        errs.append("objective_policy_engine_context_rollback_errors")
    return errs


def _validate_policy_context_semantics(policy: Any, context: Any) -> list[str]:
    if not isinstance(policy, dict) or not isinstance(context, dict):
        return []
    decision = policy.get("decision")
    reason = policy.get("reason")
    review_status = context.get("review_status")
    failed_hard_stop_count = context.get("failed_hard_stop_count")
    score_floor_ok = context.get("score_floor_ok")
    rollback_errors = context.get("rollback_errors")
    if (
        decision not in _ALLOWED_DECISIONS
        or not isinstance(reason, str)
        or not isinstance(review_status, str)
        or isinstance(failed_hard_stop_count, bool)
        or not isinstance(failed_hard_stop_count, int)
        or not isinstance(score_floor_ok, bool)
        or not isinstance(rollback_errors, list)
    ):
        return []
    rollback_ok = len(rollback_errors) == 0
    if decision == "allow":
        return _validate_allow_semantics(failed_hard_stop_count, score_floor_ok, rollback_ok, review_status)
    if decision == "defer":
        return _validate_defer_semantics(failed_hard_stop_count, score_floor_ok, rollback_ok, review_status)
    if decision == "deny":
        return _validate_deny_semantics(
            reason,
            failed_hard_stop_count,
            score_floor_ok,
            rollback_ok,
            review_status,
        )
    return []


def _validate_allow_semantics(
    failed_hard_stop_count: int,
    score_floor_ok: bool,
    rollback_ok: bool,
    review_status: str,
) -> list[str]:
    if failed_hard_stop_count == 0 and score_floor_ok and rollback_ok and review_status == "completed_review_pass":
        return []
    return ["objective_policy_engine_policy_context_mismatch"]


def _validate_defer_semantics(
    failed_hard_stop_count: int,
    score_floor_ok: bool,
    rollback_ok: bool,
    review_status: str,
) -> list[str]:
    if failed_hard_stop_count == 0 and score_floor_ok and rollback_ok and review_status != "completed_review_pass":
        return []
    return ["objective_policy_engine_policy_context_mismatch"]


def _validate_deny_semantics(
    reason: str,
    failed_hard_stop_count: int,
    score_floor_ok: bool,
    rollback_ok: bool,
    review_status: str,
) -> list[str]:
    fully_passing = failed_hard_stop_count == 0 and score_floor_ok and rollback_ok and review_status == "completed_review_pass"
    if fully_passing:
        return ["objective_policy_engine_policy_context_mismatch"]
    if reason == "hard_stop_failure" and failed_hard_stop_count == 0:
        return ["objective_policy_engine_policy_context_mismatch"]
    if reason == "score_floor_failure" and score_floor_ok:
        return ["objective_policy_engine_policy_context_mismatch"]
    if reason == "rollback_validation_failure" and rollback_ok:
        return ["objective_policy_engine_policy_context_mismatch"]
    return []


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["objective_policy_engine_evidence"]
    errs: list[str] = []
    for key in _REQUIRED_EVIDENCE:
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"objective_policy_engine_evidence_ref:{key}")
    return errs


def validate_objective_policy_engine_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["objective_policy_engine_not_object"]
    errs: list[str] = []
    if body.get("schema") != OBJECTIVE_POLICY_ENGINE_CONTRACT:
        errs.append("objective_policy_engine_schema")
    if body.get("schema_version") != OBJECTIVE_POLICY_ENGINE_SCHEMA_VERSION:
        errs.append("objective_policy_engine_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("objective_policy_engine_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("objective_policy_engine_mode")
    errs.extend(_validate_execution(body.get("execution")))
    errs.extend(_validate_scores(body.get("scores")))
    policy = body.get("policy")
    context = body.get("context")
    errs.extend(_validate_policy(policy))
    errs.extend(_validate_context(context))
    errs.extend(_validate_evidence(body.get("evidence")))
    if not errs:
        errs.extend(_validate_policy_context_semantics(policy, context))
    return errs


def validate_objective_policy_engine_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["objective_policy_engine_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["objective_policy_engine_json"]
    return validate_objective_policy_engine_dict(body)
