"""Surface metadata for closure/security/reliability/scalability plans."""

from __future__ import annotations

SUBHEADING = "implementation_roadmap/closure_security_reliability_scalability_plans"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "implementation_roadmap.closure_security_reliability_scalability_plans.runtime",
    "implementation_roadmap.closure_security_reliability_scalability_plans.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.closure_security_reliability_scalability_plans_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }

