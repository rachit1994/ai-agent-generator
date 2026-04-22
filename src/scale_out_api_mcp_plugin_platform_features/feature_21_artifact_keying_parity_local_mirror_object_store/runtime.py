"""Runtime for feature 21 artifact keying parity gate."""

from __future__ import annotations

from typing import Any

from .contracts import ARTIFACT_KEY_PARITY_SCHEMA, ARTIFACT_KEY_PARITY_SCHEMA_VERSION


def build_artifact_key_schema_contract() -> dict[str, object]:
    return {
        "canonical_key_schema": True,
        "object_store_adapter": True,
        "local_object_reconciliation": True,
        "collision_drift_detection": True,
        "checksum_integrity_verification": True,
        "legacy_key_migration": True,
        "conflict_resolution_semantics": True,
        "backend_parity_integration_tests": True,
    }


def _key_format_versions_align(
    *, local_index: dict[str, Any], object_index: dict[str, Any], migration: dict[str, Any]
) -> bool:
    local_version = local_index.get("key_format_version")
    object_version = object_index.get("key_format_version")
    migration_version = migration.get("key_format_version")
    return (
        isinstance(local_version, str)
        and local_version.strip() != ""
        and local_version == object_version
        and local_version == migration_version
    )


def _valid_artifact_row(row: Any) -> bool:
    if not isinstance(row, dict):
        return False
    artifact_id = row.get("artifact_id")
    key = row.get("key")
    checksum = row.get("checksum")
    return (
        isinstance(artifact_id, str)
        and artifact_id.strip() != ""
        and isinstance(key, str)
        and key.strip() != ""
        and isinstance(checksum, str)
        and checksum.strip() != ""
    )


def _artifact_rows(index: dict[str, Any]) -> list[dict[str, str]]:
    rows = index.get("artifacts")
    if not isinstance(rows, list):
        return []
    normalized: list[dict[str, str]] = []
    for row in rows:
        if not _valid_artifact_row(row):
            continue
        normalized.append(
            {
                "artifact_id": row["artifact_id"],
                "key": row["key"],
                "checksum": row["checksum"],
            }
        )
    return normalized


def _checksum_map(rows: list[dict[str, str]]) -> dict[str, str]:
    return {row["artifact_id"]: row["checksum"] for row in rows}


def _key_map(rows: list[dict[str, str]]) -> dict[str, str]:
    return {row["artifact_id"]: row["key"] for row in rows}


def _is_canonical_key(*, key: str, prefix: str, artifact_id: str, checksum: str) -> bool:
    expected = f"{prefix.rstrip('/')}/{artifact_id}/{checksum}"
    return key == expected


def _reconciliation_drift_for_shared_ids(
    *,
    shared_ids: list[str],
    local_keys: dict[str, str],
    object_keys: dict[str, str],
    local_checksums: dict[str, str],
    object_checksums: dict[str, str],
    prefix: str,
) -> dict[str, Any]:
    key_mismatches: list[str] = []
    checksum_mismatches: list[str] = []
    canonical_violations: list[str] = []
    for artifact_id in shared_ids:
        local_key = local_keys[artifact_id]
        object_key = object_keys[artifact_id]
        local_checksum = local_checksums[artifact_id]
        object_checksum = object_checksums[artifact_id]
        if local_key != object_key:
            key_mismatches.append(artifact_id)
        if local_checksum != object_checksum:
            checksum_mismatches.append(artifact_id)
        if not _is_canonical_key(
            key=local_key,
            prefix=prefix,
            artifact_id=artifact_id,
            checksum=local_checksum,
        ):
            canonical_violations.append(artifact_id)
    return {
        "key_mismatches": key_mismatches,
        "checksum_mismatches": checksum_mismatches,
        "canonical_violations": canonical_violations,
    }


