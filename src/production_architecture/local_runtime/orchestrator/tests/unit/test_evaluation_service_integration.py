from __future__ import annotations

from pathlib import Path

from core_components.evaluation_service import validate_evaluation_service_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evaluation_service_layer import (
    write_evaluation_service_artifact,
)


def test_evaluation_service_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-evaluation-service"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir)
    write_json(run_dir / "summary.json", {"metrics": {"passRate": 1.0}})
    write_json(run_dir / "learning" / "online_evaluation_shadow_canary.json", {"status": "finished"})
    write_json(run_dir / "learning" / "promotion_evaluation.json", {"status": "promote"})
    payload = write_evaluation_service_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "ready"
    assert validate_evaluation_service_path(run_dir / "evaluation" / "service_runtime.json") == []


def test_evaluation_service_degraded_for_payloads_without_status(tmp_path: Path) -> None:
    run_id = "run-evaluation-service-degraded"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir)
    write_json(run_dir / "summary.json", {"metrics": {"passRate": 1.0}})
    write_json(run_dir / "learning" / "online_evaluation_shadow_canary.json", {"result": "finished"})
    write_json(run_dir / "learning" / "promotion_evaluation.json", {"result": "promote"})
    payload = write_evaluation_service_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["status"] == "degraded"
    assert payload["metrics"]["has_online_eval"] is False
    assert payload["metrics"]["has_promotion_eval"] is False
