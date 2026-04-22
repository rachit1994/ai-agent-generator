"""Deterministic derivation for core observability component health."""

from __future__ import annotations

from typing import Any

from .contracts import OBSERVABILITY_COMPONENT_CONTRACT, OBSERVABILITY_COMPONENT_SCHEMA_VERSION


def execute_observability_runtime(
    *,
    production_observability: dict[str, Any],
    has_run_log: bool,
    has_traces: bool,
    has_orchestration_log: bool,
) -> dict[str, Any]:
    missing_signal_sources: list[str] = []
    if not (isinstance(production_observability, dict) and production_observability.get("status") == "healthy"):
        missing_signal_sources.append("production_observability")
    if has_run_log is not True:
        missing_signal_sources.append("run_log")
    if has_traces is not True:
        missing_signal_sources.append("traces")
    if has_orchestration_log is not True:
        missing_signal_sources.append("orchestration_log")
    return {
        "signals_processed": 4,
        "missing_signal_sources": missing_signal_sources,
        "healthy_production_observability": isinstance(production_observability, dict)
        and production_observability.get("status") == "healthy",
    }


def build_observability_component(
    *,
    run_id: str,
    production_observability: dict[str, Any],
    has_run_log: bool,
    has_traces: bool,
    has_orchestration_log: bool,
) -> dict[str, Any]:
    execution = execute_observability_runtime(
        production_observability=production_observability,
        has_run_log=has_run_log,
        has_traces=has_traces,
        has_orchestration_log=has_orchestration_log,
    )
    has_production_observability = (
        isinstance(production_observability, dict)
        and production_observability.get("status") == "healthy"
    )
    all_checks_passed = (
        has_production_observability and has_run_log and has_traces and has_orchestration_log
    )
    status = "ready" if all_checks_passed else "degraded"
    return {
        "schema": OBSERVABILITY_COMPONENT_CONTRACT,
        "schema_version": OBSERVABILITY_COMPONENT_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "execution": execution,
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
