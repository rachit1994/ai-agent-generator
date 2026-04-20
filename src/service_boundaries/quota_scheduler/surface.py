"""Surface scaffold for `service_boundaries/quota_scheduler`."""

from __future__ import annotations

SUBHEADING = "service_boundaries/quota_scheduler"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.api.project_scheduler",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
