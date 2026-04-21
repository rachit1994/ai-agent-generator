from __future__ import annotations

from pathlib import Path

from core_components.observability import validate_observability_component_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.observability_component_layer import (
    write_observability_component_artifact,
)


def test_observability_component_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-observability-component"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir)
    write_json(run_dir / "observability" / "production_observability.json", {"status": "ready"})
    (run_dir / "run.log").write_text("run log\n", encoding="utf-8")
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    (run_dir / "orchestration.jsonl").write_text("", encoding="utf-8")
    payload = write_observability_component_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "ready"
    assert validate_observability_component_path(run_dir / "observability" / "component_runtime.json") == []
