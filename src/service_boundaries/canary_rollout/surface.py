"""Surface scaffold for `service_boundaries/canary_rollout`."""

from __future__ import annotations

SUBHEADING = "service_boundaries/canary_rollout"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES: list[str] = []

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
