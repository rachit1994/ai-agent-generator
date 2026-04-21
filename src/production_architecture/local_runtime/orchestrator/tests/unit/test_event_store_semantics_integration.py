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


def test_event_store_semantics_fails_closed_on_malformed_trace_row(tmp_path: Path) -> None:
    run_id = "run-event-store-semantics-malformed-trace-row"
    run_dir = tmp_path / "runs" / run_id
    traces_path = run_dir / "traces.jsonl"
    traces_path.parent.mkdir(parents=True, exist_ok=True)
    traces_path.write_text('{"type":"run_start"}\nnot-json\n', encoding="utf-8")
    write_event_lineage_artifacts(output_dir=run_dir, run_id=run_id)
    try:
        write_event_store_semantics_artifact(output_dir=run_dir, run_id=run_id)
    except ValueError as exc:
        assert "event_store_semantics_jsonl_invalid:" in str(exc)
    else:
        raise AssertionError("expected fail-closed error for malformed traces row")


def test_event_store_semantics_fails_closed_on_non_object_run_event_row(tmp_path: Path) -> None:
    run_id = "run-event-store-semantics-non-object-event-row"
    run_dir = tmp_path / "runs" / run_id
    traces_path = run_dir / "traces.jsonl"
    traces_path.parent.mkdir(parents=True, exist_ok=True)
    traces_path.write_text('{"type":"run_start"}\n', encoding="utf-8")
    write_event_lineage_artifacts(output_dir=run_dir, run_id=run_id)
    (run_dir / "event_store").mkdir(parents=True, exist_ok=True)
    (run_dir / "event_store" / "run_events.jsonl").write_text('{"event_id":"evt-1"}\n[]\n', encoding="utf-8")
    try:
        write_event_store_semantics_artifact(output_dir=run_dir, run_id=run_id)
    except ValueError as exc:
        assert "event_store_semantics_jsonl_row_not_object:" in str(exc)
    else:
        raise AssertionError("expected fail-closed error for non-object run-events row")
