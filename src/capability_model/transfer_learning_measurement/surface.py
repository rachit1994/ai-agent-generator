"""Surface scaffold for `capability_model/transfer_learning_measurement`."""

from __future__ import annotations

SUBHEADING = "capability_model/transfer_learning_measurement"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES: list[str] = []

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
