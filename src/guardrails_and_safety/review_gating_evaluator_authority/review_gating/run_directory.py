"""Validate a completed run directory against the V1 artifact contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_organization.reviewer_evaluator_agents.evaluator import validate_reviewer_evaluator_gate
from guardrails_and_safety.risk_budgets_permission_matrix.gates_manifest.manifest import all_required_execution_paths
from guardrails_and_safety.dual_control import validate_dual_control_path
from guardrails_and_safety.rollback_rules_policy_bundle.policy_bundle_rollback import validate_policy_bundle_rollback
from guardrails_and_safety.rollback_rules_policy_bundle import validate_rollback_rules_policy_bundle_path
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.balanced_gates import validation_ready
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops import evaluate_hard_stops
from implementation_roadmap.consolidated_improvements import validate_consolidated_improvements_path
from implementation_roadmap.closure_security_reliability_scalability_plans import (
    validate_closure_security_reliability_scalability_plans_path,
)
from implementation_roadmap.production_readiness_program import validate_production_readiness_program_path
from implementation_roadmap.implementation_roadmap import validate_implementation_roadmap_path
from implementation_roadmap.topology_and_repository_layout import (
    validate_topology_and_repository_layout_path,
)
from event_sourced_architecture.auditability import validate_auditability_path
from event_sourced_architecture.event_store import validate_event_store_semantics_path
from event_sourced_architecture.learning_lineage import validate_learning_lineage_path
from event_sourced_architecture.replay_fail_closed import validate_replay_fail_closed_path
from evaluation_framework.online_evaluation_shadow_canary_artifact import (
    validate_online_evaluation_shadow_canary_path,
)
from evaluation_framework.promotion_evaluation import validate_promotion_evaluation_path
from evaluation_framework.regression_testing_surface import validate_regression_testing_surface_path
from production_architecture.storage import validate_storage_architecture_path
from production_architecture.observability import validate_production_observability_path
from production_architecture.orchestration import validate_production_orchestration_path
from production_architecture.local_runtime import validate_local_runtime_spine_path
from production_architecture.memory_architecture_in_runtime import (
    validate_memory_architecture_in_runtime_path,
)
from production_architecture.identity_and_authorization import (
    validate_production_identity_authorization_path,
)
from core_components.career_strategy_layer import validate_career_strategy_layer_path
from core_components.event_store import validate_event_store_component_path
from core_components.evaluation_service import validate_evaluation_service_path
from core_components.observability import validate_observability_component_path
from core_components.identity_and_authorization_plane import validate_identity_authz_plane_path
from core_components.learning_service import validate_learning_service_path
from core_components.memory_system import validate_memory_system_path
from core_components.objective_policy_engine import validate_objective_policy_engine_path
from core_components.orchestrator import validate_orchestrator_component_path
from core_components.practice_engine import validate_practice_engine_path
from core_components.role_agents import validate_role_agents_path
from core_components.safety_controller import validate_safety_controller_path
from guardrails_and_safety.risk_budgets_permission_matrix import validate_risk_budgets_permission_matrix_path
from core_components.self_learning_loop import validate_self_learning_loop_path
from service_boundaries import validate_service_boundaries_path
from scalability_strategy import validate_scalability_strategy_path
from scalability_strategy.full_build_order_progression import (
    validate_full_build_order_progression_path,
)
from success_criteria.capability_growth_metrics import validate_capability_growth_metrics_path
from success_criteria.error_reduction_metrics import validate_error_reduction_metrics_path
from success_criteria.hard_release_gates import validate_hard_release_gates_path
from success_criteria.stability_metrics import validate_stability_metrics_path
from success_criteria.extended_binary_gates import validate_extended_binary_gates_path
from success_criteria.transfer_learning_metrics import validate_transfer_learning_metrics_path
from workflow_pipelines.strategy_overlay import validate_strategy_overlay_runtime_path
from workflow_pipelines.production_pipeline_plan_artifact import (
    validate_production_pipeline_plan_artifact_path,
)
from workflow_pipelines.failure_path_artifacts import validate_failure_path_artifacts_path
from workflow_pipelines.orchestration_run_error import validate_orchestration_run_error_runtime_path
from workflow_pipelines.orchestration_run_end import validate_orchestration_run_end_runtime_path
from workflow_pipelines.orchestration_run_start import validate_orchestration_run_start_runtime_path
from workflow_pipelines.orchestration_stage_event import validate_orchestration_stage_event_runtime_path
from workflow_pipelines.traces_jsonl import validate_traces_jsonl_event_row_runtime_path
from workflow_pipelines.run_manifest import validate_run_manifest_path, validate_run_manifest_runtime_path
from workflow_pipelines.retry_repeat_profile import validate_retry_repeat_profile_runtime_path

_COMPONENT_RUNTIME_FILENAME = "component_runtime.json"


def _read_json_file(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, f"missing:{path.name}"
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, f"invalid_json:{path.name}"
    if not isinstance(body, dict):
        return None, f"json_not_object:{path.name}"
    return body, None


def validate_execution_run_directory(output_dir: Path, *, mode: str) -> dict[str, Any]:
    """Quality gate for tests and CI: verify V1 artifact contract on a completed run directory."""
    errors: list[str] = []
    summary, summary_error = _read_json_file(output_dir / "summary.json")
    if summary_error:
        errors.append("missing_summary_json" if summary_error == "missing:summary.json" else summary_error)
        summary = {}
    if "balanced_gates" not in summary:
        errors.append("missing_balanced_gates")
    review: dict[str, Any] = {}
    review_body, review_error = _read_json_file(output_dir / "review.json")
    if review_error:
        errors.append("missing_review_json" if review_error == "missing:review.json" else review_error)
    else:
        review = review_body or {}
        errors.extend(validate_reviewer_evaluator_gate(review))
    token_ctx_body, token_ctx_error = _read_json_file(output_dir / "token_context.json")
    if token_ctx_error:
        errors.append("missing_token_context_json" if token_ctx_error == "missing:token_context.json" else token_ctx_error)
        token_ctx_body = {}
    if not (output_dir / "outputs").is_dir():
        errors.append("missing_outputs_dir")
    out_files = list((output_dir / "outputs").glob("*")) if (output_dir / "outputs").is_dir() else []
    if len(out_files) < 2:
        errors.append("outputs_dir_needs_at_least_two_entries")
    for rel in all_required_execution_paths(mode, output_dir):
        if not (output_dir / rel).exists():
            errors.append(f"missing:{rel}")
    run_manifest_path = output_dir / "run-manifest.json"
    if run_manifest_path.exists():
        run_manifest_errors = validate_run_manifest_path(run_manifest_path)
        for token in run_manifest_errors:
            errors.append(f"run_manifest_contract:{token}")
    run_manifest_runtime_path = output_dir / "program" / "run_manifest_runtime.json"
    if run_manifest_runtime_path.exists():
        run_manifest_runtime_errors = validate_run_manifest_runtime_path(run_manifest_runtime_path)
        for token in run_manifest_runtime_errors:
            errors.append(f"run_manifest_runtime_contract:{token}")
    retry_repeat_profile_runtime_path = output_dir / "program" / "retry_repeat_profile_runtime.json"
    if retry_repeat_profile_runtime_path.exists():
        retry_repeat_profile_runtime_errors = validate_retry_repeat_profile_runtime_path(
            retry_repeat_profile_runtime_path
        )
        for token in retry_repeat_profile_runtime_errors:
            errors.append(f"retry_repeat_profile_runtime_contract:{token}")
    transfer_metrics_path = output_dir / "learning" / "transfer_learning_metrics.json"
    if transfer_metrics_path.exists():
        transfer_metric_errors = validate_transfer_learning_metrics_path(transfer_metrics_path)
        for token in transfer_metric_errors:
            errors.append(f"transfer_learning_metrics_contract:{token}")
    capability_growth_path = output_dir / "learning" / "capability_growth_metrics.json"
    if capability_growth_path.exists():
        capability_growth_errors = validate_capability_growth_metrics_path(capability_growth_path)
        for token in capability_growth_errors:
            errors.append(f"capability_growth_metrics_contract:{token}")
    extended_binary_path = output_dir / "learning" / "extended_binary_gates.json"
    if extended_binary_path.exists():
        extended_binary_errors = validate_extended_binary_gates_path(extended_binary_path)
        for token in extended_binary_errors:
            errors.append(f"extended_binary_gates_contract:{token}")
    error_reduction_path = output_dir / "learning" / "error_reduction_metrics.json"
    if error_reduction_path.exists():
        error_reduction_errors = validate_error_reduction_metrics_path(error_reduction_path)
        for token in error_reduction_errors:
            errors.append(f"error_reduction_metrics_contract:{token}")
    hard_release_gates_path = output_dir / "learning" / "hard_release_gates.json"
    if hard_release_gates_path.exists():
        hard_release_gates_errors = validate_hard_release_gates_path(hard_release_gates_path)
        for token in hard_release_gates_errors:
            errors.append(f"hard_release_gates_contract:{token}")
    online_eval_shadow_path = output_dir / "learning" / "online_evaluation_shadow_canary.json"
    if online_eval_shadow_path.exists():
        online_eval_shadow_errors = validate_online_evaluation_shadow_canary_path(
            online_eval_shadow_path
        )
        for token in online_eval_shadow_errors:
            errors.append(f"online_evaluation_shadow_canary_contract:{token}")
    stability_metrics_path = output_dir / "learning" / "stability_metrics.json"
    if stability_metrics_path.exists():
        stability_metrics_errors = validate_stability_metrics_path(stability_metrics_path)
        for token in stability_metrics_errors:
            errors.append(f"stability_metrics_contract:{token}")
    learning_lineage_path = output_dir / "learning" / "learning_lineage.json"
    if learning_lineage_path.exists():
        learning_lineage_errors = validate_learning_lineage_path(learning_lineage_path)
        for token in learning_lineage_errors:
            errors.append(f"learning_lineage_contract:{token}")
    learning_service_path = output_dir / "learning" / "learning_service.json"
    if learning_service_path.exists():
        learning_service_errors = validate_learning_service_path(learning_service_path)
        for token in learning_service_errors:
            errors.append(f"learning_service_contract:{token}")
    promotion_evaluation_path = output_dir / "learning" / "promotion_evaluation.json"
    if promotion_evaluation_path.exists():
        promotion_evaluation_errors = validate_promotion_evaluation_path(promotion_evaluation_path)
        for token in promotion_evaluation_errors:
            errors.append(f"promotion_evaluation_contract:{token}")
    regression_testing_surface_path = output_dir / "learning" / "regression_testing_surface.json"
    if regression_testing_surface_path.exists():
        regression_testing_surface_errors = validate_regression_testing_surface_path(
            regression_testing_surface_path
        )
        for token in regression_testing_surface_errors:
            errors.append(f"regression_testing_surface_contract:{token}")
    evaluation_service_path = output_dir / "evaluation" / "service_runtime.json"
    if evaluation_service_path.exists():
        evaluation_service_errors = validate_evaluation_service_path(evaluation_service_path)
        for token in evaluation_service_errors:
            errors.append(f"evaluation_service_contract:{token}")
    practice_engine_path = output_dir / "practice" / "practice_engine.json"
    if practice_engine_path.exists():
        practice_engine_errors = validate_practice_engine_path(practice_engine_path)
        for token in practice_engine_errors:
            errors.append(f"practice_engine_contract:{token}")
    self_learning_loop_path = output_dir / "learning" / "self_learning_loop.json"
    if self_learning_loop_path.exists():
        self_learning_loop_errors = validate_self_learning_loop_path(self_learning_loop_path)
        for token in self_learning_loop_errors:
            errors.append(f"self_learning_loop_contract:{token}")
    readiness_path = output_dir / "program" / "production_readiness.json"
    if readiness_path.exists():
        readiness_errors = validate_production_readiness_program_path(readiness_path)
        for token in readiness_errors:
            errors.append(f"production_readiness_program_contract:{token}")
    implementation_roadmap_path = output_dir / "program" / "implementation_roadmap.json"
    if implementation_roadmap_path.exists():
        implementation_roadmap_errors = validate_implementation_roadmap_path(implementation_roadmap_path)
        for token in implementation_roadmap_errors:
            errors.append(f"implementation_roadmap_contract:{token}")
    production_pipeline_plan_artifact_path = (
        output_dir / "program" / "production_pipeline_plan_artifact.json"
    )
    if production_pipeline_plan_artifact_path.exists():
        production_pipeline_plan_artifact_errors = validate_production_pipeline_plan_artifact_path(
            production_pipeline_plan_artifact_path
        )
        for token in production_pipeline_plan_artifact_errors:
            errors.append(f"production_pipeline_plan_artifact_contract:{token}")
    dual_control_path = output_dir / "program" / "dual_control_runtime.json"
    if dual_control_path.exists():
        dual_control_errors = validate_dual_control_path(dual_control_path)
        for token in dual_control_errors:
            errors.append(f"dual_control_contract:{token}")
    rollback_rules_path = output_dir / "program" / "rollback_rules_policy_bundle.json"
    if rollback_rules_path.exists():
        rollback_rules_errors = validate_rollback_rules_policy_bundle_path(rollback_rules_path)
        for token in rollback_rules_errors:
            errors.append(f"rollback_rules_policy_bundle_contract:{token}")
    consolidated_path = output_dir / "program" / "consolidated_improvements.json"
    if consolidated_path.exists():
        consolidated_errors = validate_consolidated_improvements_path(consolidated_path)
        for token in consolidated_errors:
            errors.append(f"consolidated_improvements_contract:{token}")
    closure_plan_path = output_dir / "program" / "closure_security_reliability_scalability_plans.json"
    if closure_plan_path.exists():
        closure_plan_errors = validate_closure_security_reliability_scalability_plans_path(
            closure_plan_path
        )
        for token in closure_plan_errors:
            errors.append(f"closure_security_reliability_scalability_plans_contract:{token}")
    topology_layout_path = output_dir / "program" / "topology_and_repository_layout.json"
    if topology_layout_path.exists():
        topology_layout_errors = validate_topology_and_repository_layout_path(topology_layout_path)
        for token in topology_layout_errors:
            errors.append(f"topology_and_repository_layout_contract:{token}")
    scalability_path = output_dir / "strategy" / "scalability_strategy.json"
    if scalability_path.exists():
        scalability_errors = validate_scalability_strategy_path(scalability_path)
        for token in scalability_errors:
            errors.append(f"scalability_strategy_contract:{token}")
    full_build_order_path = output_dir / "strategy" / "full_build_order_progression.json"
    if full_build_order_path.exists():
        full_build_order_errors = validate_full_build_order_progression_path(full_build_order_path)
        for token in full_build_order_errors:
            errors.append(f"full_build_order_progression_contract:{token}")
    service_boundaries_path = output_dir / "strategy" / "service_boundaries.json"
    if service_boundaries_path.exists():
        service_boundaries_errors = validate_service_boundaries_path(service_boundaries_path)
        for token in service_boundaries_errors:
            errors.append(f"service_boundaries_contract:{token}")
    storage_architecture_path = output_dir / "storage" / "storage_architecture.json"
    if storage_architecture_path.exists():
        storage_architecture_errors = validate_storage_architecture_path(storage_architecture_path)
        for token in storage_architecture_errors:
            errors.append(f"storage_architecture_contract:{token}")
    production_observability_path = output_dir / "observability" / "production_observability.json"
    if production_observability_path.exists():
        production_observability_errors = validate_production_observability_path(
            production_observability_path
        )
        for token in production_observability_errors:
            errors.append(f"production_observability_contract:{token}")
    observability_component_path = output_dir / "observability" / _COMPONENT_RUNTIME_FILENAME
    if observability_component_path.exists():
        observability_component_errors = validate_observability_component_path(observability_component_path)
        for token in observability_component_errors:
            errors.append(f"observability_component_contract:{token}")
    production_orchestration_path = output_dir / "orchestration" / "production_orchestration.json"
    if production_orchestration_path.exists():
        production_orchestration_errors = validate_production_orchestration_path(
            production_orchestration_path
        )
        for token in production_orchestration_errors:
            errors.append(f"production_orchestration_contract:{token}")
    local_runtime_spine_path = output_dir / "orchestrator" / "local_runtime_spine.json"
    if local_runtime_spine_path.exists():
        local_runtime_spine_errors = validate_local_runtime_spine_path(local_runtime_spine_path)
        for token in local_runtime_spine_errors:
            errors.append(f"local_runtime_spine_contract:{token}")
    career_strategy_path = output_dir / "strategy" / "career_strategy_layer.json"
    if career_strategy_path.exists():
        career_strategy_errors = validate_career_strategy_layer_path(career_strategy_path)
        for token in career_strategy_errors:
            errors.append(f"career_strategy_layer_contract:{token}")
    identity_authz_plane_path = output_dir / "iam" / "identity_authz_plane.json"
    if identity_authz_plane_path.exists():
        identity_authz_plane_errors = validate_identity_authz_plane_path(identity_authz_plane_path)
        for token in identity_authz_plane_errors:
            errors.append(f"identity_authz_plane_contract:{token}")
    production_identity_authz_path = output_dir / "iam" / "production_identity_authorization.json"
    if production_identity_authz_path.exists():
        production_identity_authz_errors = validate_production_identity_authorization_path(
            production_identity_authz_path
        )
        for token in production_identity_authz_errors:
            errors.append(f"production_identity_authorization_contract:{token}")
    role_agents_path = output_dir / "capability" / "role_agents.json"
    if role_agents_path.exists():
        role_agents_errors = validate_role_agents_path(role_agents_path)
        for token in role_agents_errors:
            errors.append(f"role_agents_contract:{token}")
    memory_architecture_path = output_dir / "memory" / "runtime_memory_architecture.json"
    if memory_architecture_path.exists():
        memory_architecture_errors = validate_memory_architecture_in_runtime_path(
            memory_architecture_path
        )
        for token in memory_architecture_errors:
            errors.append(f"memory_architecture_in_runtime_contract:{token}")
    memory_system_path = output_dir / "memory" / "memory_system.json"
    if memory_system_path.exists():
        memory_system_errors = validate_memory_system_path(memory_system_path)
        for token in memory_system_errors:
            errors.append(f"memory_system_contract:{token}")
    objective_policy_path = output_dir / "strategy" / "objective_policy_engine.json"
    if objective_policy_path.exists():
        objective_policy_errors = validate_objective_policy_engine_path(objective_policy_path)
        for token in objective_policy_errors:
            errors.append(f"objective_policy_engine_contract:{token}")
    safety_controller_path = output_dir / "safety" / "controller_runtime.json"
    if safety_controller_path.exists():
        safety_controller_errors = validate_safety_controller_path(safety_controller_path)
        for token in safety_controller_errors:
            errors.append(f"safety_controller_contract:{token}")
    risk_budgets_permission_matrix_path = output_dir / "safety" / "risk_budgets_permission_matrix_runtime.json"
    if risk_budgets_permission_matrix_path.exists():
        risk_budgets_permission_matrix_errors = validate_risk_budgets_permission_matrix_path(
            risk_budgets_permission_matrix_path
        )
        for token in risk_budgets_permission_matrix_errors:
            errors.append(f"risk_budgets_permission_matrix_contract:{token}")
    auditability_path = output_dir / "audit" / "auditability.json"
    if auditability_path.exists():
        auditability_errors = validate_auditability_path(auditability_path)
        for token in auditability_errors:
            errors.append(f"auditability_contract:{token}")
    event_store_component_path = output_dir / "event_store" / _COMPONENT_RUNTIME_FILENAME
    if event_store_component_path.exists():
        event_store_component_errors = validate_event_store_component_path(event_store_component_path)
        for token in event_store_component_errors:
            errors.append(f"event_store_component_contract:{token}")
    orchestrator_component_path = output_dir / "orchestrator" / _COMPONENT_RUNTIME_FILENAME
    if orchestrator_component_path.exists():
        orchestrator_component_errors = validate_orchestrator_component_path(orchestrator_component_path)
        for token in orchestrator_component_errors:
            errors.append(f"orchestrator_component_contract:{token}")
    event_store_semantics_path = output_dir / "event_store" / "semantics.json"
    if event_store_semantics_path.exists():
        event_store_semantics_errors = validate_event_store_semantics_path(event_store_semantics_path)
        for token in event_store_semantics_errors:
            errors.append(f"event_store_semantics_contract:{token}")
    replay_fail_closed_path = output_dir / "replay" / "fail_closed.json"
    if replay_fail_closed_path.exists():
        replay_fail_closed_errors = validate_replay_fail_closed_path(replay_fail_closed_path)
        for token in replay_fail_closed_errors:
            errors.append(f"replay_fail_closed_contract:{token}")
    failure_path_artifacts_path = output_dir / "replay" / "failure_path_artifacts.json"
    if failure_path_artifacts_path.exists():
        failure_path_artifacts_errors = validate_failure_path_artifacts_path(failure_path_artifacts_path)
        for token in failure_path_artifacts_errors:
            errors.append(f"failure_path_artifacts_contract:{token}")
    orchestration_run_start_runtime_path = output_dir / "orchestration" / "run_start_runtime.json"
    if orchestration_run_start_runtime_path.exists():
        orchestration_run_start_runtime_errors = validate_orchestration_run_start_runtime_path(
            orchestration_run_start_runtime_path
        )
        for token in orchestration_run_start_runtime_errors:
            errors.append(f"orchestration_run_start_runtime_contract:{token}")
    orchestration_stage_event_runtime_path = output_dir / "orchestration" / "stage_event_runtime.json"
    if orchestration_stage_event_runtime_path.exists():
        orchestration_stage_event_runtime_errors = validate_orchestration_stage_event_runtime_path(
            orchestration_stage_event_runtime_path
        )
        for token in orchestration_stage_event_runtime_errors:
            errors.append(f"orchestration_stage_event_runtime_contract:{token}")
    orchestration_run_error_runtime_path = output_dir / "orchestration" / "run_error_runtime.json"
    if orchestration_run_error_runtime_path.exists():
        orchestration_run_error_runtime_errors = validate_orchestration_run_error_runtime_path(
            orchestration_run_error_runtime_path
        )
        for token in orchestration_run_error_runtime_errors:
            errors.append(f"orchestration_run_error_runtime_contract:{token}")
    orchestration_run_end_runtime_path = output_dir / "orchestration" / "run_end_runtime.json"
    if orchestration_run_end_runtime_path.exists():
        orchestration_run_end_runtime_errors = validate_orchestration_run_end_runtime_path(
            orchestration_run_end_runtime_path
        )
        for token in orchestration_run_end_runtime_errors:
            errors.append(f"orchestration_run_end_runtime_contract:{token}")
    traces_event_row_runtime_path = output_dir / "traces" / "event_row_runtime.json"
    if traces_event_row_runtime_path.exists():
        traces_event_row_runtime_errors = validate_traces_jsonl_event_row_runtime_path(
            traces_event_row_runtime_path
        )
        for token in traces_event_row_runtime_errors:
            errors.append(f"traces_jsonl_event_row_runtime_contract:{token}")
    strategy_overlay_runtime_path = output_dir / "strategy" / "overlay.json"
    if strategy_overlay_runtime_path.exists():
        strategy_overlay_runtime_errors = validate_strategy_overlay_runtime_path(
            strategy_overlay_runtime_path
        )
        for token in strategy_overlay_runtime_errors:
            errors.append(f"strategy_overlay_runtime_contract:{token}")
    errors.extend(validate_policy_bundle_rollback(output_dir))
    events: list[dict[str, Any]] = []
    traces = output_dir / "traces.jsonl"
    if traces.is_file():
        for idx, line in enumerate(traces.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"invalid_jsonl:traces.jsonl:{idx + 1}")
                continue
            if isinstance(row, dict):
                events.append(row)
            else:
                errors.append(f"jsonl_not_object:traces.jsonl:{idx + 1}")
    hard = evaluate_hard_stops(
        output_dir,
        events,
        token_ctx_body or {},
        run_status=summary.get("runStatus", "ok"),
        mode=mode,
    )
    failed_hard_stop_ids = [str(row.get("id")) for row in hard if not bool(row.get("passed"))]
    for hs_id in failed_hard_stop_ids:
        errors.append(f"hard_stop_failed:{hs_id}")
    ready = validation_ready(summary["balanced_gates"]) if summary.get("balanced_gates") else False
    strict_ok = ready and not errors and len(failed_hard_stop_ids) == 0
    return {"ok": strict_ok, "errors": errors, "hard_stops": hard, "validation_ready": ready}
