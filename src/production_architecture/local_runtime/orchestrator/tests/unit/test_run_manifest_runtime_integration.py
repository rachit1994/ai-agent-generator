from __future__ import annotations

from pathlib import Path

from production_architecture.storage.storage.storage import write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.run_manifest_runtime_layer import (
    write_run_manifest_runtime_artifact,
)
from workflow_pipelines.run_manifest import validate_run_manifest_runtime_path


def test_run_manifest_runtime_written_and_valid(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "run-rm-runtime"
    write_json(
        run_dir / "run-manifest.json",
        {
            "schema": "sde.run_manifest.v1",
            "run_id": "run-rm-runtime",
            "mode": "guarded_pipeline",
            "task": "do it",
            "project_step_id": "step-1",
            "project_session_dir": "/tmp/session",
        },
    )
    payload = write_run_manifest_runtime_artifact(output_dir=run_dir)
    assert payload["run_id"] == "run-rm-runtime"
    assert payload["status"] == "linked"
    assert validate_run_manifest_runtime_path(run_dir / "program" / "run_manifest_runtime.json") == []
