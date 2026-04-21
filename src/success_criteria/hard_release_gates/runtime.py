"""Deterministic hard release gates derivation."""

from __future__ import annotations

from typing import Any

from .contracts import HARD_RELEASE_GATES_CONTRACT, HARD_RELEASE_GATES_SCHEMA_VERSION


def _clamp_percent(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 100.0:
        return 100.0
    return round(value, 2)


def _derive_governance_from_checks(checks: list[dict[str, Any]]) -> float:
    non_review_checks = [row for row in checks if isinstance(row, dict) and row.get("name") != "review"]
    check_total = len(non_review_checks)
    check_passed = sum(1 for row in non_review_checks if bool(row.get("passed")))
    return _clamp_percent((100.0 * check_passed / check_total) if check_total else 0.0)


def _derive_finalize_scores(events: list[dict[str, Any]]) -> tuple[float, float]:
    finals = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    finalize_total = len(finals)
    finalize_passed = 0
    reliability_values: list[float] = []
    for row in finals:
        score = row.get("score")
        if not isinstance(score, dict):
            continue
        finalize_passed += 1 if bool(score.get("passed")) else 0
        reliability = score.get("reliability")
        if isinstance(reliability, (int, float)) and not isinstance(reliability, bool):
            reliability_values.append(float(reliability) * 100.0)
    delivery = _clamp_percent((100.0 * finalize_passed / finalize_total) if finalize_total else 0.0)
    reliability = _clamp_percent(
        (sum(reliability_values) / len(reliability_values)) if reliability_values else 0.0
    )
    return reliability, delivery


def _collect_failed_hard_stop_ids(parsed: dict[str, Any]) -> list[str]:
    hard_stops = parsed.get("hard_stops") if isinstance(parsed, dict) else []
    if not isinstance(hard_stops, list):
        hard_stops = []
    failed_hard_stop_ids: list[str] = []
    for row in hard_stops:
        if not isinstance(row, dict):
            continue
        if bool(row.get("passed")):
            continue
        hs_id = row.get("id")
        if isinstance(hs_id, str) and hs_id.strip():
            failed_hard_stop_ids.append(hs_id.strip())
    return sorted(set(failed_hard_stop_ids))


def build_hard_release_gates(
    *,
    run_id: str,
    mode: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    checks = parsed.get("checks") if isinstance(parsed, dict) else []
    if not isinstance(checks, list):
        checks = []
    governance = _derive_governance_from_checks(checks)
    reliability, delivery = _derive_finalize_scores(events)
    composite = _clamp_percent((reliability + delivery + governance) / 3.0)
    gates = {
        "reliability_gate": reliability >= 85.0,
        "delivery_gate": delivery >= 85.0,
        "governance_gate": governance >= 85.0,
        "composite_gate": composite >= 90.0,
    }
    failed_hard_stop_ids = _collect_failed_hard_stop_ids(parsed)
    overall_pass = all(gates.values()) and len(failed_hard_stop_ids) == 0
    return {
        "schema": HARD_RELEASE_GATES_CONTRACT,
        "schema_version": HARD_RELEASE_GATES_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "overall_pass": overall_pass,
        "validation_ready": overall_pass,
        "gates": gates,
        "failed_hard_stop_ids": failed_hard_stop_ids,
        "scores": {
            "reliability": reliability,
            "delivery": delivery,
            "governance": governance,
            "composite": composite,
        },
        "evidence": {
            "summary_ref": "summary.json",
            "traces_ref": "traces.jsonl",
            "hard_release_gates_ref": "learning/hard_release_gates.json",
        },
    }
