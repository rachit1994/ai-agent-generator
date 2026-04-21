from __future__ import annotations

from pathlib import Path

from evaluation_framework.promotion_evaluation import validate_promotion_evaluation_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.promotion_evaluation_layer import (
    write_promotion_evaluation_artifact,
)


def test_promotion_evaluation_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-promotion-evaluation"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    traces = run_dir / "traces.jsonl"
    traces.parent.mkdir(parents=True, exist_ok=True)
    traces.write_text('{"stage":"finalize","score":{"passed":true}}\n', encoding="utf-8")
    write_evolution_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        skill_nodes={"nodes": [{"score": 0.8}]},
    )
    payload = write_promotion_evaluation_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert validate_promotion_evaluation_path(run_dir / "learning" / "promotion_evaluation.json") == []
