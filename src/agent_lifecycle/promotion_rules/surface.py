"""Surface scaffold for `agent_lifecycle/promotion_rules`."""

from __future__ import annotations

SUBHEADING = "agent_lifecycle/promotion_rules"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_promotion_eval_package_contract",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.promotion_eval_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
