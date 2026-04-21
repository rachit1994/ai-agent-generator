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
    write_json(run_dir / "observability" / "production_observability.json", {"status": "healthy"})
    (run_dir / "run.log").write_text("run log\n", encoding="utf-8")
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    (run_dir / "orchestration.jsonl").write_text("", encoding="utf-8")
    payload = write_observability_component_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "ready"
    assert validate_observability_component_path(run_dir / "observability" / "component_runtime.json") == []


def test_observability_component_degraded_when_production_observability_not_healthy(
    tmp_path: Path,
) -> None:
    run_id = "run-observability-component-upstream-degraded"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir)
    write_json(run_dir / "observability" / "production_observability.json", {"status": "degraded"})
    (run_dir / "run.log").write_text("run log\n", encoding="utf-8")
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    (run_dir / "orchestration.jsonl").write_text("", encoding="utf-8")
    payload = write_observability_component_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["status"] == "degraded"
    assert payload["metrics"]["has_production_observability"] is False


def test_validate_observability_component_path_rejects_non_canonical_evidence_ref(
    tmp_path: Path,
) -> None:
    run_id = "run-observability-component-evidence-mismatch"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir / "observability")
    write_json(
        run_dir / "observability" / "component_runtime.json",
        {
            "schema": "sde.observability_component.v1",
            "schema_version": "1.0",
            "run_id": run_id,
            "status": "ready",
            "metrics": {
                "has_production_observability": True,
                "has_run_log": True,
                "has_traces": True,
                "has_orchestration_log": True,
                "all_checks_passed": True,
            },
            "evidence": {
                "production_observability_ref": "observability/production_observability.json",
                "run_log_ref": "run.log",
                "traces_ref": "trace.jsonl",
                "orchestration_ref": "orchestration.jsonl",
                "component_ref": "observability/component_runtime.json",
            },
        },
    )
    errs = validate_observability_component_path(run_dir / "observability" / "component_runtime.json")
    assert "observability_component_evidence_ref_mismatch:traces_ref" in errs
