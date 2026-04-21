"""Surface descriptor for guardrails dual-control feature."""

from __future__ import annotations

SUBHEADING = "guardrails_and_safety/dual_control"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "guardrails_and_safety.dual_control.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.dual_control_layer",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_dual_control_runtime_surface",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
