"""Surface scaffold for `workflow_pipelines/benchmark_aggregate_manifest`."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/benchmark_aggregate_manifest"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_benchmark_aggregate_summary_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_benchmark_manifest_contract",
    "workflow_pipelines.benchmark_aggregate_summary.benchmark_aggregate_summary_contract",
    "workflow_pipelines.benchmark_aggregate_manifest.benchmark_manifest_contract",
    "workflow_pipelines.benchmark_aggregate_manifest.runtime",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_benchmark_aggregate_manifest_runtime_surface",
    "workflow_pipelines.run_manifest.run_manifest_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
