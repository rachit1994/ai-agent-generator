from __future__ import annotations

import json
from pathlib import Path

from core_components.self_learning_loop import validate_self_learning_loop_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.practice_engine_layer import (
    write_practice_engine_artifact,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.self_learning_loop_layer import (
    write_self_learning_loop_artifact,
)


def test_self_learning_loop_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-self-learning-loop"
    run_dir = tmp_path / "runs" / run_id
    parsed = {
        "checks": [{"name": "shape", "passed": True}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": True}],
    }
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.95}}]
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
    write_practice_engine_artifact(output_dir=run_dir, run_id=run_id)
    payload = write_self_learning_loop_artifact(
        output_dir=run_dir, run_id=run_id, mode="guarded_pipeline"
    )
    loop_path = run_dir / "learning" / "self_learning_loop.json"
    assert validate_self_learning_loop_path(loop_path) == []
    assert payload["run_id"] == run_id
    body = json.loads(loop_path.read_text(encoding="utf-8"))
    assert body["decision"]["loop_state"] in {"hold", "iterate", "promote"}
