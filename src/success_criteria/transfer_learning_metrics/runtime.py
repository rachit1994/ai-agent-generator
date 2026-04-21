"""Deterministic transfer learning metrics derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    TRANSFER_LEARNING_METRICS_CONTRACT,
    TRANSFER_LEARNING_METRICS_SCHEMA_VERSION,
)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _is_passed(value: Any) -> bool:
    return value is True


def _finalize_pass_rate(events: list[dict[str, Any]]) -> float:
    finals = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    if not finals:
        return 0.0
    passed = 0
    for row in finals:
        score = row.get("score")
        if isinstance(score, dict) and _is_passed(score.get("passed")):
            passed += 1
    return _clamp01(passed / len(finals))


def build_transfer_learning_metrics(
    *,
    run_id: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    skill_nodes: dict[str, Any] | None,
) -> dict[str, Any]:
    if not run_id.strip():
        raise ValueError("transfer_learning_metrics_run_id")
    _ = parsed
    pass_rate = _finalize_pass_rate(events)
    capability_score = 0.0
    if isinstance(skill_nodes, dict):
        nodes = skill_nodes.get("nodes")
        if isinstance(nodes, list) and nodes and isinstance(nodes[0], dict):
            raw = nodes[0].get("score")
            if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                capability_score = float(raw)
    capability_score = _clamp01(capability_score)
    transfer_gain_rate = _clamp01((0.6 * capability_score) + (0.4 * pass_rate))
    negative_transfer_rate = _clamp01(max(0.0, 0.5 - transfer_gain_rate) / 2.0)
    retained_success_rate = _clamp01(min(pass_rate, capability_score))
    net_transfer_points = round((transfer_gain_rate - negative_transfer_rate) * 100.0, 4)
    transfer_efficiency_score = _clamp01(
        0.5 * transfer_gain_rate + 0.3 * retained_success_rate + 0.2 * (1.0 - negative_transfer_rate)
    )
    return {
        "schema": TRANSFER_LEARNING_METRICS_CONTRACT,
        "schema_version": TRANSFER_LEARNING_METRICS_SCHEMA_VERSION,
        "run_id": run_id,
        "metrics": {
            "transfer_gain_rate": transfer_gain_rate,
            "negative_transfer_rate": negative_transfer_rate,
            "retained_success_rate": retained_success_rate,
            "net_transfer_points": net_transfer_points,
            "transfer_efficiency_score": transfer_efficiency_score,
        },
        "evidence": {"traces_ref": "traces.jsonl", "skill_nodes_ref": "capability/skill_nodes.json"},
    }

