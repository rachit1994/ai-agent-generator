from __future__ import annotations

import json
from pathlib import Path

from core_components.role_agents import validate_role_agents_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.role_agents_layer import (
    write_role_agents_artifact,
)


def test_role_agents_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-role-agents"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    payload = write_role_agents_artifact(
        output_dir=run_dir,
        run_id=run_id,
        parsed=parsed,
        events=events,
        skill_nodes=skill_nodes,
    )
    assert payload["run_id"] == run_id
    role_agents_path = run_dir / "capability" / "role_agents.json"
    assert validate_role_agents_path(role_agents_path) == []
    body = json.loads(role_agents_path.read_text(encoding="utf-8"))
    assert body["status"] in {"balanced", "drifted", "insufficient_signal"}
