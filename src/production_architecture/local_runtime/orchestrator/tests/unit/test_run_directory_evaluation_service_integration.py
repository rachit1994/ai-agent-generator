from __future__ import annotations

import json
from pathlib import Path

import pytest

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


def test_run_directory_surfaces_invalid_evaluation_service_contract(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "evaluation").mkdir(parents=True, exist_ok=True)
    (out / "evaluation" / "service_runtime.json").write_text(
        json.dumps({"schema": "bad"}),
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
    assert "evaluation_service_contract:evaluation_service_schema" in result["errors"]


def test_run_directory_reports_missing_evaluation_service_evidence_refs(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "evaluation").mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "sde.evaluation_service.v1",
        "schema_version": "1.0",
        "run_id": "rid-1",
        "status": "degraded",
        "metrics": {
            "has_online_eval": False,
            "has_promotion_eval": False,
            "summary_has_metrics": False,
            "all_checks_passed": False,
        },
        "evidence": {
            "summary_ref": "summary.json",
            "online_eval_ref": "learning/online_evaluation_shadow_canary.json",
            "promotion_eval_ref": "learning/promotion_evaluation.json",
            "evaluation_service_ref": "evaluation/service_runtime.json",
        },
    }
    (out / "evaluation" / "service_runtime.json").write_text(
        json.dumps(payload),
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
        "evaluation_service_contract:evaluation_service_evidence_ref:online_eval_ref_missing"
        in result["errors"]
    )
    assert (
        "evaluation_service_contract:evaluation_service_evidence_ref:promotion_eval_ref_missing"
        in result["errors"]
    )


def test_run_directory_surfaces_unreadable_evaluation_service_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "evaluation").mkdir(parents=True, exist_ok=True)
    runtime_path = out / "evaluation" / "service_runtime.json"
    runtime_path.write_text("{}", encoding="utf-8")
    original_read_text = Path.read_text

    def _patched_read_text(self: Path, encoding: str = "utf-8") -> str:
        if self == runtime_path:
            raise OSError("boom")
        return original_read_text(self, encoding=encoding)

    monkeypatch.setattr(Path, "read_text", _patched_read_text)
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "evaluation_service_contract:evaluation_service_unreadable" in result["errors"]


def test_run_directory_reports_missing_evaluation_service_summary_ref(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "evaluation").mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "sde.evaluation_service.v1",
        "schema_version": "1.0",
        "run_id": "rid-1",
        "status": "degraded",
        "metrics": {
            "has_online_eval": False,
            "has_promotion_eval": False,
            "summary_has_metrics": False,
            "all_checks_passed": False,
        },
        "evidence": {
            "summary_ref": "summary.json",
            "online_eval_ref": "learning/online_evaluation_shadow_canary.json",
            "promotion_eval_ref": "learning/promotion_evaluation.json",
            "evaluation_service_ref": "evaluation/service_runtime.json",
        },
    }
    (out / "evaluation" / "service_runtime.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    (out / "summary.json").unlink()
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
        "evaluation_service_contract:evaluation_service_evidence_ref:summary_ref_missing"
        in result["errors"]
    )
