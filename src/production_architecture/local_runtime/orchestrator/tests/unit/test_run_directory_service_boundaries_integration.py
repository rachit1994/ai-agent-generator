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
    return out


def _write_valid_service_boundaries_artifact(out: Path) -> None:
    (out / "strategy" / "service_boundaries.json").write_text(
        json.dumps(
            {
                "schema": "sde.service_boundaries.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "baseline",
                "status": "boundary_violation",
                "violations": [{"service": "event_store", "missing_path": "event_store/run_events.jsonl"}],
                "services": {
                    "orchestrator": {
                        "owned_paths": ["traces.jsonl", "orchestration.jsonl", "summary.json", "review.json"],
                        "present_count": 4,
                        "required_count": 4,
                        "coverage": 1.0,
                    },
                    "event_store": {
                        "owned_paths": [
                            "event_store/run_events.jsonl",
                            "replay_manifest.json",
                            "kill_switch_state.json",
                        ],
                        "present_count": 0,
                        "required_count": 3,
                        "coverage": 0.0,
                    },
                    "memory_system": {
                        "owned_paths": [
                            "memory/retrieval_bundle.json",
                            "memory/quarantine.jsonl",
                            "memory/quality_metrics.json",
                            "capability/skill_nodes.json",
                        ],
                        "present_count": 0,
                        "required_count": 4,
                        "coverage": 0.0,
                    },
                    "learning_service": {
                        "owned_paths": [
                            "learning/reflection_bundle.json",
                            "learning/canary_report.json",
                            "learning/transfer_learning_metrics.json",
                            "learning/capability_growth_metrics.json",
                            "learning/extended_binary_gates.json",
                        ],
                        "present_count": 0,
                        "required_count": 5,
                        "coverage": 0.0,
                    },
                },
                "evidence": {
                    "review_ref": "review.json",
                    "boundaries_ref": "strategy/service_boundaries.json",
                },
            }
        ),
        encoding="utf-8",
    )


def test_run_directory_reports_missing_service_boundaries_review_ref_file(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    _write_valid_service_boundaries_artifact(out)
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
    assert "service_boundaries_contract:service_boundaries_evidence_ref:review_ref_missing" in result["errors"]

