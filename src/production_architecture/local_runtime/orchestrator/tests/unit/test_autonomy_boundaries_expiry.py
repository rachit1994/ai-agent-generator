"""§11 autonomy: token_context window expiry + high-risk approval token expiry (HS06 / HS30)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from guardrails_and_safety.autonomy_boundaries.autonomy_boundaries_tokens_expiry.token_context import build_token_context
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops import evaluate_hard_stops
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops_organization import evaluate_organization_hard_stops
from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import parse_iso_utc


def test_parse_iso_utc_accepts_zulu_and_rejects_garbage() -> None:
    assert parse_iso_utc("2030-01-01T12:00:00+00:00") is not None
    assert parse_iso_utc("2030-01-01T12:00:00Z") is not None
    assert parse_iso_utc("not-a-date") is None


def test_build_token_context_emits_expiry_fields() -> None:
    ctx = build_token_context("r1", [], max_tokens=100, context_ttl_seconds=3600)
    assert ctx["context_ttl_seconds"] == 3600
    a = parse_iso_utc(str(ctx["autonomy_anchor_at"]))
    e = parse_iso_utc(str(ctx["context_expires_at"]))
    assert a is not None and e is not None
    assert e > a


def test_hs06_fails_on_expired_context(tmp_path: Path) -> None:
    past = (datetime.now(timezone.utc) - timedelta(hours=1)).replace(microsecond=0).isoformat()
    tc: dict[str, object] = {
        "schema_version": "1.0",
        "stages": [],
        "context_expires_at": past,
    }
    hs = evaluate_hard_stops(tmp_path, [], tc, run_status="ok", mode="baseline")
    assert next(h for h in hs if h["id"] == "HS06")["passed"] is False


def test_hs06_passes_when_expiry_absent(tmp_path: Path) -> None:
    tc: dict[str, object] = {"schema_version": "1.0", "stages": []}
    hs = evaluate_hard_stops(tmp_path, [], tc, run_status="ok", mode="baseline")
    assert next(h for h in hs if h["id"] == "HS06")["passed"] is True


def _org_plane_dirs(tmp_path: Path, audit_line: dict[str, object]) -> None:
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    (tmp_path / "coordination").mkdir(parents=True)
    (tmp_path / "coordination" / "lease_table.json").write_text(
        json.dumps({"leases": [{"lease_id": "lease-a", "lane_id": "x", "active": True}]}),
        encoding="utf-8",
    )
    (tmp_path / "iam").mkdir(parents=True)
    (tmp_path / "iam" / "action_audit.jsonl").write_text(json.dumps(audit_line) + "\n", encoding="utf-8")
    (tmp_path / "orchestration").mkdir(parents=True)
    (tmp_path / "orchestration" / "shard_map.json").write_text(
        json.dumps({"single_shard": True}),
        encoding="utf-8",
    )
    (tmp_path / "strategy").mkdir(parents=True)
    (tmp_path / "strategy" / "proposal.json").write_text(
        json.dumps({"applied_autonomy": False}),
        encoding="utf-8",
    )


def test_hs30_fails_when_high_risk_approval_expired(tmp_path: Path) -> None:
    past = (datetime.now(timezone.utc) - timedelta(days=1)).replace(microsecond=0).isoformat()
    _org_plane_dirs(
        tmp_path,
        {
            "risk": "high",
            "approval_token_id": "tok-1",
            "approval_token_expires_at": past,
            "lease_id": "lease-a",
        },
    )
    hs = {h["id"]: h["passed"] for h in evaluate_organization_hard_stops(tmp_path)}
    assert hs["HS30"] is False


def test_hs30_passes_high_risk_with_future_approval_expiry(tmp_path: Path) -> None:
    future = (datetime.now(timezone.utc) + timedelta(days=30)).replace(microsecond=0).isoformat()
    _org_plane_dirs(
        tmp_path,
        {
            "risk": "high",
            "approval_token_id": "tok-1",
            "approval_token_expires_at": future,
            "lease_id": "lease-a",
        },
    )
    hs = {h["id"]: h["passed"] for h in evaluate_organization_hard_stops(tmp_path)}
    assert hs["HS30"] is True
