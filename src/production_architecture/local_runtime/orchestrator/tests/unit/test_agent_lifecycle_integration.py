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
from agent_lifecycle import build_lifecycle_decision
from agent_lifecycle import build_promotion_package


def test_agent_lifecycle_artifacts_validate_contracts(tmp_path) -> None:
    parsed = {"checks": [{"name": "a", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.8}]}
    write_evolution_artifacts(
        output_dir=tmp_path, run_id="rid-lifecycle", parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    assert validate_promotion_package_path(tmp_path / "lifecycle" / "promotion_package.json") == []
    assert validate_canary_report_path(tmp_path / "learning" / "canary_report.json") == []


def test_agent_lifecycle_decision_fails_closed_for_truthy_non_boolean_passed() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": "true"}} for _ in range(4)]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.6}]}
    decision = build_lifecycle_decision(run_id="rid-lifecycle-fail-closed", parsed=parsed, events=events, skill_nodes=skill_nodes)
    assert "stagnation_detected" in decision["reasons"]


def test_agent_lifecycle_promotion_package_fails_closed_for_non_numeric_score() -> None:
    promotion = build_promotion_package(
        run_id="rid-lifecycle-non-numeric",
        decision={"score": "bad", "current_stage": "junior", "proposed_stage": "junior"},
    )
    assert promotion["independent_evaluator_signal_ids"] == ["lifecycle-score:0.000"]
