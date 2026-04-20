"""Surface scaffold for `service_boundaries/reflection_rca`."""

from __future__ import annotations

SUBHEADING = "service_boundaries/reflection_rca"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES: list[str] = []

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
