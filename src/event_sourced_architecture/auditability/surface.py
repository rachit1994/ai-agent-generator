"""Surface scaffold for `event_sourced_architecture/auditability`."""

from __future__ import annotations

SUBHEADING = "event_sourced_architecture/auditability"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES: list[str] = []

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
