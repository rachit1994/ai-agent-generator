from __future__ import annotations

from pathlib import Path

from production_architecture.identity_and_authorization import (
    validate_production_identity_authorization_path,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.organization_layer import (
    write_organization_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.production_identity_authorization_layer import (
    write_production_identity_authorization_artifact,
)


def test_production_identity_and_authorization_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-prod-identity-authz"
    run_dir = tmp_path / "runs" / run_id
    write_organization_artifacts(output_dir=run_dir, run_id=run_id)
    payload = write_production_identity_authorization_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    artifact_path = run_dir / "iam" / "production_identity_authorization.json"
    assert validate_production_identity_authorization_path(artifact_path) == []
