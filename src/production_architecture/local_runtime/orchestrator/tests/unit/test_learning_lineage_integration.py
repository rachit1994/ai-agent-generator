from __future__ import annotations

import json
from pathlib import Path

from event_sourced_architecture.learning_lineage import validate_learning_lineage_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_lineage_layer import (
    write_event_lineage_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.learning_lineage_layer import (
    write_learning_lineage_artifact,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)


def test_learning_lineage_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-learning-lineage"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "traces.jsonl").write_text(
        '{"stage":"finalize","score":{"passed":true,"reliability":0.9}}\n',
        encoding="utf-8",
    )
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    write_event_lineage_artifacts(output_dir=run_dir, run_id=run_id)
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
    payload = write_learning_lineage_artifact(
        output_dir=run_dir, run_id=run_id, mode="guarded_pipeline"
    )
    assert payload["run_id"] == run_id
    lineage_path = run_dir / "learning" / "learning_lineage.json"
    assert validate_learning_lineage_path(lineage_path) == []
    body = json.loads(lineage_path.read_text(encoding="utf-8"))
    assert body["status"] in {"aligned", "partial", "broken"}
