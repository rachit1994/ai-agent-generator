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
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    return out


def test_run_directory_reports_missing_readiness_evidence_refs(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "program" / "production_readiness.json").write_text(
        json.dumps(
            {
                "schema": "sde.production_readiness_program.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "baseline",
                "status": "not_ready",
                "checks": {
                    "run_manifest_valid": False,
                    "review_gate_passed": False,
                    "hard_stops_passed": False,
                    "balanced_gates_ready": False,
                    "required_artifacts_present": False,
                    "policy_bundle_valid": False,
                },
                "evidence": {
                    "summary_ref": "summary.json",
                    "review_ref": "review.json",
                    "readiness_ref": "program/production_readiness.json",
                },
            }
        ),
        encoding="utf-8",
    )
    (out / "summary.json").unlink()
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
        "production_readiness_program_contract:"
        "production_readiness_program_evidence_ref:summary_ref_missing"
    ) in result["errors"]
    assert (
        "production_readiness_program_contract:"
        "production_readiness_program_evidence_ref:review_ref_missing"
    ) in result["errors"]
