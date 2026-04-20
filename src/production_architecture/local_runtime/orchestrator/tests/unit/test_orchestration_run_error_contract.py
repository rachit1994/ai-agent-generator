"""§10.L — ``single_task`` ``run_error`` ``orchestration.jsonl`` line shape."""

from __future__ import annotations

from workflow_pipelines.orchestration_run_error.orchestration_run_error_contract import (
    ORCHESTRATION_RUN_ERROR_CONTRACT,
    validate_orchestration_run_error_dict,
)


def test_orchestration_run_error_contract_id() -> None:
    assert ORCHESTRATION_RUN_ERROR_CONTRACT == "sde.orchestration_run_error.v1"


def test_validate_run_error_ok_minimal() -> None:
    body = {
        "run_id": "r-1",
        "type": "run_error",
        "mode": "baseline",
        "error_type": "RuntimeError",
        "error_message": "x",
    }
    assert validate_orchestration_run_error_dict(body) == []


def test_validate_run_error_ok_with_detail() -> None:
    body = {
        "run_id": "r-1",
        "type": "run_error",
        "mode": "guarded_pipeline",
        "error_type": "JSONDecodeError",
        "error_message": "",
        "detail": "output_parse_failed",
    }
    assert validate_orchestration_run_error_dict(body) == []


def test_validate_run_error_unknown_key() -> None:
    body = {
        "run_id": "r",
        "type": "run_error",
        "mode": "baseline",
        "error_type": "E",
        "error_message": "m",
        "extra": 1,
    }
    assert "orchestration_run_error_unknown_keys" in validate_orchestration_run_error_dict(body)


def test_validate_run_error_bad_mode() -> None:
    body = {
        "run_id": "r",
        "type": "run_error",
        "mode": "both",
        "error_type": "E",
        "error_message": "m",
    }
    assert "orchestration_run_error_mode" in validate_orchestration_run_error_dict(body)


def test_validate_run_error_blank_detail() -> None:
    body = {
        "run_id": "r",
        "type": "run_error",
        "mode": "baseline",
        "error_type": "E",
        "error_message": "m",
        "detail": "   ",
    }
    assert "orchestration_run_error_detail" in validate_orchestration_run_error_dict(body)
