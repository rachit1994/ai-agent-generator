"""Surface scaffold for `workflow_pipelines/benchmark_checkpoint`."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/benchmark_checkpoint"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_benchmark_checkpoint_contract",
    "workflow_pipelines.benchmark_checkpoint.benchmark_checkpoint_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_benchmark_aggregate_summary_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_benchmark_harvest",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_benchmark_manifest_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
