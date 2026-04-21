from __future__ import annotations

import json
from pathlib import Path

from evaluation_framework.online_evaluation_shadow_canary_artifact import (
    validate_online_evaluation_shadow_canary_path,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.online_evaluation_shadow_canary_layer import (
    write_online_evaluation_shadow_canary_artifact,
)


def test_online_evaluation_shadow_canary_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-online-shadow"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
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
    payload = write_online_evaluation_shadow_canary_artifact(
        output_dir=run_dir, run_id=run_id
    )
    assert payload["run_id"] == run_id
    canary_path = run_dir / "learning" / "online_evaluation_shadow_canary.json"
    assert validate_online_evaluation_shadow_canary_path(canary_path) == []
    body = json.loads(canary_path.read_text(encoding="utf-8"))
    assert body["decision"] in {"promote", "hold"}
