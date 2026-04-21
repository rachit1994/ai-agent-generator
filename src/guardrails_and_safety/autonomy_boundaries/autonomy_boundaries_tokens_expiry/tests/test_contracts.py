from __future__ import annotations

from datetime import datetime, timezone

from guardrails_and_safety.autonomy_boundaries.autonomy_boundaries_tokens_expiry.contracts import (
    validate_high_risk_approval_token_row,
    validate_stage_budget_row,
    validate_token_context_payload,
)


def _now() -> datetime:
    return datetime(2030, 1, 1, 0, 0, tzinfo=timezone.utc)


def test_stage_budget_rejects_bool_numeric_fields() -> None:
    errs = validate_stage_budget_row(
        {
            "budget_status": "ok",
            "input_token_budget": True,
            "output_token_budget": 5,
            "planned_input_tokens": 1,
            "actual_input_tokens": 1,
            "actual_output_tokens": 1,
        }
    )
    assert "token_context_stage_int:input_token_budget" in errs


def test_stage_budget_rejects_invalid_budget_status() -> None:
    errs = validate_stage_budget_row(
        {
            "budget_status": "invalid",
            "input_token_budget": 10,
            "output_token_budget": 10,
            "planned_input_tokens": 1,
            "actual_input_tokens": 1,
            "actual_output_tokens": 1,
        }
    )
    assert "token_context_stage_budget_status" in errs


def test_token_context_rejects_expiry_before_anchor() -> None:
    errs = validate_token_context_payload(
        {
            "run_id": "rid",
            "stages": [],
            "context_ttl_seconds": 60,
            "autonomy_anchor_at": "2030-01-01T00:01:00+00:00",
            "context_expires_at": "2030-01-01T00:00:00+00:00",
        },
        now_utc=_now(),
    )
    assert "token_context_expiry_before_anchor" in errs


def test_high_risk_row_rejects_whitespace_token_id() -> None:
    errs = validate_high_risk_approval_token_row(
        {"risk": "high", "approval_token_id": "   ", "approval_token_expires_at": "2030-01-01T01:00:00+00:00"},
        now_utc=_now(),
    )
    assert "approval_token_id" in errs
