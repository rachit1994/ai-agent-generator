from __future__ import annotations

import json
from pathlib import Path

from event_sourced_architecture.auditability import validate_auditability_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.auditability_layer import (
    write_auditability_artifact,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_lineage_layer import (
    write_event_lineage_artifacts,
)


def test_write_auditability_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-auditability"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir)
    (output_dir / "traces.jsonl").write_text(
        '{"event_id":"evt-1","payload":{"sha256":"abc123"}}\n',
        encoding="utf-8",
    )
    write_json(
        output_dir / "review.json",
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "status": "completed_review_pass",
            "review_findings": [],
            "artifact_manifest": [],
        },
    )
    write_event_lineage_artifacts(output_dir=output_dir, run_id=run_id)
    payload = write_auditability_artifact(output_dir=output_dir, run_id=run_id, mode="guarded_pipeline")
    assert payload["run_id"] == run_id
    assert validate_auditability_path(output_dir / "audit" / "auditability.json") == []
    body = json.loads((output_dir / "audit" / "auditability.json").read_text(encoding="utf-8"))
    assert body["status"] == "verifiable"
