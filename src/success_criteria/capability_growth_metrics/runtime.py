"""Deterministic capability growth metrics derivation."""

from __future__ import annotations

import math
from typing import Any

from .contracts import (
    CAPABILITY_GROWTH_METRICS_CONTRACT,
    CAPABILITY_GROWTH_METRICS_SCHEMA_VERSION,
)


def _clamp01(value: float) -> float:
    if not math.isfinite(value):
        return 0.0
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _finalize_stats(events: list[dict[str, Any]]) -> tuple[float, float]:
    finals = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    if not finals:
        return 0.0, 0.0
    passed = 0
    reliabilities: list[float] = []
    for row in finals:
        score = row.get("score")
        if not isinstance(score, dict):
            continue
        passed += 1 if score.get("passed") is True else 0
        rel = score.get("reliability", 0.0)
        if isinstance(rel, (int, float)) and not isinstance(rel, bool):
            reliabilities.append(float(rel))
    pass_rate = _clamp01(passed / len(finals))
    reliability = _clamp01((sum(reliabilities) / len(reliabilities)) if reliabilities else 0.0)
    return pass_rate, reliability


def build_capability_growth_metrics(
    *,
    run_id: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    skill_nodes: dict[str, Any] | None,
) -> dict[str, Any]:
    _ = parsed
    pass_rate, reliability = _finalize_stats(events)
    skill_score = 0.0
    if isinstance(skill_nodes, dict):
        nodes = skill_nodes.get("nodes")
        if isinstance(nodes, list) and nodes and isinstance(nodes[0], dict):
            score = nodes[0].get("score")
            if isinstance(score, (int, float)) and not isinstance(score, bool):
                skill_score = float(score)
    skill_score = _clamp01(skill_score)
    capability_growth_rate = _clamp01((0.5 * skill_score) + (0.5 * pass_rate))
    capability_stability_rate = _clamp01((0.6 * reliability) + (0.4 * (1.0 - abs(skill_score - pass_rate))))
    promotion_readiness_delta = round(capability_growth_rate - 0.5, 4)
    growth_confidence = _clamp01((0.7 * capability_stability_rate) + (0.3 * capability_growth_rate))
    return {
        "schema": CAPABILITY_GROWTH_METRICS_CONTRACT,
        "schema_version": CAPABILITY_GROWTH_METRICS_SCHEMA_VERSION,
        "run_id": run_id,
        "metrics": {
            "capability_growth_rate": capability_growth_rate,
            "capability_stability_rate": capability_stability_rate,
            "promotion_readiness_delta": promotion_readiness_delta,
            "growth_confidence": growth_confidence,
        },
        "evidence": {"traces_ref": "traces.jsonl", "skill_nodes_ref": "capability/skill_nodes.json"},
    }

