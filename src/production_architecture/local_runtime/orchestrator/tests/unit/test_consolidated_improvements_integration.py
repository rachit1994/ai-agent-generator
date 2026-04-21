from __future__ import annotations

import json
from pathlib import Path

from implementation_roadmap.consolidated_improvements import validate_consolidated_improvements_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.consolidated_improvements_layer import (
    write_consolidated_improvements_artifact,
)


def test_write_consolidated_improvements_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-consolidated"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "program")
    ensure_dir(output_dir / "strategy")
    ensure_dir(output_dir / "storage")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "summary.json", {"quality": {"validation_ready": True}})
    write_json(
        output_dir / "review.json",
        {"status": "completed_review_pass", "artifact_manifest": [{"path": "a", "present": True}]},
    )
    write_json(output_dir / "program" / "production_readiness.json", {"status": "ready"})
    write_json(output_dir / "strategy" / "scalability_strategy.json", {"status": "scalable"})
    write_json(output_dir / "strategy" / "service_boundaries.json", {"status": "bounded"})
    write_json(output_dir / "storage" / "storage_architecture.json", {"status": "consistent"})
    write_json(output_dir / "learning" / "capability_growth_metrics.json", {"ok": True})
    write_json(output_dir / "learning" / "error_reduction_metrics.json", {"ok": True})
    write_json(output_dir / "learning" / "extended_binary_gates.json", {"ok": True})
    write_json(output_dir / "learning" / "transfer_learning_metrics.json", {"ok": True})
    payload = write_consolidated_improvements_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode="guarded_pipeline",
    )
    assert payload["run_id"] == run_id
    assert validate_consolidated_improvements_path(output_dir / "program" / "consolidated_improvements.json") == []
    body = json.loads((output_dir / "program" / "consolidated_improvements.json").read_text(encoding="utf-8"))
    assert body["run_id"] == run_id


def test_write_consolidated_improvements_fails_closed_for_truthy_non_boolean_inputs(
    tmp_path: Path,
) -> None:
    run_id = "run-consolidated-fail-closed"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "program")
    ensure_dir(output_dir / "strategy")
    ensure_dir(output_dir / "storage")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "summary.json", {"quality": {"validation_ready": "true"}})
    write_json(
        output_dir / "review.json",
        {"status": "completed_review_pass", "artifact_manifest": [{"path": "a", "present": "true"}]},
    )
    write_json(output_dir / "program" / "production_readiness.json", {"status": "ready"})
    write_json(output_dir / "strategy" / "scalability_strategy.json", {"status": "scalable"})
    write_json(output_dir / "strategy" / "service_boundaries.json", {"status": "bounded"})
    write_json(output_dir / "storage" / "storage_architecture.json", {"status": "consistent"})
    write_json(output_dir / "learning" / "capability_growth_metrics.json", {"ok": "true"})
    write_json(output_dir / "learning" / "error_reduction_metrics.json", {"ok": "true"})
    write_json(output_dir / "learning" / "extended_binary_gates.json", {"ok": "true"})
    write_json(output_dir / "learning" / "transfer_learning_metrics.json", {"ok": "true"})
    payload = write_consolidated_improvements_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode="guarded_pipeline",
    )
    assert payload["status"] == "not_ready"
    assert payload["summary"]["validation_ready"] is False
    assert payload["summary"]["required_artifacts_present"] is False


def test_write_consolidated_improvements_requires_non_empty_artifact_manifest(
    tmp_path: Path,
) -> None:
    run_id = "run-consolidated-empty-artifacts"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "program")
    ensure_dir(output_dir / "strategy")
    ensure_dir(output_dir / "storage")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "summary.json", {"quality": {"validation_ready": True}})
    write_json(
        output_dir / "review.json",
        {"status": "completed_review_pass", "artifact_manifest": []},
    )
    write_json(output_dir / "program" / "production_readiness.json", {"status": "ready"})
    write_json(output_dir / "strategy" / "scalability_strategy.json", {"status": "scalable"})
    write_json(output_dir / "strategy" / "service_boundaries.json", {"status": "bounded"})
    write_json(output_dir / "storage" / "storage_architecture.json", {"status": "consistent"})
    write_json(output_dir / "learning" / "capability_growth_metrics.json", {"ok": True})
    write_json(output_dir / "learning" / "error_reduction_metrics.json", {"ok": True})
    write_json(output_dir / "learning" / "extended_binary_gates.json", {"ok": True})
    write_json(output_dir / "learning" / "transfer_learning_metrics.json", {"ok": True})
    payload = write_consolidated_improvements_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode="guarded_pipeline",
    )
    assert payload["status"] == "not_ready"
    assert payload["summary"]["required_artifacts_present"] is False
    assert validate_consolidated_improvements_path(output_dir / "program" / "consolidated_improvements.json") == []

