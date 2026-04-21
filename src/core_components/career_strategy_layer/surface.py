"""Surface scaffold for `core_components/career_strategy_layer`."""

from __future__ import annotations

SUBHEADING = "core_components/career_strategy_layer"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "core_components.career_strategy_layer.runtime",
    "core_components.career_strategy_layer.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.career_strategy_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
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
