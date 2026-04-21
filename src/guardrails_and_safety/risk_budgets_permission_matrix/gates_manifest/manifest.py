"""Artifact path lists and manifest rows for review.json."""

from __future__ import annotations

from pathlib import Path
from typing import Any

EVENT_LINEAGE_MANIFEST_PATHS = [
    "replay_manifest.json",
    "kill_switch_state.json",
    "traces/event_row_runtime.json",
    "orchestration/run_start_runtime.json",
    "orchestration/stage_event_runtime.json",
    "orchestration/run_error_runtime.json",
    "orchestration/run_end_runtime.json",
    "orchestrator/component_runtime.json",
    "event_store/run_events.jsonl",
    "replay/fail_closed.json",
    "replay/failure_path_artifacts.json",
    "event_store/semantics.json",
    "event_store/component_runtime.json",
    "audit/auditability.json",
    "learning/learning_lineage.json",
]

MEMORY_MANIFEST_PATHS = [
    "memory/retrieval_bundle.json",
    "memory/quarantine.jsonl",
    "memory/quality_metrics.json",
    "memory/memory_system.json",
    "memory/runtime_memory_architecture.json",
    "capability/skill_nodes.json",
    "capability/role_agents.json",
]

EVOLUTION_MANIFEST_PATHS = [
    "learning/reflection_bundle.json",
    "learning/canary_report.json",
    "learning/transfer_learning_metrics.json",
    "learning/capability_growth_metrics.json",
    "learning/extended_binary_gates.json",
    "learning/error_reduction_metrics.json",
    "learning/hard_release_gates.json",
    "learning/online_evaluation_shadow_canary.json",
    "learning/regression_testing_surface.json",
    "learning/learning_service.json",
    "learning/promotion_evaluation.json",
    "evaluation/service_runtime.json",
    "learning/stability_metrics.json",
    "learning/self_learning_loop.json",
    "lifecycle/promotion_package.json",
    "practice/task_spec.json",
    "practice/evaluation_result.json",
    "practice/practice_engine.json",
]

ORGANIZATION_MANIFEST_PATHS = [
    "coordination/lease_table.json",
    "iam/permission_matrix.json",
    "iam/action_audit.jsonl",
    "iam/identity_authz_plane.json",
    "iam/production_identity_authorization.json",
    "orchestration/shard_map.json",
    "orchestration/production_orchestration.json",
    "orchestrator/local_runtime_spine.json",
    "strategy/proposal.json",
    "strategy/overlay.json",
    "strategy/objective_policy_engine.json",
    "strategy/scalability_strategy.json",
    "strategy/full_build_order_progression.json",
    "strategy/service_boundaries.json",
    "strategy/career_strategy_layer.json",
]

STORAGE_MANIFEST_PATHS = [
    "storage/storage_architecture.json",
    "observability/production_observability.json",
    "observability/component_runtime.json",
    "safety/risk_budgets_permission_matrix_runtime.json",
    "safety/controller_runtime.json",
    "safety/autonomy_boundaries_tokens_expiry.json",
]

GUARDED_CORE_PATHS = [
    "planner_doc.md",
    "executor_prompt.txt",
    "verifier_report.json",
]

PHASED_PLAN_PATH = "program/phased_plan.json"

GUARDED_COMPLETION_PATHS = [
    "program/project_plan.json",
    "program/progress.json",
    "program/work_batch.json",
    "program/discovery.json",
    "program/research_digest.md",
    "program/doc_review.json",
    "program/dual_control_ack.json",
    "program/dual_control_runtime.json",
    "program/question_workbook.jsonl",
    "program/learning_events.jsonl",
    "program/doc_pack_manifest.json",
    "program/plan_lock.json",
    "program/policy_bundle_rollback.json",
    "program/rollback_rules_policy_bundle.json",
    "product_brief.md",
    "architecture_sketch.md",
    "test_plan_stub.md",
    "step_reviews/step_planner.json",
    "step_reviews/step_implement.json",
    "step_reviews/step_verify.json",
    "verification_bundle.json",
    "program/production_pipeline_plan_artifact.json",
]


def manifest_paths_for_review(mode: str, *, include_guarded_completion: bool = False) -> list[str]:
    """Paths checked in ``review.json`` artifact_manifest (before review file itself exists)."""
    base = [
        "traces.jsonl",
        "orchestration.jsonl",
        "report.md",
        "run.log",
        "answer.txt",
        "static_gates_report.json",
        "outputs/README.txt",
        "outputs/manifest.json",
        *EVENT_LINEAGE_MANIFEST_PATHS,
        *MEMORY_MANIFEST_PATHS,
        *EVOLUTION_MANIFEST_PATHS,
        *ORGANIZATION_MANIFEST_PATHS,
        *STORAGE_MANIFEST_PATHS,
    ]
    if mode in ("guarded_pipeline", "phased_pipeline"):
        base.extend(GUARDED_CORE_PATHS)
        if include_guarded_completion:
            base.extend(GUARDED_COMPLETION_PATHS)
        if mode == "phased_pipeline":
            base.append(PHASED_PLAN_PATH)
    base.append("program/closure_security_reliability_scalability_plans.json")
    base.append("program/consolidated_improvements.json")
    base.append("program/topology_and_repository_layout.json")
    base.append("program/production_readiness.json")
    base.append("program/implementation_roadmap.json")
    base.append("program/run_manifest_runtime.json")
    base.append("program/retry_repeat_profile_runtime.json")
    return base


def all_required_execution_paths(mode: str, output_dir: Path | None = None) -> list[str]:
    include_completion = False
    if mode in ("guarded_pipeline", "phased_pipeline") and output_dir is not None:
        include_completion = (output_dir / "program" / "project_plan.json").is_file()
    return [
        "summary.json",
        "review.json",
        "token_context.json",
        *manifest_paths_for_review(mode, include_guarded_completion=include_completion),
    ]


def manifest_entries(output_dir: Path, relative_paths: list[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for rel in relative_paths:
        p = output_dir / rel
        entries.append({"path": rel, "present": p.is_file() or p.is_dir()})
    return entries
