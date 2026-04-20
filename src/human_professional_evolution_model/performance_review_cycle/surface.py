"""Surface scaffold for `human_professional_evolution_model/performance_review_cycle`."""

from __future__ import annotations

SUBHEADING = "human_professional_evolution_model/performance_review_cycle"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "guardrails_and_safety.rollback_rules_policy_bundle.policy_bundle_rollback",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.review",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
    "guardrails_and_safety.review_gating_evaluator_authority.safeguards.safeguards",
    "production_architecture.local_runtime.orchestrator.api.gemma_roadmap_review",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
