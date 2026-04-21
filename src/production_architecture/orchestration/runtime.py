"""Deterministic production orchestration derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    PRODUCTION_ORCHESTRATION_CONTRACT,
    PRODUCTION_ORCHESTRATION_SCHEMA_VERSION,
)


def build_production_orchestration(
    *,
    run_id: str,
    lease_table: dict[str, Any],
    shard_map: dict[str, Any],
) -> dict[str, Any]:
    leases = lease_table.get("leases") if isinstance(lease_table, dict) else []
    if not isinstance(leases, list):
        leases = []
    shards = shard_map.get("shards") if isinstance(shard_map, dict) else []
    if not isinstance(shards, list):
        shards = []
    lease_count = len([row for row in leases if isinstance(row, dict)])
    active_lease_count = len(
        [row for row in leases if isinstance(row, dict) and bool(row.get("active"))]
    )
    shard_count = len([row for row in shards if isinstance(row, dict)])
    status = "missing"
    if active_lease_count > 0 and shard_count > 0:
        status = "healthy"
    elif lease_count > 0 or shard_count > 0:
        status = "degraded"
    return {
        "schema": PRODUCTION_ORCHESTRATION_CONTRACT,
        "schema_version": PRODUCTION_ORCHESTRATION_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "metrics": {
            "lease_count": lease_count,
            "active_lease_count": active_lease_count,
            "shard_count": shard_count,
        },
        "evidence": {
            "lease_table_ref": "coordination/lease_table.json",
            "shard_map_ref": "orchestration/shard_map.json",
            "orchestration_ref": "orchestration/production_orchestration.json",
        },
    }
