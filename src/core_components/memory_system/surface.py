"""Surface scaffold for `core_components/memory_system`."""

from __future__ import annotations

SUBHEADING = "core_components/memory_system"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops_memory",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_memory_hard_stops",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
