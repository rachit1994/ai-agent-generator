from __future__ import annotations

import json
from pathlib import Path

from implementation_roadmap.closure_security_reliability_scalability_plans import (
    validate_closure_security_reliability_scalability_plans_path,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.closure_security_reliability_scalability_plans_layer import (
    write_closure_security_reliability_scalability_plans_artifact,
)


def test_write_closure_plan_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-closure-plans"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "program")
    ensure_dir(output_dir / "strategy")
    ensure_dir(output_dir / "storage")
    write_json(
        output_dir / "summary.json",
        {"quality": {"validation_ready": True}, "metrics": {"reliability": 0.9, "retryFrequency": 0.1, "passRate": 1.0}},
    )
    write_json(output_dir / "review.json", {"status": "completed_review_pass"})
    write_json(output_dir / "program" / "production_readiness.json", {"status": "ready"})
    write_json(output_dir / "strategy" / "scalability_strategy.json", {"status": "scalable"})
    write_json(output_dir / "strategy" / "service_boundaries.json", {"status": "bounded"})
    write_json(output_dir / "storage" / "storage_architecture.json", {"status": "consistent"})
    payload = write_closure_security_reliability_scalability_plans_artifact(
        output_dir=output_dir, run_id=run_id, mode="guarded_pipeline", policy_bundle_valid=True
    )
    assert payload["run_id"] == run_id
    assert (
        validate_closure_security_reliability_scalability_plans_path(
            output_dir / "program" / "closure_security_reliability_scalability_plans.json"
        )
        == []
    )
    body = json.loads(
        (output_dir / "program" / "closure_security_reliability_scalability_plans.json").read_text(
            encoding="utf-8"
        )
    )
    assert body["run_id"] == run_id

