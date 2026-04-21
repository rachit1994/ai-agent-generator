from __future__ import annotations

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.promotion_eval_contract import (
    validate_promotion_package_path,
)


def test_capability_model_artifacts_are_valid_and_connected(tmp_path) -> None:
    parsed = {"checks": [{"name": "ok", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    nodes = write_memory_artifacts(output_dir=tmp_path, run_id="rid-int", parsed=parsed, events=events)
    write_evolution_artifacts(
        output_dir=tmp_path, run_id="rid-int", parsed=parsed, events=events, skill_nodes=nodes
    )
    assert validate_promotion_package_path(tmp_path / "lifecycle" / "promotion_package.json") == []
