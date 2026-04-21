from __future__ import annotations

from pathlib import Path

from production_architecture.orchestration import validate_production_orchestration_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.organization_layer import (
    write_organization_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.production_orchestration_layer import (
    write_production_orchestration_artifact,
)


def test_production_orchestration_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-production-orchestration"
    run_dir = tmp_path / "runs" / run_id
    write_organization_artifacts(output_dir=run_dir, run_id=run_id)
    payload = write_production_orchestration_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    path = run_dir / "orchestration" / "production_orchestration.json"
    assert validate_production_orchestration_path(path) == []


def test_production_orchestration_degraded_for_truthy_non_boolean_active_lease(
    tmp_path: Path,
) -> None:
    run_id = "run-production-orchestration-degraded"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "coordination").mkdir(parents=True, exist_ok=True)
    (run_dir / "orchestration").mkdir(parents=True, exist_ok=True)
    (run_dir / "coordination" / "lease_table.json").write_text(
        '{"leases":[{"lease_id":"l1","active":"true"}]}',
        encoding="utf-8",
    )
    (run_dir / "orchestration" / "shard_map.json").write_text(
        '{"shards":[{"id":"s1"}]}',
        encoding="utf-8",
    )
    payload = write_production_orchestration_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["metrics"]["active_lease_count"] == 0
    assert payload["status"] == "degraded"
