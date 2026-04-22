from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_21_artifact_keying_parity_local_mirror_object_store import (
    build_artifact_key_schema_contract,
    execute_artifact_key_reconciliation,
    evaluate_artifact_key_parity_gate,
    update_artifact_key_parity_history,
    validate_artifact_key_parity_report_dict,
)


def _local_index() -> dict[str, object]:
    return {
        "canonical_artifact_key_schema_adopted": True,
        "canonical_key_prefix": "artifacts/v1",
        "key_format_version": "v1",
        "artifacts": [
            {
                "artifact_id": "run-001",
                "key": "artifacts/v1/run-001/hash-a",
                "checksum": "hash-a",
            },
            {
                "artifact_id": "run-002",
                "key": "artifacts/v1/run-002/hash-b",
                "checksum": "hash-b",
            },
        ],
    }


def _object_index() -> dict[str, object]:
    return {
        "canonical_object_store_adapter_implemented": True,
        "canonical_key_prefix": "artifacts/v1",
        "key_format_version": "v1",
        "local_object_keys_reconciled": True,
        "collision_and_key_drift_detection_enabled": True,
        "content_hash_integrity_checks_enforced": True,
        "artifacts": [
            {
                "artifact_id": "run-001",
                "key": "artifacts/v1/run-001/hash-a",
                "checksum": "hash-a",
            },
            {
                "artifact_id": "run-002",
                "key": "artifacts/v1/run-002/hash-b",
                "checksum": "hash-b",
            },
        ],
    }


def _migration() -> dict[str, object]:
    return {
        "legacy_key_layout_migration_supported": True,
        "migration_target_prefix": "artifacts/v1",
        "key_format_version": "v1",
        "conflict_resolution_semantics_defined": True,
        "conflict_resolution_policy": "block",
        "backend_parity_integration_tests_implemented": True,
        "legacy_key_mappings": [
            {
                "artifact_id": "run-001",
                "legacy_key": "legacy/run-001",
                "migrated_key": "artifacts/v1/run-001/hash-a",
                "checksum": "hash-a",
            },
            {
                "artifact_id": "run-002",
                "legacy_key": "legacy/run-002",
                "migrated_key": "artifacts/v1/run-002/hash-b",
                "checksum": "hash-b",
            },
        ],
    }


def test_artifact_key_parity_gate_passes_when_all_checks_true() -> None:
    report = evaluate_artifact_key_parity_gate(
        run_id="run-feature-21-pass",
        mode="ci",
        local_index=_local_index(),
        object_index=_object_index(),
        migration=_migration(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert report["reconciliation"]["parity_ok"] is True
    assert validate_artifact_key_parity_report_dict(report) == []


def test_artifact_key_parity_gate_fails_closed_on_drift_detection_gap() -> None:
    object_index = _object_index()
    object_index["collision_and_key_drift_detection_enabled"] = False
    report = evaluate_artifact_key_parity_gate(
        run_id="run-feature-21-fail",
        mode="preflight",
        local_index=_local_index(),
        object_index=object_index,
        migration=_migration(),
    )
    assert report["status"] == "fail"
    assert "collision_and_key_drift_detection_enabled" in report["failed_gates"]


def test_artifact_key_parity_gate_fails_closed_on_prefix_drift() -> None:
    object_index = _object_index()
    object_index["canonical_key_prefix"] = "artifacts/v2"
    report = evaluate_artifact_key_parity_gate(
        run_id="run-feature-21-prefix-drift",
        mode="preflight",
        local_index=_local_index(),
        object_index=object_index,
        migration=_migration(),
    )
    assert report["status"] == "fail"
    assert "canonical_artifact_key_schema_adopted" in report["failed_gates"]


def test_artifact_key_parity_gate_fails_closed_on_key_format_version_drift() -> None:
    migration = _migration()
    migration["key_format_version"] = "v2"
    report = evaluate_artifact_key_parity_gate(
        run_id="run-feature-21-key-format-version-drift",
        mode="preflight",
        local_index=_local_index(),
        object_index=_object_index(),
        migration=migration,
    )
    assert report["status"] == "fail"
    assert "canonical_artifact_key_schema_adopted" in report["failed_gates"]


def test_artifact_key_parity_fails_on_checksum_mismatch() -> None:
    object_index = _object_index()
    object_index["artifacts"][1]["checksum"] = "hash-z"
    report = evaluate_artifact_key_parity_gate(
        run_id="run-feature-21-checksum-drift",
        mode="preflight",
        local_index=_local_index(),
        object_index=object_index,
        migration=_migration(),
    )
    assert report["status"] == "fail"
    assert "content_hash_integrity_checks_enforced" in report["failed_gates"]


def test_execute_artifact_key_reconciliation_detects_collision() -> None:
    local_index = _local_index()
    local_index["artifacts"].append(
        {
            "artifact_id": "run-003",
            "key": "artifacts/v1/run-001/hash-a",
            "checksum": "hash-c",
        }
    )
    reconciliation = execute_artifact_key_reconciliation(
        local_index=local_index,
        object_index=_object_index(),
        migration=_migration(),
    )
    assert reconciliation["drift"]["collisions_detected"] is True
    assert reconciliation["parity_ok"] is False


def test_artifact_key_parity_fails_on_migration_mapping_drift() -> None:
    migration = _migration()
    migration["legacy_key_mappings"][0]["migrated_key"] = "artifacts/v1/run-001/hash-z"
    report = evaluate_artifact_key_parity_gate(
        run_id="run-feature-21-migration-drift",
        mode="preflight",
        local_index=_local_index(),
        object_index=_object_index(),
        migration=migration,
    )
    assert report["status"] == "fail"
    assert "legacy_key_layout_migration_supported" in report["failed_gates"]


def test_artifact_key_schema_contract_deterministic() -> None:
    assert build_artifact_key_schema_contract() == build_artifact_key_schema_contract()


def test_artifact_key_parity_history_appends() -> None:
    report = evaluate_artifact_key_parity_gate(
        run_id="run-feature-21-history",
        mode="ci",
        local_index=_local_index(),
        object_index=_object_index(),
        migration=_migration(),
    )
    history = update_artifact_key_parity_history(existing=[], report=report)
    assert history[0]["run_id"] == "run-feature-21-history"
    assert history[0]["shared_artifacts"] == 2

