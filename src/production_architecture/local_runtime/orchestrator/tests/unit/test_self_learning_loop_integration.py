from __future__ import annotations

import json
from pathlib import Path

import pytest

from core_components.self_learning_loop import validate_self_learning_loop_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.practice_engine_layer import (
    write_practice_engine_artifact,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.self_learning_loop_layer import (
    write_self_learning_loop_artifact,
)


def test_self_learning_loop_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-self-learning-loop"
    run_dir = tmp_path / "runs" / run_id
    parsed = {
        "checks": [{"name": "shape", "passed": True}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": True}],
    }
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.95}}]
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    write_evolution_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        skill_nodes=skill_nodes,
    )
    write_practice_engine_artifact(output_dir=run_dir, run_id=run_id)
    payload = write_self_learning_loop_artifact(
        output_dir=run_dir, run_id=run_id, mode="guarded_pipeline"
    )
    loop_path = run_dir / "learning" / "self_learning_loop.json"
    assert validate_self_learning_loop_path(loop_path) == []
    assert payload["run_id"] == run_id
    body = json.loads(loop_path.read_text(encoding="utf-8"))
    assert body["decision"]["decision"] in {"hold", "reject", "promote"}
    assert (run_dir / "learning" / "self_learning_candidates.jsonl").is_file()


def test_self_learning_loop_fail_closed_for_truthy_non_boolean_finalize_passed(
    tmp_path: Path,
) -> None:
    run_id = "run-self-learning-loop-truthy"
    run_dir = tmp_path / "runs" / run_id
    parsed = {
        "checks": [{"name": "shape", "passed": True}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": True}],
    }
    events = [{"stage": "finalize", "score": {"passed": "true", "reliability": 0.95}}]
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    write_evolution_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        skill_nodes=skill_nodes,
    )
    write_practice_engine_artifact(output_dir=run_dir, run_id=run_id)
    payload = write_self_learning_loop_artifact(
        output_dir=run_dir, run_id=run_id, mode="guarded_pipeline"
    )
    assert payload["signals"]["finalize_pass_rate"] == pytest.approx(0.0)
    assert "verifier_pass_rate" in payload["decision"]["failed_gates"]


def test_validate_self_learning_loop_path_rejects_loop_state_mismatch(tmp_path: Path) -> None:
    run_id = "run-self-learning-loop-loop-state-mismatch"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True)
    loop_path = run_dir / "learning" / "self_learning_loop.json"
    loop_path.write_text(
        json.dumps(
            {
                "schema": "sde.self_learning_loop.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "mode": "guarded_pipeline",
                "signals": {
                    "finalize_pass_rate": 1.0,
                    "capability_score": 0.9,
                    "transfer_efficiency": 0.9,
                    "growth_signal": 0.9,
                    "practice_readiness": 0.9,
                },
                "decision": {
                    "decision": "promote",
                    "loop_state": "hold",
                    "failed_gates": [],
                    "decision_reasons": [],
                    "next_action": "open_promotion_review",
                    "primary_reason": "self_learning_loop_contract:all_gates_passed",
                },
                "evidence": {
                    "traces_ref": "traces.jsonl",
                    "skill_nodes_ref": "capability/skill_nodes.json",
                    "practice_engine_ref": "practice/practice_engine.json",
                    "transfer_learning_metrics_ref": "learning/transfer_learning_metrics.json",
                    "capability_growth_metrics_ref": "learning/capability_growth_metrics.json",
                    "self_learning_candidates_ref": "learning/self_learning_candidates.jsonl",
                    "self_learning_loop_ref": "learning/self_learning_loop.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_self_learning_loop_path(loop_path)
    assert "self_learning_loop_loop_state_mismatch" in errs


def test_validate_self_learning_loop_path_rejects_next_action_mismatch(tmp_path: Path) -> None:
    run_id = "run-self-learning-loop-next-action-mismatch"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True)
    loop_path = run_dir / "learning" / "self_learning_loop.json"
    loop_path.write_text(
        json.dumps(
            {
                "schema": "sde.self_learning_loop.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "mode": "guarded_pipeline",
                "signals": {
                    "finalize_pass_rate": 1.0,
                    "capability_score": 0.9,
                    "transfer_efficiency": 0.9,
                    "growth_signal": 0.9,
                    "practice_readiness": 0.9,
                },
                "decision": {
                    "decision": "promote",
                    "loop_state": "promote",
                    "failed_gates": [],
                    "decision_reasons": [],
                    "next_action": "halt_and_repair",
                    "primary_reason": "self_learning_loop_contract:all_gates_passed",
                },
                "evidence": {
                    "traces_ref": "traces.jsonl",
                    "skill_nodes_ref": "capability/skill_nodes.json",
                    "practice_engine_ref": "practice/practice_engine.json",
                    "transfer_learning_metrics_ref": "learning/transfer_learning_metrics.json",
                    "capability_growth_metrics_ref": "learning/capability_growth_metrics.json",
                    "self_learning_candidates_ref": "learning/self_learning_candidates.jsonl",
                    "self_learning_loop_ref": "learning/self_learning_loop.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_self_learning_loop_path(loop_path)
    assert "self_learning_loop_next_action_mismatch" in errs
