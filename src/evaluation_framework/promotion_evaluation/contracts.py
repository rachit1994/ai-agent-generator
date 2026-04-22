"""Contracts for promotion-evaluation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROMOTION_EVALUATION_CONTRACT = "sde.promotion_evaluation.v1"
PROMOTION_EVALUATION_SCHEMA_VERSION = "1.0"
_FLOAT_TOLERANCE = 1e-4
_CANONICAL_EVIDENCE_REFS = {
    "promotion_package_ref": "lifecycle/promotion_package.json",
    "review_ref": "review.json",
    "traces_ref": "traces.jsonl",
    "promotion_evaluation_ref": "learning/promotion_evaluation.json",
}


def _validate_signals(signals: Any) -> list[str]:
    if not isinstance(signals, dict):
        return ["promotion_evaluation_signals"]
    errs: list[str] = []
    promotion_readiness_score = signals.get("promotion_readiness_score")
    finalize_pass_rate = signals.get("finalize_pass_rate")
    review_pass = signals.get("review_pass")
    for key, value in (
        ("promotion_readiness_score", promotion_readiness_score),
        ("finalize_pass_rate", finalize_pass_rate),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"promotion_evaluation_signal_type:{key}")
            continue
        if float(value) < 0.0 or float(value) > 1.0:
            errs.append(f"promotion_evaluation_signal_range:{key}")
    if not isinstance(review_pass, bool):
        errs.append("promotion_evaluation_signal_type:review_pass")
    return errs


def _validate_decision_semantics(decision: Any, confidence: Any, signals: Any) -> list[str]:
    if (
        decision not in ("promote", "hold")
        or isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not isinstance(signals, dict)
    ):
        return []
    readiness = signals.get("promotion_readiness_score")
    finalize = signals.get("finalize_pass_rate")
    review_pass = signals.get("review_pass")
    if (
        isinstance(readiness, bool)
        or not isinstance(readiness, (int, float))
        or isinstance(finalize, bool)
        or not isinstance(finalize, (int, float))
        or not isinstance(review_pass, bool)
    ):
        return []
    errs: list[str] = []
    expected_confidence = round((float(readiness) * 0.6) + (float(finalize) * 0.4), 4)
    if abs(float(confidence) - expected_confidence) > _FLOAT_TOLERANCE:
        errs.append("promotion_evaluation_confidence_semantics")
    expected_decision = "promote" if review_pass and float(confidence) >= 0.8 else "hold"
    if decision != expected_decision:
        errs.append("promotion_evaluation_decision_semantics")
    return errs


def validate_promotion_evaluation_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["promotion_evaluation_not_object"]
    errs: list[str] = []
    if body.get("schema") != PROMOTION_EVALUATION_CONTRACT:
        errs.append("promotion_evaluation_schema")
    if body.get("schema_version") != PROMOTION_EVALUATION_SCHEMA_VERSION:
        errs.append("promotion_evaluation_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("promotion_evaluation_run_id")
    decision = body.get("decision")
    if decision not in ("promote", "hold"):
        errs.append("promotion_evaluation_decision")
    confidence = body.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        errs.append("promotion_evaluation_confidence_type")
    elif float(confidence) < 0.0 or float(confidence) > 1.0:
        errs.append("promotion_evaluation_confidence_range")
    signals = body.get("signals")
    errs.extend(_validate_signals(signals))
    errs.extend(_validate_evidence(body.get("evidence")))
    if not errs:
        errs.extend(_validate_decision_semantics(decision, confidence, signals))
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["promotion_evaluation_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"promotion_evaluation_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized.startswith("/") or ".." in normalized.split("/") or normalized != expected:
            errs.append(f"promotion_evaluation_evidence_ref:{key}")
    return errs


def validate_promotion_evaluation_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["promotion_evaluation_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["promotion_evaluation_json"]
    return validate_promotion_evaluation_dict(body)
