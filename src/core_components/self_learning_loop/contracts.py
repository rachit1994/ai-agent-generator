"""Contracts for self-learning loop artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .policy_defaults import MANDATORY_GATE_IDS

SELF_LEARNING_LOOP_CONTRACT = "sde.self_learning_loop.v1"
SELF_LEARNING_LOOP_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_ALLOWED_DECISIONS = {"promote", "hold", "reject"}
_REASON_PREFIX = "self_learning_loop_contract:"
_CANONICAL_EVIDENCE_REFS = {
    "traces_ref": "traces.jsonl",
    "skill_nodes_ref": "capability/skill_nodes.json",
    "practice_engine_ref": "practice/practice_engine.json",
    "transfer_learning_metrics_ref": "learning/transfer_learning_metrics.json",
    "capability_growth_metrics_ref": "learning/capability_growth_metrics.json",
    "self_learning_candidates_ref": "learning/self_learning_candidates.jsonl",
    "self_learning_loop_ref": "learning/self_learning_loop.json",
}


def _validate_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["self_learning_loop_execution"]
    errs: list[str] = []
    for key in ("events_processed", "finalize_events_processed", "malformed_event_rows"):
        value = execution.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errs.append(f"self_learning_loop_execution_type:{key}")
    if not isinstance(execution.get("missing_signal_sources"), list):
        errs.append("self_learning_loop_execution_type:missing_signal_sources")
    return errs


def _validate_failed_gates(failed_gates: Any) -> tuple[list[str], list[str]]:
    if not isinstance(failed_gates, list) or any(not isinstance(row, str) for row in failed_gates):
        return [], ["self_learning_loop_failed_gates"]
    if any(row not in MANDATORY_GATE_IDS for row in failed_gates):
        return failed_gates, ["self_learning_loop_unknown_gate_id"]
    if len(set(failed_gates)) != len(failed_gates):
        return failed_gates, ["self_learning_loop_duplicate_failed_gates"]
    if failed_gates != sorted(failed_gates, key=MANDATORY_GATE_IDS.index):
        return failed_gates, ["self_learning_loop_failed_gates_order"]
    return failed_gates, []


def _validate_decision_reasons(decision_reasons: Any) -> list[str]:
    if not isinstance(decision_reasons, list) or any(
        not isinstance(row, str) or not row for row in decision_reasons
    ):
        return ["self_learning_loop_decision_reasons"]
    if any(not row.startswith(_REASON_PREFIX) for row in decision_reasons):
        return ["self_learning_loop_reason_prefix"]
    if len(set(decision_reasons)) != len(decision_reasons):
        return ["self_learning_loop_duplicate_decision_reasons"]
    return []


def _validate_signals(signals: Any) -> list[str]:
    if not isinstance(signals, dict):
        return ["self_learning_loop_signals"]
    errs: list[str] = []
    for key in (
        "finalize_pass_rate",
        "capability_score",
        "transfer_efficiency",
        "growth_signal",
        "practice_readiness",
    ):
        value = signals.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"self_learning_loop_signal_type:{key}")
            continue
        numeric = float(value)
        if not math.isfinite(numeric):
            errs.append(f"self_learning_loop_signal_non_finite:{key}")
            continue
        if numeric < 0.0 or numeric > 1.0:
            errs.append(f"self_learning_loop_signal_range:{key}")
    return errs


def _validate_decision(decision: Any) -> list[str]:
    if not isinstance(decision, dict):
        return ["self_learning_loop_decision"]
    errs: list[str] = []
    decision_value = decision.get("decision")
    if decision_value not in _ALLOWED_DECISIONS:
        errs.append("self_learning_loop_decision_value")
    errs.extend(_validate_loop_state(decision_value, decision.get("loop_state")))
    failed_gates, failed_gate_errors = _validate_failed_gates(decision.get("failed_gates"))
    errs.extend(failed_gate_errors)
    decision_reasons = decision.get("decision_reasons")
    reason_errs = _validate_decision_reasons(decision_reasons)
    errs.extend(reason_errs)
    if decision_value == "promote" and failed_gates:
        errs.append("self_learning_loop_promote_failed_gates")
    if decision_value in {"hold", "reject"} and not failed_gates:
        errs.append("self_learning_loop_non_promote_missing_failed_gates")
    errs.extend(_validate_next_action(decision_value, decision.get("next_action")))
    errs.extend(
        _validate_primary_reason(
            primary_reason=decision.get("primary_reason"),
            decision_reasons=decision_reasons,
            reason_errs=reason_errs,
        )
    )
    return errs


def _validate_next_action(decision_value: Any, next_action: Any) -> list[str]:
    expected = {
        "promote": "open_promotion_review",
        "hold": "run_practice_cycle",
        "reject": "halt_and_repair",
    }
    if decision_value not in expected:
        return []
    if next_action != expected[decision_value]:
        return ["self_learning_loop_next_action_mismatch"]
    return []


def _validate_loop_state(decision_value: Any, loop_state: Any) -> list[str]:
    if loop_state not in _ALLOWED_DECISIONS:
        return ["self_learning_loop_loop_state"]
    if decision_value in _ALLOWED_DECISIONS and loop_state != decision_value:
        return ["self_learning_loop_loop_state_mismatch"]
    return []


def _validate_primary_reason(
    *,
    primary_reason: Any,
    decision_reasons: Any,
    reason_errs: list[str],
) -> list[str]:
    if not isinstance(primary_reason, str) or not primary_reason.startswith(_REASON_PREFIX):
        return ["self_learning_loop_primary_reason"]
    if reason_errs or not isinstance(decision_reasons, list):
        return []
    expected_primary_reason = (
        decision_reasons[0]
        if decision_reasons
        else "self_learning_loop_contract:all_gates_passed"
    )
    if primary_reason != expected_primary_reason:
        return ["self_learning_loop_primary_reason_mismatch"]
    return []


def validate_self_learning_loop_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["self_learning_loop_not_object"]
    errs: list[str] = []
    if body.get("schema") != SELF_LEARNING_LOOP_CONTRACT:
        errs.append("self_learning_loop_schema")
    if body.get("schema_version") != SELF_LEARNING_LOOP_SCHEMA_VERSION:
        errs.append("self_learning_loop_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("self_learning_loop_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("self_learning_loop_mode")
    errs.extend(_validate_execution(body.get("execution")))
    errs.extend(_validate_signals(body.get("signals")))
    errs.extend(_validate_decision(body.get("decision")))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        errs.append("self_learning_loop_evidence")
        evidence = {}
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"self_learning_loop_evidence_{key}")
            continue
        normalized = value.strip()
        if normalized.startswith("/") or ".." in normalized.split("/") or normalized != expected:
            errs.append(f"self_learning_loop_evidence_{key}")
    return errs


def validate_self_learning_loop_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["self_learning_loop_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["self_learning_loop_json"]
    return validate_self_learning_loop_dict(body)


def validate_self_learning_candidates_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["self_learning_candidates_file_missing"]
    rows = path.read_text(encoding="utf-8").splitlines()
    if not rows:
        return ["self_learning_candidates_empty"]
    errs: list[str] = []
    seen_candidate_ids: set[str] = set()
    has_non_empty_row = False
    for idx, line in enumerate(rows, start=1):
        line_errs, has_content, candidate_id = _validate_candidate_line(line, idx)
        errs.extend(line_errs)
        if has_content:
            has_non_empty_row = True
        if candidate_id is not None:
            if candidate_id in seen_candidate_ids:
                errs.append(f"self_learning_candidates_duplicate_candidate_id:{idx}")
            seen_candidate_ids.add(candidate_id)
    if not has_non_empty_row:
        errs.append("self_learning_candidates_empty")
    return errs


def _validate_candidate_line(
    line: str,
    idx: int,
) -> tuple[list[str], bool, str | None]:
    if not line.strip():
        return [], False, None
    try:
        body = json.loads(line)
    except json.JSONDecodeError:
        return [f"self_learning_candidates_json:{idx}"], True, None
    if not isinstance(body, dict):
        return [f"self_learning_candidates_not_object:{idx}"], True, None
    errs: list[str] = []
    for key in ("candidate_id", "run_id", "trace_id", "event_hash"):
        value = body.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"self_learning_candidates_{key}:{idx}")
    candidate_id = body.get("candidate_id")
    normalized_candidate_id = candidate_id if isinstance(candidate_id, str) and candidate_id.strip() else None
    return errs, True, normalized_candidate_id
