from __future__ import annotations

import json
from pathlib import Path

import pytest

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


def test_production_identity_writer_is_byte_deterministic_for_identical_inputs(tmp_path: Path) -> None:
    run_id = "run-prod-identity-byte-determinism"
    run_dir_one = tmp_path / "runs" / "one"
    run_dir_two = tmp_path / "runs" / "two"

    write_organization_artifacts(output_dir=run_dir_one, run_id=run_id)
    write_organization_artifacts(output_dir=run_dir_two, run_id=run_id)

    write_production_identity_authorization_artifact(output_dir=run_dir_one, run_id=run_id)
    write_production_identity_authorization_artifact(output_dir=run_dir_two, run_id=run_id)

    bytes_one = (run_dir_one / "iam" / "production_identity_authorization.json").read_bytes()
    bytes_two = (run_dir_two / "iam" / "production_identity_authorization.json").read_bytes()
    assert bytes_one == bytes_two


def test_production_identity_writer_fails_closed_for_malformed_jsonl(tmp_path: Path) -> None:
    run_id = "run-prod-identity-malformed-jsonl"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "iam").mkdir(parents=True)
    (run_dir / "strategy").mkdir(parents=True)
    (run_dir / "iam" / "permission_matrix.json").write_text(
        json.dumps({"roles": {"operator": ["read"]}}),
        encoding="utf-8",
    )
    (run_dir / "strategy" / "proposal.json").write_text(
        json.dumps({"requires_promotion_package": True, "applied_autonomy": True}),
        encoding="utf-8",
    )
    (run_dir / "iam" / "action_audit.jsonl").write_text("{bad}\n", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match=(
            "^production_identity_authorization_contract:invalid_jsonl:iam/action_audit.jsonl:1$"
        ),
    ):
        write_production_identity_authorization_artifact(output_dir=run_dir, run_id=run_id)


def test_production_identity_writer_fails_closed_for_non_object_strategy_proposal(tmp_path: Path) -> None:
    run_id = "run-prod-identity-proposal-type"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "iam").mkdir(parents=True)
    (run_dir / "strategy").mkdir(parents=True)
    (run_dir / "iam" / "permission_matrix.json").write_text(
        json.dumps({"roles": {"operator": ["read"]}}),
        encoding="utf-8",
    )
    (run_dir / "strategy" / "proposal.json").write_text(json.dumps([]), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="^production_identity_authorization_contract:json_not_object:strategy/proposal.json$",
    ):
        write_production_identity_authorization_artifact(output_dir=run_dir, run_id=run_id)


def test_production_identity_writer_fails_closed_for_jsonl_non_object_row(tmp_path: Path) -> None:
    run_id = "run-prod-identity-jsonl-non-object-row"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "iam").mkdir(parents=True)
    (run_dir / "strategy").mkdir(parents=True)
    (run_dir / "iam" / "permission_matrix.json").write_text(
        json.dumps({"roles": {"operator": ["read"]}}),
        encoding="utf-8",
    )
    (run_dir / "strategy" / "proposal.json").write_text(
        json.dumps({"requires_promotion_package": True, "applied_autonomy": True}),
        encoding="utf-8",
    )
    (run_dir / "iam" / "action_audit.jsonl").write_text("[]\n", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match=(
            "^production_identity_authorization_contract:jsonl_not_object:iam/action_audit.jsonl:1$"
        ),
    ):
        write_production_identity_authorization_artifact(output_dir=run_dir, run_id=run_id)


def test_production_identity_writer_fails_closed_for_malformed_permission_matrix_json(tmp_path: Path) -> None:
    run_id = "run-prod-identity-permission-malformed-json"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "iam").mkdir(parents=True)
    (run_dir / "strategy").mkdir(parents=True)
    (run_dir / "iam" / "permission_matrix.json").write_text("{bad}\n", encoding="utf-8")
    (run_dir / "strategy" / "proposal.json").write_text(
        json.dumps({"requires_promotion_package": True, "applied_autonomy": True}),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="^production_identity_authorization_contract:invalid_json:iam/permission_matrix.json$",
    ):
        write_production_identity_authorization_artifact(output_dir=run_dir, run_id=run_id)


def test_production_identity_writer_fails_closed_for_malformed_strategy_json(tmp_path: Path) -> None:
    run_id = "run-prod-identity-strategy-malformed-json"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "iam").mkdir(parents=True)
    (run_dir / "strategy").mkdir(parents=True)
    (run_dir / "iam" / "permission_matrix.json").write_text(
        json.dumps({"roles": {"operator": ["read"]}}),
        encoding="utf-8",
    )
    (run_dir / "strategy" / "proposal.json").write_text("{bad}\n", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="^production_identity_authorization_contract:invalid_json:strategy/proposal.json$",
    ):
        write_production_identity_authorization_artifact(output_dir=run_dir, run_id=run_id)
