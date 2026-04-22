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
    (out / "memory").mkdir(parents=True)
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0", "stages": []}), encoding="utf-8")
    (out / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    return out


def test_run_directory_reports_missing_memory_architecture_evidence_refs(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "memory" / "quality_metrics.json").write_text("{}", encoding="utf-8")
    (out / "memory" / "quarantine.jsonl").write_text("", encoding="utf-8")
    (out / "memory" / "runtime_memory_architecture.json").write_text(
        json.dumps(
            {
                "schema": "sde.memory_architecture_in_runtime.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "status": "missing",
                "metrics": {
                    "retrieval_coverage": 0.0,
                    "quality_signal": 0.0,
                    "quarantine_rate": 0.0,
                    "health_score": 0.0,
                },
                "evidence": {
                    "retrieval_bundle_ref": "memory/retrieval_bundle.json",
                    "quality_metrics_ref": "memory/quality_metrics.json",
                    "quarantine_ref": "memory/quarantine.jsonl",
                    "memory_architecture_ref": "memory/runtime_memory_architecture.json",
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
        "memory_architecture_in_runtime_contract:"
        "memory_architecture_in_runtime_evidence_ref:retrieval_bundle_ref_missing"
    ) in result["errors"]
