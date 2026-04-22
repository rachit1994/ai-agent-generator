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


def test_run_directory_surfaces_invalid_dual_control_contract(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "program" / "dual_control_runtime.json").write_text(json.dumps({"schema": "bad"}), encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "dual_control_contract:dual_control_schema" in result["errors"]


def test_run_directory_surfaces_malformed_dual_control_json(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "program" / "dual_control_runtime.json").write_text("{bad", encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "dual_control_contract:dual_control_json" in result["errors"]


def test_run_directory_reports_missing_dual_control_evidence_refs(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    runtime = {
        "schema": "sde.dual_control.v1",
        "schema_version": "1.0",
        "run_id": "rid-1",
        "status": "validated",
        "metrics": {
            "doc_review_passed": True,
            "dual_required": False,
            "ack_present": False,
            "ack_valid": False,
            "distinct_actors": False,
        },
        "evidence": {
            "doc_review_ref": "program/doc_review.json",
            "dual_control_ack_ref": "program/dual_control_ack.json",
            "dual_control_runtime_ref": "program/dual_control_runtime.json",
        },
    }
    (out / "program" / "dual_control_runtime.json").write_text(json.dumps(runtime), encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "dual_control_contract:dual_control_evidence_ref:doc_review_ref_missing" in result["errors"]
    assert "dual_control_contract:dual_control_evidence_ref:dual_control_ack_ref_missing" in result["errors"]
