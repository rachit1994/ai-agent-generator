from __future__ import annotations

import json
from pathlib import Path

from orchestrator.api import apply_intake_doc_review_result


def test_apply_intake_doc_review_result_review_passed(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    intake = sess / "intake"
    intake.mkdir(parents=True)
    (intake / "doc_review.json").write_text(
        json.dumps({"passed": True, "findings": []}),
        encoding="utf-8",
    )
    out = apply_intake_doc_review_result(sess, max_retries=2)
    assert out["ok"] is True
    assert out["state"] == "review_passed"
    assert (intake / "revise_metrics.jsonl").is_file()
    metrics = (intake / "revise_metrics.jsonl").read_text(encoding="utf-8")
    assert "intake_revise_result" in metrics
    assert "\"status\": \"review_passed\"" in metrics
    st = json.loads((intake / "revise_state.json").read_text(encoding="utf-8"))
    assert st["status"] == "review_passed"


def test_apply_intake_doc_review_result_failed_then_blocked(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    intake = sess / "intake"
    intake.mkdir(parents=True)
    (intake / "doc_review.json").write_text(
        json.dumps({"passed": False, "findings": [{"severity": "high"}]}),
        encoding="utf-8",
    )
    out1 = apply_intake_doc_review_result(sess, max_retries=2)
    assert out1["ok"] is True
    assert out1["state"] == "retry_allowed"
    assert out1["blocked_human"] is False
    assert (intake / "revise_autogen.json").is_file()
    digest = (intake / "research_digest.md").read_text(encoding="utf-8")
    assert "auto-revise attempt 1" in digest
    workbook = (intake / "question_workbook.jsonl").read_text(encoding="utf-8")
    assert "auto-revise-1" in workbook
    out2 = apply_intake_doc_review_result(sess, max_retries=2)
    assert out2["ok"] is True
    assert out2["state"] == "blocked_human"
    assert out2["blocked_human"] is True
    st = json.loads((intake / "revise_state.json").read_text(encoding="utf-8"))
    assert st["status"] == "blocked_human"
    assert st["blocked_reason"] == "doc_review_failed_max_retries"


def test_apply_intake_doc_review_result_invalid_doc_review_rejected(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    intake = sess / "intake"
    intake.mkdir(parents=True)
    (intake / "doc_review.json").write_text(
        json.dumps({"passed": "bad", "findings": "bad"}),
        encoding="utf-8",
    )
    out = apply_intake_doc_review_result(sess)
    assert out["ok"] is False
    assert out["error"] == "invalid_doc_review_json"


def test_apply_intake_doc_review_result_failed_dict_findings_autogen(tmp_path: Path) -> None:
    sess = tmp_path / "s3"
    intake = sess / "intake"
    intake.mkdir(parents=True)
    (intake / "doc_review.json").write_text(
        json.dumps({"passed": False, "findings": {"severity": "medium", "issue": "x"}}),
        encoding="utf-8",
    )
    out = apply_intake_doc_review_result(sess, max_retries=3)
    assert out["ok"] is True
    assert out["state"] == "retry_allowed"
    regen = out.get("auto_regen") or {}
    assert regen.get("ok") is True
    assert regen.get("finding_count") == 1
