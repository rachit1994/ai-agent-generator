"""Negative-path tests for review_gating evaluator authority."""

from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.review_gating_evaluator_authority.review_gating.review import (
    is_evaluator_pass_eligible,
    validate_review_payload,
)
from guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory import (
    validate_execution_run_directory,
)


def _base_review() -> dict[str, object]:
    return {
        "schema_version": "1.1",
        "run_id": "rid-1",
        "status": "completed_review_pass",
        "reasons": [],
        "required_fixes": [],
        "gate_snapshot": {},
        "artifact_manifest": [],
        "review_findings": [{"severity": "warn", "code": "w", "message": "m", "evidence_ref": "e"}],
        "completed_at": "2026-01-01T00:00:00Z",
    }


def test_validate_review_payload_rejects_missing_required_key() -> None:
    review = _base_review()
    del review["run_id"]
    errors = validate_review_payload(review)
    assert "missing_review_key:run_id" in errors


def test_validate_review_payload_rejects_invalid_severity() -> None:
    review = _base_review()
    review["review_findings"] = [{"severity": "fatal", "code": "x", "message": "m", "evidence_ref": "e"}]
    errors = validate_review_payload(review)
    assert any(err.startswith("review_finding_invalid_severity:") for err in errors)


def test_validate_review_payload_rejects_invalid_status() -> None:
    review = _base_review()
    review["status"] = "unknown"
    errors = validate_review_payload(review)
    assert "invalid_review_status" in errors


def test_validate_review_payload_rejects_non_list_findings() -> None:
    review = _base_review()
    review["review_findings"] = {"severity": "warn"}
    errors = validate_review_payload(review)
    assert "review_findings_not_list" in errors


def test_validate_review_payload_rejects_non_object_finding() -> None:
    review = _base_review()
    review["review_findings"] = ["bad"]
    errors = validate_review_payload(review)
    assert any(err.startswith("review_finding_not_object:") for err in errors)


def test_validate_review_payload_rejects_missing_finding_key() -> None:
    review = _base_review()
    review["review_findings"] = [{"severity": "warn", "code": "x", "message": "m"}]
    errors = validate_review_payload(review)
    assert any(err.startswith("review_finding_missing_key:") for err in errors)


def test_is_evaluator_pass_eligible_false_when_blocker_present() -> None:
    review = _base_review()
    review["review_findings"] = [{"severity": "blocker", "code": "x", "message": "m", "evidence_ref": "e"}]
    assert is_evaluator_pass_eligible(review) is False


def test_is_evaluator_pass_eligible_false_when_status_not_pass() -> None:
    review = _base_review()
    review["status"] = "completed_review_fail"
    assert is_evaluator_pass_eligible(review) is False


def test_is_evaluator_pass_eligible_false_when_findings_not_list() -> None:
    review = _base_review()
    review["review_findings"] = {"severity": "warn"}
    assert is_evaluator_pass_eligible(review) is False


def test_is_evaluator_pass_eligible_false_when_finding_is_not_object() -> None:
    review = _base_review()
    review["review_findings"] = ["bad"]
    assert is_evaluator_pass_eligible(review) is False


def test_is_evaluator_pass_eligible_false_when_pass_contract_is_invalid() -> None:
    review = _base_review()
    del review["run_id"]
    assert is_evaluator_pass_eligible(review) is False


def test_validate_execution_run_directory_flags_review_pass_not_eligible(
    tmp_path: Path, monkeypatch,
) -> None:
    out = tmp_path / "run"
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
    review = _base_review()
    review["review_findings"] = [{"severity": "blocker", "code": "x", "message": "m", "evidence_ref": "e"}]
    (out / "review.json").write_text(json.dumps(review), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")

    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )

    result = validate_execution_run_directory(out, mode="baseline")
    assert "review_pass_not_evaluator_eligible" in result["errors"]


def test_validate_execution_run_directory_flags_malformed_review_json(tmp_path: Path) -> None:
    out = tmp_path / "bad-review"
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
    (out / "review.json").write_text("{", encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")

    result = validate_execution_run_directory(out, mode="baseline")
    assert "invalid_json:review.json" in result["errors"]
