from __future__ import annotations

import json
from pathlib import Path

from orchestrator.api import intake_merge_anchor_present
from orchestrator.api.project_intake_util import intake_doc_review_errors


def test_intake_merge_anchor_false_without_intake_dir(tmp_path: Path) -> None:
    assert intake_merge_anchor_present(tmp_path) is False


def test_intake_merge_anchor_true_with_discovery(tmp_path: Path) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()
    (intake / "discovery.json").write_text(json.dumps({"goal_excerpt": "g"}), encoding="utf-8")
    assert intake_merge_anchor_present(tmp_path) is True


def test_intake_merge_anchor_true_with_doc_review_only(tmp_path: Path) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()
    (intake / "doc_review.json").write_text(json.dumps({"passed": True, "findings": []}), encoding="utf-8")
    assert intake_merge_anchor_present(tmp_path) is True


def test_intake_merge_anchor_false_workbook_only(tmp_path: Path) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()
    (intake / "question_workbook.jsonl").write_text("{}\n", encoding="utf-8")
    assert intake_merge_anchor_present(tmp_path) is False


def test_intake_merge_anchor_false_with_invalid_doc_review_shape(tmp_path: Path) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()
    (intake / "doc_review.json").write_text(
        json.dumps({"passed": "yes", "findings": []}),
        encoding="utf-8",
    )
    assert intake_merge_anchor_present(tmp_path) is False


def test_intake_merge_anchor_false_with_discovery_missing_goal_excerpt(tmp_path: Path) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()
    (intake / "discovery.json").write_text(json.dumps({"constraints": []}), encoding="utf-8")
    assert intake_merge_anchor_present(tmp_path) is False


def test_intake_doc_review_errors_for_bad_shape(tmp_path: Path) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()
    (intake / "doc_review.json").write_text(json.dumps({"passed": "x", "findings": "y"}), encoding="utf-8")
    errs = intake_doc_review_errors(tmp_path)
    assert "doc_review_passed_not_bool" in errs
    assert "doc_review_findings_bad_type" in errs
