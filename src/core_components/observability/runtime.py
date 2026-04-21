"""Deterministic derivation for core observability component health."""

from __future__ import annotations

from typing import Any

from .contracts import OBSERVABILITY_COMPONENT_CONTRACT, OBSERVABILITY_COMPONENT_SCHEMA_VERSION


def build_observability_component(
    *,
    run_id: str,
    production_observability: dict[str, Any],
    has_run_log: bool,
    has_traces: bool,
    has_orchestration_log: bool,
) -> dict[str, Any]:
    has_production_observability = bool(production_observability)
    all_checks_passed = (
        has_production_observability and has_run_log and has_traces and has_orchestration_log
    )
    status = "ready" if all_checks_passed else "degraded"
    return {
        "schema": OBSERVABILITY_COMPONENT_CONTRACT,
        "schema_version": OBSERVABILITY_COMPONENT_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "metrics": {
            "has_production_observability": has_production_observability,
            "has_run_log": has_run_log,
            "has_traces": has_traces,
            "has_orchestration_log": has_orchestration_log,
            "all_checks_passed": all_checks_passed,
        },
        "evidence": {
            "production_observability_ref": "observability/production_observability.json",
            "run_log_ref": "run.log",
            "traces_ref": "traces.jsonl",
            "orchestration_ref": "orchestration.jsonl",
            "component_ref": "observability/component_runtime.json",
        },
    }
