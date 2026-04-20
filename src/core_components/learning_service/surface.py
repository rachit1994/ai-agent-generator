"""Surface scaffold for `core_components/learning_service`."""

from __future__ import annotations

SUBHEADING = "core_components/learning_service"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES: list[str] = []

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
