from __future__ import annotations

import json
import subprocess


def test_artifact_key_parity_gate_script_passes(tmp_path) -> None:
    local_index = {
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
    object_index = {
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
    migration = {
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
    local_index_path = tmp_path / "local_index.json"
    object_index_path = tmp_path / "object_index.json"
    migration_path = tmp_path / "migration.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    local_index_path.write_text(json.dumps(local_index), encoding="utf-8")
    object_index_path.write_text(json.dumps(object_index), encoding="utf-8")
    migration_path.write_text(json.dumps(migration), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/artifact_key_parity_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-21-ci",
            "--local-index",
            str(local_index_path),
            "--object-index",
            str(object_index_path),
            "--migration",
            str(migration_path),
            "--out",
            str(out_path),
            "--history",
            str(history_path),
        ],
        check=False,
        text=True,
    )
    assert result.returncode == 0
    report = json.loads(out_path.read_text(encoding="utf-8"))
    assert report["status"] == "pass"
    assert report["reconciliation"]["parity_ok"] is True
    reconciliation_path = out_path.parent / "reconciliation_details.json"
    assert reconciliation_path.is_file()
    assert history_path.read_text(encoding="utf-8").strip()

