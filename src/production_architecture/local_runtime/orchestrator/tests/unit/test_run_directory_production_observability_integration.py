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


def test_run_directory_surfaces_invalid_production_observability_status_metrics_mismatch(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "observability").mkdir(parents=True, exist_ok=True)
    (out / "observability" / "production_observability.json").write_text(
        json.dumps(
            {
                "schema": "sde.production_observability.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "baseline",
                "status": "missing",
                "metrics": {
                    "trace_rows": 1,
                    "orchestration_rows": 1,
                    "run_log_lines": 1,
                },
                "evidence": {
                    "traces_ref": "traces.jsonl",
                    "orchestration_ref": "orchestration.jsonl",
                    "run_log_ref": "run.log",
                    "observability_ref": "observability/production_observability.json",
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
    assert "production_observability_contract:production_observability_status_metrics_mismatch" in result["errors"]


def test_run_directory_surfaces_missing_production_observability_evidence_ref_file(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "observability").mkdir(parents=True, exist_ok=True)
    (out / "orchestration.jsonl").write_text('{"stage":"plan"}\n', encoding="utf-8")
    (out / "run.log").write_text("log line\n", encoding="utf-8")
    (out / "observability" / "production_observability.json").write_text(
        json.dumps(
            {
                "schema": "sde.production_observability.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "mode": "baseline",
                "status": "degraded",
                "metrics": {
                    "trace_rows": 0,
                    "orchestration_rows": 1,
                    "run_log_lines": 1,
                },
                "evidence": {
                    "traces_ref": "traces.jsonl",
                    "orchestration_ref": "orchestration.jsonl",
                    "run_log_ref": "run.log",
                    "observability_ref": "observability/production_observability.json",
                },
            }
        ),
        encoding="utf-8",
    )
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
    assert (
        "production_observability_contract:production_observability_evidence_ref:traces_ref_missing"
        in result["errors"]
    )
