from __future__ import annotations

from workflow_pipelines.benchmark_checkpoint import (
    build_benchmark_checkpoint_runtime,
    validate_benchmark_checkpoint_runtime_dict,
)


def test_build_benchmark_checkpoint_runtime_deterministic() -> None:
    checkpoint = {"run_id": "bench-ck", "finished": False, "completed_task_ids": ["a"]}
    one = build_benchmark_checkpoint_runtime(checkpoint=checkpoint)
    two = build_benchmark_checkpoint_runtime(checkpoint=checkpoint)
    assert one == two
    assert one["status"] == "in_progress"
    assert validate_benchmark_checkpoint_runtime_dict(one) == []


def test_validate_benchmark_checkpoint_runtime_fail_closed() -> None:
    errs = validate_benchmark_checkpoint_runtime_dict({"schema": "bad"})
    assert "benchmark_checkpoint_runtime_schema" in errs
    assert "benchmark_checkpoint_runtime_schema_version" in errs
