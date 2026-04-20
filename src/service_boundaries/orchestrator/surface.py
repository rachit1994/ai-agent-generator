"""Surface scaffold for `service_boundaries/orchestrator`."""

from __future__ import annotations

SUBHEADING = "service_boundaries/orchestrator"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "core_components.orchestrator.common.utils",
    "core_components.orchestrator.sde_types.types",
    "production_architecture.local_runtime.orchestrator.api.context_pack",
    "production_architecture.local_runtime.orchestrator.api.continuous_run",
    "production_architecture.local_runtime.orchestrator.api.gemma_roadmap_review",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
