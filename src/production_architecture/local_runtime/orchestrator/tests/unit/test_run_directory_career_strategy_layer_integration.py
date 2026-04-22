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
    (out / "strategy").mkdir(parents=True)
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0", "stages": []}), encoding="utf-8")
    (out / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    return out


def test_run_directory_reports_missing_career_strategy_evidence_refs(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    payload = {
        "schema": "sde.career_strategy_layer.v1",
        "schema_version": "1.0",
        "run_id": "rid-1",
        "mode": "guarded_pipeline",
        "status": "watchlist",
        "focus": "stabilization",
        "horizon": "next_cycle",
        "strategy": {
            "career_signal_score": 0.6,
            "readiness_score": 0.6,
            "risk_score": 0.4,
            "priority": "stabilize",
            "recommended_actions": ["close_review_blockers"],
        },
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "promotion_package_ref": "lifecycle/promotion_package.json",
            "career_strategy_ref": "strategy/career_strategy_layer.json",
        },
    }
    (out / "strategy" / "career_strategy_layer.json").write_text(json.dumps(payload), encoding="utf-8")
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
        "career_strategy_layer_contract:career_strategy_layer_evidence_ref:promotion_package_ref_missing"
        in result["errors"]
    )
