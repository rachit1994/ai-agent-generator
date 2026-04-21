from __future__ import annotations

from pathlib import Path

from core_components.orchestrator import validate_orchestrator_component_path
from production_architecture.storage.storage.storage import write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.orchestrator_component_layer import (
    write_orchestrator_component_artifact,
)


def test_orchestrator_component_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-orchestrator-component"
    run_dir = tmp_path / "runs" / run_id
    write_json(
        run_dir / "run-manifest.json",
        {
            "schema": "sde.run_manifest.v1",
            "run_id": run_id,
            "mode": "baseline",
            "task": "hello",
        },
    )
    write_json(
        run_dir / "program" / "run_manifest_runtime.json",
        {
            "schema": "sde.run_manifest_runtime.v1",
            "schema_version": "1.0",
            "run_id": run_id,
            "status": "standalone",
            "links": {
                "has_project_step_id": False,
                "has_project_session_dir": False,
                "project_linkage_valid": True,
            },
            "evidence": {},
        },
    )
    (run_dir / "traces.jsonl").parent.mkdir(parents=True, exist_ok=True)
    (run_dir / "traces.jsonl").write_text('{"type":"run_start"}\n', encoding="utf-8")
    (run_dir / "orchestration.jsonl").write_text('{"type":"run_start"}\n', encoding="utf-8")
    payload = write_orchestrator_component_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "ready"
    assert validate_orchestrator_component_path(run_dir / "orchestrator" / "component_runtime.json") == []
