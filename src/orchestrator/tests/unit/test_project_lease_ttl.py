"""Phase 8: stale lease pruning + persisted lease conflict detection."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator.api.project_lease import (
    DEFAULT_LEASE_TTL_SEC,
    prune_stale_leases,
    resolve_lease_ttl_sec,
    try_acquire,
)


def test_prune_stale_leases_removes_old_rows(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    leases = {
        "leases": [
            {
                "step_id": "ghost",
                "path_scope": ["src/**"],
                "acquired_at": "2020-01-01T00:00:00+00:00",
                "heartbeat_at": "2020-01-01T00:00:00+00:00",
            },
            {
                "step_id": "fresh",
                "path_scope": ["docs/**"],
                "acquired_at": "2035-01-01T00:00:00+00:00",
                "heartbeat_at": "2035-01-01T00:00:00+00:00",
            },
        ]
    }
    (sess / "leases.json").write_text(json.dumps(leases), encoding="utf-8")
    n = prune_stale_leases(sess, ttl_sec=3600)
    assert n == 1
    body = json.loads((sess / "leases.json").read_text(encoding="utf-8"))
    ids = [r["step_id"] for r in body.get("leases", []) if isinstance(r, dict)]
    assert ids == ["fresh"]


def test_prune_stale_leases_zero_noop(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "leases.json").write_text('{"leases":[]}', encoding="utf-8")
    assert prune_stale_leases(sess, 0) == 0


def test_resolve_lease_ttl_sec_override_and_plan() -> None:
    assert resolve_lease_ttl_sec({"workspace": {"lease_ttl_sec": 120}}, 0) == 0
    assert resolve_lease_ttl_sec({"workspace": {"lease_ttl_sec": 7200}}, None) == 7200
    assert resolve_lease_ttl_sec({}, None) == DEFAULT_LEASE_TTL_SEC


def test_try_acquire_persisted_overlap_blocks(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    held = {
        "leases": [
            {
                "step_id": "other",
                "path_scope": ["src/**"],
                "acquired_at": "2035-06-01T00:00:00+00:00",
                "heartbeat_at": "2035-06-01T00:00:00+00:00",
            }
        ]
    }
    (sess / "leases.json").write_text(json.dumps(held), encoding="utf-8")
    plan_steps = {
        "a": {"path_scope": ["src/**"]},
    }
    ok, reason = try_acquire(
        sess,
        step_id="a",
        path_scopes=["src/foo/**"],
        active_step_ids=["a"],
        plan_steps=plan_steps,
    )
    assert ok is False
    assert reason == "lease_conflict"


def test_try_acquire_persisted_same_tick_peer_skipped(tmp_path: Path) -> None:
    """In-batch overlap is decided via plan_steps, not persisted rows for active ids."""
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "leases.json").write_text('{"leases":[]}', encoding="utf-8")
    plan_steps = {
        "a": {"path_scope": ["src/**"]},
        "b": {"path_scope": ["docs/**"]},
    }
    assert try_acquire(sess, step_id="a", path_scopes=["src/**"], active_step_ids=["a", "b"], plan_steps=plan_steps)[
        0
    ]
    assert try_acquire(sess, step_id="b", path_scopes=["docs/**"], active_step_ids=["a", "b"], plan_steps=plan_steps)[
        0
    ]
