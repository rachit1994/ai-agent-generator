"""Deterministic error reduction metrics derivation."""

from __future__ import annotations

from typing import Any

from .contracts import ERROR_REDUCTION_METRICS_CONTRACT, ERROR_REDUCTION_METRICS_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _is_passed(value: Any) -> bool:
    return value is True


def build_error_reduction_metrics(
    *,
    run_id: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    skill_nodes: dict[str, Any] | None,
) -> dict[str, Any]:
    _ = skill_nodes
    checks = parsed.get("checks") if isinstance(parsed, dict) else []
    if not isinstance(checks, list):
        checks = []
    baseline_errors = sum(
        1 for row in checks if isinstance(row, dict) and (not _is_passed(row.get("passed")))
    )
    finals = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    candidate_errors = 0
    for row in finals:
        score = row.get("score")
        if not isinstance(score, dict):
            candidate_errors += 1
            continue
        if not _is_passed(score.get("passed")):
            candidate_errors += 1
    resolved = baseline_errors - candidate_errors
    if resolved < 0:
        resolved = 0
    error_reduction_rate = _clamp01((resolved / baseline_errors) if baseline_errors else 0.0)
    net_error_delta = float(candidate_errors - baseline_errors)
    return {
        "schema": ERROR_REDUCTION_METRICS_CONTRACT,
        "schema_version": ERROR_REDUCTION_METRICS_SCHEMA_VERSION,
        "run_id": run_id,
        "metrics": {
            "baseline_error_count": baseline_errors,
            "candidate_error_count": candidate_errors,
            "resolved_error_count": resolved,
            "error_reduction_rate": error_reduction_rate,
            "net_error_delta": net_error_delta,
        },
        "evidence": {"traces_ref": "traces.jsonl", "summary_ref": "summary.json"},
    }

