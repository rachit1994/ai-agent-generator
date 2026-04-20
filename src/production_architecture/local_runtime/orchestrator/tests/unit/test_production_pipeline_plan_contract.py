"""§10.B — harness ``program/project_plan.json`` (production pipeline slice)."""

from __future__ import annotations

from pathlib import Path

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.production_pipeline_plan_contract import (
    PRODUCTION_PIPELINE_PLAN_CONTRACT,
    validate_harness_project_plan_dict,
    validate_harness_project_plan_path,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.completion_layer import (
    write_completion_artifacts,
)


def test_production_pipeline_plan_contract_id() -> None:
    assert PRODUCTION_PIPELINE_PLAN_CONTRACT == "sde.production_pipeline_plan.v1"


def test_validate_harness_project_plan_dict_ok() -> None:
    body = {
        "plan_version": "1.0",
        "steps": [
            {"step_id": "step_planner", "depends_on": [], "phase": "planning"},
        ],
    }
    assert validate_harness_project_plan_dict(body) == []


def test_validate_harness_project_plan_dict_not_object() -> None:
    assert validate_harness_project_plan_dict([]) == ["harness_project_plan_not_object"]


def test_validate_harness_project_plan_dict_empty_steps() -> None:
    body = {"plan_version": "1.0", "steps": []}
    assert "harness_project_plan_steps" in validate_harness_project_plan_dict(body)


def test_validate_harness_project_plan_path_missing(tmp_path: Path) -> None:
    assert validate_harness_project_plan_path(tmp_path / "x.json") == ["harness_project_plan_file_missing"]


def test_validate_harness_project_plan_path_bad_json(tmp_path: Path) -> None:
    p = tmp_path / "p.json"
    p.write_text("{", encoding="utf-8")
    assert validate_harness_project_plan_path(p) == ["harness_project_plan_json"]


def test_write_completion_artifacts_writes_valid_project_plan(tmp_path: Path) -> None:
    (tmp_path / "planner_doc.md").write_text("# plan\n", encoding="utf-8")
    parsed = {"checks": [{"name": "verifier_passed", "passed": True}]}
    write_completion_artifacts(
        output_dir=tmp_path,
        run_id="rid-plan",
        task="t",
        parsed=parsed,
        events=[],
    )
    pp = tmp_path / "program" / "project_plan.json"
    assert validate_harness_project_plan_path(pp) == []
