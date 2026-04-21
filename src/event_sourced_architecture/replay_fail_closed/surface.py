"""Surface metadata for replay fail-closed."""

from __future__ import annotations

SUBHEADING = "event_sourced_architecture/replay_fail_closed"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "event_sourced_architecture.replay_fail_closed.contracts",
    "event_sourced_architecture.replay_fail_closed.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.replay_fail_closed_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
