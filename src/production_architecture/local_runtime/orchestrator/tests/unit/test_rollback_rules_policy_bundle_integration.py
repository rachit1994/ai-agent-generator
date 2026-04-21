from __future__ import annotations

from pathlib import Path

import pytest

from guardrails_and_safety.rollback_rules_policy_bundle import validate_rollback_rules_policy_bundle_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.completion_layer import (
    write_completion_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.rollback_rules_policy_bundle_layer import (
    write_rollback_rules_policy_bundle_artifact,
)


def test_rollback_rules_policy_bundle_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-rollback-rules"
    run_dir = tmp_path / "runs" / run_id
    write_completion_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        task="validate rollback evidence",
        parsed={},
        events=[],
    )
    payload = write_rollback_rules_policy_bundle_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "none"
    assert validate_rollback_rules_policy_bundle_path(
        run_dir / "program" / "rollback_rules_policy_bundle.json"
    ) == []


def test_rollback_rules_policy_bundle_layer_fails_closed_for_invalid_source_json(tmp_path: Path) -> None:
    run_id = "run-rollback-rules"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "program").mkdir(parents=True)
    (run_dir / "program" / "policy_bundle_rollback.json").write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="rollback_rules_policy_bundle_contract:policy_bundle_rollback_invalid_json"):
        write_rollback_rules_policy_bundle_artifact(output_dir=run_dir, run_id=run_id)


def test_rollback_rules_policy_bundle_layer_fails_closed_for_non_object_source_json(tmp_path: Path) -> None:
    run_id = "run-rollback-rules"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "program").mkdir(parents=True)
    (run_dir / "program" / "policy_bundle_rollback.json").write_text("[]", encoding="utf-8")
    with pytest.raises(
        ValueError,
        match="rollback_rules_policy_bundle_contract:policy_bundle_rollback_json_not_object",
    ):
        write_rollback_rules_policy_bundle_artifact(output_dir=run_dir, run_id=run_id)
