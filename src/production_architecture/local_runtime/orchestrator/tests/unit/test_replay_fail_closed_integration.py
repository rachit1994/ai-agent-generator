from __future__ import annotations

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
