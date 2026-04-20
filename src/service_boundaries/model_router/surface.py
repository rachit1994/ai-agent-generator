"""Surface scaffold for `service_boundaries/model_router`."""

from __future__ import annotations

SUBHEADING = "service_boundaries/model_router"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.model_adapter.model_adapter",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
