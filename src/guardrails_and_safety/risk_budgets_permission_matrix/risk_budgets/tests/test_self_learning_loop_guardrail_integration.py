from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory import (
    validate_execution_run_directory,
)


def _valid_review() -> dict[str, object]:
    return {
        "schema_version": "1.1",
        "run_id": "rid-guardrail",
        "status": "completed_review_pass",
        "reasons": [],
        "required_fixes": [],
        "gate_snapshot": {},
        "artifact_manifest": [],
        "review_findings": [],
        "completed_at": "2026-01-01T00:00:00Z",
    }


def test_guardrails_block_promote_when_hard_stop_active(tmp_path: Path, monkeypatch) -> None:
    run_dir = tmp_path / "run"
    (run_dir / "learning").mkdir(parents=True)
    (run_dir / "outputs").mkdir(parents=True)
    (run_dir / "capability").mkdir(parents=True)
    (run_dir / "practice").mkdir(parents=True)
    (run_dir / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (run_dir / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (run_dir / "summary.json").write_text(
        json.dumps({"runStatus": "ok", "balanced_gates": {}}),
        encoding="utf-8",
    )
    (run_dir / "token_context.json").write_text(
        json.dumps({"schema_version": "1.0", "stages": []}),
        encoding="utf-8",
    )
    (run_dir / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    (run_dir / "capability" / "skill_nodes.json").write_text('{"nodes":[{"score":0.9}]}', encoding="utf-8")
    (run_dir / "practice" / "practice_engine.json").write_text(
        '{"scores":{"readiness_signal":0.9}}',
        encoding="utf-8",
    )
    (run_dir / "learning" / "transfer_learning_metrics.json").write_text(
        '{"scores":{"transfer_efficiency":0.9}}',
        encoding="utf-8",
    )
    (run_dir / "learning" / "capability_growth_metrics.json").write_text(
        '{"scores":{"capability_growth_rate":0.9}}',
        encoding="utf-8",
    )
    (run_dir / "learning" / "self_learning_candidates.jsonl").write_text("{}", encoding="utf-8")
    (run_dir / "learning" / "self_learning_loop.json").write_text(
        json.dumps(
            {
                "schema": "sde.self_learning_loop.v1",
                "schema_version": "1.0",
                "run_id": "rid-guardrail",
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
                    "failed_gates": [],
                    "decision_reasons": ["self_learning_loop_contract:all_gates_passed"],
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
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [{"id": "HS19", "passed": False}],
    )

    result = validate_execution_run_directory(run_dir, mode="guarded_pipeline")
    assert "hard_stop_failed:HS19" in result["errors"]
    assert "self_learning_loop_contract:self_learning_loop_promote_with_active_hard_stop" in result["errors"]
