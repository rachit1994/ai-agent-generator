"""Deterministic core-orchestrator runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import ORCHESTRATOR_COMPONENT_CONTRACT, ORCHESTRATOR_COMPONENT_SCHEMA_VERSION


def build_orchestrator_component(
    *,
    run_id: str,
    run_manifest: dict[str, Any],
    run_manifest_runtime: dict[str, Any],
    has_traces: bool,
    has_orchestration_log: bool,
) -> dict[str, Any]:
    has_run_manifest = bool(run_manifest)
    has_run_manifest_runtime = bool(run_manifest_runtime)
    status = "ready" if has_run_manifest and has_run_manifest_runtime and has_traces and has_orchestration_log else "degraded"
    return {
        "schema": ORCHESTRATOR_COMPONENT_CONTRACT,
        "schema_version": ORCHESTRATOR_COMPONENT_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "metrics": {
            "has_run_manifest": has_run_manifest,
            "has_run_manifest_runtime": has_run_manifest_runtime,
            "has_traces": has_traces,
            "has_orchestration_log": has_orchestration_log,
        },
        "evidence": {
            "run_manifest_ref": "run-manifest.json",
            "run_manifest_runtime_ref": "program/run_manifest_runtime.json",
            "traces_ref": "traces.jsonl",
            "orchestration_ref": "orchestration.jsonl",
            "orchestrator_component_ref": "orchestrator/component_runtime.json",
        },
    }
