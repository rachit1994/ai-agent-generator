"""§10.C — ``execute_single_task`` repeat profile envelope (``repeat`` >= 2)."""

from __future__ import annotations

from workflow_pipelines.production_pipeline_task_to_promote.benchmark.retry_pipeline_contract import (
    RETRY_PIPELINE_REPEAT_CONTRACT,
    validate_repeat_profile_result,
)


def test_retry_pipeline_repeat_contract_id() -> None:
    assert RETRY_PIPELINE_REPEAT_CONTRACT == "sde.retry_pipeline_repeat_profile.v1"


def test_validate_repeat_profile_skips_when_repeat_lt_2() -> None:
    assert validate_repeat_profile_result({"not": "validated"}, repeat=1) == []


def test_validate_repeat_profile_ok() -> None:
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
    assert validate_repeat_profile_result(body, repeat=2) == []


def test_validate_repeat_profile_error_run_ok() -> None:
    body = {
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
