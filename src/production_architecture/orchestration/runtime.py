"""Deterministic production orchestration derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    PRODUCTION_ORCHESTRATION_CONTRACT,
    PRODUCTION_ORCHESTRATION_SCHEMA_VERSION,
)


def execute_production_orchestration_runtime(
    *,
    lease_table: dict[str, Any],
    shard_map: dict[str, Any],
) -> dict[str, Any]:
    leases = lease_table.get("leases") if isinstance(lease_table, dict) else []
    shards = shard_map.get("shards") if isinstance(shard_map, dict) else []
    leases = leases if isinstance(leases, list) else []
    shards = shards if isinstance(shards, list) else []
    malformed_lease_rows = len([row for row in leases if not isinstance(row, dict)])
    malformed_shard_rows = len([row for row in shards if not isinstance(row, dict)])
    inactive_or_missing_lease_ids = len(
        [
            row
            for row in leases
            if not isinstance(row, dict)
            or row.get("active") is not True
            or not isinstance(row.get("lease_id"), str)
            or not row.get("lease_id").strip()
        ]
    )
    return {
        "lease_rows_processed": len(leases),
        "shard_rows_processed": len(shards),
        "malformed_lease_rows": malformed_lease_rows,
        "malformed_shard_rows": malformed_shard_rows,
        "inactive_or_missing_lease_ids": inactive_or_missing_lease_ids,
    }


def build_production_orchestration(
    *,
    run_id: str,
    lease_table: dict[str, Any],
    shard_map: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_production_orchestration_runtime(
        lease_table=lease_table, shard_map=shard_map
    )
    leases = lease_table.get("leases") if isinstance(lease_table, dict) else []
    if not isinstance(leases, list):
        leases = []
    shards = shard_map.get("shards") if isinstance(shard_map, dict) else []
    if not isinstance(shards, list):
        shards = []
    lease_count = len([row for row in leases if isinstance(row, dict)])
    active_lease_count = len(
        [row for row in leases if isinstance(row, dict) and row.get("active") is True]
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
        "execution": execution,
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
