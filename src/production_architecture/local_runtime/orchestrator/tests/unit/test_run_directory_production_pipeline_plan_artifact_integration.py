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


def test_run_directory_reports_missing_production_pipeline_plan_artifact_evidence_refs(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    payload = {
        "schema": "sde.production_pipeline_plan_artifact.v1",
        "schema_version": "1.0",
        "run_id": "rid-1",
        "mode": "guarded_pipeline",
        "status": "partial",
        "checks": {
            "project_plan_present": False,
            "progress_present": True,
            "work_batch_present": True,
            "discovery_present": True,
            "verification_bundle_present": True,
        },
        "metrics": {"step_count": 0, "checked_program_artifacts": 5},
        "evidence": {
            "project_plan_ref": "program/project_plan.json",
            "progress_ref": "program/progress.json",
            "work_batch_ref": "program/work_batch.json",
            "discovery_ref": "program/discovery.json",
            "verification_bundle_ref": "program/verification_bundle.json",
            "production_pipeline_plan_artifact_ref": "program/production_pipeline_plan_artifact.json",
        },
    }
    (out / "program" / "production_pipeline_plan_artifact.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )
    (out / "program" / "progress.json").write_text("{}", encoding="utf-8")
    (out / "program" / "work_batch.json").write_text("{}", encoding="utf-8")
    (out / "program" / "discovery.json").write_text("{}", encoding="utf-8")
    (out / "program" / "verification_bundle.json").write_text("{}", encoding="utf-8")
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
        "production_pipeline_plan_artifact_contract:"
        "production_pipeline_plan_artifact_evidence_ref:project_plan_ref_missing"
        in result["errors"]
    )
