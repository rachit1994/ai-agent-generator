from __future__ import annotations

import json
from pathlib import Path

import pytest

from core_components.role_agents import validate_role_agents_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.role_agents_layer import (
    write_role_agents_artifact,
)


def test_role_agents_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-role-agents"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    payload = write_role_agents_artifact(
        output_dir=run_dir,
        run_id=run_id,
        parsed=parsed,
        events=events,
        skill_nodes=skill_nodes,
    )
    assert payload["run_id"] == run_id
    role_agents_path = run_dir / "capability" / "role_agents.json"
    assert validate_role_agents_path(role_agents_path) == []
    body = json.loads(role_agents_path.read_text(encoding="utf-8"))
    assert body["status"] in {"balanced", "drifted", "insufficient_signal"}


def test_role_agents_fail_closed_for_truthy_non_boolean_passed(tmp_path: Path) -> None:
    run_id = "run-role-agents-fail-closed"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": "true"}]}
    events = [{"stage": "finalize", "score": {"passed": "yes"}}]
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    payload = write_role_agents_artifact(
        output_dir=run_dir,
        run_id=run_id,
        parsed=parsed,
        events=events,
        skill_nodes=skill_nodes,
    )
    assert payload["role_scores"]["planner"] == pytest.approx(0.0)
    assert payload["role_scores"]["implementor"] == pytest.approx(0.0)


def test_validate_role_agents_path_rejects_status_spread_mismatch(tmp_path: Path) -> None:
    run_id = "run-role-agents-status-mismatch"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "capability").mkdir(parents=True)
    role_agents_path = run_dir / "capability" / "role_agents.json"
    role_agents_path.write_text(
        json.dumps(
            {
                "schema": "sde.role_agents.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "status": "drifted",
                "role_scores": {"planner": 0.5, "implementor": 0.5, "verifier": 0.5},
                "evidence": {
                    "summary_ref": "summary.json",
                    "traces_ref": "traces.jsonl",
                    "skill_nodes_ref": "capability/skill_nodes.json",
                    "role_agents_ref": "capability/role_agents.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_role_agents_path(role_agents_path)
    assert "role_agents_status_semantics:drifted" in errs
