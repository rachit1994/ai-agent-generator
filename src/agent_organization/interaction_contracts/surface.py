"""Surface scaffold for `agent_organization/interaction_contracts`."""

from __future__ import annotations

SUBHEADING = "agent_organization/interaction_contracts"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES: list[str] = []

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
