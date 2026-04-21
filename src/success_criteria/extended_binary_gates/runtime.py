"""Deterministic extended binary gates derivation."""

from __future__ import annotations

from typing import Any

from .contracts import EXTENDED_BINARY_GATES_CONTRACT, EXTENDED_BINARY_GATES_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _finalize_signals(events: list[dict[str, Any]]) -> tuple[float, float]:
    finals = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    if not finals:
        return 0.0, 0.0
    passed = 0
    reliability_values: list[float] = []
    for row in finals:
        score = row.get("score")
        if not isinstance(score, dict):
            continue
        passed += 1 if bool(score.get("passed")) else 0
        reliability = score.get("reliability")
        if isinstance(reliability, (int, float)) and not isinstance(reliability, bool):
            reliability_values.append(float(reliability))
    pass_rate = _clamp01(passed / len(finals))
    reliability_rate = _clamp01(
        (sum(reliability_values) / len(reliability_values)) if reliability_values else 0.0
    )
    return pass_rate, reliability_rate


def build_extended_binary_gates(
    *,
    run_id: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    skill_nodes: dict[str, Any] | None,
) -> dict[str, Any]:
    checks = parsed.get("checks") if isinstance(parsed, dict) else []
    if not isinstance(checks, list):
        checks = []
    total_checks = len(checks)
    passed_checks = sum(
        1 for row in checks if isinstance(row, dict) and bool(row.get("passed")) and row.get("name") != "review"
    )
    governance_rate = _clamp01((passed_checks / total_checks) if total_checks else 0.0)
    pass_rate, reliability_rate = _finalize_signals(events)
    learning_score = 0.0
    if isinstance(skill_nodes, dict):
        nodes = skill_nodes.get("nodes")
        if isinstance(nodes, list) and nodes and isinstance(nodes[0], dict):
            raw = nodes[0].get("score")
            if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                learning_score = float(raw)
    learning_score = _clamp01(learning_score)
    gates = {
        "reliability_gate": reliability_rate >= 0.85,
        "delivery_gate": pass_rate >= 0.85,
        "governance_gate": governance_rate >= 0.85,
        "learning_gate": learning_score >= 0.6,
    }
    return {
        "schema": EXTENDED_BINARY_GATES_CONTRACT,
        "schema_version": EXTENDED_BINARY_GATES_SCHEMA_VERSION,
        "run_id": run_id,
        "overall_pass": all(gates.values()),
        "gates": gates,
        "evidence": {
            "traces_ref": "traces.jsonl",
            "checks_ref": "summary.json",
            "skill_nodes_ref": "capability/skill_nodes.json",
        },
    }

