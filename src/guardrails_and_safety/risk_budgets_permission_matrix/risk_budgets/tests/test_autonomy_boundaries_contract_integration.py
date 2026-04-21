from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops import evaluate_hard_stops
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops_organization import (
    evaluate_organization_hard_stops,
)


def test_hs06_fails_for_contract_invalid_token_context(tmp_path: Path) -> None:
    token_context = {"schema_version": "1.0", "stages": []}
    hard_stops = evaluate_hard_stops(tmp_path, [], token_context, run_status="ok", mode="baseline")
    hs06 = next(row for row in hard_stops if row["id"] == "HS06")
    assert hs06["passed"] is False


def test_hs30_uses_high_risk_token_contract_validation(tmp_path: Path) -> None:
    (tmp_path / "summary.json").write_text('{"run_class":"full"}', encoding="utf-8")
    (tmp_path / "coordination").mkdir(parents=True)
    (tmp_path / "coordination" / "lease_table.json").write_text(
        '{"leases":[{"lease_id":"lease-a","lane_id":"x","active":true}]}',
        encoding="utf-8",
    )
    (tmp_path / "iam").mkdir(parents=True)
    (tmp_path / "iam" / "permission_matrix.json").write_text(
        '{"schema_version":"1.0","version":1,"roles":[{"name":"implementor","risk_tier":"standard"}]}',
        encoding="utf-8",
    )
    expired = (datetime.now(timezone.utc) - timedelta(days=1)).replace(microsecond=0).isoformat()
    (tmp_path / "iam" / "action_audit.jsonl").write_text(
        f'{{"risk":"high","approval_token_id":"autonomy:tok-1","approval_token_expires_at":"{expired}","lease_id":"lease-a","action":"x","actor_id":"a","occurred_at":"2030-01-01T00:00:00Z"}}\n',
        encoding="utf-8",
    )
    (tmp_path / "orchestration").mkdir(parents=True)
    (tmp_path / "orchestration" / "shard_map.json").write_text('{"single_shard":true}', encoding="utf-8")
    (tmp_path / "strategy").mkdir(parents=True)
    (tmp_path / "strategy" / "proposal.json").write_text('{"applied_autonomy":false}', encoding="utf-8")
    hs = {row["id"]: row["passed"] for row in evaluate_organization_hard_stops(tmp_path)}
    assert hs["HS30"] is False
