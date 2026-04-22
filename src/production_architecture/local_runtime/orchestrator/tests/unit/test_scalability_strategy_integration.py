from __future__ import annotations

from pathlib import Path
import json

from production_architecture.storage.storage.storage import ensure_dir
from scalability_strategy import validate_scalability_strategy_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.scalability_strategy_layer import (
    write_scalability_strategy_artifact,
)


def test_write_scalability_strategy_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-scalability-layer"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "strategy")
    payload = write_scalability_strategy_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        parsed={"checks": [{"name": "a", "passed": True}]},
        events=[{"stage": "finalize", "retry_count": 0, "score": {"passed": True}}],
        cto={"balanced_gates": {"validation_ready": True}, "hard_stops": [{"id": "HS01", "passed": True}]},
    )
    assert payload["run_id"] == run_id
    assert payload["evidence"] == {
        "summary_ref": "summary.json",
        "review_ref": "review.json",
        "scalability_ref": "strategy/scalability_strategy.json",
    }
    assert validate_scalability_strategy_path(output_dir / "strategy" / "scalability_strategy.json") == []


def test_validate_scalability_strategy_path_rejects_status_score_mismatch(tmp_path: Path) -> None:
    run_id = "run-scalability-mismatch"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "strategy")
    path = output_dir / "strategy" / "scalability_strategy.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.scalability_strategy.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "mode": "guarded_pipeline",
                "status": "scalable",
                "scores": {
                    "event_scaling_score": 0.1,
                    "memory_scaling_score": 0.1,
                    "replay_scaling_score": 0.1,
                    "multi_agent_scaling_score": 0.1,
                    "overall_scaling_score": 0.1,
                },
                "evidence": {
                    "summary_ref": "summary.json",
                    "review_ref": "review.json",
                    "scalability_ref": "strategy/scalability_strategy.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_scalability_strategy_path(path)
    assert "scalability_strategy_status_score_mismatch" in errs


def test_validate_scalability_strategy_path_rejects_overall_score_weight_mismatch(
    tmp_path: Path,
) -> None:
    run_id = "run-scalability-weight-mismatch"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "strategy")
    path = output_dir / "strategy" / "scalability_strategy.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.scalability_strategy.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "mode": "guarded_pipeline",
                "status": "constrained",
                "scores": {
                    "event_scaling_score": 1.0,
                    "memory_scaling_score": 1.0,
                    "replay_scaling_score": 1.0,
                    "multi_agent_scaling_score": 1.0,
                    "overall_scaling_score": 0.0,
                },
                "evidence": {
                    "summary_ref": "summary.json",
                    "review_ref": "review.json",
                    "scalability_ref": "strategy/scalability_strategy.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_scalability_strategy_path(path)
    assert "scalability_strategy_overall_score_mismatch" in errs


def test_validate_scalability_strategy_path_rejects_constrained_high_score_mismatch(
    tmp_path: Path,
) -> None:
    run_id = "run-scalability-constrained-high"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "strategy")
    path = output_dir / "strategy" / "scalability_strategy.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.scalability_strategy.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "mode": "guarded_pipeline",
                "status": "constrained",
                "scores": {
                    "event_scaling_score": 1.0,
                    "memory_scaling_score": 1.0,
                    "replay_scaling_score": 1.0,
                    "multi_agent_scaling_score": 1.0,
                    "overall_scaling_score": 1.0,
                },
                "evidence": {
                    "summary_ref": "summary.json",
                    "review_ref": "review.json",
                    "scalability_ref": "strategy/scalability_strategy.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_scalability_strategy_path(path)
    assert "scalability_strategy_status_score_mismatch" in errs

