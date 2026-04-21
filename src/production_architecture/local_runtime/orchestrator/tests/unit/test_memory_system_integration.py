from __future__ import annotations

from pathlib import Path

from core_components.memory_system import validate_memory_system_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_system_layer import (
    write_memory_system_artifact,
)


def test_memory_system_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-memory-system"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    write_memory_artifacts(output_dir=run_dir, run_id=run_id, parsed=parsed, events=events)
    payload = write_memory_system_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert validate_memory_system_path(run_dir / "memory" / "memory_system.json") == []
