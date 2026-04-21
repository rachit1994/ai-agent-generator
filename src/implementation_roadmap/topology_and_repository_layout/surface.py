"""Surface metadata for topology and repository layout."""

from __future__ import annotations

SUBHEADING = "implementation_roadmap/topology_and_repository_layout"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "implementation_roadmap.topology_and_repository_layout.runtime",
    "implementation_roadmap.topology_and_repository_layout.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.topology_and_repository_layout_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }

