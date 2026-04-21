from __future__ import annotations

from guardrails_and_safety.rollback_rules_policy_bundle import (
    build_rollback_rules_policy_bundle,
    validate_rollback_rules_policy_bundle_dict,
)


def test_build_rollback_rules_policy_bundle_is_deterministic() -> None:
    record = {
        "schema_version": "1.0",
        "status": "rolled_back_atomic",
        "previous_policy_sha256": "0" * 64,
        "current_policy_sha256": "f" * 64,
        "paths_touched": ["program/project_plan.json"],
    }
    one = build_rollback_rules_policy_bundle(run_id="rid-rb", rollback_record=record)
    two = build_rollback_rules_policy_bundle(run_id="rid-rb", rollback_record=record)
    assert one == two
    assert validate_rollback_rules_policy_bundle_dict(one) == []


def test_validate_rollback_rules_policy_bundle_fail_closed() -> None:
    errs = validate_rollback_rules_policy_bundle_dict({"schema": "bad"})
    assert "rollback_rules_policy_bundle_schema" in errs
    assert "rollback_rules_policy_bundle_schema_version" in errs
