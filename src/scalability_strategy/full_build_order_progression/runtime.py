"""Deterministic full build order progression derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    FULL_BUILD_ORDER_PROGRESSION_CONTRACT,
    FULL_BUILD_ORDER_PROGRESSION_SCHEMA_VERSION,
)

_EXPECTED_ORDER = [
    "planner_doc",
    "planner_prompt",
    "executor",
    "verifier",
    "executor_fix",
    "verifier_fix",
    "repair",
    "finalize",
]
_EXPECTED_RANK = {name: idx for idx, name in enumerate(_EXPECTED_ORDER)}


def _expected_for_mode(mode: str) -> list[str]:
    if mode == "baseline":
        return ["executor", "finalize"]
    if mode == "guarded_pipeline":
        return ["planner_doc", "planner_prompt", "executor", "finalize"]
    return ["planner_doc", "planner_prompt", "executor", "finalize"]


def build_full_build_order_progression(
    *,
    run_id: str,
    mode: str,
    orchestration_events: list[dict[str, Any]],
) -> dict[str, Any]:
    sequence: list[str] = []
    for row in orchestration_events:
        if not isinstance(row, dict):
            continue
        if row.get("type") != "stage_event":
            continue
        stage = row.get("stage")
        if isinstance(stage, str) and stage.strip():
            sequence.append(stage.strip())
    all_known = all(stage in _EXPECTED_RANK for stage in sequence)
    starts_ok = bool(sequence) and sequence[0] in {"planner_doc", "executor"}
    ends_ok = bool(sequence) and sequence[-1] == "finalize"
    monotonic = True
    last_rank = -1
    for stage in sequence:
        rank = _EXPECTED_RANK.get(stage, -1)
        if rank < last_rank:
            monotonic = False
            break
        last_rank = rank
    expected_required = _expected_for_mode(mode)
    required_present = all(stage in sequence for stage in expected_required)
    status = "ordered"
    if not ends_ok or not required_present:
        status = "incomplete"
    if not all_known or not monotonic:
        status = "out_of_order"
    score_checks = [all_known, starts_ok, ends_ok, monotonic, required_present]
    score = round(sum(1 for ok in score_checks if ok) / len(score_checks), 4)
    violations: list[dict[str, str]] = []
    if not all_known:
        for stage in sequence:
            if stage not in _EXPECTED_RANK:
                violations.append({"type": "unknown_stage", "stage": stage})
    if not monotonic:
        violations.append({"type": "order_regression", "stage": "sequence"})
    if not required_present:
        for stage in expected_required:
            if stage not in sequence:
                violations.append({"type": "missing_required_stage", "stage": stage})
    return {
        "schema": FULL_BUILD_ORDER_PROGRESSION_CONTRACT,
        "schema_version": FULL_BUILD_ORDER_PROGRESSION_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "stage_sequence": sequence,
        "expected_order": _EXPECTED_ORDER,
        "checks": {
            "all_stages_known": all_known,
            "starts_with_allowed_entry_stage": starts_ok,
            "ends_with_finalize": ends_ok,
            "monotonic_progression": monotonic,
            "required_stages_present": required_present,
        },
        "summary": {
            "observed_stage_count": len(sequence),
            "distinct_stage_count": len(set(sequence)),
            "required_stage_count": len(expected_required),
            "required_stage_present_count": sum(1 for stage in expected_required if stage in sequence),
            "order_score": score,
        },
        "violations": violations,
        "evidence": {
            "run_manifest_ref": "run-manifest.json",
            "orchestration_ref": "orchestration.jsonl",
            "progression_ref": "strategy/full_build_order_progression.json",
        },
    }

