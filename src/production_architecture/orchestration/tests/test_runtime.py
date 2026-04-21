from __future__ import annotations

from production_architecture.orchestration import (
    build_production_orchestration,
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
