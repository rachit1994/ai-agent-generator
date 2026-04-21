"""Surface scaffold for `workflow_pipelines/retry_repeat_profile`."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/retry_repeat_profile"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "workflow_pipelines.retry_repeat_profile.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.retry_repeat_profile_layer",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_retry_repeat_profile_runtime_integration",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
