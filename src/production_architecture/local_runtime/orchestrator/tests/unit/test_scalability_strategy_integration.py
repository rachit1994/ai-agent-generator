from __future__ import annotations

from pathlib import Path

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
    assert validate_scalability_strategy_path(output_dir / "strategy" / "scalability_strategy.json") == []

