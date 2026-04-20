"""Surface scaffold for `agent_lifecycle/stagnation_detection`."""

from __future__ import annotations

SUBHEADING = "agent_lifecycle/stagnation_detection"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES: list[str] = []

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
