"""Surface scaffold for `core_components/evaluation_service`."""

from __future__ import annotations

SUBHEADING = "core_components/evaluation_service"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "evaluation_framework.offline_evaluation.sde_eval.eval",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
