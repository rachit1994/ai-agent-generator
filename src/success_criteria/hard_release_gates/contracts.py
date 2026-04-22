"""Contracts for hard release gates artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

HARD_RELEASE_GATES_CONTRACT = "sde.hard_release_gates.v1"
HARD_RELEASE_GATES_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_CANONICAL_EVIDENCE_REFS = {
    "summary_ref": "summary.json",
    "traces_ref": "traces.jsonl",
    "hard_release_gates_ref": "learning/hard_release_gates.json",
}


def _validate_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["hard_release_gates_execution"]
    errs: list[str] = []
    int_fields = (
        "events_processed",
        "finalize_events_processed",
        "malformed_event_rows",
        "checks_processed",
    )
    for field in int_fields:
        value = execution.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errs.append(f"hard_release_gates_execution_type:{field}")
    if not isinstance(execution.get("strict_boolean_violations"), list):
        errs.append("hard_release_gates_execution_type:strict_boolean_violations")
    return errs


def _validate_top_level_fields(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if body.get("schema") != HARD_RELEASE_GATES_CONTRACT:
        errs.append("hard_release_gates_schema")
    if body.get("schema_version") != HARD_RELEASE_GATES_SCHEMA_VERSION:
        errs.append("hard_release_gates_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("hard_release_gates_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("hard_release_gates_mode")
    for key in ("overall_pass", "validation_ready"):
        if not isinstance(body.get(key), bool):
            errs.append(f"hard_release_gates_{key}")
    return errs


def _validate_gates(gates: Any) -> list[str]:
    if not isinstance(gates, dict):
        return ["hard_release_gates_gates"]
    errs: list[str] = []
    for key in ("reliability_gate", "delivery_gate", "governance_gate", "composite_gate"):
        value = gates.get(key)
        if not isinstance(value, bool):
            errs.append(f"hard_release_gates_gate_type:{key}")
    return errs


def _validate_failed_hard_stop_ids(failed_hard_stop_ids: Any) -> list[str]:
    if not isinstance(failed_hard_stop_ids, list):
        return ["hard_release_gates_failed_hard_stop_ids"]
    errs: list[str] = []
    for idx, row in enumerate(failed_hard_stop_ids):
        if not isinstance(row, str) or not row.strip():
            errs.append(f"hard_release_gates_failed_hard_stop_id:{idx}")
    return errs


def _validate_scores(scores: Any) -> list[str]:
    if not isinstance(scores, dict):
        return ["hard_release_gates_scores"]
    errs: list[str] = []
    for key in ("reliability", "delivery", "governance", "composite"):
        value = scores.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"hard_release_gates_score_type:{key}")
            continue
        numeric = float(value)
        if not math.isfinite(numeric):
            errs.append(f"hard_release_gates_score_finite:{key}")
            continue
        if numeric < 0.0 or numeric > 100.0:
            errs.append(f"hard_release_gates_score_range:{key}")
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["hard_release_gates_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"hard_release_gates_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized != expected:
            errs.append(f"hard_release_gates_evidence_ref:{key}")
            continue
        ref_path = Path(normalized)
        if ref_path.is_absolute() or ".." in ref_path.parts:
            errs.append(f"hard_release_gates_evidence_ref:{key}")
    return errs


def _validate_gate_score_coherence(gates: Any, scores: Any) -> list[str]:
    if not isinstance(gates, dict) or not isinstance(scores, dict):
        return []
    required_gate_keys = ("reliability_gate", "delivery_gate", "governance_gate", "composite_gate")
    required_score_keys = ("reliability", "delivery", "governance", "composite")
    if any(not isinstance(gates.get(key), bool) for key in required_gate_keys):
        return []
    if any(isinstance(scores.get(key), bool) or not isinstance(scores.get(key), (int, float)) for key in required_score_keys):
        return []
    errs: list[str] = []
    if gates["reliability_gate"] is not (float(scores["reliability"]) >= 85.0):
        errs.append("hard_release_gates_gate_score_mismatch:reliability")
    if gates["delivery_gate"] is not (float(scores["delivery"]) >= 85.0):
        errs.append("hard_release_gates_gate_score_mismatch:delivery")
    if gates["governance_gate"] is not (float(scores["governance"]) >= 85.0):
        errs.append("hard_release_gates_gate_score_mismatch:governance")
    if gates["composite_gate"] is not (float(scores["composite"]) >= 90.0):
        errs.append("hard_release_gates_gate_score_mismatch:composite")
    return errs


def _validate_status_coherence(body: dict[str, Any], gates: Any, failed_hard_stop_ids: Any) -> list[str]:
    if not isinstance(gates, dict) or not isinstance(failed_hard_stop_ids, list):
        return []
    required_gate_keys = ("reliability_gate", "delivery_gate", "governance_gate", "composite_gate")
    if any(not isinstance(gates.get(key), bool) for key in required_gate_keys):
        return []
    overall_pass = body.get("overall_pass")
    validation_ready = body.get("validation_ready")
    if not isinstance(overall_pass, bool) or not isinstance(validation_ready, bool):
        return []
    expected_overall_pass = all(gates[key] for key in required_gate_keys) and len(failed_hard_stop_ids) == 0
    errs: list[str] = []
    if overall_pass is not expected_overall_pass:
        errs.append("hard_release_gates_overall_pass_mismatch")
    if validation_ready is not overall_pass:
        errs.append("hard_release_gates_validation_ready_mismatch")
    return errs


def validate_hard_release_gates_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["hard_release_gates_not_object"]
    errs = _validate_top_level_fields(body)
    errs.extend(_validate_execution(body.get("execution")))
    errs.extend(_validate_gates(body.get("gates")))
    errs.extend(_validate_failed_hard_stop_ids(body.get("failed_hard_stop_ids")))
    gates = body.get("gates")
    failed_hard_stop_ids = body.get("failed_hard_stop_ids")
    scores = body.get("scores")
    errs.extend(_validate_scores(scores))
    errs.extend(_validate_evidence(body.get("evidence")))
    errs.extend(_validate_gate_score_coherence(gates, scores))
    errs.extend(_validate_status_coherence(body, gates, failed_hard_stop_ids))
    return errs


def validate_hard_release_gates_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["hard_release_gates_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["hard_release_gates_json"]
    return validate_hard_release_gates_dict(body)
