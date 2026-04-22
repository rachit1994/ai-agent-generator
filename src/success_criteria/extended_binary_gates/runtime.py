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


def _is_passed(value: Any) -> bool:
    return value is True


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
        passed += 1 if _is_passed(score.get("passed")) else 0
        reliability = score.get("reliability")
        if isinstance(reliability, (int, float)) and not isinstance(reliability, bool):
            reliability_values.append(float(reliability))
    pass_rate = _clamp01(passed / len(finals))
    reliability_rate = _clamp01(
        (sum(reliability_values) / len(reliability_values)) if reliability_values else 0.0
    )
    return pass_rate, reliability_rate


def _valid_binary_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "stage", "score")
    if not all(key in event for key in required):
        return False
    if event.get("stage") != "finalize":
        return False
    return isinstance(event.get("score"), dict)


def execute_extended_binary_runtime(*, parsed: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    finalize_events = [event for event in events if _valid_binary_event(event)]
    malformed_event_rows = len(events) - len(finalize_events)
    strict_boolean_violations: list[str] = []
    for event in finalize_events:
        passed = event["score"].get("passed")
        if passed is not True and passed is not False:
            strict_boolean_violations.append(str(event["event_id"]))
    checks = parsed.get("checks") if isinstance(parsed, dict) else []
    check_count = len(checks) if isinstance(checks, list) else 0
    return {
        "events_processed": len(events),
        "finalize_events_processed": len(finalize_events),
        "malformed_event_rows": malformed_event_rows,
        "strict_boolean_violations": strict_boolean_violations,
        "checks_processed": check_count,
    }


def build_extended_binary_gates(
    *,
    run_id: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    skill_nodes: dict[str, Any] | None,
) -> dict[str, Any]:
    execution = execute_extended_binary_runtime(parsed=parsed, events=events)
    checks = parsed.get("checks") if isinstance(parsed, dict) else []
    if not isinstance(checks, list):
        checks = []
    governance_checks = [
        row for row in checks if isinstance(row, dict) and row.get("name") != "review"
    ]
    total_checks = len(governance_checks)
    passed_checks = sum(
        1 for row in governance_checks if _is_passed(row.get("passed"))
    )
    governance_rate = _clamp01((passed_checks / total_checks) if total_checks else 0.0)
    pass_rate, reliability_rate = _finalize_signals(events)
    learning_score = 0.0
    if isinstance(skill_nodes, dict):
        nodes = skill_nodes.get("nodes")
        if isinstance(nodes, list):
            valid_scores = [
                float(node.get("score"))
                for node in nodes
                if isinstance(node, dict)
                and isinstance(node.get("score"), (int, float))
                and not isinstance(node.get("score"), bool)
            ]
            if valid_scores:
                learning_score = max(valid_scores)
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
        "execution": execution,
        "gates": gates,
        "evidence": {
            "traces_ref": "traces.jsonl",
            "checks_ref": "summary.json",
            "skill_nodes_ref": "capability/skill_nodes.json",
        },
    }

