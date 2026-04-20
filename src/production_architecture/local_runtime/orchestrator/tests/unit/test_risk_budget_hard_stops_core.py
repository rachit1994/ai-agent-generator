from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops import evaluate_hard_stops


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


def _hs(hard_stops: list[dict[str, object]], hs_id: str) -> bool:
    row = next(item for item in hard_stops if item["id"] == hs_id)
    return bool(row["passed"])


def test_hs01_fails_for_semantically_invalid_review_payload(tmp_path: Path) -> None:
    review = _valid_review()
    review["status"] = "unknown"
    (tmp_path / "review.json").write_text(json.dumps(review), encoding="utf-8")
    hard_stops = evaluate_hard_stops(tmp_path, [], {"schema_version": "1.0", "stages": []}, run_status="ok", mode="baseline")
    assert _hs(hard_stops, "HS01") is False


def test_hs03_fails_when_truncation_row_missing_provenance_id(tmp_path: Path) -> None:
    (tmp_path / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    token_context = {
        "schema_version": "1.0",
        "stages": [],
        "truncation_events": [{"bytes": 10}],
        "reductions": [{"provenance_id": "p1"}],
    }
    hard_stops = evaluate_hard_stops(tmp_path, [], token_context, run_status="ok", mode="baseline")
    assert _hs(hard_stops, "HS03") is False


def test_hs06_fails_closed_for_non_numeric_budget_values(tmp_path: Path) -> None:
    (tmp_path / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    token_context = {
        "schema_version": "1.0",
        "stages": [
            {
                "budget_status": "ok",
                "actual_input_tokens": "12",
                "input_token_budget": "n/a",
                "actual_output_tokens": 1,
                "output_token_budget": 2,
            }
        ],
    }
    hard_stops = evaluate_hard_stops(tmp_path, [], token_context, run_status="ok", mode="baseline")
    assert _hs(hard_stops, "HS06") is False


def test_hs04_fails_closed_when_static_gates_passed_all_is_not_bool(tmp_path: Path) -> None:
    (tmp_path / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    (tmp_path / "static_gates_report.json").write_text(
        json.dumps({"schema_version": "1.0", "passed_all": "false"}),
        encoding="utf-8",
    )
    hard_stops = evaluate_hard_stops(tmp_path, [], {"schema_version": "1.0", "stages": []}, run_status="ok", mode="baseline")
    assert _hs(hard_stops, "HS04") is False
