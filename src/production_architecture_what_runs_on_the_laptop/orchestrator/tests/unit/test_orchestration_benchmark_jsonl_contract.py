"""§10.J — ``run_benchmark`` ``orchestration.jsonl`` resume + error line shapes."""

from __future__ import annotations

from workflow_pipelines.production_pipeline_task_to_promote.benchmark.orchestration_benchmark_jsonl_contract import (
    ORCHESTRATION_BENCHMARK_ERROR_CONTRACT,
    ORCHESTRATION_BENCHMARK_RESUME_CONTRACT,
    validate_orchestration_benchmark_error_dict,
    validate_orchestration_benchmark_resume_dict,
)


def test_orchestration_benchmark_resume_contract_id() -> None:
    assert ORCHESTRATION_BENCHMARK_RESUME_CONTRACT == "sde.orchestration_benchmark_resume.v1"


def test_orchestration_benchmark_error_contract_id() -> None:
    assert ORCHESTRATION_BENCHMARK_ERROR_CONTRACT == "sde.orchestration_benchmark_error.v1"


def test_validate_benchmark_resume_ok() -> None:
    body = {"run_id": "b-1", "type": "benchmark_resume", "pending_task_count": 3}
    assert validate_orchestration_benchmark_resume_dict(body) == []


def test_validate_benchmark_resume_bad_pending() -> None:
    body = {"run_id": "b", "type": "benchmark_resume", "pending_task_count": -1}
    assert "orchestration_benchmark_resume_pending_task_count" in validate_orchestration_benchmark_resume_dict(body)


def test_validate_benchmark_resume_wrong_type() -> None:
    body = {"run_id": "b", "type": "benchmark_error", "pending_task_count": 0}
    assert "orchestration_benchmark_resume_type" in validate_orchestration_benchmark_resume_dict(body)


def test_validate_benchmark_error_ok() -> None:
    body = {
        "run_id": "b-1",
        "type": "benchmark_error",
        "error_type": "RuntimeError",
        "error_message": "x",
    }
    assert validate_orchestration_benchmark_error_dict(body) == []


def test_validate_benchmark_error_empty_message_ok() -> None:
    body = {
        "run_id": "b-1",
        "type": "benchmark_error",
        "error_type": "ValueError",
        "error_message": "",
    }
    assert validate_orchestration_benchmark_error_dict(body) == []


def test_validate_benchmark_error_blank_error_type() -> None:
    body = {
        "run_id": "b",
        "type": "benchmark_error",
        "error_type": "   ",
        "error_message": "m",
    }
    assert "orchestration_benchmark_error_error_type" in validate_orchestration_benchmark_error_dict(body)
