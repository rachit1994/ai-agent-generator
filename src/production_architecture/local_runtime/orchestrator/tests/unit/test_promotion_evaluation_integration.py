from __future__ import annotations

import json
from pathlib import Path

import pytest

from evaluation_framework.promotion_evaluation import validate_promotion_evaluation_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.promotion_evaluation_layer import (
    write_promotion_evaluation_artifact,
)


def test_promotion_evaluation_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-promotion-evaluation"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    traces = run_dir / "traces.jsonl"
    traces.parent.mkdir(parents=True, exist_ok=True)
    traces.write_text('{"stage":"finalize","score":{"passed":true}}\n', encoding="utf-8")
    write_evolution_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        skill_nodes={"nodes": [{"score": 0.8}]},
    )
    payload = write_promotion_evaluation_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert validate_promotion_evaluation_path(run_dir / "learning" / "promotion_evaluation.json") == []


def test_promotion_evaluation_holds_on_truthy_non_bool_finalize_pass(tmp_path: Path) -> None:
    run_id = "run-promotion-evaluation-fail-closed"
    run_dir = tmp_path / "runs" / run_id
    traces = run_dir / "traces.jsonl"
    traces.parent.mkdir(parents=True, exist_ok=True)
    traces.write_text('{"stage":"finalize","score":{"passed":"true"}}\n', encoding="utf-8")
    (run_dir / "lifecycle").mkdir(parents=True, exist_ok=True)
    (run_dir / "lifecycle" / "promotion_package.json").write_text(
        '{"readiness":{"score":1.0}}', encoding="utf-8"
    )
    (run_dir / "review.json").write_text('{"status":"completed_review_pass"}', encoding="utf-8")
    payload = write_promotion_evaluation_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["signals"]["finalize_pass_rate"] == pytest.approx(0.0)
    assert payload["decision"] == "hold"


def test_validate_promotion_evaluation_path_rejects_decision_signal_mismatch(tmp_path: Path) -> None:
    run_id = "run-promotion-evaluation-mismatch"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True, exist_ok=True)
    path = run_dir / "learning" / "promotion_evaluation.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.promotion_evaluation.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "decision": "promote",
                "confidence": 0.1,
                "signals": {
                    "promotion_readiness_score": 0.9,
                    "finalize_pass_rate": 0.9,
                    "review_pass": True,
                },
                "evidence": {
                    "promotion_package_ref": "lifecycle/promotion_package.json",
                    "review_ref": "review.json",
                    "traces_ref": "traces.jsonl",
                    "promotion_evaluation_ref": "learning/promotion_evaluation.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_promotion_evaluation_path(path)
    assert "promotion_evaluation_confidence_semantics" in errs
