from __future__ import annotations

import json
from pathlib import Path

import pytest

from core_components.learning_service import validate_learning_service_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.learning_service_layer import (
    write_learning_service_artifact,
)


def test_learning_service_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-learning-service"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    write_evolution_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        skill_nodes={"nodes": [{"score": 0.8}]},
    )
    trace_rows = [
        {"stage": "finalize", "score": {"passed": True}},
        {"stage": "finalize", "score": {"passed": "true"}},
    ]
    (run_dir / "traces.jsonl").write_text(
        "\n".join(json.dumps(row) for row in trace_rows) + "\n",
        encoding="utf-8",
    )
    payload = write_learning_service_artifact(output_dir=run_dir, run_id=run_id, mode="guarded_pipeline")
    assert payload["run_id"] == run_id
    assert payload["metrics"]["finalize_pass_rate"] == pytest.approx(0.5)
    assert validate_learning_service_path(run_dir / "learning" / "learning_service.json") == []


def test_validate_learning_service_path_rejects_metric_semantics_mismatch(tmp_path: Path) -> None:
    run_id = "run-learning-service-metric-mismatch"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True)
    path = run_dir / "learning" / "learning_service.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.learning_service.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "mode": "guarded_pipeline",
                "status": "degraded",
                "metrics": {
                    "reflection_count": 1,
                    "canary_count": 0,
                    "finalize_rows": 1,
                    "finalize_pass_rate": 1.0,
                    "health_score": 0.0,
                },
                "evidence": {
                    "reflection_bundle_ref": "learning/reflection_bundle.json",
                    "canary_report_ref": "learning/canary_report.json",
                    "traces_ref": "traces.jsonl",
                    "learning_service_ref": "learning/learning_service.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_learning_service_path(path)
    assert "learning_service_metric_semantics:health_score" in errs
