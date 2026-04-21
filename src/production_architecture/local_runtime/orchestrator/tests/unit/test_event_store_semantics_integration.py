from __future__ import annotations

from pathlib import Path

from event_sourced_architecture.event_store import validate_event_store_semantics_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_lineage_layer import (
    write_event_lineage_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_store_semantics_layer import (
    write_event_store_semantics_artifact,
)


def test_event_store_semantics_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-event-store-semantics"
    run_dir = tmp_path / "runs" / run_id
    traces_path = run_dir / "traces.jsonl"
    traces_path.parent.mkdir(parents=True, exist_ok=True)
    traces_path.write_text('{"type":"run_start"}\n', encoding="utf-8")
    write_event_lineage_artifacts(output_dir=run_dir, run_id=run_id)
    payload = write_event_store_semantics_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert validate_event_store_semantics_path(run_dir / "event_store" / "semantics.json") == []
