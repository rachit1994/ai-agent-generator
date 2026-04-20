"""Surface scaffold for `workflow_pipelines/benchmark_aggregate_summary`."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/benchmark_aggregate_summary"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_benchmark_aggregate_summary_contract",
    "workflow_pipelines.benchmark_aggregate_summary.benchmark_aggregate_summary_contract",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.summary_payload",
    "production_architecture.local_runtime.orchestrator.api.project_aggregate",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_benchmark_checkpoint_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
