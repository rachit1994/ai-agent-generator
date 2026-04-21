from __future__ import annotations

import json
from pathlib import Path

import pytest

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


def test_identity_authz_writer_is_byte_deterministic_for_identical_inputs(tmp_path: Path) -> None:
    run_id = "run-identity-authz-byte-determinism"
    run_dir_one = tmp_path / "runs" / "one"
    run_dir_two = tmp_path / "runs" / "two"

    write_organization_artifacts(output_dir=run_dir_one, run_id=run_id)
    write_organization_artifacts(output_dir=run_dir_two, run_id=run_id)

    write_identity_authz_plane_artifact(output_dir=run_dir_one, run_id=run_id)
    write_identity_authz_plane_artifact(output_dir=run_dir_two, run_id=run_id)

    bytes_one = (run_dir_one / "iam" / "identity_authz_plane.json").read_bytes()
    bytes_two = (run_dir_two / "iam" / "identity_authz_plane.json").read_bytes()
    assert bytes_one == bytes_two


def test_identity_authz_writer_fails_closed_for_malformed_jsonl(tmp_path: Path) -> None:
    run_id = "run-identity-authz-malformed-jsonl"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "iam").mkdir(parents=True)
    (run_dir / "coordination").mkdir(parents=True)
    (run_dir / "iam" / "permission_matrix.json").write_text(json.dumps({"roles": [{"name": "r"}]}), encoding="utf-8")
    (run_dir / "coordination" / "lease_table.json").write_text(
        json.dumps({"leases": [{"lease_id": "l1", "active": True}]}),
        encoding="utf-8",
    )
    (run_dir / "iam" / "action_audit.jsonl").write_text("{bad}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="^identity_authz_plane_contract:invalid_jsonl:iam/action_audit.jsonl:1$"):
        write_identity_authz_plane_artifact(output_dir=run_dir, run_id=run_id)


def test_identity_authz_writer_fails_closed_for_non_object_permission_matrix(tmp_path: Path) -> None:
    run_id = "run-identity-authz-permission-type"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "iam").mkdir(parents=True)
    (run_dir / "coordination").mkdir(parents=True)
    (run_dir / "iam" / "permission_matrix.json").write_text(json.dumps([]), encoding="utf-8")
    (run_dir / "coordination" / "lease_table.json").write_text(json.dumps({"leases": []}), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="^identity_authz_plane_contract:json_not_object:iam/permission_matrix.json$",
    ):
        write_identity_authz_plane_artifact(output_dir=run_dir, run_id=run_id)


def test_identity_authz_writer_fails_closed_for_non_object_lease_table(tmp_path: Path) -> None:
    run_id = "run-identity-authz-lease-type"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "iam").mkdir(parents=True)
    (run_dir / "coordination").mkdir(parents=True)
    (run_dir / "iam" / "permission_matrix.json").write_text(json.dumps({"roles": [{"name": "r"}]}), encoding="utf-8")
    (run_dir / "coordination" / "lease_table.json").write_text(json.dumps([]), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="^identity_authz_plane_contract:json_not_object:coordination/lease_table.json$",
    ):
        write_identity_authz_plane_artifact(output_dir=run_dir, run_id=run_id)
