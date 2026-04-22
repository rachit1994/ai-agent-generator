from __future__ import annotations

import json
from pathlib import Path

import pytest

from core_components.objective_policy_engine import validate_objective_policy_engine_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.objective_policy_engine_layer import (
    write_objective_policy_engine_artifact,
)


def test_write_objective_policy_engine_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-objective-policy"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "program")
    write_json(
        output_dir / "summary.json",
        {"balanced_gates": {"reliability": 95, "delivery": 94, "governance": 96, "composite": 95}},
    )
    write_json(output_dir / "review.json", {"status": "completed_review_pass"})
    cto = {"hard_stops": [{"id": "HS01", "passed": True}]}
    payload = write_objective_policy_engine_artifact(
        output_dir=output_dir, run_id=run_id, mode="guarded_pipeline", cto=cto
    )
    assert payload["run_id"] == run_id
    policy_path = output_dir / "strategy" / "objective_policy_engine.json"
    assert validate_objective_policy_engine_path(policy_path) == []
    body = json.loads(policy_path.read_text(encoding="utf-8"))
    assert body["policy"]["decision"] in {"allow", "defer", "deny"}


def test_write_objective_policy_engine_fails_closed_for_truthy_non_boolean_hard_stop(
    tmp_path: Path,
) -> None:
    run_id = "run-objective-policy-fail-closed"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "program")
    write_json(
        output_dir / "summary.json",
        {"balanced_gates": {"reliability": 95, "delivery": 94, "governance": 96, "composite": 95}},
    )
    write_json(output_dir / "review.json", {"status": "completed_review_pass"})
    payload = write_objective_policy_engine_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        cto={"hard_stops": [{"id": "HS01", "passed": "true"}]},
    )
    assert payload["policy"]["decision"] == "deny"
    assert payload["context"]["failed_hard_stop_count"] == 1


def test_write_objective_policy_engine_denies_when_scores_below_floor(tmp_path: Path) -> None:
    run_id = "run-objective-policy-score-floor"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "program")
    write_json(
        output_dir / "summary.json",
        {"balanced_gates": {"reliability": 95, "delivery": 94, "governance": 96, "composite": 60}},
    )
    write_json(output_dir / "review.json", {"status": "completed_review_pass"})
    payload = write_objective_policy_engine_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        cto={"hard_stops": [{"id": "HS01", "passed": True}]},
    )
    assert payload["policy"]["decision"] == "deny"
    assert payload["policy"]["reason"] == "score_floor_failure"


def test_write_objective_policy_engine_denies_when_rollback_validation_fails(tmp_path: Path) -> None:
    run_id = "run-objective-policy-rollback-failure"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "program")
    write_json(
        output_dir / "summary.json",
        {"balanced_gates": {"reliability": 95, "delivery": 94, "governance": 96, "composite": 95}},
    )
    write_json(output_dir / "review.json", {"status": "completed_review_pass"})
    (output_dir / "program" / "policy_bundle_rollback.json").write_text("{bad", encoding="utf-8")
    payload = write_objective_policy_engine_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        cto={"hard_stops": [{"id": "HS01", "passed": True}]},
    )
    assert payload["policy"]["decision"] == "deny"
    assert payload["policy"]["reason"] == "rollback_validation_failure"


def test_write_objective_policy_engine_fail_closes_malformed_summary_review_inputs(
    tmp_path: Path,
) -> None:
    run_id = "run-objective-policy-malformed-upstream"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "program")
    (output_dir / "summary.json").write_text("{bad", encoding="utf-8")
    (output_dir / "review.json").write_text("{bad", encoding="utf-8")
    with pytest.raises(ValueError, match="^objective_policy_engine_contract:"):
        write_objective_policy_engine_artifact(
            output_dir=output_dir,
            run_id=run_id,
            mode="guarded_pipeline",
            cto={"hard_stops": [{"id": "HS01", "passed": True}]},
        )
