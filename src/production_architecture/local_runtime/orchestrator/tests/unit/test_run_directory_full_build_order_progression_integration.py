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
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    (out / "run-manifest.json").write_text(
        json.dumps({"schema": "sde.run_manifest.v1", "run_id": "rid-1", "mode": "baseline", "task": "t"}),
        encoding="utf-8",
    )
    (out / "orchestration.jsonl").write_text(
        '{"type":"stage_event","stage":"executor"}\n{"type":"stage_event","stage":"finalize"}\n',
        encoding="utf-8",
    )
    return out


def _write_valid_full_build_order_progression(out: Path) -> None:
    (out / "strategy" / "full_build_order_progression.json").write_text(
        json.dumps(
            {
                "schema": "sde.full_build_order_progression.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "baseline",
                "status": "ordered",
                "stage_sequence": ["executor", "finalize"],
                "expected_order": [
                    "planner_doc",
                    "planner_prompt",
                    "executor",
                    "verifier",
                    "executor_fix",
                    "verifier_fix",
                    "repair",
                    "finalize",
                ],
                "checks": {
                    "all_stages_known": True,
                    "starts_with_allowed_entry_stage": True,
                    "ends_with_finalize": True,
                    "monotonic_progression": True,
                    "required_stages_present": True,
                },
                "summary": {
                    "observed_stage_count": 2,
                    "distinct_stage_count": 2,
                    "required_stage_count": 2,
                    "required_stage_present_count": 2,
                    "order_score": 1.0,
                },
                "violations": [],
                "evidence": {
                    "run_manifest_ref": "run-manifest.json",
                    "orchestration_ref": "orchestration.jsonl",
                    "progression_ref": "strategy/full_build_order_progression.json",
                },
            }
        ),
        encoding="utf-8",
    )


def test_run_directory_reports_missing_full_build_order_orchestration_ref_file(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    _write_valid_full_build_order_progression(out)
    (out / "orchestration.jsonl").unlink()
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
        "full_build_order_progression_contract:full_build_order_progression_evidence_ref:"
        "orchestration_ref_missing"
    ) in result["errors"]
