from __future__ import annotations

from pathlib import Path

from core_components.event_store import validate_event_store_component_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_lineage_layer import (
    write_event_lineage_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_store_component_layer import (
    write_event_store_component_artifact,
)


def test_event_store_component_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-event-store-component"
    run_dir = tmp_path / "runs" / run_id
    traces_path = run_dir / "traces.jsonl"
    traces_path.parent.mkdir(parents=True, exist_ok=True)
    traces_path.write_text('{"type":"run_start"}\n', encoding="utf-8")
    write_event_lineage_artifacts(output_dir=run_dir, run_id=run_id)
    payload = write_event_store_component_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    component_path = run_dir / "event_store" / "component_runtime.json"
    assert validate_event_store_component_path(component_path) == []
