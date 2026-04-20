"""Surface scaffold for `core_components/safety_controller`."""

from __future__ import annotations

SUBHEADING = "core_components/safety_controller"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "guardrails_and_safety.autonomy_boundaries.autonomy_boundaries_tokens_expiry.token_context",
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
