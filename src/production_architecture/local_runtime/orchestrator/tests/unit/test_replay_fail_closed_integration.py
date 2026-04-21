from __future__ import annotations

import json
from pathlib import Path

from event_sourced_architecture.replay_fail_closed import validate_replay_fail_closed_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_lineage_layer import (
    write_event_lineage_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.replay_fail_closed_layer import (
    write_replay_fail_closed_artifact,
)


def test_replay_fail_closed_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-replay-fc"
    run_dir = tmp_path / "runs" / run_id
    traces = run_dir / "traces.jsonl"
    traces.parent.mkdir(parents=True, exist_ok=True)
    traces.write_text('{"type":"run_start"}\n', encoding="utf-8")
    write_event_lineage_artifacts(output_dir=run_dir, run_id=run_id)
    payload = write_replay_fail_closed_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert validate_replay_fail_closed_path(run_dir / "replay" / "fail_closed.json") == []


def test_validate_replay_fail_closed_path_rejects_status_checks_mismatch(tmp_path: Path) -> None:
    run_id = "run-replay-fc-status-mismatch"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "replay").mkdir(parents=True)
    path = run_dir / "replay" / "fail_closed.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.replay_fail_closed.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "status": "pass",
                "checks": {
                    "replay_manifest_present": True,
                    "trace_rows_present": True,
                    "event_rows_present": False,
                    "chain_root_present": True,
                    "chain_root_matches_trace_hash": True,
                },
                "evidence": {
                    "replay_manifest_ref": "replay_manifest.json",
                    "traces_ref": "traces.jsonl",
                    "run_events_ref": "event_store/run_events.jsonl",
                    "replay_fail_closed_ref": "replay/fail_closed.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_replay_fail_closed_path(path)
    assert "replay_fail_closed_status_checks_mismatch" in errs
