from __future__ import annotations

import json
from pathlib import Path

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.organization_layer import (
    write_organization_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.strategy_overlay_layer import (
    write_strategy_overlay_runtime_artifact,
)
from workflow_pipelines.strategy_overlay import validate_strategy_overlay_runtime_path


def test_write_strategy_overlay_runtime_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-strategy-overlay"
    output_dir = tmp_path / "runs" / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    write_organization_artifacts(output_dir=output_dir, run_id=run_id)
    (output_dir / "traces.jsonl").write_text(
        '{"stage":"finalize","score":{"passed":true}}\n',
        encoding="utf-8",
    )
    payload = write_strategy_overlay_runtime_artifact(
        output_dir=output_dir, run_id=run_id, mode="guarded_pipeline"
    )
    assert payload["run_id"] == run_id
    overlay_path = output_dir / "strategy" / "overlay.json"
    assert validate_strategy_overlay_runtime_path(overlay_path) == []
    body = json.loads(overlay_path.read_text(encoding="utf-8"))
    assert body["strategy_name"] in {"stabilize", "accelerate", "hold"}
