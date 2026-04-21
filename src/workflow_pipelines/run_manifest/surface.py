"""Surface descriptor for workflow-pipelines run-manifest feature."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/run_manifest"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "workflow_pipelines.run_manifest.run_manifest_contract",
    "workflow_pipelines.run_manifest.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.run_manifest_runtime_layer",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_run_manifest_runtime_surface",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
