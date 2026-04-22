from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, cast
import pytest

from guardrails_and_safety.autonomy_boundaries.autonomy_boundaries_tokens_expiry.runtime import (
    build_autonomy_boundaries_runtime_payload,
)


def _token_context() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "run_id": "rid",
        "model_context_limit": 64,
        "stages": [
            {
                "name": "s1",
                "input_token_budget": 10,
                "output_token_budget": 10,
                "planned_input_tokens": 1,
                "actual_input_tokens": 1,
                "actual_output_tokens": 1,
                "budget_status": "ok",
            }
        ],
        "context_policy": {"priority": ["a"], "version_hash": "hash"},
        "reductions": [],
        "truncation_events": [],
        "autonomy_anchor_at": "2030-01-01T00:00:00+00:00",
        "context_expires_at": "2030-01-01T00:01:00+00:00",
        "context_ttl_seconds": 60,
    }


def test_runtime_payload_builds_and_is_deterministic() -> None:
    now = datetime(2030, 1, 1, 0, 0, tzinfo=timezone.utc)
    first = build_autonomy_boundaries_runtime_payload(run_id="rid", token_context=_token_context(), now_utc=now)
    second = build_autonomy_boundaries_runtime_payload(run_id="rid", token_context=_token_context(), now_utc=now)
    assert first == second
    assert first["schema"] == "sde.autonomy_boundaries_tokens_expiry.v1"


def test_runtime_payload_fails_on_missing_required_token_context_fields() -> None:
    with pytest.raises(ValueError, match="token_context_context_expires_at"):
        build_autonomy_boundaries_runtime_payload(
            run_id="rid",
            token_context={"run_id": "rid", "stages": [], "autonomy_anchor_at": "2030-01-01T00:00:00+00:00"},
            now_utc=datetime(2030, 1, 1, 0, 0, tzinfo=timezone.utc),
        )


def test_runtime_payload_fails_on_run_id_mismatch() -> None:
    with pytest.raises(ValueError, match="autonomy_boundaries_run_id_mismatch"):
        build_autonomy_boundaries_runtime_payload(
            run_id="rid-a",
            token_context=_token_context(),
            now_utc=datetime(2030, 1, 1, 0, 0, tzinfo=timezone.utc),
        )


def test_runtime_payload_fails_when_token_context_not_object() -> None:
    bad_token_context = cast(dict[str, Any], [])
    with pytest.raises(ValueError, match="token_context_not_object"):
        build_autonomy_boundaries_runtime_payload(
            run_id="rid",
            token_context=bad_token_context,
            now_utc=datetime(2030, 1, 1, 0, 0, tzinfo=timezone.utc),
        )
