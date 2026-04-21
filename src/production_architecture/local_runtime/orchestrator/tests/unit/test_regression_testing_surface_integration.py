from __future__ import annotations

from pathlib import Path

from evaluation_framework.regression_testing_surface import validate_regression_testing_surface_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.regression_surface_contract import (
    REGRESSION_DIMENSION_ANCHORS,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.regression_testing_surface_layer import (
    write_regression_testing_surface_artifact,
)


def test_regression_testing_surface_written_and_valid(tmp_path: Path, monkeypatch) -> None:
    run_id = "run-regression-testing-surface"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir)
    for _dimension, rel in REGRESSION_DIMENSION_ANCHORS:
        anchor_path = tmp_path / rel
        anchor_path.parent.mkdir(parents=True, exist_ok=True)
        anchor_path.write_text("ok", encoding="utf-8")
    monkeypatch.setattr(
        "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.regression_testing_surface_layer._repo_root",
        lambda: tmp_path,
    )
    write_json(run_dir / "summary.json", {"metrics": {"passRate": 1.0}})
    write_json(run_dir / "learning" / "promotion_evaluation.json", {"decision": "promote"})
    write_json(run_dir / "learning" / "online_evaluation_shadow_canary.json", {"decision": "promote"})
    payload = write_regression_testing_surface_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "ready"
    assert validate_regression_testing_surface_path(run_dir / "learning" / "regression_testing_surface.json") == []
