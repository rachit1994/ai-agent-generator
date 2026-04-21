from __future__ import annotations

import json
from pathlib import Path

from core_components.identity_and_authorization_plane import (
    validate_identity_authz_plane_path,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.identity_authz_plane_layer import (
    write_identity_authz_plane_artifact,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.organization_layer import (
    write_organization_artifacts,
)


def test_identity_authz_plane_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-identity-authz-plane"
    run_dir = tmp_path / "runs" / run_id
    write_organization_artifacts(output_dir=run_dir, run_id=run_id)
    payload = write_identity_authz_plane_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    identity_path = run_dir / "iam" / "identity_authz_plane.json"
    assert validate_identity_authz_plane_path(identity_path) == []
    body = json.loads(identity_path.read_text(encoding="utf-8"))
    assert body["status"] in {"enforced", "degraded", "missing"}