def _migration_failures(
    *,
    migration_rows: Any,
    local_checksums: dict[str, str],
    local_keys: dict[str, str],
) -> list[str]:
    if not isinstance(migration_rows, list):
        return []
    failures: list[str] = []
    for row in migration_rows:
        if not isinstance(row, dict):
            failures.append("invalid_mapping_shape")
            continue
        artifact_id = row.get("artifact_id")
        legacy_key = row.get("legacy_key")
        migrated_key = row.get("migrated_key")
        checksum = row.get("checksum")
        if not all(
            (
                isinstance(artifact_id, str) and artifact_id.strip(),
                isinstance(legacy_key, str) and legacy_key.strip(),
                isinstance(migrated_key, str) and migrated_key.strip(),
                isinstance(checksum, str) and checksum.strip(),
            )
        ):
            failures.append("invalid_mapping_fields")
            continue
        if artifact_id not in local_checksums:
            failures.append(f"unknown_mapping_artifact:{artifact_id}")
            continue
        if local_checksums[artifact_id] != checksum:
            failures.append(f"mapping_checksum_drift:{artifact_id}")
            continue
        if local_keys[artifact_id] != migrated_key:
            failures.append(f"mapping_key_drift:{artifact_id}")
    return failures


def _parity_ok(
    *,
    missing_in_object: list[str],
    missing_in_local: list[str],
    key_mismatches: list[str],
    checksum_mismatches: list[str],
    canonical_violations: list[str],
    collisions: bool,
    migration_ready: bool,
) -> bool:
    return not any(
        (
            missing_in_object,
            missing_in_local,
            key_mismatches,
            checksum_mismatches,
            canonical_violations,
            collisions,
            not migration_ready,
        )
    )


def execute_artifact_key_reconciliation(
    *, local_index: dict[str, Any], object_index: dict[str, Any], migration: dict[str, Any]
) -> dict[str, Any]:
    local_rows = _artifact_rows(local_index)
    object_rows = _artifact_rows(object_index)
    local_keys = _key_map(local_rows)
    object_keys = _key_map(object_rows)
    local_checksums = _checksum_map(local_rows)
    object_checksums = _checksum_map(object_rows)
    local_ids = set(local_keys)
    object_ids = set(object_keys)
    shared_ids = sorted(local_ids & object_ids)
    missing_in_object = sorted(local_ids - object_ids)
    missing_in_local = sorted(object_ids - local_ids)
    prefix = str(local_index.get("canonical_key_prefix", ""))
    shared_drift = _reconciliation_drift_for_shared_ids(
        shared_ids=shared_ids,
        local_keys=local_keys,
        object_keys=object_keys,
        local_checksums=local_checksums,
        object_checksums=object_checksums,
        prefix=prefix,
    )
    key_mismatches = shared_drift["key_mismatches"]
    checksum_mismatches = shared_drift["checksum_mismatches"]
    canonical_violations = shared_drift["canonical_violations"]
    local_key_values = [row["key"] for row in local_rows]
    collisions = len(local_key_values) != len(set(local_key_values))
    migration_failures = _migration_failures(
        migration_rows=migration.get("legacy_key_mappings"),
        local_checksums=local_checksums,
        local_keys=local_keys,
    )
    migration_ready = len(migration_failures) == 0
    parity_ok = _parity_ok(
        missing_in_object=missing_in_object,
        missing_in_local=missing_in_local,
        key_mismatches=key_mismatches,
        checksum_mismatches=checksum_mismatches,
        canonical_violations=canonical_violations,
        collisions=collisions,
        migration_ready=migration_ready,
    )
    return {
        "counts": {
            "local_artifacts": len(local_rows),
            "object_artifacts": len(object_rows),
            "shared_artifacts": len(shared_ids),
        },
        "drift": {
            "missing_in_object": missing_in_object,
            "missing_in_local": missing_in_local,
            "key_mismatches": key_mismatches,
            "checksum_mismatches": checksum_mismatches,
            "canonical_key_violations": canonical_violations,
            "collisions_detected": collisions,
            "migration_failures": migration_failures,
        },
        "parity_ok": parity_ok,
    }


