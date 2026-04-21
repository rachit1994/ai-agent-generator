"""Deterministic local-runtime CLI spine derivation."""

from __future__ import annotations

from .contracts import (
    LOCAL_RUNTIME_SPINE_CONTRACT,
    LOCAL_RUNTIME_SPINE_SCHEMA_VERSION,
)


def build_local_runtime_spine(
    *,
    run_id: str,
    mode: str,
    has_run_manifest: bool,
    has_orchestration: bool,
    has_traces: bool,
) -> dict[str, object]:
    status = "ready" if has_run_manifest and has_orchestration and has_traces else "degraded"
    return {
        "schema": LOCAL_RUNTIME_SPINE_CONTRACT,
        "schema_version": LOCAL_RUNTIME_SPINE_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "checks": {
            "has_run_manifest": has_run_manifest,
            "has_orchestration": has_orchestration,
            "has_traces": has_traces,
        },
        "evidence": {
            "run_manifest_ref": "run-manifest.json",
            "orchestration_ref": "orchestration.jsonl",
            "traces_ref": "traces.jsonl",
            "spine_ref": "orchestrator/local_runtime_spine.json",
        },
    }
