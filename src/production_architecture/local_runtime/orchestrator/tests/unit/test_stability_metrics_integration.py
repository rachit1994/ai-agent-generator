from __future__ import annotations

import json
from pathlib import Path

from success_criteria.stability_metrics import validate_stability_metrics_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)


def test_stability_metrics_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-stability-metrics"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [
        {"stage": "finalize", "score": {"passed": True, "reliability": 0.92}},
        {"stage": "repair"},
    ]
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    write_evolution_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        skill_nodes=skill_nodes,
    )
    metrics_path = run_dir / "learning" / "stability_metrics.json"
    assert validate_stability_metrics_path(metrics_path) == []
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == run_id


def test_validate_stability_metrics_path_rejects_status_score_mismatch(tmp_path: Path) -> None:
    run_id = "run-stability-status-mismatch"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True)
    path = run_dir / "learning" / "stability_metrics.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.stability_metrics.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "status": "stable",
                "metrics": {
                    "finalize_pass_rate": 0.2,
                    "reliability_score": 0.2,
                    "retry_pressure": 0.8,
                    "stability_score": 0.2,
                },
                "evidence": {
                    "traces_ref": "traces.jsonl",
                    "stability_metrics_ref": "learning/stability_metrics.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_stability_metrics_path(path)
    assert "stability_metrics_status_score_mismatch" in errs


def test_validate_stability_metrics_path_rejects_stability_score_arithmetic_mismatch(
    tmp_path: Path,
) -> None:
    run_id = "run-stability-arithmetic-mismatch"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True)
    path = run_dir / "learning" / "stability_metrics.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.stability_metrics.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "status": "degraded",
                "metrics": {
                    "finalize_pass_rate": 0.7,
                    "reliability_score": 0.6,
                    "retry_pressure": 0.2,
                    "stability_score": 0.0,
                },
                "evidence": {
                    "traces_ref": "traces.jsonl",
                    "stability_metrics_ref": "learning/stability_metrics.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_stability_metrics_path(path)
    assert "stability_metrics_metric_semantics:stability_score" in errs
