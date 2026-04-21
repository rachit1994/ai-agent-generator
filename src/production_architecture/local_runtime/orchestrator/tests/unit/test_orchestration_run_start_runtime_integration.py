from __future__ import annotations

from pathlib import Path

from production_architecture.storage.storage.storage import ensure_dir
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.orchestration_run_start_layer import (
    write_orchestration_run_start_runtime_artifact,
)
from workflow_pipelines.orchestration_run_start import validate_orchestration_run_start_runtime_path


def test_orchestration_run_start_runtime_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-start-runtime"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir)
    (run_dir / "orchestration.jsonl").write_text(
        '{"run_id":"run-start-runtime","type":"run_start","mode":"baseline","provider":"p","model":"m"}\n',
        encoding="utf-8",
    )
    payload = write_orchestration_run_start_runtime_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "ready"
    assert validate_orchestration_run_start_runtime_path(
        run_dir / "orchestration" / "run_start_runtime.json"
    ) == []
