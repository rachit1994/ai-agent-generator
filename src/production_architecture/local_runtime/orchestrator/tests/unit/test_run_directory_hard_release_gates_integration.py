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


def test_run_directory_reports_missing_hard_release_gates_evidence_refs(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "learning" / "hard_release_gates.json").write_text(
        json.dumps(
            {
                "schema": "sde.hard_release_gates.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "baseline",
                "overall_pass": False,
                "validation_ready": False,
                "gates": {
                    "reliability_gate": False,
                    "delivery_gate": False,
                    "governance_gate": False,
                    "composite_gate": False,
                },
                "failed_hard_stop_ids": [],
                "scores": {
                    "reliability": 0.0,
                    "delivery": 0.0,
                    "governance": 0.0,
                    "composite": 0.0,
                },
                "evidence": {
                    "summary_ref": "summary.json",
                    "traces_ref": "traces.jsonl",
                    "hard_release_gates_ref": "learning/hard_release_gates.json",
                },
            }
        ),
        encoding="utf-8",
    )
    (out / "summary.json").unlink()
    (out / "traces.jsonl").unlink()
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "hard_release_gates_contract:hard_release_gates_evidence_ref:summary_ref_missing" in result["errors"]
    assert "hard_release_gates_contract:hard_release_gates_evidence_ref:traces_ref_missing" in result["errors"]
