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


def _passed(value: Any) -> bool:
    return value is True


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
    scored_checks = [
        row for row in checks if isinstance(row, dict) and row.get("name") != "review"
    ]
    planner_score = _clamp01(
        sum(1 for row in scored_checks if _passed(row.get("passed")))
        / max(1, len(scored_checks))
    )
    finalize_rows = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    implementor_score = _clamp01(
        sum(
            1
            for row in finalize_rows
            if isinstance(row.get("score"), dict)
            and _passed(row.get("score", {}).get("passed"))
        )
        / max(1, len(finalize_rows))
    )
    verifier_score = 0.0
    nodes = skill_nodes.get("nodes") if isinstance(skill_nodes, dict) else []
    if isinstance(nodes, list):
        valid_scores = [
            float(node.get("score"))
            for node in nodes
            if isinstance(node, dict)
            and isinstance(node.get("score"), (int, float))
            and not isinstance(node.get("score"), bool)
        ]
        if valid_scores:
            verifier_score = _clamp01(max(valid_scores))
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
