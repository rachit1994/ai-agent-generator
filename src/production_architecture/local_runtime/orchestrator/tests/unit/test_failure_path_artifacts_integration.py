from __future__ import annotations

from pathlib import Path

from production_architecture.storage.storage.storage import write_json
from workflow_pipelines.failure_path_artifacts import validate_failure_path_artifacts_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_lineage_layer import (
    write_event_lineage_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.failure_path_artifacts_layer import (
    write_failure_path_artifacts,
)


def test_failure_path_artifacts_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-failure-path"
    run_dir = tmp_path / "runs" / run_id
    traces = run_dir / "traces.jsonl"
    traces.parent.mkdir(parents=True, exist_ok=True)
    traces.write_text('{"type":"run_start"}\n', encoding="utf-8")
    write_json(
        run_dir / "summary.json",
        {
            "runId": run_id,
            "mode": "baseline",
            "runStatus": "failed",
            "partial": False,
            "error": {"type": "RuntimeError", "message": "boom"},
            "provider": "p",
            "model": "m",
        },
    )
    write_event_lineage_artifacts(output_dir=run_dir, run_id=run_id)
    payload = write_failure_path_artifacts(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert validate_failure_path_artifacts_path(run_dir / "replay" / "failure_path_artifacts.json") == []
