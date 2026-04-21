"""Deterministic implementation-roadmap derivation."""

from __future__ import annotations

from typing import Any

from .contracts import IMPLEMENTATION_ROADMAP_CONTRACT, IMPLEMENTATION_ROADMAP_SCHEMA_VERSION


def build_implementation_roadmap(
    *,
    run_id: str,
    mode: str,
    summary: dict[str, Any],
    review: dict[str, Any],
    production_readiness: dict[str, Any],
    topology_layout: dict[str, Any],
    consolidated_improvements: dict[str, Any],
    closure_plan: dict[str, Any],
) -> dict[str, Any]:
    milestones = {
        "production_readiness_present": bool(production_readiness),
        "topology_layout_present": bool(topology_layout),
        "consolidated_improvements_present": bool(consolidated_improvements),
        "closure_plan_present": bool(closure_plan),
    }
    balanced = summary.get("balanced_gates") if isinstance(summary, dict) else {}
    review_pass = bool(review.get("status") == "completed_review_pass") if isinstance(review, dict) else False
    validation_ready = bool(isinstance(balanced, dict) and balanced.get("validation_ready"))
    status = "on_track" if all(milestones.values()) and review_pass and validation_ready else "at_risk"
    return {
        "schema": IMPLEMENTATION_ROADMAP_CONTRACT,
        "schema_version": IMPLEMENTATION_ROADMAP_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "milestones": milestones,
        "signals": {
            "review_pass": review_pass,
            "validation_ready": validation_ready,
        },
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "production_readiness_ref": "program/production_readiness.json",
            "topology_layout_ref": "program/topology_and_repository_layout.json",
            "consolidated_improvements_ref": "program/consolidated_improvements.json",
            "closure_plan_ref": "program/closure_security_reliability_scalability_plans.json",
            "implementation_roadmap_ref": "program/implementation_roadmap.json",
        },
    }
