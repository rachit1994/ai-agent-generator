from __future__ import annotations

import math

from human_professional_evolution_model import build_mentorship_plan, build_reflection_bundle
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


def test_human_professional_evolution_artifacts_fail_closed_for_non_finite_skill_score(tmp_path) -> None:
    parsed = {"checks": [{"name": "a", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": math.nan}]}
    write_evolution_artifacts(
        output_dir=tmp_path, run_id="rid-hpem-nan", parsed=parsed, events=events, skill_nodes=nodes
    )
    assert validate_promotion_package_path(tmp_path / "lifecycle" / "promotion_package.json") == []
    assert validate_canary_report_path(tmp_path / "learning" / "canary_report.json") == []


def test_human_professional_evolution_artifacts_fail_closed_for_truthy_non_boolean_finalize_passed(
    tmp_path,
) -> None:
    parsed = {"checks": [{"name": "a", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": "true"}}]
    nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.8}]}
    write_evolution_artifacts(
        output_dir=tmp_path, run_id="rid-hpem-truthy", parsed=parsed, events=events, skill_nodes=nodes
    )
    assert validate_promotion_package_path(tmp_path / "lifecycle" / "promotion_package.json") == []
    assert validate_canary_report_path(tmp_path / "learning" / "canary_report.json") == []


def test_human_professional_evolution_mentorship_plan_fail_closed_for_truthy_flag() -> None:
    plan = build_mentorship_plan(
        run_id="rid-hpem-mentorship",
        decision={"focus_areas": "delivery.structured_output", "mentorship_required": "true"},
    )
    assert plan["focus_areas"] == ["delivery.structured_output"]
    assert plan["mentorship_required"] is False


def test_human_professional_evolution_reflection_bundle_fail_closed_for_truthy_flag() -> None:
    bundle = build_reflection_bundle(
        run_id="rid-hpem-reflection",
        decision={"growth_trend": "steady", "mentorship_required": "true"},
        event_ref="evt-hpem-reflection",
    )
    assert bundle["proposed_intervention"] == "none"
