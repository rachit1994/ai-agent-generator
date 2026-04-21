from __future__ import annotations

import json
from pathlib import Path

from production_architecture.storage.storage.storage import ensure_dir, write_json
from service_boundaries import validate_service_boundaries_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.service_boundaries_layer import (
    write_service_boundaries_artifact,
)


def test_write_service_boundaries_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-service-boundaries"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir)
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
                {"path": "traces.jsonl", "present": True},
                {"path": "orchestration.jsonl", "present": True},
                {"path": "summary.json", "present": True},
                {"path": "review.json", "present": True},
            ],
        },
    )
    payload = write_service_boundaries_artifact(output_dir=output_dir, run_id=run_id, mode="guarded_pipeline")
    assert payload["run_id"] == run_id
    assert validate_service_boundaries_path(output_dir / "strategy" / "service_boundaries.json") == []
    body = json.loads((output_dir / "strategy" / "service_boundaries.json").read_text(encoding="utf-8"))
    assert body["run_id"] == run_id


def test_validate_service_boundaries_path_rejects_coverage_mismatch(tmp_path: Path) -> None:
    run_id = "run-service-boundaries-coverage-mismatch"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "strategy")
    path = output_dir / "strategy" / "service_boundaries.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.service_boundaries.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "mode": "guarded_pipeline",
                "status": "boundary_violation",
                "violations": [{"service": "event_store", "missing_path": "event_store/run_events.jsonl"}],
                "services": {
                    "orchestrator": {
                        "owned_paths": ["traces.jsonl", "orchestration.jsonl", "summary.json", "review.json"],
                        "present_count": 4,
                        "required_count": 4,
                        "coverage": 0.0,
                    },
                    "event_store": {
                        "owned_paths": ["event_store/run_events.jsonl"],
                        "present_count": 0,
                        "required_count": 1,
                        "coverage": 0.0,
                    },
                    "memory_system": {
                        "owned_paths": ["memory/retrieval_bundle.json"],
                        "present_count": 0,
                        "required_count": 1,
                        "coverage": 0.0,
                    },
                    "learning_service": {
                        "owned_paths": ["learning/reflection_bundle.json"],
                        "present_count": 0,
                        "required_count": 1,
                        "coverage": 0.0,
                    },
                },
                "evidence": {"review_ref": "review.json", "boundaries_ref": "strategy/service_boundaries.json"},
            }
        ),
        encoding="utf-8",
    )
    errs = validate_service_boundaries_path(path)
    assert "service_boundaries_coverage_mismatch:orchestrator" in errs

