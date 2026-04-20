"""Select runnable steps with optional multi-lane disjoint path scopes (Category 3)."""

from __future__ import annotations

from typing import Any

from .project_lease import scopes_conflict
from .project_plan import runnable_step_ids


def _normalize_scopes(step_row: dict[str, Any]) -> tuple[list[str], bool]:
    raw_scopes = step_row.get("path_scope")
    if raw_scopes is None:
        return [], False
    if not isinstance(raw_scopes, list):
        return [], True
    out: list[str] = []
    for item in raw_scopes:
        if not isinstance(item, str):
            return [], True
        scope = item.strip()
        if not scope:
            return [], True
        out.append(scope)
    return out, False


def _by_step_id(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in plan.get("steps") or []:
        if isinstance(row, dict) and isinstance(row.get("step_id"), str):
            out[row["step_id"]] = row
    return out


def _conflicts_with_chosen(
    *,
    sid: str,
    by_id: dict[str, dict[str, Any]],
    chosen: list[str],
) -> bool:
    row = by_id.get(sid) or {}
    scopes_str, malformed = _normalize_scopes(row)
    if malformed and chosen:
        return True
    for prev in chosen:
        prow = by_id.get(prev) or {}
        prev_scopes, prev_malformed = _normalize_scopes(prow)
        if malformed or prev_malformed:
            return True
        if scopes_conflict(scopes_str, prev_scopes):
            return True
    return False


def select_steps_for_tick(
    plan: dict[str, Any],
    completed: set[str],
    *,
    max_concurrent_agents: int,
) -> list[str]:
    """
    Return up to ``max_concurrent_agents`` runnable steps whose ``path_scope`` sets are pairwise non-overlapping.

    When scopes overlap, only the first runnable step (plan order) is returned so the driver stays safe on one worktree.
    """
    ready = runnable_step_ids(plan, completed)
    if not isinstance(max_concurrent_agents, int) or isinstance(max_concurrent_agents, bool):
        return []
    if not ready or max_concurrent_agents < 1:
        return []
    by_id = _by_step_id(plan)

    chosen: list[str] = []
    for sid in ready:
        if len(chosen) >= max_concurrent_agents:
            break
        if not _conflicts_with_chosen(sid=sid, by_id=by_id, chosen=chosen):
            chosen.append(sid)
    return chosen
