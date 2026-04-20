"""Session-scoped path leases (Category 3 MVP — serial lane default)."""

from __future__ import annotations

import fnmatch
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import iso_now

DEFAULT_LEASE_TTL_SEC = 86_400


def _parse_iso_utc(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def prune_stale_leases(session_dir: Path, ttl_sec: int) -> int:
    """
    Remove lease rows whose ``heartbeat_at`` / ``acquired_at`` is older than ``ttl_sec``.

    Returns the number of rows removed. No-op when ``ttl_sec`` <= 0.
    """
    if ttl_sec <= 0:
        return 0
    path = session_dir / "leases.json"
    body = _load(path)
    leases = body.get("leases")
    if not isinstance(leases, list):
        return 0
    now = datetime.now(timezone.utc).replace(microsecond=0)
    kept: list[dict[str, Any]] = []
    removed = 0
    for row in leases:
        if not isinstance(row, dict):
            continue
        ts = row.get("heartbeat_at") or row.get("acquired_at")
        if not isinstance(ts, str):
            kept.append(row)
            continue
        dt = _parse_iso_utc(ts)
        if dt is None:
            kept.append(row)
            continue
        age_sec = (now - dt).total_seconds()
        if age_sec > ttl_sec:
            removed += 1
        else:
            kept.append(row)
    body["leases"] = kept
    _save(path, body)
    return removed


def resolve_lease_ttl_sec(plan: dict[str, Any], override: int | None) -> int:
    """
    Seconds before a lease row is treated as stale and pruned each driver tick.

    ``override`` from CLI: ``None`` → plan or ``DEFAULT_LEASE_TTL_SEC``; ``0`` → disable pruning.
    """
    if override is not None:
        return max(0, int(override))
    ws = plan.get("workspace")
    if isinstance(ws, dict):
        v = ws.get("lease_ttl_sec")
        if isinstance(v, int) and v > 0:
            return v
    return DEFAULT_LEASE_TTL_SEC


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"leases": []}
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
        return body if isinstance(body, dict) else {"leases": []}
    except json.JSONDecodeError:
        return {"leases": []}


def _save(path: Path, body: dict[str, Any]) -> None:
    path.write_text(json.dumps(body, indent=2), encoding="utf-8")


def _patterns_overlap(a: str, b: str) -> bool:
    """Conservative overlap check for glob-ish path scopes."""
    if a == b:
        return True
    if fnmatch.fnmatch(a, b) or fnmatch.fnmatch(b, a):
        return True
    return a.rstrip("/") in b or b.rstrip("/") in a


def scopes_conflict(scopes_a: list[str], scopes_b: list[str]) -> bool:
    for x in scopes_a:
        for y in scopes_b:
            if _patterns_overlap(x.rstrip("/"), y.rstrip("/")):
                return True
    return False


def try_acquire(
    session_dir: Path,
    *,
    step_id: str,
    path_scopes: list[str],
    active_step_ids: list[str],
    plan_steps: dict[str, dict[str, Any]],
) -> tuple[bool, str | None]:
    """
    Return (ok, reason). Fails with ``lease_conflict`` if another step overlaps paths
    (in-batch peers or **persisted** lease rows left from a prior crash).
    """
    path = session_dir / "leases.json"
    body = _load(path)
    leases = body.get("leases")
    if not isinstance(leases, list):
        leases = []
    active_set = set(active_step_ids)
    for row in leases:
        if not isinstance(row, dict):
            continue
        oid = row.get("step_id")
        if not isinstance(oid, str) or oid == step_id:
            continue
        if oid in active_set:
            continue
        os_raw = row.get("path_scope") or []
        if not isinstance(os_raw, list):
            os_raw = []
        os_str = [str(s) for s in os_raw if isinstance(s, str)]
        if scopes_conflict(path_scopes, os_str):
            return False, "lease_conflict"
    for other in active_step_ids:
        if other == step_id:
            continue
        other_row = plan_steps.get(other) or {}
        other_scopes = other_row.get("path_scope") or []
        if not isinstance(other_scopes, list):
            other_scopes = []
        os_str = [str(s) for s in other_scopes if isinstance(s, str)]
        if scopes_conflict(path_scopes, os_str):
            return False, "lease_conflict"
    now = iso_now()
    row = {
        "step_id": step_id,
        "path_scope": path_scopes,
        "acquired_at": now,
        "heartbeat_at": now,
    }
    leases = [x for x in leases if isinstance(x, dict) and x.get("step_id") != step_id]
    leases.append(row)
    body["leases"] = leases
    _save(path, body)
    return True, None


def touch_lease_heartbeat(session_dir: Path, step_id: str) -> None:
    """Update ``heartbeat_at`` for an active lease (Phase 6 / V7-style liveness)."""
    path = session_dir / "leases.json"
    body = _load(path)
    leases = body.get("leases")
    if not isinstance(leases, list):
        return
    now = iso_now()
    for row in leases:
        if isinstance(row, dict) and row.get("step_id") == step_id:
            row["heartbeat_at"] = now
            break
    body["leases"] = leases
    _save(path, body)


def release(session_dir: Path, step_id: str) -> None:
    path = session_dir / "leases.json"
    body = _load(path)
    leases = [x for x in body.get("leases", []) if isinstance(x, dict) and x.get("step_id") != step_id]
    body["leases"] = leases
    _save(path, body)
