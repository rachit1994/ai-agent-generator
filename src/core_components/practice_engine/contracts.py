"""Contracts for practice engine artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRACTICE_ENGINE_CONTRACT = "sde.practice_engine.v1"
PRACTICE_ENGINE_SCHEMA_VERSION = "1.0"
_CANONICAL_EVIDENCE_REFS = {
    "task_spec_ref": "practice/task_spec.json",
    "evaluation_result_ref": "practice/evaluation_result.json",
    "practice_engine_ref": "practice/practice_engine.json",
}


def _validate_status_score_semantics(status: Any, scores: dict[str, Any]) -> list[str]:
    readiness_signal = scores.get("readiness_signal")
    expected_improvement = scores.get("expected_improvement")
    if (
        status not in ("ready", "needs_practice", "blocked")
        or isinstance(readiness_signal, bool)
        or not isinstance(readiness_signal, (int, float))
        or isinstance(expected_improvement, bool)
        or not isinstance(expected_improvement, (int, float))
    ):
        return []
    readiness = float(readiness_signal)
    expected = float(expected_improvement)
    if status == "ready" and (readiness < 0.6 or expected < 0.25):
        return ["practice_engine_status_scores_mismatch"]
    if status == "needs_practice" and readiness < 0.35:
        return ["practice_engine_status_scores_mismatch"]
    if status == "blocked" and readiness >= 0.35:
        return ["practice_engine_status_scores_mismatch"]
    return []


def _validate_result_status_coherence(status: Any, result: Any) -> list[str]:
    if status not in ("ready", "needs_practice", "blocked"):
        return []
    if not isinstance(result, dict):
        return ["practice_engine_result"]
    passed = result.get("passed")
    if not isinstance(passed, bool):
        return ["practice_engine_result_passed"]
    if passed is not (status == "ready"):
        return ["practice_engine_result_status_mismatch"]
    return []


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["practice_engine_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"practice_engine_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized.startswith("/") or ".." in normalized.split("/") or normalized != expected:
            errs.append(f"practice_engine_evidence_ref:{key}")
    return errs


def validate_practice_engine_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["practice_engine_not_object"]
    errs: list[str] = []
    if body.get("schema") != PRACTICE_ENGINE_CONTRACT:
        errs.append("practice_engine_schema")
    if body.get("schema_version") != PRACTICE_ENGINE_SCHEMA_VERSION:
        errs.append("practice_engine_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("practice_engine_run_id")
    status = body.get("status")
    if status not in ("ready", "needs_practice", "blocked"):
        errs.append("practice_engine_status")
    scores = body.get("scores")
    if not isinstance(scores, dict):
        errs.append("practice_engine_scores")
        return errs
    for key in ("gap_severity", "readiness_signal", "expected_improvement"):
        value = scores.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"practice_engine_score_type:{key}")
            continue
        num = float(value)
        if num < 0.0 or num > 1.0:
            errs.append(f"practice_engine_score_range:{key}")
    if not errs:
        errs.extend(_validate_status_score_semantics(status, scores))
    errs.extend(_validate_result_status_coherence(status, body.get("result")))
    errs.extend(_validate_evidence(body.get("evidence")))
    return errs


def validate_practice_engine_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["practice_engine_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["practice_engine_json"]
    return validate_practice_engine_dict(body)

