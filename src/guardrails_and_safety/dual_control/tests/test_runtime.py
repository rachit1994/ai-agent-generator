from __future__ import annotations

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
