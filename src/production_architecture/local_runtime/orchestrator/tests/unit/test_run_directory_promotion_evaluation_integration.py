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


def test_run_directory_reports_missing_promotion_evaluation_evidence_ref_files(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "learning" / "promotion_evaluation.json").write_text(
        json.dumps(
            {
                "schema": "sde.promotion_evaluation.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "decision": "hold",
                "confidence": 0.0,
                "signals": {
                    "promotion_readiness_score": 0.0,
                    "finalize_pass_rate": 0.0,
                    "review_pass": False,
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
        "promotion_evaluation_contract:promotion_evaluation_evidence_ref:promotion_package_ref_missing"
        in result["errors"]
    )


def test_run_directory_reports_promotion_evaluation_review_pass_mismatch(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "lifecycle").mkdir(parents=True, exist_ok=True)
    (out / "lifecycle" / "promotion_package.json").write_text("{}", encoding="utf-8")
    (out / "review.json").write_text(
        json.dumps({**_valid_review(), "status": "completed_review_fail"}),
        encoding="utf-8",
    )
    (out / "learning" / "promotion_evaluation.json").write_text(
        json.dumps(
            {
                "schema": "sde.promotion_evaluation.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "decision": "promote",
                "confidence": 0.88,
                "signals": {
                    "promotion_readiness_score": 0.8,
                    "finalize_pass_rate": 1.0,
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
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "promotion_evaluation_contract:promotion_evaluation_review_pass_mismatch" in result["errors"]
