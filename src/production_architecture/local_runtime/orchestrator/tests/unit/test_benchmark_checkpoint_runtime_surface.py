from __future__ import annotations

from workflow_pipelines.benchmark_checkpoint import build_benchmark_checkpoint_runtime
from workflow_pipelines.benchmark_checkpoint.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "workflow_pipelines/benchmark_checkpoint"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "workflow_pipelines.benchmark_checkpoint.runtime" in refs


def test_benchmark_checkpoint_runtime_treats_truthy_non_boolean_finished_as_false() -> None:
    runtime = build_benchmark_checkpoint_runtime(
        checkpoint={"run_id": "bench-ck", "finished": "true", "completed_task_ids": ["task-1"]}
    )
    assert runtime["status"] == "in_progress"
    assert runtime["checks"]["finished"] is False
