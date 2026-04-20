"""Surface scaffold for `agent_organization/reviewer_evaluator_agents`."""

from __future__ import annotations

SUBHEADING = "agent_organization/reviewer_evaluator_agents"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "guardrails_and_safety.rollback_rules_policy_bundle.policy_bundle_rollback",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.review",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
    "guardrails_and_safety.review_gating_evaluator_authority.safeguards.safeguards",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
