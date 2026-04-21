from __future__ import annotations

from pathlib import Path

from guardrails_and_safety.dual_control import validate_dual_control_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.completion_layer import (
    write_completion_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.dual_control_layer import (
    write_dual_control_artifact,
)


def test_dual_control_runtime_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-dual-control"
    run_dir = tmp_path / "runs" / run_id
    write_completion_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        task="dual control validation",
        parsed={},
        events=[],
    )
    payload = write_dual_control_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert validate_dual_control_path(run_dir / "program" / "dual_control_runtime.json") == []
