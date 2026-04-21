from __future__ import annotations

import json
from pathlib import Path

from core_components.career_strategy_layer import validate_career_strategy_layer_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.career_strategy_layer import (
    write_career_strategy_layer_artifact,
)


def test_write_career_strategy_layer_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-career-layer"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "lifecycle")
    ensure_dir(output_dir / "learning")
    ensure_dir(output_dir / "strategy")
    write_json(output_dir / "summary.json", {"quality": {"validation_ready": True}})
    write_json(output_dir / "review.json", {"status": "completed_review_pass"})
    write_json(output_dir / "lifecycle" / "promotion_package.json", {"proposed_stage": "senior"})
    write_json(output_dir / "learning" / "capability_growth_metrics.json", {"metrics": {"capability_growth_rate": 0.8}})
    write_json(output_dir / "learning" / "transfer_learning_metrics.json", {"metrics": {"transfer_efficiency_score": 0.7}})
    write_json(output_dir / "learning" / "error_reduction_metrics.json", {"metrics": {"error_reduction_rate": 0.6}})
    write_json(output_dir / "strategy" / "scalability_strategy.json", {"scores": {"overall_scaling_score": 0.7}})
    payload = write_career_strategy_layer_artifact(output_dir=output_dir, run_id=run_id, mode="guarded_pipeline")
    assert payload["run_id"] == run_id
    assert validate_career_strategy_layer_path(output_dir / "strategy" / "career_strategy_layer.json") == []
    body = json.loads((output_dir / "strategy" / "career_strategy_layer.json").read_text(encoding="utf-8"))
    assert body["run_id"] == run_id

