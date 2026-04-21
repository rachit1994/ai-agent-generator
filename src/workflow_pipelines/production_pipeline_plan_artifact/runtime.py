"""Deterministic derivation for production pipeline plan artifact."""

from __future__ import annotations

from typing import Any

from .contracts import (
    PRODUCTION_PIPELINE_PLAN_ARTIFACT_CONTRACT,
    PRODUCTION_PIPELINE_PLAN_ARTIFACT_SCHEMA_VERSION,
)


def build_production_pipeline_plan_artifact(
    *,
    run_id: str,
    mode: str,
    program_manifest: dict[str, bool],
    project_plan: dict[str, Any],
) -> dict[str, Any]:
    checks = {
        "project_plan_present": bool(program_manifest.get("project_plan")),
        "progress_present": bool(program_manifest.get("progress")),
        "work_batch_present": bool(program_manifest.get("work_batch")),
        "discovery_present": bool(program_manifest.get("discovery")),
        "verification_bundle_present": bool(program_manifest.get("verification_bundle")),
    }
    steps = project_plan.get("steps") if isinstance(project_plan, dict) else []
    step_count = len(steps) if isinstance(steps, list) else 0
    status = "ready" if all(checks.values()) and step_count > 0 else "partial"
    return {
        "schema": PRODUCTION_PIPELINE_PLAN_ARTIFACT_CONTRACT,
        "schema_version": PRODUCTION_PIPELINE_PLAN_ARTIFACT_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "checks": checks,
        "metrics": {
            "step_count": step_count,
            "checked_program_artifacts": len(checks),
        },
        "evidence": {
            "project_plan_ref": "program/project_plan.json",
            "progress_ref": "program/progress.json",
            "work_batch_ref": "program/work_batch.json",
            "discovery_ref": "program/discovery.json",
            "verification_bundle_ref": "program/verification_bundle.json",
            "production_pipeline_plan_artifact_ref": "program/production_pipeline_plan_artifact.json",
        },
    }
