"""Deterministic practice engine derivation."""

from __future__ import annotations

from typing import Any

from .contracts import PRACTICE_ENGINE_CONTRACT, PRACTICE_ENGINE_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def execute_practice_engine_runtime(
    *,
    task_spec: dict[str, Any],
    evaluation_result: dict[str, Any],
    reflection_bundle: dict[str, Any],
    review: dict[str, Any],
) -> dict[str, Any]:
    missing_signal_sources: list[str] = []
    if not isinstance(task_spec, dict) or not task_spec:
        missing_signal_sources.append("task_spec")
    if not isinstance(evaluation_result, dict) or "passed" not in evaluation_result:
        missing_signal_sources.append("evaluation_result")
    root_causes = reflection_bundle.get("root_causes") if isinstance(reflection_bundle, dict) else None
    if not isinstance(root_causes, list):
        missing_signal_sources.append("reflection_bundle")
        root_causes = []
    if not isinstance(review, dict) or not isinstance(review.get("status"), str):
        missing_signal_sources.append("review")
    malformed_root_cause_rows = len([row for row in root_causes if not isinstance(row, str)])
    return {
        "signals_processed": 4,
        "root_causes_processed": len(root_causes),
        "malformed_root_cause_rows": malformed_root_cause_rows,
        "missing_signal_sources": missing_signal_sources,
    }


def build_practice_engine(
    *,
    run_id: str,
    task_spec: dict[str, Any],
    evaluation_result: dict[str, Any],
    reflection_bundle: dict[str, Any],
    review: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_practice_engine_runtime(
        task_spec=task_spec,
        evaluation_result=evaluation_result,
        reflection_bundle=reflection_bundle,
        review=review,
    )
    _ = task_spec
    readiness_signal = 0.0
    expected_improvement = 0.0
    if isinstance(evaluation_result, dict):
        passed = evaluation_result.get("passed") is True
        readiness_signal = 1.0 if passed else 0.4
        expected_improvement = 0.8 if passed else 0.3
    root_causes = reflection_bundle.get("root_causes") if isinstance(reflection_bundle, dict) else []
    root_count = len(root_causes) if isinstance(root_causes, list) else 0
    gap_severity = _clamp01(0.3 + min(0.7, root_count * 0.1))
    review_pass = str(review.get("status", "")) == "completed_review_pass"
    if not review_pass:
        readiness_signal = _clamp01(readiness_signal - 0.2)
    readiness_signal = _clamp01(readiness_signal)
    expected_improvement = _clamp01(expected_improvement)
    status = "blocked"
    if review_pass and readiness_signal >= 0.6 and expected_improvement >= 0.25:
        status = "ready"
    elif readiness_signal >= 0.35:
        status = "needs_practice"
    return {
        "schema": PRACTICE_ENGINE_CONTRACT,
        "schema_version": PRACTICE_ENGINE_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "execution": execution,
        "scores": {
            "gap_severity": gap_severity,
            "readiness_signal": readiness_signal,
            "expected_improvement": expected_improvement,
        },
        "plan": {
            "task": "deliberate_practice_cycle",
            "focus_area": "delivery.structured_output",
            "acceptance_criteria": ["focus:delivery.structured_output"],
        },
        "result": {"passed": status == "ready"},
        "evidence": {
            "task_spec_ref": "practice/task_spec.json",
            "evaluation_result_ref": "practice/evaluation_result.json",
            "practice_engine_ref": "practice/practice_engine.json",
        },
    }

