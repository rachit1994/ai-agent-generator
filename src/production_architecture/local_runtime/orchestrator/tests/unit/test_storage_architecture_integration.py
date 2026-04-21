from __future__ import annotations

import json
from pathlib import Path

from production_architecture.storage import validate_storage_architecture_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.storage_layer import (
    write_storage_architecture_artifact,
)


def test_write_storage_architecture_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-storage-arch"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "event_store")
    ensure_dir(output_dir / "memory")
    write_json(
        output_dir / "review.json",
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "status": "completed_review_pass",
            "reasons": [],
            "required_fixes": [],
            "review_findings": [],
            "artifact_manifest": [
                {"path": "summary.json", "present": True},
                {"path": "review.json", "present": True},
                {"path": "event_store/run_events.jsonl", "present": True},
                {"path": "replay_manifest.json", "present": True},
                {"path": "memory/retrieval_bundle.json", "present": True},
                {"path": "memory/quality_metrics.json", "present": True},
            ],
        },
    )
    (output_dir / "event_store" / "run_events.jsonl").write_text(
        '{"run_id":"run-storage-arch","payload":{"event_id":"evt-1","type":"x","sha256":"abc"}}\n',
        encoding="utf-8",
    )
    write_json(output_dir / "memory" / "retrieval_bundle.json", {"chunks": [{"confidence": 0.5}]})
    write_json(output_dir / "memory" / "quality_metrics.json", {"contradiction_rate": 0.0})
    payload = write_storage_architecture_artifact(output_dir=output_dir, run_id=run_id, mode="guarded_pipeline")
    assert payload["run_id"] == run_id
    assert validate_storage_architecture_path(output_dir / "storage" / "storage_architecture.json") == []
    body = json.loads((output_dir / "storage" / "storage_architecture.json").read_text(encoding="utf-8"))
    assert body["run_id"] == run_id

