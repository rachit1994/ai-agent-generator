from __future__ import annotations

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.online_eval_shadow_contract import (
    validate_canary_report_path,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.promotion_eval_contract import (
    validate_promotion_package_path,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)


def test_agent_lifecycle_artifacts_validate_contracts(tmp_path) -> None:
    parsed = {"checks": [{"name": "a", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.8}]}
    write_evolution_artifacts(
        output_dir=tmp_path, run_id="rid-lifecycle", parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    assert validate_promotion_package_path(tmp_path / "lifecycle" / "promotion_package.json") == []
    assert validate_canary_report_path(tmp_path / "learning" / "canary_report.json") == []
