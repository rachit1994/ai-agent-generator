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
