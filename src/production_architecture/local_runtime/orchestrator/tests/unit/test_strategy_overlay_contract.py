"""§10.A — ``strategy/proposal.json`` contract (strategy → production / **HS32**)."""

from __future__ import annotations

from pathlib import Path

from workflow_pipelines.strategy_overlay.strategy_overlay_contract import (
    STRATEGY_OVERLAY_CONTRACT,
    validate_strategy_proposal_dict,
    validate_strategy_proposal_path,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.organization_layer import (
    write_organization_artifacts,
)


def test_strategy_overlay_contract_id() -> None:
    assert STRATEGY_OVERLAY_CONTRACT == "sde.strategy_overlay_proposal.v1"


def test_validate_strategy_proposal_dict_harness_ok() -> None:
    body = {
        "schema_version": "1.0",
        "actor_id": "strategy-agent-harness",
        "requires_promotion_package": True,
        "applied_autonomy": False,
        "proposal_ref": "lifecycle/promotion_package.json",
    }
    assert validate_strategy_proposal_dict(body) == []


def test_validate_strategy_proposal_dict_not_object() -> None:
    assert validate_strategy_proposal_dict([]) == ["strategy_overlay_not_object"]


def test_validate_strategy_proposal_dict_autonomy_without_promotion() -> None:
    body = {
        "schema_version": "1.0",
        "actor_id": "a",
        "requires_promotion_package": False,
        "applied_autonomy": True,
        "proposal_ref": "x",
    }
    assert "strategy_overlay_autonomy_requires_promotion" in validate_strategy_proposal_dict(body)


def test_validate_strategy_proposal_dict_missing_ref_when_required() -> None:
    body = {
        "schema_version": "1.0",
        "actor_id": "a",
        "requires_promotion_package": True,
        "applied_autonomy": False,
    }
    assert "strategy_overlay_proposal_ref" in validate_strategy_proposal_dict(body)


def test_validate_strategy_proposal_path_missing(tmp_path: Path) -> None:
    assert validate_strategy_proposal_path(tmp_path / "p.json") == ["strategy_overlay_file_missing"]


def test_validate_strategy_proposal_path_bad_json(tmp_path: Path) -> None:
    p = tmp_path / "p.json"
    p.write_text("{", encoding="utf-8")
    assert validate_strategy_proposal_path(p) == ["strategy_overlay_json"]


def test_write_organization_artifacts_writes_valid_proposal(tmp_path: Path) -> None:
    write_organization_artifacts(output_dir=tmp_path, run_id="rid-strat")
    prop = tmp_path / "strategy" / "proposal.json"
    assert validate_strategy_proposal_path(prop) == []
