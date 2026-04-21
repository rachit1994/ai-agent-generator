"""Surface scaffold for `workflow_pipelines/benchmark_orchestration_jsonl`."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/benchmark_orchestration_jsonl"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "workflow_pipelines.benchmark_orchestration_jsonl.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.run_benchmark",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_benchmark_orchestration_jsonl_runtime_surface",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
