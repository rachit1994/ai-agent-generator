"""Surface scaffold for `service_boundaries/boundary_contracts`."""

from __future__ import annotations

SUBHEADING = "service_boundaries/boundary_contracts"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES: list[str] = []

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
