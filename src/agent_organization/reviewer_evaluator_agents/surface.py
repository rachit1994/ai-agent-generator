"""Surface scaffold for `agent_organization/reviewer_evaluator_agents`."""

from __future__ import annotations

SUBHEADING = "agent_organization/reviewer_evaluator_agents"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "agent_organization.reviewer_evaluator_agents.runtime",
    "agent_organization.reviewer_evaluator_agents.evaluator",
    "agent_organization.reviewer_evaluator_agents.findings",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.review",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.cto_publish",
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
