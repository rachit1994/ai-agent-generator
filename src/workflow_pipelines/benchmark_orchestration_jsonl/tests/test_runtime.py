from __future__ import annotations

from workflow_pipelines.benchmark_orchestration_jsonl import (
    build_benchmark_orchestration_jsonl_runtime,
    validate_benchmark_orchestration_jsonl_runtime_dict,
)


def test_build_benchmark_orchestration_jsonl_runtime_is_deterministic() -> None:
    rows = [
        {"run_id": "rid-bench", "type": "benchmark_resume", "pending_task_count": 2},
        {
            "run_id": "rid-bench",
            "type": "benchmark_error",
            "error_type": "RuntimeError",
            "error_message": "x",
        },
    ]
    one = build_benchmark_orchestration_jsonl_runtime(run_id="rid-bench", orchestration_rows=rows)
    two = build_benchmark_orchestration_jsonl_runtime(run_id="rid-bench", orchestration_rows=rows)
    assert one == two
    assert one["status"] == "clean"
    assert validate_benchmark_orchestration_jsonl_runtime_dict(one) == []


def test_validate_benchmark_orchestration_jsonl_runtime_fail_closed() -> None:
    errs = validate_benchmark_orchestration_jsonl_runtime_dict({"schema": "bad"})
    assert "benchmark_orchestration_jsonl_runtime_schema" in errs
    assert "benchmark_orchestration_jsonl_runtime_schema_version" in errs


def test_validate_benchmark_orchestration_jsonl_runtime_rejects_counts_status_mismatch() -> None:
    errs = validate_benchmark_orchestration_jsonl_runtime_dict(
        {
            "schema": "sde.benchmark_orchestration_jsonl_runtime.v1",
            "schema_version": "1.0",
            "run_id": "rid-bench",
            "status": "clean",
            "checks": {
                "orchestration_present": False,
                "resume_lines_valid": True,
                "error_lines_valid": True,
            },
            "counts": {
                "row_count": 1,
                "resume_count": 1,
                "error_count": 0,
            },
            "evidence": {},
        }
    )
    assert "benchmark_orchestration_jsonl_runtime_counts_mismatch" in errs
