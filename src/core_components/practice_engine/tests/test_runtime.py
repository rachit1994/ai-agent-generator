from __future__ import annotations

import pytest

from core_components.practice_engine import (
    build_practice_engine,
    execute_practice_engine_runtime,
    validate_practice_engine_dict,
)


def test_build_practice_engine_is_deterministic() -> None:
    one = build_practice_engine(
        run_id="rid-practice",
        task_spec={"task": "x"},
        evaluation_result={"passed": False},
        reflection_bundle={"root_causes": ["a"]},
        review={"status": "completed_review_pass"},
    )
    two = build_practice_engine(
        run_id="rid-practice",
        task_spec={"task": "x"},
        evaluation_result={"passed": False},
        reflection_bundle={"root_causes": ["a"]},
        review={"status": "completed_review_pass"},
    )
    assert one == two
    assert validate_practice_engine_dict(one) == []
    assert one["execution"]["signals_processed"] == 4


def test_validate_practice_engine_fail_closed() -> None:
    errs = validate_practice_engine_dict({"schema": "bad"})
    assert "practice_engine_schema" in errs
    assert "practice_engine_schema_version" in errs


def test_build_practice_engine_treats_truthy_non_boolean_passed_as_false() -> None:
    payload = build_practice_engine(
        run_id="rid-practice-truthy",
        task_spec={"task": "x"},
        evaluation_result={"passed": "true"},
        reflection_bundle={"root_causes": []},
        review={"status": "completed_review_pass"},
    )
    assert payload["scores"]["readiness_signal"] == pytest.approx(0.4)
    assert payload["status"] != "ready"


def test_build_practice_engine_does_not_mark_ready_without_review_pass() -> None:
    payload = build_practice_engine(
        run_id="rid-practice-no-review-pass",
        task_spec={"task": "x"},
        evaluation_result={"passed": True},
        reflection_bundle={"root_causes": []},
        review={},
    )
    assert payload["status"] != "ready"
    assert payload["result"]["passed"] is False


def test_validate_practice_engine_rejects_status_scores_mismatch() -> None:
    payload = build_practice_engine(
        run_id="rid-practice-mismatch",
        task_spec={"task": "x"},
        evaluation_result={"passed": False},
        reflection_bundle={"root_causes": []},
        review={"status": "completed_review_pass"},
    )
    payload["status"] = "ready"
    errs = validate_practice_engine_dict(payload)
    assert "practice_engine_status_scores_mismatch" in errs


def test_validate_practice_engine_rejects_result_status_mismatch() -> None:
    payload = build_practice_engine(
        run_id="rid-practice-mismatch",
        task_spec={"task": "x"},
        evaluation_result={"passed": False},
        reflection_bundle={"root_causes": []},
        review={"status": "completed_review_pass"},
    )
    payload["result"]["passed"] = True
    errs = validate_practice_engine_dict(payload)
    assert "practice_engine_result_status_mismatch" in errs


def test_validate_practice_engine_rejects_invalid_evidence_refs() -> None:
    payload = build_practice_engine(
        run_id="rid-practice-evidence",
        task_spec={"task": "x"},
        evaluation_result={"passed": False},
        reflection_bundle={"root_causes": []},
        review={"status": "completed_review_pass"},
    )
    payload["evidence"]["task_spec_ref"] = "../practice/task_spec.json"
    payload["evidence"]["evaluation_result_ref"] = ""
    errs = validate_practice_engine_dict(payload)
    assert "practice_engine_evidence_ref:task_spec_ref" in errs
    assert "practice_engine_evidence_ref:evaluation_result_ref" in errs


def test_execute_practice_engine_runtime_detects_missing_sources() -> None:
    execution = execute_practice_engine_runtime(
        task_spec={},
        evaluation_result={},
        reflection_bundle={"root_causes": ["ok", {"bad": True}]},  # type: ignore[list-item]
        review={},
    )
    assert execution["signals_processed"] == 4
    assert execution["root_causes_processed"] == 2
    assert execution["malformed_root_cause_rows"] == 1
    assert execution["missing_signal_sources"] == ["task_spec", "evaluation_result", "review"]

