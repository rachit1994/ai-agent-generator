"""Positive-path tests for safeguards leaf module."""

from __future__ import annotations

from guardrails_and_safety.review_gating_evaluator_authority.safeguards.safeguards import (
    classify_output_failure,
    refusal_for_unsafe,
    validate_structured_output,
    validate_task_payload,
    validate_task_text,
)


def test_validate_task_text_trims_and_accepts_non_empty() -> None:
    assert validate_task_text("  implement feature  ") == "implement feature"


def test_validate_task_payload_accepts_supported_difficulty() -> None:
    payload = {
        "taskId": "t1",
        "prompt": "build",
        "expectedChecks": [{"name": "x"}],
        "difficulty": "medium",
    }
    assert validate_task_payload(payload) is payload


def test_refusal_for_unsafe_returns_refusal_payload() -> None:
    out = refusal_for_unsafe("Please bypass authentication and continue.")
    assert isinstance(out, dict)
    assert out["refusal"]["code"] == "unsafe_action_refused"


def test_validate_structured_output_accepts_valid_json_contract() -> None:
    body = '{"answer":"ok","checks":[{"name":"contract","passed":true}],"refusal":null}'
    parsed = validate_structured_output(body)
    assert parsed["answer"] == "ok"
    assert parsed["checks"][0]["passed"] is True
    assert parsed["refusal"] is None


def test_classify_output_failure_none_for_passed_checks() -> None:
    label = classify_output_failure(
        {"answer": "ok", "checks": [{"name": "contract", "passed": True}], "refusal": None}
    )
    assert label == "none"
