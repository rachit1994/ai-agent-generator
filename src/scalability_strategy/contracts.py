"""Contracts for scalability strategy artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

SCALABILITY_STRATEGY_CONTRACT = "sde.scalability_strategy.v1"
SCALABILITY_STRATEGY_SCHEMA_VERSION = "1.0"
_OVERALL_SCORE_TOLERANCE = 1e-4
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_CANONICAL_EVIDENCE_REFS = {
    "summary_ref": "summary.json",
    "review_ref": "review.json",
    "scalability_ref": "strategy/scalability_strategy.json",
}


def _validate_scores(scores: Any) -> tuple[list[str], float | None]:
    if not isinstance(scores, dict):
        return (["scalability_strategy_scores"], None)
    errs: list[str] = []
    required = (
        "event_scaling_score",
        "memory_scaling_score",
        "replay_scaling_score",
        "multi_agent_scaling_score",
        "overall_scaling_score",
    )
    for key in required:
        value = scores.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"scalability_strategy_score_type:{key}")
            continue
        num = float(value)
        if not math.isfinite(num):
            errs.append(f"scalability_strategy_score_range:{key}")
            continue
        if num < 0.0 or num > 1.0:
            errs.append(f"scalability_strategy_score_range:{key}")
    if errs:
        return (errs, None)
    overall = scores.get("overall_scaling_score")
    return ([], float(overall) if isinstance(overall, (int, float)) and not isinstance(overall, bool) else None)


def _has_weighted_score_mismatch(scores: dict[str, Any]) -> bool:
    weighted = (
        0.3 * float(scores["event_scaling_score"])
        + 0.2 * float(scores["memory_scaling_score"])
        + 0.2 * float(scores["replay_scaling_score"])
        + 0.3 * float(scores["multi_agent_scaling_score"])
    )
    overall = float(scores["overall_scaling_score"])
    return abs(weighted - overall) > _OVERALL_SCORE_TOLERANCE


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["scalability_strategy_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"scalability_strategy_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized.startswith("/") or ".." in normalized.split("/"):
            errs.append(f"scalability_strategy_evidence_ref:{key}")
            continue
        if normalized != expected:
            errs.append(f"scalability_strategy_evidence_ref:{key}")
    return errs


def validate_scalability_strategy_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["scalability_strategy_not_object"]
    errs: list[str] = []
    if body.get("schema") != SCALABILITY_STRATEGY_CONTRACT:
        errs.append("scalability_strategy_schema")
    if body.get("schema_version") != SCALABILITY_STRATEGY_SCHEMA_VERSION:
        errs.append("scalability_strategy_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("scalability_strategy_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("scalability_strategy_mode")
    status = body.get("status")
    if status not in ("scalable", "constrained"):
        errs.append("scalability_strategy_status")
    score_errs, overall = _validate_scores(body.get("scores"))
    errs.extend(score_errs)
    if status == "scalable" and overall is not None and overall < 0.7:
        errs.append("scalability_strategy_status_score_mismatch")
    if status == "constrained" and overall is not None and overall >= 0.7:
        errs.append("scalability_strategy_status_score_mismatch")
    scores = body.get("scores")
    if not score_errs and isinstance(scores, dict) and _has_weighted_score_mismatch(scores):
        errs.append("scalability_strategy_overall_score_mismatch")
    errs.extend(_validate_evidence(body.get("evidence")))
    return errs


def validate_scalability_strategy_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["scalability_strategy_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["scalability_strategy_json"]
    return validate_scalability_strategy_dict(body)

