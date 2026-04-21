"""Deterministic topology and repository layout derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    TOPOLOGY_AND_REPOSITORY_LAYOUT_CONTRACT,
    TOPOLOGY_AND_REPOSITORY_LAYOUT_SCHEMA_VERSION,
)

_REQUIRED_PREFIXES = {
    "implementation_roadmap": [
        "program/production_readiness.json",
        "program/consolidated_improvements.json",
        "program/implementation_roadmap.json",
    ],
    "scalability_strategy": ["strategy/scalability_strategy.json", "strategy/service_boundaries.json"],
    "core_components": [
        "event_store/component_runtime.json",
        "orchestrator/component_runtime.json",
        "iam/identity_authz_plane.json",
        "learning/learning_service.json",
        "memory/memory_system.json",
        "strategy/career_strategy_layer.json",
        "strategy/objective_policy_engine.json",
        "practice/practice_engine.json",
        "learning/self_learning_loop.json",
        "safety/controller_runtime.json",
        "evaluation/service_runtime.json",
        "observability/component_runtime.json",
    ],
    "success_criteria": ["learning/transfer_learning_metrics.json", "learning/error_reduction_metrics.json"],
    "workflow_pipelines": [
        "traces.jsonl",
        "traces/event_row_runtime.json",
        "orchestration.jsonl",
        "orchestration/run_start_runtime.json",
        "orchestration/stage_event_runtime.json",
        "orchestration/run_error_runtime.json",
        "orchestration/run_end_runtime.json",
        "run-manifest.json",
        "program/run_manifest_runtime.json",
        "program/retry_repeat_profile_runtime.json",
    ],
}


def build_topology_and_repository_layout(
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
    topology: dict[str, dict[str, Any]] = {}
    all_ok = True
    for pillar, required in _REQUIRED_PREFIXES.items():
        present = sum(1 for path in required if path in present_paths)
        total = len(required)
        coverage = round((present / total) if total else 0.0, 4)
        topology[pillar] = {
            "required_prefixes": required,
            "present_count": present,
            "required_count": total,
            "coverage": coverage,
        }
        if coverage < 1.0:
            all_ok = False
    status = "ready" if all_ok else "not_ready"
    required_run_artifacts = [
        {"path": path, "present": path in present_paths}
        for path in sorted({path for required in _REQUIRED_PREFIXES.values() for path in required})
    ]
    missing_paths = [row["path"] for row in required_run_artifacts if not row["present"]]
    return {
        "schema": TOPOLOGY_AND_REPOSITORY_LAYOUT_CONTRACT,
        "schema_version": TOPOLOGY_AND_REPOSITORY_LAYOUT_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "topology": topology,
        "repository_layout": {
            "required_run_artifacts": required_run_artifacts,
            "missing_paths": missing_paths,
        },
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "topology_ref": "program/topology_and_repository_layout.json",
        },
    }

