"""Contracts for full build order progression artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FULL_BUILD_ORDER_PROGRESSION_CONTRACT = "sde.full_build_order_progression.v1"
FULL_BUILD_ORDER_PROGRESSION_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_ALLOWED_STATUS = {"ordered", "out_of_order", "incomplete"}
_CANONICAL_EVIDENCE_REFS = {
    "run_manifest_ref": "run-manifest.json",
    "orchestration_ref": "orchestration.jsonl",
    "progression_ref": "strategy/full_build_order_progression.json",
}


def _expected_required_for_mode(mode: str) -> list[str]:
    if mode == "baseline":
        return ["executor", "finalize"]
    return ["planner_doc", "planner_prompt", "executor", "finalize"]


def _has_ordered_status_mismatch(checks: dict[str, bool]) -> bool:
    return not all(
        (
            checks["all_stages_known"],
            checks["starts_with_allowed_entry_stage"],
            checks["ends_with_finalize"],
            checks["monotonic_progression"],
            checks["required_stages_present"],
        )
    )


def _has_out_of_order_status_mismatch(checks: dict[str, bool]) -> bool:
    return checks["all_stages_known"] and checks["monotonic_progression"]


def _has_incomplete_status_mismatch(checks: dict[str, bool]) -> bool:
    if not checks["all_stages_known"] or not checks["monotonic_progression"]:
        return True
    return all(
        (
            checks["starts_with_allowed_entry_stage"],
            checks["ends_with_finalize"],
            checks["required_stages_present"],
        )
    )


def _coerced_checks(checks: dict[str, Any]) -> dict[str, bool] | None:
    all_stages_known = checks.get("all_stages_known")
    starts_with_allowed_entry_stage = checks.get("starts_with_allowed_entry_stage")
    ends_with_finalize = checks.get("ends_with_finalize")
    monotonic_progression = checks.get("monotonic_progression")
    required_stages_present = checks.get("required_stages_present")
    check_values = (
        all_stages_known,
        starts_with_allowed_entry_stage,
        ends_with_finalize,
        monotonic_progression,
        required_stages_present,
    )
    if any(not isinstance(value, bool) for value in check_values):
        return None
    return {
        "all_stages_known": all_stages_known,
        "starts_with_allowed_entry_stage": starts_with_allowed_entry_stage,
        "ends_with_finalize": ends_with_finalize,
        "monotonic_progression": monotonic_progression,
        "required_stages_present": required_stages_present,
    }


def _validate_status_semantics(status: Any, checks: Any) -> list[str]:
    if status not in _ALLOWED_STATUS or not isinstance(checks, dict):
        return []
    typed_checks = _coerced_checks(checks)
    if typed_checks is None:
        return []
    if status == "ordered":
        return ["full_build_order_progression_status_checks_mismatch"] if _has_ordered_status_mismatch(typed_checks) else []
    if status == "out_of_order":
        return ["full_build_order_progression_status_checks_mismatch"] if _has_out_of_order_status_mismatch(typed_checks) else []
    return ["full_build_order_progression_status_checks_mismatch"] if _has_incomplete_status_mismatch(typed_checks) else []


def _validate_core_fields(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if body.get("schema") != FULL_BUILD_ORDER_PROGRESSION_CONTRACT:
        errs.append("full_build_order_progression_schema")
    if body.get("schema_version") != FULL_BUILD_ORDER_PROGRESSION_SCHEMA_VERSION:
        errs.append("full_build_order_progression_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("full_build_order_progression_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("full_build_order_progression_mode")
    status = body.get("status")
    if status not in _ALLOWED_STATUS:
        errs.append("full_build_order_progression_status")
    sequence = body.get("stage_sequence")
    if not isinstance(sequence, list) or any(not isinstance(row, str) or not row.strip() for row in sequence):
        errs.append("full_build_order_progression_stage_sequence")
    return errs


def _validate_checks(checks: Any) -> list[str]:
    if not isinstance(checks, dict):
        return ["full_build_order_progression_checks"]
    errs: list[str] = []
    for key in (
        "all_stages_known",
        "starts_with_allowed_entry_stage",
        "ends_with_finalize",
        "monotonic_progression",
        "required_stages_present",
    ):
        if not isinstance(checks.get(key), bool):
            errs.append(f"full_build_order_progression_check_type:{key}")
    return errs


def _validate_summary(summary: Any) -> list[str]:
    if not isinstance(summary, dict):
        return ["full_build_order_progression_summary"]
    score = summary.get("order_score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return ["full_build_order_progression_order_score_type"]
    numeric_score = float(score)
    if numeric_score < 0.0 or numeric_score > 1.0:
        return ["full_build_order_progression_order_score_range"]
    return []


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["full_build_order_progression_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        ref = evidence.get(key)
        if not isinstance(ref, str) or not ref.strip():
            errs.append(f"full_build_order_progression_evidence_ref:{key}")
            continue
        normalized = ref.strip()
        if normalized != expected:
            errs.append(f"full_build_order_progression_evidence_ref:{key}")
            continue
        ref_path = Path(normalized)
        if ref_path.is_absolute() or ".." in ref_path.parts:
            errs.append(f"full_build_order_progression_evidence_ref:{key}")
    return errs


def _validate_summary_sequence_semantics(
    *,
    mode: Any,
    sequence: Any,
    summary: Any,
) -> list[str]:
    if (
        mode not in _ALLOWED_MODES
        or not isinstance(sequence, list)
        or any(not isinstance(row, str) or not row.strip() for row in sequence)
        or not isinstance(summary, dict)
    ):
        return []
    observed_stage_count = summary.get("observed_stage_count")
    distinct_stage_count = summary.get("distinct_stage_count")
    required_stage_count = summary.get("required_stage_count")
    required_stage_present_count = summary.get("required_stage_present_count")
    count_values = (
        observed_stage_count,
        distinct_stage_count,
        required_stage_count,
        required_stage_present_count,
    )
    if any(isinstance(value, bool) or not isinstance(value, int) for value in count_values):
        return []
    expected_required = _expected_required_for_mode(mode)
    expected_observed = len(sequence)
    expected_distinct = len(set(sequence))
    expected_required_count = len(expected_required)
    expected_required_present_count = sum(1 for stage in expected_required if stage in sequence)
    if (
        observed_stage_count != expected_observed
        or distinct_stage_count != expected_distinct
        or required_stage_count != expected_required_count
        or required_stage_present_count != expected_required_present_count
    ):
        return ["full_build_order_progression_summary_sequence_mismatch"]
    return []


def _validate_order_score_semantics(summary: Any, checks: Any) -> list[str]:
    if not isinstance(summary, dict) or not isinstance(checks, dict):
        return []
    typed_checks = _coerced_checks(checks)
    score = summary.get("order_score")
    if typed_checks is None or isinstance(score, bool) or not isinstance(score, (int, float)):
        return []
    expected = round(sum(1 for value in typed_checks.values() if value) / 5, 4)
    if round(float(score), 4) != expected:
        return ["full_build_order_progression_order_score_mismatch"]
    return []


def _validate_mode_entry_semantics(mode: Any, sequence: Any, checks: Any) -> list[str]:
    if mode != "baseline" or not isinstance(sequence, list) or not isinstance(checks, dict):
        return []
    typed_checks = _coerced_checks(checks)
    if typed_checks is None or not sequence:
        return []
    if typed_checks["starts_with_allowed_entry_stage"] and sequence[0] != "executor":
        return ["full_build_order_progression_mode_entry_stage_mismatch"]
    return []


def validate_full_build_order_progression_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["full_build_order_progression_not_object"]
    errs = _validate_core_fields(body)
    status = body.get("status")
    checks = body.get("checks")
    errs.extend(_validate_checks(checks))
    summary = body.get("summary")
    errs.extend(_validate_summary(summary))
    errs.extend(_validate_evidence(body.get("evidence")))
    if not errs:
        errs.extend(_validate_status_semantics(status, checks))
        errs.extend(_validate_order_score_semantics(summary, checks))
        errs.extend(
            _validate_mode_entry_semantics(
                body.get("mode"),
                body.get("stage_sequence"),
                checks,
            )
        )
        errs.extend(
            _validate_summary_sequence_semantics(
                mode=body.get("mode"),
                sequence=body.get("stage_sequence"),
                summary=summary,
            )
        )
    return errs


def validate_full_build_order_progression_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["full_build_order_progression_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["full_build_order_progression_json"]
    return validate_full_build_order_progression_dict(body)

