from __future__ import annotations

from pathlib import Path

from workflow_pipelines.production_pipeline_plan_artifact import (
    validate_production_pipeline_plan_artifact_path,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.completion_layer import (
    write_completion_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.production_pipeline_plan_artifact_layer import (
    write_production_pipeline_plan_artifact,
)


def test_production_pipeline_plan_artifact_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-plan-artifact"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "planner_doc.md").parent.mkdir(parents=True, exist_ok=True)
    (run_dir / "planner_doc.md").write_text("# plan\n", encoding="utf-8")
    parsed = {"checks": [{"name": "verifier_passed", "passed": True}]}
    write_completion_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        task="t",
        parsed=parsed,
        events=[],
    )
    payload = write_production_pipeline_plan_artifact(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
    )
    assert payload["run_id"] == run_id
    path = run_dir / "program" / "production_pipeline_plan_artifact.json"
    assert validate_production_pipeline_plan_artifact_path(path) == []


def test_production_pipeline_plan_artifact_partial_when_project_plan_steps_missing(
    tmp_path: Path,
) -> None:
    run_id = "run-plan-artifact-partial"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "program").mkdir(parents=True, exist_ok=True)
    (run_dir / "program" / "project_plan.json").write_text("{}", encoding="utf-8")
    (run_dir / "program" / "progress.json").write_text("{}", encoding="utf-8")
    (run_dir / "program" / "work_batch.json").write_text("{}", encoding="utf-8")
    (run_dir / "program" / "discovery.json").write_text("{}", encoding="utf-8")
    (run_dir / "program" / "verification_bundle.json").write_text("{}", encoding="utf-8")
    payload = write_production_pipeline_plan_artifact(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
    )
    assert payload["status"] == "partial"
    assert payload["metrics"]["step_count"] == 0


def test_production_pipeline_plan_artifact_fail_closes_malformed_project_plan_json(
    tmp_path: Path,
) -> None:
    run_id = "run-plan-artifact-malformed-plan"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "program").mkdir(parents=True, exist_ok=True)
    (run_dir / "program" / "project_plan.json").write_text("{bad json", encoding="utf-8")
    (run_dir / "program" / "progress.json").write_text("{}", encoding="utf-8")
    (run_dir / "program" / "work_batch.json").write_text("{}", encoding="utf-8")
    (run_dir / "program" / "discovery.json").write_text("{}", encoding="utf-8")
    (run_dir / "program" / "verification_bundle.json").write_text("{}", encoding="utf-8")
    payload = write_production_pipeline_plan_artifact(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
    )
    assert payload["status"] == "partial"
    assert payload["metrics"]["step_count"] == 0
    assert payload["checks"]["project_plan_present"] is False
