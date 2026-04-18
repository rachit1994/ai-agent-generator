"""Organization harness: leases, IAM matrix, audit trail, shard map, strategy proposal."""

from __future__ import annotations

from pathlib import Path

from sde_foundations.storage import ensure_dir, write_json
from sde_gates.time_util import iso_now


def write_organization_artifacts(*, output_dir: Path, run_id: str) -> None:
    """Minimal coordination + IAM surface (single-lane harness)."""
    coord = output_dir / "coordination"
    ensure_dir(coord)
    iam = output_dir / "iam"
    ensure_dir(iam)
    shard_dir = output_dir / "orchestration"
    ensure_dir(shard_dir)
    strategy = output_dir / "strategy"
    ensure_dir(strategy)

    lease_id = "lease-default"
    write_json(
        coord / "lease_table.json",
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "leases": [
                {
                    "lease_id": lease_id,
                    "lane_id": "default",
                    "file_scope": "**",
                    "active": True,
                    "acquired_at": iso_now(),
                }
            ],
        },
    )
    write_json(
        iam / "permission_matrix.json",
        {"schema_version": "1.0", "version": 1, "roles": [{"name": "implementor", "risk_tier": "standard"}]},
    )
    audit_line = (
        '{"action":"artifact_write","risk":"low","lease_id":"'
        + lease_id
        + '","actor_id":"orchestrator","occurred_at":"'
        + iso_now()
        + '"}\n'
    )
    (iam / "action_audit.jsonl").write_text(audit_line, encoding="utf-8")
    write_json(
        shard_dir / "shard_map.json",
        {"schema_version": "1.0", "single_shard": True, "shards": [{"id": "shard-0", "run_id": run_id}]},
    )
    write_json(
        strategy / "proposal.json",
        {
            "schema_version": "1.0",
            "actor_id": "strategy-agent-harness",
            "requires_promotion_package": True,
            "applied_autonomy": False,
            "proposal_ref": "lifecycle/promotion_package.json",
        },
    )
