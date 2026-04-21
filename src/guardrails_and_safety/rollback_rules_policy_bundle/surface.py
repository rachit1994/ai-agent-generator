"""Surface scaffold for `guardrails_and_safety/rollback_rules_policy_bundle`."""

from __future__ import annotations

SUBHEADING = "guardrails_and_safety/rollback_rules_policy_bundle"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "guardrails_and_safety.rollback_rules_policy_bundle.policy_bundle_rollback",
    "guardrails_and_safety.rollback_rules_policy_bundle.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.rollback_rules_policy_bundle_layer",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_policy_bundle_rollback",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
