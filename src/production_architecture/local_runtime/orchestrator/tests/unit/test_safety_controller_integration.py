from __future__ import annotations

from pathlib import Path

from core_components.safety_controller import validate_safety_controller_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.safety_controller_layer import (
    write_safety_controller_artifact,
)


def test_safety_controller_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-safety-controller"
    run_dir = tmp_path / "runs" / run_id
    payload = write_safety_controller_artifact(
        output_dir=run_dir,
        run_id=run_id,
        cto={"validation_ready": True, "hard_stops": [{"id": "HS01", "passed": True}]},
    )
    assert payload["run_id"] == run_id
    assert payload["status"] == "allow"
    assert validate_safety_controller_path(run_dir / "safety" / "controller_runtime.json") == []


def test_safety_controller_blocks_on_truthy_non_boolean_inputs(tmp_path: Path) -> None:
    run_id = "run-safety-controller-block"
    run_dir = tmp_path / "runs" / run_id
    payload = write_safety_controller_artifact(
        output_dir=run_dir,
        run_id=run_id,
        cto={"validation_ready": "true", "hard_stops": [{"id": "HS01", "passed": "true"}]},
    )
    assert payload["status"] == "block"
    assert payload["metrics"]["validation_ready"] is False
    assert payload["metrics"]["hard_stop_failures"] is True
