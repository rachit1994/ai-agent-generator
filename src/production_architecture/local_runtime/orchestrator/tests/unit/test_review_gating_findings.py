"""§11 review gating: severity-tagged ``review_findings`` in ``review.json`` + HS15 honesty."""

from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.review_gating_evaluator_authority.review_gating import review as review_mod
from guardrails_and_safety.review_gating_evaluator_authority.review_gating.review import build_review
from guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory import (
    validate_execution_run_directory,
)
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops_guarded import _hs15_terminal_honesty


def test_review_findings_include_static_gate_blockers(tmp_path: Path) -> None:
    out = tmp_path / "o"
    out.mkdir()
    (out / "static_gates_report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "passed_all": False,
                "blockers": [{"id": "eval_call", "severity": "blocker", "pattern": "p"}],
                "warnings": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    findings = review_mod._review_findings_from_static_gates(out)
    assert any(f.get("code") == "eval_call" and f.get("severity") == "blocker" for f in findings)


def test_build_review_adds_verifier_blocker_when_checks_fail(tmp_path: Path) -> None:
    out = tmp_path / "o2"
    out.mkdir()
    review = build_review(
        "rid-x",
        "baseline",
        {"answer": "", "checks": [{"name": "c", "passed": False}], "refusal": None},
        out,
        [{"stage": "finalize", "score": {"passed": False}}],
        run_status="ok",
    )
    assert review["status"] == "completed_review_fail"
    assert any(f.get("code") == "verifier_or_checks_failed" for f in review["review_findings"])


def test_hs15_rejects_completed_review_pass_with_blocker_review_findings(tmp_path: Path) -> None:
    out = tmp_path / "r"
    out.mkdir()
    body = {
        "schema_version": "1.1",
        "status": "completed_review_pass",
        "definition_of_done": {"schema_version": "1.0", "checks": [], "all_required_passed": True},
        "review_findings": [
            {"severity": "blocker", "code": "manual", "message": "inconsistent", "evidence_ref": "test"},
        ],
    }
    (out / "review.json").write_text(json.dumps(body), encoding="utf-8")
    assert _hs15_terminal_honesty(out, []) is False


def test_hs15_accepts_completed_review_pass_with_only_warn_findings(tmp_path: Path) -> None:
    out = tmp_path / "r2"
    out.mkdir()
    body = {
        "schema_version": "1.1",
        "status": "completed_review_pass",
        "definition_of_done": {"schema_version": "1.0", "checks": [], "all_required_passed": True},
        "review_findings": [
            {"severity": "warn", "code": "note", "message": "n", "evidence_ref": "x"},
        ],
    }
    (out / "review.json").write_text(json.dumps(body), encoding="utf-8")
    assert _hs15_terminal_honesty(out, []) is True


def test_hs15_rejects_completed_review_pass_when_dod_not_passed(tmp_path: Path) -> None:
    out = tmp_path / "r2b"
    out.mkdir()
    body = {
        "schema_version": "1.1",
        "status": "completed_review_pass",
        "definition_of_done": {"schema_version": "1.0", "checks": [], "all_required_passed": False},
        "review_findings": [],
    }
    (out / "review.json").write_text(json.dumps(body), encoding="utf-8")
    assert _hs15_terminal_honesty(out, []) is False


def test_hs15_rejects_when_step_review_event_fails(tmp_path: Path) -> None:
    out = tmp_path / "r2c"
    out.mkdir()
    body = {
        "schema_version": "1.1",
        "status": "completed_review_pass",
        "definition_of_done": {"schema_version": "1.0", "checks": [], "all_required_passed": True},
        "review_findings": [],
    }
    (out / "review.json").write_text(json.dumps(body), encoding="utf-8")
    events = [{"metadata": {"step_review": "fail"}}]
    assert _hs15_terminal_honesty(out, events) is False


def test_build_review_always_includes_review_findings_list(tmp_path: Path) -> None:
    out = tmp_path / "r3"
    out.mkdir()
    review = build_review(
        "rid-2",
        "baseline",
        {"answer": "x", "checks": [{"name": "c", "passed": True}], "refusal": None},
        out,
        [{"stage": "finalize", "score": {"passed": True}}],
        run_status="ok",
    )
    assert "review_findings" in review
    assert isinstance(review["review_findings"], list)


def test_validate_review_payload_rejects_invalid_finding_severity() -> None:
    review = {
        "schema_version": "1.1",
        "run_id": "rid",
        "status": "completed_review_pass",
        "reasons": [],
        "required_fixes": [],
        "gate_snapshot": {},
        "artifact_manifest": [],
        "review_findings": [{"severity": "fatal", "code": "x", "message": "m", "evidence_ref": "e"}],
        "completed_at": "2026-01-01T00:00:00Z",
    }
    errors = review_mod.validate_review_payload(review)
    assert any(e.startswith("review_finding_invalid_severity:") for e in errors)


def test_run_directory_flags_review_pass_with_blocker_finding(tmp_path: Path) -> None:
    out = tmp_path / "run"
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    (out / "review.json").write_text(
        json.dumps(
            {
                "schema_version": "1.1",
                "run_id": "rid",
                "status": "completed_review_pass",
                "reasons": [],
                "required_fixes": [],
                "gate_snapshot": {},
                "artifact_manifest": [],
                "review_findings": [
                    {"severity": "blocker", "code": "x", "message": "m", "evidence_ref": "e"},
                ],
                "completed_at": "2026-01-01T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "review_pass_not_evaluator_eligible" in result["errors"]


def test_run_directory_flags_review_pass_with_malformed_finding_evidence_ref(tmp_path: Path) -> None:
    out = tmp_path / "run-malformed-review-finding"
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    (out / "review.json").write_text(
        json.dumps(
            {
                "schema_version": "1.1",
                "run_id": "rid",
                "status": "completed_review_pass",
                "reasons": [],
                "required_fixes": [],
                "gate_snapshot": {},
                "artifact_manifest": [],
                "review_findings": [
                    {"severity": "warn", "code": "x", "message": "m", "evidence_ref": 1},
                ],
                "completed_at": "2026-01-01T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "review_finding_invalid_field:0:evidence_ref" in result["errors"]
    assert "review_pass_not_evaluator_eligible" in result["errors"]


def test_run_directory_surfaces_unreadable_review_json(tmp_path: Path, monkeypatch) -> None:
    out = tmp_path / "run-unreadable-review"
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    review_path = out / "review.json"
    review_path.write_text("{}", encoding="utf-8")
    original_read_text = Path.read_text

    def _raise_for_review(self: Path, encoding: str = "utf-8") -> str:
        if self == review_path:
            raise OSError("permission denied")
        return original_read_text(self, encoding=encoding)

    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    monkeypatch.setattr(Path, "read_text", _raise_for_review)
    result = validate_execution_run_directory(out, mode="baseline")
    assert "unreadable:review.json" in result["errors"]
