"""Surface scaffold for `human_professional_evolution_model`."""

from __future__ import annotations

SUBHEADING = "human_professional_evolution_model"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "human_professional_evolution_model.career_progression_model.surface",
    "human_professional_evolution_model.deliberate_practice.surface",
    "human_professional_evolution_model.feedback_loops.surface",
    "human_professional_evolution_model.human_growth_loop.surface",
    "human_professional_evolution_model.human_to_agent_behavior_mapping.surface",
    "human_professional_evolution_model.institutional_memory.surface",
    "human_professional_evolution_model.mentorship_operating_model.surface",
    "human_professional_evolution_model.performance_review_cycle.surface",
]


def _normalized_references(modules: object) -> list[str]:
    if not isinstance(modules, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in modules:
        if not isinstance(item, str):
            return []
        ref = item.strip()
        if not ref:
            return []
        if ref in seen:
            return []
        seen.add(ref)
        out.append(ref)
    return out


def describe_surface() -> dict[str, object]:
    if not isinstance(SUBHEADING, str) or not SUBHEADING.strip():
        raise ValueError("SUBHEADING must be a non-empty string")
    if not isinstance(IMPLEMENTATION_STATUS, str) or not IMPLEMENTATION_STATUS.strip():
        raise ValueError("IMPLEMENTATION_STATUS must be a non-empty string")
    refs = _normalized_references(REFERENCE_MODULES)
    return {
        "subheading": SUBHEADING.strip(),
        "status": IMPLEMENTATION_STATUS.strip(),
        "references": refs,
    }
