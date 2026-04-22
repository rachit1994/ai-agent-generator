from __future__ import annotations

import json
from pathlib import Path

from success_criteria.capability_growth_metrics import validate_capability_growth_metrics_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)


def test_capability_growth_metrics_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-cap-growth"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    write_evolution_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    metrics_path = run_dir / "learning" / "capability_growth_metrics.json"
    assert validate_capability_growth_metrics_path(metrics_path) == []
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == run_id


def test_capability_growth_metrics_truthy_non_boolean_finalize_pass_is_fail_closed(
    tmp_path: Path,
) -> None:
    run_id = "run-cap-growth-truthy-pass"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": "true", "reliability": 0.9}}]
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    write_evolution_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    metrics_path = run_dir / "learning" / "capability_growth_metrics.json"
    assert validate_capability_growth_metrics_path(metrics_path) == []
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert payload["metrics"]["capability_growth_rate"] < 0.5
