"""§11 review gating: severity-tagged ``review_findings`` in ``review.json`` + HS15 honesty."""

from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.review_gating import review as review_mod
from guardrails_and_safety.review_gating.review import build_review
from guardrails_and_safety.risk_budgets.hard_stops_guarded import _hs15_terminal_honesty


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
