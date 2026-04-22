from __future__ import annotations

from production_architecture.orchestration import (
    build_production_orchestration,
    execute_production_orchestration_runtime,
    validate_production_orchestration_dict,
)


def test_build_production_orchestration_is_deterministic() -> None:
    one = build_production_orchestration(
        run_id="rid-orchestration",
        lease_table={"leases": [{"lease_id": "l1", "active": True}]},
        shard_map={"shards": [{"id": "s1"}]},
    )
    two = build_production_orchestration(
        run_id="rid-orchestration",
        lease_table={"leases": [{"lease_id": "l1", "active": True}]},
        shard_map={"shards": [{"id": "s1"}]},
    )
    assert one == two
    assert validate_production_orchestration_dict(one) == []
    assert one["execution"]["lease_rows_processed"] == 1


def test_validate_production_orchestration_fail_closed() -> None:
    errs = validate_production_orchestration_dict({"schema": "bad"})
    assert "production_orchestration_schema" in errs
    assert "production_orchestration_schema_version" in errs


def test_build_production_orchestration_treats_truthy_non_boolean_active_as_inactive() -> None:
    payload = build_production_orchestration(
        run_id="rid-orchestration",
        lease_table={"leases": [{"lease_id": "l1", "active": "true"}]},
        shard_map={"shards": [{"id": "s1"}]},
    )
    assert payload["metrics"]["active_lease_count"] == 0
    assert payload["status"] == "degraded"


def test_validate_production_orchestration_rejects_status_metrics_mismatch() -> None:
    payload = build_production_orchestration(
        run_id="rid-orchestration",
        lease_table={"leases": [{"lease_id": "l1", "active": True}]},
        shard_map={"shards": [{"id": "s1"}]},
    )
    payload["status"] = "missing"
    errs = validate_production_orchestration_dict(payload)
    assert "production_orchestration_status_metrics_mismatch" in errs


def test_validate_production_orchestration_rejects_invalid_evidence_refs() -> None:
    payload = build_production_orchestration(
        run_id="rid-orchestration",
        lease_table={"leases": [{"lease_id": "l1", "active": True}]},
        shard_map={"shards": [{"id": "s1"}]},
    )
    payload["evidence"]["lease_table_ref"] = "../coordination/lease_table.json"
    payload["evidence"]["shard_map_ref"] = "orchestration/other.json"
    errs = validate_production_orchestration_dict(payload)
    assert "production_orchestration_evidence_ref:lease_table_ref" in errs
    assert "production_orchestration_evidence_ref:shard_map_ref" in errs


def test_execute_production_orchestration_runtime_detects_malformed_rows() -> None:
    execution = execute_production_orchestration_runtime(
        lease_table={"leases": [{"lease_id": "l1", "active": True}, {"active": False}, "bad-row"]},  # type: ignore[list-item]
        shard_map={"shards": [{"id": "s1"}, "bad-row"]},  # type: ignore[list-item]
    )
    assert execution["lease_rows_processed"] == 3
    assert execution["shard_rows_processed"] == 2
    assert execution["malformed_lease_rows"] == 1
    assert execution["malformed_shard_rows"] == 1
    assert execution["inactive_or_missing_lease_ids"] == 2
