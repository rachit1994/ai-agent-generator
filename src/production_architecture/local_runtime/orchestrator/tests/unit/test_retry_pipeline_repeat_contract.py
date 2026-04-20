"""§10.C — ``execute_single_task`` repeat profile envelope (``repeat`` >= 2)."""

from __future__ import annotations

from workflow_pipelines.retry_repeat_profile.retry_pipeline_contract import (
    RETRY_PIPELINE_REPEAT_CONTRACT,
    validate_repeat_profile_result,
)


def test_retry_pipeline_repeat_contract_id() -> None:
    assert RETRY_PIPELINE_REPEAT_CONTRACT == "sde.retry_pipeline_repeat_profile.v1"


def test_validate_repeat_profile_skips_when_repeat_lt_2() -> None:
    assert validate_repeat_profile_result({"not": "validated"}, repeat=1) == []


def test_validate_repeat_profile_ok() -> None:
    body = {
        "schema": RETRY_PIPELINE_REPEAT_CONTRACT,
        "repeat": 2,
        "task": "t",
        "mode": "baseline",
        "runs": [
            {"run_id": "a", "output_dir": "/tmp/1", "output": "{}"},
            {"run_id": "b", "output_dir": "/tmp/2", "output": "{}"},
        ],
        "all_runs_no_pipeline_error": True,
        "validation_ready_all": False,
    }
    assert validate_repeat_profile_result(body, repeat=2) == []


def test_validate_repeat_profile_error_run_ok() -> None:
    body = {
        "schema": RETRY_PIPELINE_REPEAT_CONTRACT,
        "repeat": 2,
        "task": "",
        "mode": "baseline",
        "runs": [
            {"run_id": "a", "output_dir": "/tmp/1", "output": "{}"},
            {"run_id": "b", "output_dir": "/tmp/2", "error": {"type": "X", "message": "m"}},
        ],
        "all_runs_no_pipeline_error": False,
        "validation_ready_all": False,
    }
    assert validate_repeat_profile_result(body, repeat=2) == []


def test_validate_repeat_profile_repeat_mismatch() -> None:
    body = {
        "schema": RETRY_PIPELINE_REPEAT_CONTRACT,
        "repeat": 3,
        "task": "t",
        "mode": "baseline",
        "runs": [{"run_id": "a", "output_dir": "/1", "output": "{}"}],
        "all_runs_no_pipeline_error": True,
        "validation_ready_all": False,
    }
    assert "repeat_profile_repeat_mismatch" in validate_repeat_profile_result(body, repeat=2)


def test_validate_repeat_profile_runs_len() -> None:
    body = {
        "schema": RETRY_PIPELINE_REPEAT_CONTRACT,
        "repeat": 2,
        "task": "t",
        "mode": "baseline",
        "runs": [{"run_id": "a", "output_dir": "/1", "output": "{}"}],
        "all_runs_no_pipeline_error": True,
        "validation_ready_all": False,
    }
    assert "repeat_profile_runs_len" in validate_repeat_profile_result(body, repeat=2)


def test_validate_repeat_profile_both_output_and_error() -> None:
    body = {
        "schema": RETRY_PIPELINE_REPEAT_CONTRACT,
        "repeat": 2,
        "task": "t",
        "mode": "baseline",
        "runs": [
            {"run_id": "a", "output_dir": "/1", "output": "{}", "error": {}},
            {"run_id": "b", "output_dir": "/2", "output": "{}"},
        ],
        "all_runs_no_pipeline_error": True,
        "validation_ready_all": False,
    }
    assert any("repeat_profile_run_outcome" in e for e in validate_repeat_profile_result(body, repeat=2))


def test_validate_repeat_profile_neither_output_nor_error() -> None:
    body = {
        "schema": RETRY_PIPELINE_REPEAT_CONTRACT,
        "repeat": 2,
        "task": "t",
        "mode": "baseline",
        "runs": [
            {"run_id": "a", "output_dir": "/1"},
            {"run_id": "b", "output_dir": "/2", "output": "{}"},
        ],
        "all_runs_no_pipeline_error": True,
        "validation_ready_all": False,
    }
    assert any("repeat_profile_run_outcome" in e for e in validate_repeat_profile_result(body, repeat=2))


def test_validate_repeat_profile_not_object_for_repeat_gte_2() -> None:
    assert validate_repeat_profile_result("bad", repeat=2) == ["repeat_profile_not_object"]


def test_validate_repeat_profile_requires_schema() -> None:
    body = {
        "repeat": 2,
        "task": "t",
        "mode": "baseline",
        "runs": [
            {"run_id": "a", "output_dir": "/tmp/1", "output": "{}"},
            {"run_id": "b", "output_dir": "/tmp/2", "output": "{}"},
        ],
        "all_runs_no_pipeline_error": True,
        "validation_ready_all": False,
    }
    assert "repeat_profile_schema" in validate_repeat_profile_result(body, repeat=2)


def test_validate_repeat_profile_error_shape_requires_type_and_message() -> None:
    body = {
        "schema": RETRY_PIPELINE_REPEAT_CONTRACT,
        "repeat": 2,
        "task": "t",
        "mode": "baseline",
        "runs": [
            {"run_id": "a", "output_dir": "/tmp/1", "output": "{}"},
            {"run_id": "b", "output_dir": "/tmp/2", "error": {"type": ""}},
        ],
        "all_runs_no_pipeline_error": False,
        "validation_ready_all": False,
    }
    errs = validate_repeat_profile_result(body, repeat=2)
    assert "repeat_profile_error_type:1" in errs or "repeat_profile_error_message:1" in errs


def test_validate_repeat_profile_enforces_consistency_flags() -> None:
    body = {
        "schema": RETRY_PIPELINE_REPEAT_CONTRACT,
        "repeat": 2,
        "task": "t",
        "mode": "baseline",
        "runs": [
            {"run_id": "a", "output_dir": "/tmp/1", "output": "{}"},
            {"run_id": "b", "output_dir": "/tmp/2", "error": {"type": "X", "message": "m"}},
        ],
        "all_runs_no_pipeline_error": True,
        "validation_ready_all": True,
    }
    errs = validate_repeat_profile_result(body, repeat=2)
    assert "repeat_profile_all_runs_no_pipeline_error_value" in errs
    assert "repeat_profile_validation_ready_all_value" in errs
