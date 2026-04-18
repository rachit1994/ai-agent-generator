"""Select runnable steps with optional multi-lane disjoint path scopes (Category 3)."""

from __future__ import annotations

from typing import Any

from .project_lease import scopes_conflict
from .project_plan import runnable_step_ids


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
    if not ready or max_concurrent_agents < 1:
        return []
    by_id: dict[str, dict[str, Any]] = {}
    for row in plan.get("steps") or []:
        if isinstance(row, dict) and isinstance(row.get("step_id"), str):
            by_id[row["step_id"]] = row

    chosen: list[str] = []
    for sid in ready:
        if len(chosen) >= max_concurrent_agents:
            break
        row = by_id.get(sid) or {}
        scopes = row.get("path_scope") or []
        if not isinstance(scopes, list):
            scopes = []
        scopes_str = [str(s) for s in scopes if isinstance(s, str)]
        conflict = False
        for prev in chosen:
            prow = by_id.get(prev) or {}
            ps = prow.get("path_scope") or []
            if not isinstance(ps, list):
                ps = []
            prev_scopes = [str(s) for s in ps if isinstance(s, str)]
            if scopes_conflict(scopes_str, prev_scopes):
                conflict = True
                break
        if not conflict:
            chosen.append(sid)
    return chosen
