from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory import (
    validate_execution_run_directory,
)


def _valid_review() -> dict[str, object]:
    return {
        "schema_version": "1.1",
        "run_id": "rid-1",
        "status": "completed_review_pass",
        "reasons": [],
        "required_fixes": [],
        "gate_snapshot": {},
        "artifact_manifest": [],
        "review_findings": [],
        "completed_at": "2026-01-01T00:00:00Z",
    }


def _baseline_dir(tmp_path: Path) -> Path:
    out = tmp_path / "run"
    (out / "learning").mkdir(parents=True)
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0", "stages": []}), encoding="utf-8")
    (out / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    return out


def test_run_directory_requires_self_learning_loop_artifact(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "self_learning_loop_contract:self_learning_loop_file_missing" in result["errors"]


def test_run_directory_rejects_invalid_self_learning_semantics(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "learning" / "self_learning_loop.json").write_text(
        json.dumps(
            {
                "schema": "sde.self_learning_loop.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "guarded_pipeline",
                "signals": {
                    "finalize_pass_rate": 0.95,
                    "capability_score": 0.9,
                    "transfer_efficiency": 0.9,
                    "growth_signal": 0.9,
                    "practice_readiness": 0.9,
                },
                "decision": {
                    "decision": "promote",
                    "failed_gates": ["min_examples"],
                    "decision_reasons": ["self_learning_loop_contract:gate_min_examples_unmet"],
                    "next_action": "open_promotion_review",
                    "primary_reason": "self_learning_loop_contract:gate_min_examples_unmet",
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
    (out / "learning" / "self_learning_candidates.jsonl").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "self_learning_loop_contract:self_learning_loop_promote_failed_gates" in result["errors"]


def test_run_directory_rejects_missing_self_learning_evidence_refs(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "learning" / "self_learning_loop.json").write_text(
        json.dumps(
            {
                "schema": "sde.self_learning_loop.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "guarded_pipeline",
                "signals": {
                    "finalize_pass_rate": 0.95,
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
    (out / "learning" / "self_learning_candidates.jsonl").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert (
        "self_learning_loop_contract:self_learning_loop_evidence_ref_missing:skill_nodes_ref"
        in result["errors"]
    )
    assert (
        "self_learning_loop_contract:self_learning_loop_evidence_ref_missing:practice_engine_ref"
        in result["errors"]
    )


def test_run_directory_rejects_promote_under_active_hard_stop(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "capability").mkdir(parents=True)
    (out / "practice").mkdir(parents=True)
    (out / "capability" / "skill_nodes.json").write_text('{"nodes":[{"score":0.9}]}', encoding="utf-8")
    (out / "practice" / "practice_engine.json").write_text(
        '{"scores":{"readiness_signal":0.9}}',
        encoding="utf-8",
    )
    (out / "learning" / "transfer_learning_metrics.json").write_text(
        '{"scores":{"transfer_efficiency":0.9}}',
        encoding="utf-8",
    )
    (out / "learning" / "capability_growth_metrics.json").write_text(
        '{"scores":{"capability_growth_rate":0.9}}',
        encoding="utf-8",
    )
    (out / "learning" / "self_learning_candidates.jsonl").write_text("{}", encoding="utf-8")
    (out / "learning" / "self_learning_loop.json").write_text(
        json.dumps(
            {
                "schema": "sde.self_learning_loop.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "guarded_pipeline",
                "signals": {
                    "finalize_pass_rate": 0.95,
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
        lambda output_dir, events, token_ctx, run_status, mode: [{"id": "HS17", "passed": False}],
    )
    result = validate_execution_run_directory(out, mode="guarded_pipeline")
    assert "hard_stop_failed:HS17" in result["errors"]
    assert "self_learning_loop_contract:self_learning_loop_promote_with_active_hard_stop" in result["errors"]


def test_run_directory_rejects_duplicate_self_learning_candidates(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "capability").mkdir(parents=True)
    (out / "practice").mkdir(parents=True)
    (out / "capability" / "skill_nodes.json").write_text('{"nodes":[{"score":0.9}]}', encoding="utf-8")
    (out / "practice" / "practice_engine.json").write_text(
        '{"scores":{"readiness_signal":0.9}}',
        encoding="utf-8",
    )
    (out / "learning" / "transfer_learning_metrics.json").write_text(
        '{"scores":{"transfer_efficiency":0.9}}',
        encoding="utf-8",
    )
    (out / "learning" / "capability_growth_metrics.json").write_text(
        '{"scores":{"capability_growth_rate":0.9}}',
        encoding="utf-8",
    )
    (out / "learning" / "self_learning_candidates.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "candidate_id": "cid-1",
                        "run_id": "rid-1",
                        "trace_id": "trace-1",
                        "event_hash": "hash-1",
                    }
                ),
                json.dumps(
                    {
                        "candidate_id": "cid-1",
                        "run_id": "rid-1",
                        "trace_id": "trace-2",
                        "event_hash": "hash-2",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )
    (out / "learning" / "self_learning_loop.json").write_text(
        json.dumps(
            {
                "schema": "sde.self_learning_loop.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "guarded_pipeline",
                "signals": {
                    "finalize_pass_rate": 0.95,
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
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="guarded_pipeline")
    assert (
        "self_learning_loop_contract:self_learning_candidates_duplicate_candidate_id:2"
        in result["errors"]
    )


def test_run_directory_rejects_malformed_self_learning_candidate_row(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "capability").mkdir(parents=True)
    (out / "practice").mkdir(parents=True)
    (out / "capability" / "skill_nodes.json").write_text('{"nodes":[{"score":0.9}]}', encoding="utf-8")
    (out / "practice" / "practice_engine.json").write_text(
        '{"scores":{"readiness_signal":0.9}}',
        encoding="utf-8",
    )
    (out / "learning" / "transfer_learning_metrics.json").write_text(
        '{"scores":{"transfer_efficiency":0.9}}',
        encoding="utf-8",
    )
    (out / "learning" / "capability_growth_metrics.json").write_text(
        '{"scores":{"capability_growth_rate":0.9}}',
        encoding="utf-8",
    )
    (out / "learning" / "self_learning_candidates.jsonl").write_text(
        json.dumps({"candidate_id": "", "run_id": "rid-1"}),
        encoding="utf-8",
    )
    (out / "learning" / "self_learning_loop.json").write_text(
        json.dumps(
            {
                "schema": "sde.self_learning_loop.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "guarded_pipeline",
                "signals": {
                    "finalize_pass_rate": 0.95,
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
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="guarded_pipeline")
    assert "self_learning_loop_contract:self_learning_candidates_candidate_id:1" in result["errors"]
    assert "self_learning_loop_contract:self_learning_candidates_trace_id:1" in result["errors"]
    assert "self_learning_loop_contract:self_learning_candidates_event_hash:1" in result["errors"]
