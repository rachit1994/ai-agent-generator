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
    assert "rollback_rules_policy_bundle_evidence" in errs


def test_build_rollback_rules_policy_bundle_defaults_to_none_without_source_record() -> None:
    payload = build_rollback_rules_policy_bundle(run_id="rid-rb", rollback_record={})
    assert payload["status"] == "none"
    assert payload["rollback_checks"]["record_present"] is False
    assert payload["evidence"]["policy_bundle_rollback_ref"] == "program/policy_bundle_rollback.json"


def test_build_rollback_rules_policy_bundle_fails_closed_on_duplicate_paths() -> None:
    record = {
        "schema_version": "1.0",
        "status": "rolled_back_atomic",
        "previous_policy_sha256": "0" * 64,
        "current_policy_sha256": "f" * 64,
        "paths_touched": ["program/project_plan.json", "program/project_plan.json"],
    }
    payload = build_rollback_rules_policy_bundle(run_id="rid-rb", rollback_record=record)
    assert payload["status"] == "invalid"
    assert payload["rollback_checks"]["paths_touched_valid"] is False
