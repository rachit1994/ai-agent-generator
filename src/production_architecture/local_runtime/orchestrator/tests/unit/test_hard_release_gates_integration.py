from __future__ import annotations

import json
from pathlib import Path

from success_criteria.hard_release_gates import validate_hard_release_gates_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)


def test_hard_release_gates_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-hard-release-gates"
    run_dir = tmp_path / "runs" / run_id
    parsed = {
        "checks": [{"name": "shape", "passed": True}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": True}],
    }
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.91}}]
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
    gates_path = run_dir / "learning" / "hard_release_gates.json"
    assert validate_hard_release_gates_path(gates_path) == []
    payload = json.loads(gates_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == run_id
