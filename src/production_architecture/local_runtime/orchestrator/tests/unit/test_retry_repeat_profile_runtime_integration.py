from __future__ import annotations

from pathlib import Path

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.retry_repeat_profile_layer import (
    write_retry_repeat_profile_runtime_artifact,
)
from workflow_pipelines.retry_repeat_profile import validate_retry_repeat_profile_runtime_path


def test_retry_repeat_profile_runtime_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-repeat-profile"
    run_dir = tmp_path / "runs" / run_id
    attempts = [
        {"run_id": run_id, "output_dir": str(run_dir), "output": "{}"},
        {"run_id": "run-repeat-profile-2", "output_dir": str(tmp_path / "runs" / "two"), "output": "{}"},
    ]
    payload = write_retry_repeat_profile_runtime_artifact(
        output_dir=run_dir,
        run_id=run_id,
        repeat=2,
        attempts=attempts,
        all_runs_no_pipeline_error=True,
        validation_ready_all=True,
    )
    assert payload["run_id"] == run_id
    assert payload["status"] == "repeat_ok"
    assert validate_retry_repeat_profile_runtime_path(
        run_dir / "program" / "retry_repeat_profile_runtime.json"
    ) == []
