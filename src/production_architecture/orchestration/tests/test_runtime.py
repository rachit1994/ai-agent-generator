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
