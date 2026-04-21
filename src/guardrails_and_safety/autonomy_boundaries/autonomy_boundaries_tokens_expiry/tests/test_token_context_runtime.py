from __future__ import annotations

from datetime import datetime, timezone

import pytest

from guardrails_and_safety.autonomy_boundaries.autonomy_boundaries_tokens_expiry.token_context import build_token_context


def test_build_token_context_is_deterministic_with_fixed_clock() -> None:
    now = datetime(2030, 1, 1, 0, 0, tzinfo=timezone.utc)
    events = [{"stage": "s1", "token_input": 1, "token_output": 2, "metadata": {}}]
    first = build_token_context("rid", events, max_tokens=100, context_ttl_seconds=60, now_utc=now)
    second = build_token_context("rid", events, max_tokens=100, context_ttl_seconds=60, now_utc=now)
    assert first == second
    assert first["autonomy_anchor_at"] == "2030-01-01T00:00:00+00:00"
    assert first["context_expires_at"] == "2030-01-01T00:01:00+00:00"


def test_build_token_context_rejects_invalid_max_tokens() -> None:
    with pytest.raises(ValueError, match="max_tokens"):
        build_token_context("rid", [], max_tokens=0)


def test_build_token_context_rejects_invalid_model_context_limit() -> None:
    with pytest.raises(ValueError, match="model_context_limit"):
        build_token_context("rid", [], max_tokens=1, model_context_limit=0)


def test_build_token_context_fail_closes_malformed_token_values() -> None:
    now = datetime(2030, 1, 1, 0, 0, tzinfo=timezone.utc)
    ctx = build_token_context(
        "rid",
        [{"stage": "s1", "token_input": "x", "token_output": 1, "metadata": {}}],
        max_tokens=10,
        now_utc=now,
    )
    assert ctx["stages"][0]["budget_status"] == "fail_closed"
