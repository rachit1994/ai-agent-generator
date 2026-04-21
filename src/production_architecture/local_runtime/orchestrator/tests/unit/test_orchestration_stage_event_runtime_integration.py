from __future__ import annotations

from pathlib import Path

from production_architecture.storage.storage.storage import ensure_dir
from workflow_pipelines.orchestration_stage_event import validate_orchestration_stage_event_runtime_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.orchestration_stage_event_layer import (
    write_orchestration_stage_event_runtime_artifact,
)


def test_orchestration_stage_event_runtime_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-stage-event-runtime"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir)
    (run_dir / "orchestration.jsonl").write_text(
        '{"run_id":"run-stage-event-runtime","type":"stage_event","stage":"executor","retry_count":0,"errors":[],"agent":null,"model":null,"model_error":null,"attempt":null,"raw_response_excerpt":null,"started_at":"a","ended_at":"b","latency_ms":1}\n',
        encoding="utf-8",
    )
    payload = write_orchestration_stage_event_runtime_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "ready"
    assert validate_orchestration_stage_event_runtime_path(
        run_dir / "orchestration" / "stage_event_runtime.json"
    ) == []
