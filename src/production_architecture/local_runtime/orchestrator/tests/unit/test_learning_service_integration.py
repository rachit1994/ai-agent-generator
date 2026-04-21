from __future__ import annotations

from pathlib import Path

from core_components.learning_service import validate_learning_service_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.learning_service_layer import (
    write_learning_service_artifact,
)


def test_learning_service_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-learning-service"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    write_evolution_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        skill_nodes={"nodes": [{"score": 0.8}]},
    )
    payload = write_learning_service_artifact(output_dir=run_dir, run_id=run_id, mode="guarded_pipeline")
    assert payload["run_id"] == run_id
    assert validate_learning_service_path(run_dir / "learning" / "learning_service.json") == []
