from __future__ import annotations

from pathlib import Path

from production_architecture.storage.storage.storage import ensure_dir
from workflow_pipelines.traces_jsonl import validate_traces_jsonl_event_row_runtime_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.traces_jsonl_event_row_layer import (
    write_traces_jsonl_event_row_runtime_artifact,
)


def test_traces_jsonl_event_row_runtime_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-traces-runtime"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir)
    (run_dir / "traces.jsonl").write_text(
        '{"run_id":"run-traces-runtime","task_id":"t-1","mode":"baseline","model":"m","provider":"p","stage":"finalize","started_at":"a","ended_at":"b","latency_ms":1,"token_input":0,"token_output":0,"estimated_cost_usd":0.0,"retry_count":0,"errors":[],"score":{"passed":true,"reliability":1.0,"validity":1.0},"metadata":null}\n',
        encoding="utf-8",
    )
    payload = write_traces_jsonl_event_row_runtime_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "ready"
    assert validate_traces_jsonl_event_row_runtime_path(
        run_dir / "traces" / "event_row_runtime.json"
    ) == []
