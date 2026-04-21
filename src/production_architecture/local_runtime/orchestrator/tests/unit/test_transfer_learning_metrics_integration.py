from __future__ import annotations

from success_criteria.transfer_learning_metrics import validate_transfer_learning_metrics_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)


def test_transfer_learning_metrics_artifact_written_and_valid(tmp_path) -> None:
    parsed = {"checks": [{"name": "a", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    nodes = write_memory_artifacts(output_dir=tmp_path, run_id="rid-transfer", parsed=parsed, events=events)
    write_evolution_artifacts(
        output_dir=tmp_path,
        run_id="rid-transfer",
        parsed=parsed,
        events=events,
        skill_nodes=nodes,
    )
    assert validate_transfer_learning_metrics_path(tmp_path / "learning" / "transfer_learning_metrics.json") == []
