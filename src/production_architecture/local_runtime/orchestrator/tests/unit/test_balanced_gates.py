from __future__ import annotations

from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.balanced_gates import (
    compute_balanced_gates,
    validation_ready,
)


def test_compute_balanced_gates_fails_closed_for_malformed_reliability() -> None:
    balanced = compute_balanced_gates(
        {"reliability": "not-a-number"},
        [{"id": "HS01", "passed": True}],
        review_status="completed_review_pass",
        manifest_complete=True,
    )
    assert balanced["reliability"] == 0
    assert balanced["delivery"] == 100
    assert balanced["governance"] == 100
    assert balanced["composite"] == 67


def test_validation_ready_fails_closed_for_missing_or_malformed_scores() -> None:
    assert validation_ready({"hard_stops": [{"passed": True}]}) is False
    assert validation_ready(
        {
            "reliability": "85",
            "delivery": "85",
            "governance": "bad",
            "composite": "90",
            "hard_stops": [{"passed": True}],
        }
    ) is False
    assert validation_ready(
        {
            "reliability": "90",
            "delivery": "90",
            "governance": "90",
            "composite": "90",
            "hard_stops": [{"passed": True}],
        }
    ) is True
