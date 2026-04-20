"""Structural contract for ``lifecycle/promotion_package.json`` (§13 promotion eval, **HS26** evidence)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

PROMOTION_EVAL_PACKAGE_CONTRACT: Final = "sde.promotion_eval_package.v1"
PROMOTION_EVAL_SCHEMA_VERSION: Final = "1.0"


def _errs_nonblank_string(body: dict[str, Any], snake: str, camel: str | None, token: str) -> list[str]:
    val = body.get(snake)
    if val is None and camel is not None:
        val = body.get(camel)
    if not isinstance(val, str) or not val.strip():
        return [token]
    return []


def _errs_evaluator_signals(body: dict[str, Any]) -> list[str]:
    sigs = body.get("independent_evaluator_signal_ids", body.get("independentEvaluatorSignalIds"))
    if not isinstance(sigs, list) or len(sigs) == 0:
        return ["promotion_package_evaluator_signals"]
    errs: list[str] = []
    for idx, item in enumerate(sigs):
        if not isinstance(item, str) or not item.strip():
            errs.append(f"promotion_package_evaluator_signal_{idx}")
    return errs


def _errs_duplicates(values: list[str], token: str) -> list[str]:
    if len(set(values)) != len(values):
        return [token]
    return []


def _errs_evidence_window(body: dict[str, Any]) -> list[str]:
    ew = body.get("evidence_window", body.get("evidenceWindow"))
    if ew is None:
        return ["promotion_package_evidence_window"]
    if not isinstance(ew, list):
        return ["promotion_package_evidence_window_type"]
    if len(ew) == 0:
        return ["promotion_package_evidence_window_empty"]
    errs: list[str] = []
    for jdx, ref in enumerate(ew):
        if not isinstance(ref, str) or not ref.strip():
            errs.append(f"promotion_package_evidence_window_{jdx}")
    return errs


def _unknown_keys(body: dict[str, Any]) -> list[str]:
    allowed = {
        "schema_version",
        "schemaVersion",
        "aggregate_id",
        "aggregateId",
        "current_stage",
        "currentStage",
        "proposed_stage",
        "proposedStage",
        "independent_evaluator_signal_ids",
        "independentEvaluatorSignalIds",
        "evidence_window",
        "evidenceWindow",
    }
    return [f"promotion_package_unknown_key_{key}" for key in body if key not in allowed]


def validate_promotion_package_dict(body: Any) -> list[str]:
    """Return stable error tokens; empty means the dict matches the repo harness shape (HS26-compatible)."""
    if not isinstance(body, dict):
        return ["promotion_package_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_nonblank_string(b, "schema_version", "schemaVersion", "promotion_package_schema_version"))
    if (
        isinstance(b.get("schema_version", b.get("schemaVersion")), str)
        and b.get("schema_version", b.get("schemaVersion")) != PROMOTION_EVAL_SCHEMA_VERSION
    ):
        errs.append("promotion_package_schema_version_value")
    errs.extend(_errs_nonblank_string(b, "aggregate_id", "aggregateId", "promotion_package_aggregate_id"))
    errs.extend(_errs_nonblank_string(b, "current_stage", "currentStage", "promotion_package_current_stage"))
    errs.extend(_errs_nonblank_string(b, "proposed_stage", "proposedStage", "promotion_package_proposed_stage"))
    errs.extend(_errs_evaluator_signals(b))
    errs.extend(_errs_evidence_window(b))
    errs.extend(_unknown_keys(b))
    sigs = b.get("independent_evaluator_signal_ids", b.get("independentEvaluatorSignalIds"))
    if isinstance(sigs, list) and all(isinstance(item, str) and item.strip() for item in sigs):
        errs.extend(_errs_duplicates([str(item).strip() for item in sigs], "promotion_package_evaluator_signals_duplicate"))
    ew = b.get("evidence_window", b.get("evidenceWindow"))
    if isinstance(ew, list) and all(isinstance(item, str) and item.strip() for item in ew):
        normalized_window = [str(item).strip() for item in ew]
        errs.extend(_errs_duplicates(normalized_window, "promotion_package_evidence_window_duplicate"))
        aggregate_id = b.get("aggregate_id", b.get("aggregateId"))
        if isinstance(aggregate_id, str) and aggregate_id.strip() and aggregate_id.strip() not in normalized_window:
            errs.append("promotion_package_evidence_window_missing_aggregate")
    return errs


def validate_promotion_package_path(path: Path) -> list[str]:
    """Return stable error tokens for JSON on disk (no raise)."""
    if not path.is_file():
        return ["promotion_package_file_missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ["promotion_package_unreadable"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return ["promotion_package_json"]
    return validate_promotion_package_dict(parsed)
