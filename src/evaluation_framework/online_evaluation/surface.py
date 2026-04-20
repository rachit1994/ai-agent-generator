"""Surface scaffold for `evaluation_framework/online_evaluation`."""

from __future__ import annotations

SUBHEADING = "evaluation_framework/online_evaluation"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "evaluation_framework.offline_evaluation.sde_eval.eval",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_online_eval_shadow_contract",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.online_eval_shadow_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
