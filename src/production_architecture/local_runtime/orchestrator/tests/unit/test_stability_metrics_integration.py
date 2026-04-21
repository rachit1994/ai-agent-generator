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
