"""Surface scaffold for `capability_model/capability_graph`."""

from __future__ import annotations

SUBHEADING = "capability_model/capability_graph"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES: list[str] = []

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
