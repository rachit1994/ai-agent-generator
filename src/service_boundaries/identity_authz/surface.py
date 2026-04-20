"""Surface scaffold for `service_boundaries/identity_authz`."""

from __future__ import annotations

SUBHEADING = "service_boundaries/identity_authz"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES: list[str] = []

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
