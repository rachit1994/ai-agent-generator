from __future__ import annotations

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

