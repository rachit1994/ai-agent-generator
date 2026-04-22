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
    (out / "program").mkdir(parents=True)
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0", "stages": []}), encoding="utf-8")
    (out / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    (out / "program" / "production_readiness.json").write_text(json.dumps({"status": "ready"}), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    return out


def _write_valid_closure_artifact(out: Path) -> None:
    (out / "program" / "closure_security_reliability_scalability_plans.json").write_text(
        json.dumps(
            {
                "schema": "sde.closure_security_reliability_scalability_plans.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "baseline",
                "status": "not_ready",
                "plans": {
                    "closure": {"status": "blocked", "ok": False},
                    "security": {"status": "blocked", "ok": False},
                    "reliability": {
                        "status": "blocked",
                        "ok": False,
                        "metrics": {"pass_rate": 0.0, "reliability": 0.0, "retry_frequency": 1.0},
                    },
                    "scalability": {"status": "blocked", "ok": False},
                },
                "summary": {"plans_ready": 0, "plans_total": 4, "overall_score": 0.0},
                "evidence": {
                    "summary_ref": "summary.json",
                    "review_ref": "review.json",
                    "readiness_ref": "program/production_readiness.json",
                    "closure_plan_ref": "program/closure_security_reliability_scalability_plans.json",
                },
            }
        ),
        encoding="utf-8",
    )


def test_run_directory_reports_missing_closure_summary_ref_file(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    _write_valid_closure_artifact(out)
    (out / "summary.json").unlink()
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
        "closure_security_reliability_scalability_plans_contract:"
        "closure_security_reliability_scalability_plans_evidence_ref:summary_ref_missing"
    ) in result["errors"]


def test_run_directory_reports_missing_closure_review_ref_file(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    _write_valid_closure_artifact(out)
    (out / "review.json").unlink()
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
        "closure_security_reliability_scalability_plans_contract:"
        "closure_security_reliability_scalability_plans_evidence_ref:review_ref_missing"
    ) in result["errors"]


def test_run_directory_reports_missing_closure_readiness_ref_file(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    _write_valid_closure_artifact(out)
    (out / "program" / "production_readiness.json").unlink()
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
        "closure_security_reliability_scalability_plans_contract:"
        "closure_security_reliability_scalability_plans_evidence_ref:readiness_ref_missing"
    ) in result["errors"]
