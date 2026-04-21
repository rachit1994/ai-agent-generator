from __future__ import annotations

import pytest

from guardrails_and_safety.dual_control import (
    build_dual_control_runtime,
    validate_dual_control_dict,
)


def test_build_dual_control_runtime_deterministic() -> None:
    doc_review = {"passed": True, "dual_control": {"required": True}}
    ack = {
        "schema_version": "1.0",
        "implementor_actor_id": "alice",
        "independent_reviewer_actor_id": "bob",
        "acknowledged_at": "2026-01-01T00:00:00Z",
    }
    one = build_dual_control_runtime(run_id="rid-dual", doc_review=doc_review, dual_control_ack=ack)
    two = build_dual_control_runtime(run_id="rid-dual", doc_review=doc_review, dual_control_ack=ack)
    assert one == two
    assert one["status"] == "validated"
    assert validate_dual_control_dict(one) == []


def test_validate_dual_control_fail_closed() -> None:
    errs = validate_dual_control_dict({"schema": "wrong"})
    assert "dual_control_schema" in errs
    assert "dual_control_schema_version" in errs
    assert "dual_control_run_id" in errs
    assert "dual_control_status" in errs


def test_validate_dual_control_rejects_invalid_status_and_metric_types() -> None:
    errs = validate_dual_control_dict(
        {
            "schema": "sde.dual_control.v1",
            "schema_version": "1.0",
            "run_id": "rid-runtime",
            "status": "unknown",
            "metrics": {
                "doc_review_passed": "yes",
                "dual_required": True,
                "ack_present": False,
                "ack_valid": False,
                "distinct_actors": 1,
            },
            "evidence": {
                "doc_review_ref": "program/doc_review.json",
                "dual_control_ack_ref": "program/dual_control_ack.json",
                "dual_control_runtime_ref": "program/dual_control_runtime.json",
            },
        }
    )
    assert "dual_control_status" in errs
    assert "dual_control_metric_type:doc_review_passed" in errs
    assert "dual_control_metric_type:distinct_actors" in errs


@pytest.mark.parametrize(
    ("doc_review", "ack", "expected_status"),
    [
        ({"passed": True, "dual_control": {"required": True}}, {}, "missing_required_ack"),
        (
            {"passed": True, "dual_control": {"required": True}},
            {
                "schema_version": "2.0",
                "implementor_actor_id": "alice",
                "independent_reviewer_actor_id": "bob",
                "acknowledged_at": "2026-01-01T00:00:00Z",
            },
            "invalid_ack",
        ),
        (
            {"passed": True, "dual_control": {"required": False}},
            {
                "schema_version": "1.0",
                "implementor_actor_id": "alice",
                "independent_reviewer_actor_id": "bob",
                "acknowledged_at": "2026-01-01T00:00:00Z",
            },
            "validated",
        ),
    ],
)
def test_runtime_status_precedence_is_deterministic(
    doc_review: dict[str, object], ack: dict[str, object], expected_status: str
) -> None:
    payload = build_dual_control_runtime(run_id="rid-precedence", doc_review=doc_review, dual_control_ack=ack)
    assert payload["status"] == expected_status
    assert validate_dual_control_dict(payload) == []


def test_runtime_fails_closed_for_malformed_dual_control_block() -> None:
    payload = build_dual_control_runtime(
        run_id="rid-malformed",
        doc_review={"passed": True, "dual_control": "not-a-dict"},
        dual_control_ack={},
    )
    assert payload["status"] == "missing_required_ack"


def test_runtime_invalid_ack_when_actor_ids_not_distinct() -> None:
    payload = build_dual_control_runtime(
        run_id="rid-same-actor",
        doc_review={"passed": True, "dual_control": {"required": True}},
        dual_control_ack={
            "schema_version": "1.0",
            "implementor_actor_id": "alice",
            "independent_reviewer_actor_id": "alice",
            "acknowledged_at": "2026-01-01T00:00:00Z",
        },
    )
    assert payload["status"] == "invalid_ack"


@pytest.mark.parametrize(
    "ack",
    [
        {
            "schema_version": "1.0",
            "implementor_actor_id": " ",
            "independent_reviewer_actor_id": "bob",
            "acknowledged_at": "2026-01-01T00:00:00Z",
        },
        {
            "schema_version": "1.0",
            "implementor_actor_id": "alice",
            "independent_reviewer_actor_id": "bob",
            "acknowledged_at": " ",
        },
    ],
)
def test_runtime_invalid_ack_when_required_and_ack_fields_blank(ack: dict[str, object]) -> None:
    payload = build_dual_control_runtime(
        run_id="rid-blank-ack",
        doc_review={"passed": True, "dual_control": {"required": True}},
        dual_control_ack=ack,
    )
    assert payload["status"] == "invalid_ack"


def test_runtime_invalid_ack_when_acknowledged_at_not_utc_timestamp_shape() -> None:
    payload = build_dual_control_runtime(
        run_id="rid-bad-ts-ack",
        doc_review={"passed": True, "dual_control": {"required": True}},
        dual_control_ack={
            "schema_version": "1.0",
            "implementor_actor_id": "alice",
            "independent_reviewer_actor_id": "bob",
            "acknowledged_at": "2026-01-01 00:00:00",
        },
    )
    assert payload["status"] == "invalid_ack"


def test_validate_dual_control_allows_validated_when_ack_not_required_and_absent() -> None:
    payload = build_dual_control_runtime(
        run_id="rid-no-ack-needed",
        doc_review={"passed": True, "dual_control": {"required": False}},
        dual_control_ack={},
    )
    assert payload["status"] == "validated"
    assert validate_dual_control_dict(payload) == []


def test_validate_dual_control_rejects_validated_when_ack_required_but_missing() -> None:
    payload = build_dual_control_runtime(
        run_id="rid-ack-required-missing",
        doc_review={"passed": True, "dual_control": {"required": True}},
        dual_control_ack={},
    )
    payload["status"] = "validated"
    errs = validate_dual_control_dict(payload)
    assert "dual_control_semantics" in errs
