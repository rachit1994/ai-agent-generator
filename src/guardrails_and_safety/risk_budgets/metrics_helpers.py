"""Metrics derived from trace events for gates."""

from __future__ import annotations

from typing import Any


def metrics_from_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    from sde_eval.eval import aggregate_metrics

    return aggregate_metrics(events)


def reliability_gate(metrics: dict[str, Any]) -> bool:
    return float(metrics.get("reliability", 0)) >= 0.85
