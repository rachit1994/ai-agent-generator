"""§11 dual control: HS08 + ``program/dual_control_ack.json`` (two distinct actor ids)."""

from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops_guarded import evaluate_guarded_hard_stops


def _program_dirs(tmp_path: Path) -> None:
    (tmp_path / "program").mkdir(parents=True)


def _minimal_guarded_doc_review(tmp_path: Path, *, dual_required: bool) -> None:
    _program_dirs(tmp_path)
    (tmp_path / "program" / "project_plan.json").write_text(json.dumps({"schema_version": "1.0", "steps": []}), encoding="utf-8")
    doc: dict[str, object] = {
        "schema_version": "1.0",
        "passed": True,
        "findings": [],
    }
    if dual_required:
        doc["dual_control"] = {"required": True}
    (tmp_path / "program" / "doc_review.json").write_text(json.dumps(doc), encoding="utf-8")


def test_hs08_passes_without_ack_when_dual_not_required(tmp_path: Path) -> None:
    _minimal_guarded_doc_review(tmp_path, dual_required=False)
    hs = {h["id"]: h["passed"] for h in evaluate_guarded_hard_stops(tmp_path, [])}
    assert hs["HS08"] is True


def test_hs08_fails_when_dual_required_but_ack_missing(tmp_path: Path) -> None:
    _minimal_guarded_doc_review(tmp_path, dual_required=True)
    hs = {h["id"]: h["passed"] for h in evaluate_guarded_hard_stops(tmp_path, [])}
    assert hs["HS08"] is False


def test_hs08_fails_when_doc_review_not_passed(tmp_path: Path) -> None:
    _program_dirs(tmp_path)
    (tmp_path / "program" / "project_plan.json").write_text(json.dumps({"schema_version": "1.0", "steps": []}), encoding="utf-8")
    (tmp_path / "program" / "doc_review.json").write_text(
        json.dumps({"schema_version": "1.0", "passed": False}),
        encoding="utf-8",
    )
    hs = {h["id"]: h["passed"] for h in evaluate_guarded_hard_stops(tmp_path, [])}
    assert hs["HS08"] is False


def test_hs08_fails_when_dual_control_block_is_malformed(tmp_path: Path) -> None:
    _program_dirs(tmp_path)
    (tmp_path / "program" / "project_plan.json").write_text(json.dumps({"schema_version": "1.0", "steps": []}), encoding="utf-8")
    (tmp_path / "program" / "doc_review.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "passed": True,
                "dual_control": {"required": "yes"},
            }
        ),
        encoding="utf-8",
    )
    hs = {h["id"]: h["passed"] for h in evaluate_guarded_hard_stops(tmp_path, [])}
    assert hs["HS08"] is False


def test_hs08_fails_when_ack_present_but_same_actor_ids(tmp_path: Path) -> None:
    _minimal_guarded_doc_review(tmp_path, dual_required=False)
    (tmp_path / "program" / "dual_control_ack.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "implementor_actor_id": "alice",
                "independent_reviewer_actor_id": "alice",
                "acknowledged_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    hs = {h["id"]: h["passed"] for h in evaluate_guarded_hard_stops(tmp_path, [])}
    assert hs["HS08"] is False


def test_hs08_passes_dual_required_with_distinct_ack(tmp_path: Path) -> None:
    _minimal_guarded_doc_review(tmp_path, dual_required=True)
    (tmp_path / "program" / "dual_control_ack.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "implementor_actor_id": "alice",
                "independent_reviewer_actor_id": "bob",
                "acknowledged_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    hs = {h["id"]: h["passed"] for h in evaluate_guarded_hard_stops(tmp_path, [])}
    assert hs["HS08"] is True


def test_hs08_passes_when_optional_ack_present_and_valid(tmp_path: Path) -> None:
    _minimal_guarded_doc_review(tmp_path, dual_required=False)
    (tmp_path / "program" / "dual_control_ack.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "implementor_actor_id": "alice",
                "independent_reviewer_actor_id": "bob",
                "acknowledged_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    hs = {h["id"]: h["passed"] for h in evaluate_guarded_hard_stops(tmp_path, [])}
    assert hs["HS08"] is True


def test_hs08_fails_when_ack_schema_invalid(tmp_path: Path) -> None:
    _minimal_guarded_doc_review(tmp_path, dual_required=True)
    (tmp_path / "program" / "dual_control_ack.json").write_text(
        json.dumps(
            {
                "schema_version": "2.0",
                "implementor_actor_id": "alice",
                "independent_reviewer_actor_id": "bob",
                "acknowledged_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    hs = {h["id"]: h["passed"] for h in evaluate_guarded_hard_stops(tmp_path, [])}
    assert hs["HS08"] is False


def test_hs08_fails_when_ack_actor_not_string(tmp_path: Path) -> None:
    _minimal_guarded_doc_review(tmp_path, dual_required=True)
    (tmp_path / "program" / "dual_control_ack.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "implementor_actor_id": "alice",
                "independent_reviewer_actor_id": 7,
                "acknowledged_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    hs = {h["id"]: h["passed"] for h in evaluate_guarded_hard_stops(tmp_path, [])}
    assert hs["HS08"] is False


def test_hs08_fails_when_acknowledged_at_missing(tmp_path: Path) -> None:
    _minimal_guarded_doc_review(tmp_path, dual_required=True)
    (tmp_path / "program" / "dual_control_ack.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "implementor_actor_id": "alice",
                "independent_reviewer_actor_id": "bob",
            }
        ),
        encoding="utf-8",
    )
    hs = {h["id"]: h["passed"] for h in evaluate_guarded_hard_stops(tmp_path, [])}
    assert hs["HS08"] is False
