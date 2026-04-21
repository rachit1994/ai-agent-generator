from __future__ import annotations

import json
from pathlib import Path

from scalability_strategy.full_build_order_progression import validate_full_build_order_progression_path
from production_architecture.storage.storage.storage import ensure_dir
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.full_build_order_progression_layer import (
    write_full_build_order_progression_artifact,
)


def test_write_full_build_order_progression_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-fbop"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir)
    (output_dir / "orchestration.jsonl").write_text(
        '{"type":"stage_event","stage":"planner_doc"}\n'
        '{"type":"stage_event","stage":"planner_prompt"}\n'
        '{"type":"stage_event","stage":"executor"}\n'
        '{"type":"stage_event","stage":"finalize"}\n',
        encoding="utf-8",
    )
    payload = write_full_build_order_progression_artifact(
        output_dir=output_dir, run_id=run_id, mode="guarded_pipeline"
    )
    assert payload["run_id"] == run_id
    assert (
        validate_full_build_order_progression_path(
            output_dir / "strategy" / "full_build_order_progression.json"
        )
        == []
    )
    body = json.loads(
        (output_dir / "strategy" / "full_build_order_progression.json").read_text(encoding="utf-8")
    )
    assert body["run_id"] == run_id

