"""Plan graph: runnable steps, cycle detection, completion."""

from __future__ import annotations

from typing import Any


def _step_by_id(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in plan.get("steps") or []:
        if isinstance(row, dict) and isinstance(row.get("step_id"), str):
            out[row["step_id"]] = row
    return out


def detect_dependency_cycle(plan: dict[str, Any]) -> list[str] | None:
    """Return two nodes that prove a cycle, or None if acyclic (missing deps ignored)."""
    by_id = _step_by_id(plan)
    white, gray, black = 0, 1, 2
    color: dict[str, int] = {n: white for n in by_id}

    def dfs(n: str) -> list[str] | None:
        color[n] = gray
        for m in by_id[n].get("depends_on") or []:
            if not isinstance(m, str) or m not in by_id:
                continue
            if color[m] == gray:
                return [n, m]
            if color[m] == white:
                cyc = dfs(m)
                if cyc:
                    return cyc
        color[n] = black
        return None

    for n in by_id:
        if color[n] == white:
            cyc = dfs(n)
            if cyc:
                return cyc
    return None


def runnable_step_ids(plan: dict[str, Any], completed: set[str]) -> list[str]:
    """Return step_ids ready to run, in plan order (stable)."""
    by_id = _step_by_id(plan)
    out: list[str] = []
    for row in plan.get("steps") or []:
        if not isinstance(row, dict):
            continue
        sid = row.get("step_id")
        if not isinstance(sid, str) or sid in completed:
            continue
        deps = row.get("depends_on") or []
        if not isinstance(deps, list):
            continue
        ok = all(isinstance(d, str) and d in completed for d in deps)
        if ok:
            out.append(sid)
    return out


def all_steps_complete(plan: dict[str, Any], completed: set[str]) -> bool:
    by_id = _step_by_id(plan)
    return bool(by_id) and all(sid in completed for sid in by_id)


def plan_step_ids(plan: dict[str, Any]) -> list[str]:
    """Stable list of all ``step_id`` values in plan order."""
    out: list[str] = []
    for row in plan.get("steps") or []:
        if isinstance(row, dict) and isinstance(row.get("step_id"), str):
            out.append(row["step_id"])
    return out
