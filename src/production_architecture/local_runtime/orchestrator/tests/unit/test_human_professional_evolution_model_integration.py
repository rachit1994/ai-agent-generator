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
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)


def test_human_professional_evolution_artifacts_validate_contracts(tmp_path) -> None:
    parsed = {"checks": [{"name": "a", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    nodes = write_memory_artifacts(output_dir=tmp_path, run_id="rid-hpem", parsed=parsed, events=events)
    write_evolution_artifacts(
        output_dir=tmp_path, run_id="rid-hpem", parsed=parsed, events=events, skill_nodes=nodes
    )
    assert validate_promotion_package_path(tmp_path / "lifecycle" / "promotion_package.json") == []
    assert validate_canary_report_path(tmp_path / "learning" / "canary_report.json") == []
    assert (tmp_path / "learning" / "mentorship_plan.json").is_file()
