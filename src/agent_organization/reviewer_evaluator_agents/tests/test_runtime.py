from __future__ import annotations

import json
from pathlib import Path

from agent_organization.reviewer_evaluator_agents import (
    build_reviewer_evaluator_findings,
    evaluate_review_contract,
    validate_reviewer_evaluator_review,
)


def test_build_reviewer_evaluator_findings_includes_terminal_and_manifest(tmp_path: Path) -> None:
    out = tmp_path / "run"
    out.mkdir()
    (out / "static_gates_report.json").write_text(
        json.dumps({"schema_version": "1.0", "passed_all": True, "blockers": [], "warnings": []}),
        encoding="utf-8",
    )
    manifest = [{"path": "review.json", "present": False}]
    findings = build_reviewer_evaluator_findings(
        output_dir=out,
        manifest=manifest,
        status="completed_review_fail",
        reasons=["verifier_or_checks_failed"],
    )
    codes = {f["code"] for f in findings}
    assert "artifact_manifest_missing" in codes
    assert "verifier_or_checks_failed" in codes


def test_validate_reviewer_evaluator_review_rejects_pass_with_blocker() -> None:
    review = {
        "schema_version": "1.1",
        "run_id": "rid-1",
        "status": "completed_review_pass",
        "reasons": [],
        "required_fixes": [],
        "gate_snapshot": {},
        "artifact_manifest": [],
        "review_findings": [
            {"severity": "blocker", "code": "x", "message": "m", "evidence_ref": "review.json"}
        ],
        "completed_at": "2026-01-01T00:00:00Z",
    }
    errors = validate_reviewer_evaluator_review(review)
    assert "review_pass_not_evaluator_eligible" in errors
    contract = evaluate_review_contract(review)
    assert contract["evaluator_eligible"] is False
    assert contract["strict_ok"] is False


def test_evaluate_review_contract_fails_closed_when_pass_payload_is_contract_invalid() -> None:
    review = {
        "schema_version": "1.1",
        "status": "completed_review_pass",
        "reasons": [],
        "required_fixes": [],
        "gate_snapshot": {},
        "artifact_manifest": [],
        "review_findings": [{"severity": "info", "code": "ok", "message": "m", "evidence_ref": "e"}],
        "completed_at": "2026-01-01T00:00:00Z",
    }
    contract = evaluate_review_contract(review)
    assert "missing_review_key:run_id" in contract["errors"]
    assert contract["evaluator_eligible"] is False
    assert contract["strict_ok"] is False


def test_evaluate_review_contract_rejects_malformed_finding_fields() -> None:
    review = {
        "schema_version": "1.1",
        "run_id": "rid-1",
        "status": "completed_review_pass",
        "reasons": [],
        "required_fixes": [],
        "gate_snapshot": {},
        "artifact_manifest": [],
        "review_findings": [{"severity": "info", "code": "ok", "message": "m", "evidence_ref": 123}],
        "completed_at": "2026-01-01T00:00:00Z",
    }
    contract = evaluate_review_contract(review)
    assert "review_finding_invalid_field:0:evidence_ref" in contract["errors"]
    assert contract["evaluator_eligible"] is False
    assert contract["strict_ok"] is False


def test_validate_reviewer_evaluator_review_rejects_blank_run_id() -> None:
    review = {
        "schema_version": "1.1",
        "run_id": "   ",
        "status": "completed_review_pass",
        "reasons": [],
        "required_fixes": [],
        "gate_snapshot": {},
        "artifact_manifest": [],
        "review_findings": [{"severity": "info", "code": "ok", "message": "m", "evidence_ref": "e"}],
        "completed_at": "2026-01-01T00:00:00Z",
    }
    errors = validate_reviewer_evaluator_review(review)
    assert "invalid_review_run_id" in errors
