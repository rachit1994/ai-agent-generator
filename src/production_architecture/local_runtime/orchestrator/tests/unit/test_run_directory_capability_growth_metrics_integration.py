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
    (out / "summary.json").write_text(
        json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8"
    )
    (out / "token_context.json").write_text(
        json.dumps({"schema_version": "1.0", "stages": []}), encoding="utf-8"
    )
    (out / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    return out


def test_run_directory_reports_missing_capability_growth_evidence_refs(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "learning" / "capability_growth_metrics.json").write_text(
        json.dumps(
            {
                "schema": "sde.capability_growth_metrics.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "metrics": {
                    "capability_growth_rate": 0.5,
                    "capability_stability_rate": 0.5,
                    "promotion_readiness_delta": 0.0,
                    "growth_confidence": 0.5,
                },
                "evidence": {
                    "traces_ref": "traces-missing.jsonl",
                    "skill_nodes_ref": "capability/skill_nodes.json",
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
        "capability_growth_metrics_contract:"
        "capability_growth_metrics_evidence_ref:traces_ref_missing"
        in result["errors"]
    )
    assert (
        "capability_growth_metrics_contract:"
        "capability_growth_metrics_evidence_ref:skill_nodes_ref_missing"
        in result["errors"]
    )
