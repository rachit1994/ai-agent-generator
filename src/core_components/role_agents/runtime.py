"""Deterministic role-agents artifact derivation."""

from __future__ import annotations

from typing import Any

from .contracts import ROLE_AGENTS_CONTRACT, ROLE_AGENTS_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def build_role_agents(
    *,
    run_id: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    skill_nodes: dict[str, Any],
) -> dict[str, Any]:
    checks = parsed.get("checks") if isinstance(parsed, dict) else []
    if not isinstance(checks, list):
        checks = []
    planner_score = _clamp01(
        sum(1 for row in checks if isinstance(row, dict) and bool(row.get("passed")))
        / max(1, len(checks))
    )
    finalize_rows = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    implementor_score = _clamp01(
        sum(
            1
            for row in finalize_rows
            if isinstance(row.get("score"), dict) and bool(row.get("score", {}).get("passed"))
        )
        / max(1, len(finalize_rows))
    )
    verifier_score = 0.0
    nodes = skill_nodes.get("nodes") if isinstance(skill_nodes, dict) else []
    if isinstance(nodes, list) and nodes and isinstance(nodes[0], dict):
        raw = nodes[0].get("score")
        if isinstance(raw, (int, float)) and not isinstance(raw, bool):
            verifier_score = _clamp01(float(raw))
    spread = max(planner_score, implementor_score, verifier_score) - min(
        planner_score, implementor_score, verifier_score
    )
    status = "balanced"
    if len(finalize_rows) == 0 and len(checks) == 0:
        status = "insufficient_signal"
    elif spread > 0.35:
        status = "drifted"
    return {
        "schema": ROLE_AGENTS_CONTRACT,
        "schema_version": ROLE_AGENTS_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "role_scores": {
            "planner": planner_score,
            "implementor": implementor_score,
            "verifier": verifier_score,
        },
        "evidence": {
            "summary_ref": "summary.json",
            "traces_ref": "traces.jsonl",
            "skill_nodes_ref": "capability/skill_nodes.json",
            "role_agents_ref": "capability/role_agents.json",
        },
    }
