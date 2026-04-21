from __future__ import annotations

import pytest

from core_components.practice_engine import build_practice_engine, validate_practice_engine_dict


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

