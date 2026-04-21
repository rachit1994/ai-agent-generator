"""Deterministic service-boundaries coverage derivation."""

from __future__ import annotations

from typing import Any

from .contracts import SERVICE_BOUNDARIES_CONTRACT, SERVICE_BOUNDARIES_SCHEMA_VERSION

_OWNERSHIP = {
    "orchestrator": ["traces.jsonl", "orchestration.jsonl", "summary.json", "review.json"],
    "event_store": ["event_store/run_events.jsonl", "replay_manifest.json", "kill_switch_state.json"],
    "memory_system": [
        "memory/retrieval_bundle.json",
        "memory/quarantine.jsonl",
        "memory/quality_metrics.json",
        "capability/skill_nodes.json",
    ],
    "learning_service": [
        "learning/reflection_bundle.json",
        "learning/canary_report.json",
        "learning/transfer_learning_metrics.json",
        "learning/capability_growth_metrics.json",
        "learning/extended_binary_gates.json",
    ],
}


def build_service_boundaries(
    *,
    run_id: str,
    mode: str,
    artifact_manifest: list[dict[str, Any]],
) -> dict[str, Any]:
    present_paths = {
        str(row.get("path"))
        for row in artifact_manifest
        if isinstance(row, dict) and bool(row.get("present")) and isinstance(row.get("path"), str)
    }
    services: dict[str, dict[str, Any]] = {}
    violations: list[dict[str, str]] = []
    for service, paths in _OWNERSHIP.items():
        present_count = sum(1 for path in paths if path in present_paths)
        required_count = len(paths)
        coverage = round((present_count / required_count) if required_count else 0.0, 4)
        missing = [path for path in paths if path not in present_paths]
        for path in missing:
            violations.append({"service": service, "missing_path": path})
        services[service] = {
            "owned_paths": paths,
            "present_count": present_count,
            "required_count": required_count,
            "coverage": coverage,
        }
    status = "bounded" if not violations else "boundary_violation"
    return {
        "schema": SERVICE_BOUNDARIES_CONTRACT,
        "schema_version": SERVICE_BOUNDARIES_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "violations": violations,
        "services": services,
        "evidence": {
            "review_ref": "review.json",
            "boundaries_ref": "strategy/service_boundaries.json",
        },
    }

