"""Positive-path tests for review_gating evaluator authority."""

from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.review_gating_evaluator_authority.review_gating.review import (
    build_review,
    is_evaluator_pass_eligible,
    validate_review_payload,
)
from guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory import (
    validate_execution_run_directory,
)


def _valid_review_payload() -> dict[str, object]:
    return {
        "schema_version": "1.1",
        "run_id": "rid-1",
        "status": "completed_review_pass",
        "reasons": [],
        "required_fixes": [],
        "gate_snapshot": {},
        "artifact_manifest": [],
        "review_findings": [{"severity": "info", "code": "ok", "message": "m", "evidence_ref": "e"}],
        "completed_at": "2026-01-01T00:00:00Z",
    }


def test_validate_review_payload_accepts_valid_payload() -> None:
    errors = validate_review_payload(_valid_review_payload())
    assert errors == []


def test_is_evaluator_pass_eligible_true_without_blockers() -> None:
    assert is_evaluator_pass_eligible(_valid_review_payload()) is True


def test_build_review_contains_required_schema_and_findings(tmp_path: Path) -> None:
    out = tmp_path / "run"
    out.mkdir()
    (out / "static_gates_report.json").write_text(
        json.dumps({"schema_version": "1.0", "passed_all": True, "blockers": [], "warnings": []}),
        encoding="utf-8",
    )
    review = build_review(
        run_id="rid-build",
        mode="baseline",
        parsed={"answer": "ok", "checks": [{"name": "c", "passed": True}], "refusal": None},
        output_dir=out,
        events=[{"stage": "finalize", "score": {"passed": True}}],
        run_status="ok",
    )
    assert review["schema_version"] == "1.1"
    assert review["status"] == "completed_review_pass"
    assert "review_findings" in review
    assert isinstance(review["review_findings"], list)


def test_validate_execution_run_directory_passes_with_eligible_review(
    tmp_path: Path, monkeypatch,
) -> None:
    out = tmp_path / "run"
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
    (out / "review.json").write_text(json.dumps(_valid_review_payload()), encoding="utf-8")
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
    assert "review_pass_not_evaluator_eligible" not in result["errors"]
