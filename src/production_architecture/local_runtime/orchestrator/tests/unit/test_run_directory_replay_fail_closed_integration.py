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
    (out / "replay").mkdir(parents=True)
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0", "stages": []}), encoding="utf-8")
    (out / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    return out


def test_run_directory_reports_missing_replay_fail_closed_artifact(tmp_path: Path, monkeypatch) -> None:
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
    assert "replay_fail_closed_contract:replay_fail_closed_file_missing" in result["errors"]


def test_run_directory_reports_missing_replay_fail_closed_evidence_ref_files(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "replay" / "fail_closed.json").write_text(
        json.dumps(
            {
                "schema": "sde.replay_fail_closed.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "status": "fail",
                "checks": {
                    "replay_manifest_present": False,
                    "trace_rows_present": False,
                    "event_rows_present": False,
                    "chain_root_present": False,
                    "chain_root_matches_trace_hash": False,
                },
                "evidence": {
                    "replay_manifest_ref": "replay_manifest.json",
                    "traces_ref": "traces.jsonl",
                    "run_events_ref": "event_store/run_events.jsonl",
                    "replay_fail_closed_ref": "replay/fail_closed.json",
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
    assert "replay_fail_closed_contract:replay_fail_closed_evidence_ref:replay_manifest_ref_missing" in result["errors"]