def summarize_artifact_key_parity_health(
    *, local_index: dict[str, Any], object_index: dict[str, Any], migration: dict[str, Any]
) -> dict[str, bool]:
    reconciliation = execute_artifact_key_reconciliation(
        local_index=local_index, object_index=object_index, migration=migration
    )
    local_prefix = local_index.get("canonical_key_prefix")
    object_prefix = object_index.get("canonical_key_prefix")
    migration_prefix = migration.get("migration_target_prefix")
    return {
        "canonical_artifact_key_schema_adopted": local_index.get("canonical_artifact_key_schema_adopted")
        is True
        and isinstance(local_prefix, str)
        and local_prefix.startswith("artifacts/")
        and local_prefix == object_prefix
        and local_prefix == migration_prefix
        and _key_format_versions_align(
            local_index=local_index, object_index=object_index, migration=migration
        ),
        "canonical_object_store_adapter_implemented": object_index.get(
            "canonical_object_store_adapter_implemented"
        )
        is True
        and isinstance(_artifact_rows(object_index), list)
        and len(_artifact_rows(object_index)) > 0,
        "local_object_keys_reconciled": object_index.get("local_object_keys_reconciled") is True
        and len(reconciliation["drift"]["missing_in_object"]) == 0
        and len(reconciliation["drift"]["missing_in_local"]) == 0
        and len(reconciliation["drift"]["key_mismatches"]) == 0,
        "collision_and_key_drift_detection_enabled": object_index.get(
            "collision_and_key_drift_detection_enabled"
        )
        is True
        and reconciliation["drift"]["collisions_detected"] is False
        and len(reconciliation["drift"]["canonical_key_violations"]) == 0,
        "content_hash_integrity_checks_enforced": object_index.get(
            "content_hash_integrity_checks_enforced"
        )
        is True
        and len(reconciliation["drift"]["checksum_mismatches"]) == 0,
        "legacy_key_layout_migration_supported": migration.get("legacy_key_layout_migration_supported")
        is True
        and len(reconciliation["drift"]["migration_failures"]) == 0,
        "conflict_resolution_semantics_defined": migration.get("conflict_resolution_semantics_defined")
        is True
        and migration.get("conflict_resolution_policy") in {"prefer-object", "prefer-local", "block"},
        "backend_parity_integration_tests_implemented": migration.get(
            "backend_parity_integration_tests_implemented"
        )
        is True
        and reconciliation["parity_ok"] is True,
    }


def evaluate_artifact_key_parity_gate(
    *,
    run_id: str,
    mode: str,
    local_index: dict[str, Any],
    object_index: dict[str, Any],
    migration: dict[str, Any],
) -> dict[str, Any]:
    reconciliation = execute_artifact_key_reconciliation(
        local_index=local_index, object_index=object_index, migration=migration
    )
    checks = summarize_artifact_key_parity_health(
        local_index=local_index, object_index=object_index, migration=migration
    )
    failed_gates = [gate for gate, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": ARTIFACT_KEY_PARITY_SCHEMA,
        "schema_version": ARTIFACT_KEY_PARITY_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "failed_gates": failed_gates,
        "reconciliation": reconciliation,
        "artifact_key_schema_contract": build_artifact_key_schema_contract(),
        "evidence": {
            "local_index_ref": "data/artifact_key_parity/local_index.json",
            "object_index_ref": "data/artifact_key_parity/object_index.json",
            "migration_ref": "data/artifact_key_parity/migration_state.json",
            "history_ref": "data/artifact_key_parity/trend_history.jsonl",
            "reconciliation_ref": "data/artifact_key_parity/reconciliation_details.json",
        },
    }


def update_artifact_key_parity_history(
    *, existing: list[dict[str, Any]], report: dict[str, Any]
) -> list[dict[str, Any]]:
    reconciliation = report.get("reconciliation")
    counts = reconciliation.get("counts", {}) if isinstance(reconciliation, dict) else {}
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "shared_artifacts": counts.get("shared_artifacts"),
    }
    return [*existing, row]

