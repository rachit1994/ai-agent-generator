"""Validate a completed run directory against the V1 artifact contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_organization.reviewer_evaluator_agents.evaluator import validate_reviewer_evaluator_gate
from guardrails_and_safety.risk_budgets_permission_matrix.gates_manifest.manifest import all_required_execution_paths
from guardrails_and_safety.autonomy_boundaries.autonomy_boundaries_tokens_expiry import (
    validate_autonomy_boundaries_runtime_path,
)
from guardrails_and_safety.dual_control import validate_dual_control_path
from guardrails_and_safety.rollback_rules_policy_bundle.policy_bundle_rollback import validate_policy_bundle_rollback
from guardrails_and_safety.rollback_rules_policy_bundle import (
    build_rollback_rules_policy_bundle,
    validate_rollback_rules_policy_bundle_path,
)
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
from core_components.self_learning_loop import (
    validate_self_learning_candidates_path,
    validate_self_learning_loop_path,
)
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

_STORAGE_CONTRACT_ERROR_PREFIX = "storage_contract:"
_AUTONOMY_BOUNDARIES_CONTRACT_ERROR_PREFIX = "autonomy_boundaries_contract:"

_COMPONENT_RUNTIME_FILENAME = "component_runtime.json"


def _read_json_file(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, f"missing:{path.name}"
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return None, f"unreadable:{path.name}"
    except json.JSONDecodeError:
        return None, f"invalid_json:{path.name}"
    if not isinstance(body, dict):
        return None, f"json_not_object:{path.name}"
    return body, None


def _validate_policy_bundle_rollback_coherence(output_dir: Path) -> list[str]:
    policy_path = output_dir / "program" / "policy_bundle_rollback.json"
    derived_path = output_dir / "program" / "rollback_rules_policy_bundle.json"
    if not derived_path.is_file():
        return ["rollback_rules_policy_bundle_contract:rollback_rules_policy_bundle_file_missing"]
    derived_body, derived_error = _read_json_file(derived_path)
    if derived_error:
        return [f"rollback_rules_policy_bundle_contract:{derived_error}"]
    assert derived_body is not None
    derived_status = derived_body.get("status")
    derived_checks = derived_body.get("rollback_checks")
    run_id = derived_body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        return ["rollback_rules_policy_bundle_source_run_id_invalid"]
    if not policy_path.is_file():
        expected = build_rollback_rules_policy_bundle(run_id=run_id, rollback_record={})
        if derived_status != expected.get("status"):
            return ["rollback_rules_policy_bundle_source_status_mismatch:none"]
        if derived_checks != expected.get("rollback_checks"):
            return ["rollback_rules_policy_bundle_source_derivation_mismatch"]
        return []
    policy_body, policy_error = _read_json_file(policy_path)
    if policy_error:
        return ["rollback_rules_policy_bundle_source_unreadable"]
    assert policy_body is not None
    expected = build_rollback_rules_policy_bundle(run_id=run_id, rollback_record=policy_body)
    if derived_status != expected.get("status"):
        source_status = policy_body.get("status")
        if source_status in {"none", "rolled_back_atomic"}:
            return [f"rollback_rules_policy_bundle_source_status_mismatch:{source_status}"]
        return ["rollback_rules_policy_bundle_source_status_mismatch:invalid"]
    if derived_checks != expected.get("rollback_checks"):
        source_status = policy_body.get("status")
        if source_status == "rolled_back_atomic":
            return ["rollback_rules_policy_bundle_source_atomic_checks_failed"]
        return ["rollback_rules_policy_bundle_source_derivation_mismatch"]
    return []


def _append_missing_evidence_ref_errors(
    *,
    output_dir: Path,
    body: dict[str, Any],
    required_keys: tuple[str, ...],
    error_prefix: str,
) -> list[str]:
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return []
    errors: list[str] = []
    for key in required_keys:
        value = evidence.get(key)
        if isinstance(value, str) and value.strip() and not (output_dir / value.strip()).is_file():
            errors.append(f"{error_prefix}:{key}_missing")
    return errors


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
        if not retry_repeat_profile_runtime_errors:
            retry_repeat_profile_runtime_body, retry_repeat_profile_runtime_read_error = _read_json_file(
                retry_repeat_profile_runtime_path
            )
            if (
                retry_repeat_profile_runtime_read_error is None
                and retry_repeat_profile_runtime_body is not None
            ):
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=retry_repeat_profile_runtime_body,
                        required_keys=("run_manifest_ref", "runtime_ref"),
                        error_prefix=(
                            "retry_repeat_profile_runtime_contract:"
                            "retry_repeat_profile_runtime_evidence_ref"
                        ),
                    )
                )
                retry_repeat_run_id = retry_repeat_profile_runtime_body.get("run_id")
                run_manifest_body, run_manifest_read_error = _read_json_file(run_manifest_path)
                if (
                    run_manifest_read_error is None
                    and run_manifest_body is not None
                    and isinstance(retry_repeat_run_id, str)
                    and retry_repeat_run_id.strip()
                ):
                    run_manifest_run_id = run_manifest_body.get("run_id")
                    if isinstance(run_manifest_run_id, str) and run_manifest_run_id.strip():
                        if retry_repeat_run_id.strip() != run_manifest_run_id.strip():
                            errors.append(
                                "retry_repeat_profile_runtime_contract:"
                                "retry_repeat_profile_runtime_run_id_mismatch"
                            )
    transfer_metrics_path = output_dir / "learning" / "transfer_learning_metrics.json"
    transfer_metric_errors = validate_transfer_learning_metrics_path(transfer_metrics_path)
    for token in transfer_metric_errors:
        errors.append(f"transfer_learning_metrics_contract:{token}")
    capability_growth_path = output_dir / "learning" / "capability_growth_metrics.json"
    if capability_growth_path.exists():
        capability_growth_errors = validate_capability_growth_metrics_path(capability_growth_path)
        for token in capability_growth_errors:
            errors.append(f"capability_growth_metrics_contract:{token}")
        if not capability_growth_errors:
            capability_growth_body, capability_growth_read_error = _read_json_file(capability_growth_path)
            if capability_growth_read_error is None and capability_growth_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=capability_growth_body,
                        required_keys=("traces_ref", "skill_nodes_ref"),
                        error_prefix=(
                            "capability_growth_metrics_contract:"
                            "capability_growth_metrics_evidence_ref"
                        ),
                    )
                )
    extended_binary_path = output_dir / "learning" / "extended_binary_gates.json"
    if extended_binary_path.exists():
        extended_binary_errors = validate_extended_binary_gates_path(extended_binary_path)
        for token in extended_binary_errors:
            errors.append(f"extended_binary_gates_contract:{token}")
        if not extended_binary_errors:
            extended_binary_body, extended_binary_read_error = _read_json_file(extended_binary_path)
            if extended_binary_read_error is None and extended_binary_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=extended_binary_body,
                        required_keys=("traces_ref", "checks_ref", "skill_nodes_ref"),
                        error_prefix="extended_binary_gates_contract:extended_binary_gates_evidence_ref",
                    )
                )
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
        if not hard_release_gates_errors:
            hard_release_gates_body, hard_release_gates_read_error = _read_json_file(hard_release_gates_path)
            if hard_release_gates_read_error is None and hard_release_gates_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=hard_release_gates_body,
                        required_keys=("summary_ref", "traces_ref"),
                        error_prefix="hard_release_gates_contract:hard_release_gates_evidence_ref",
                    )
                )
    online_eval_shadow_path = output_dir / "learning" / "online_evaluation_shadow_canary.json"
    if online_eval_shadow_path.exists():
        online_eval_shadow_errors = validate_online_evaluation_shadow_canary_path(
            online_eval_shadow_path
        )
        for token in online_eval_shadow_errors:
            errors.append(f"online_evaluation_shadow_canary_contract:{token}")
        if not online_eval_shadow_errors:
            online_eval_shadow_body, online_eval_shadow_read_error = _read_json_file(online_eval_shadow_path)
            if online_eval_shadow_read_error is None and online_eval_shadow_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=online_eval_shadow_body,
                        required_keys=("canary_report_ref",),
                        error_prefix=(
                            "online_evaluation_shadow_canary_contract:"
                            "online_evaluation_shadow_canary_evidence"
                        ),
                    )
                )
        if not (output_dir / "learning" / "online_eval_records.jsonl").is_file():
            errors.append(
                "online_evaluation_shadow_canary_contract:"
                "online_evaluation_shadow_canary_evidence_online_eval_records_ref_missing"
            )
    stability_metrics_path = output_dir / "learning" / "stability_metrics.json"
    if stability_metrics_path.exists():
        stability_metrics_errors = validate_stability_metrics_path(stability_metrics_path)
        for token in stability_metrics_errors:
            errors.append(f"stability_metrics_contract:{token}")
        if not stability_metrics_errors:
            stability_metrics_body, stability_metrics_read_error = _read_json_file(stability_metrics_path)
            if stability_metrics_read_error is None and stability_metrics_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=stability_metrics_body,
                        required_keys=("traces_ref", "stability_metrics_ref"),
                        error_prefix="stability_metrics_contract:stability_metrics_evidence_ref",
                    )
                )
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
        if not learning_service_errors:
            learning_service_body, learning_service_read_error = _read_json_file(learning_service_path)
            if learning_service_read_error is None and learning_service_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=learning_service_body,
                        required_keys=(
                            "reflection_bundle_ref",
                            "canary_report_ref",
                            "traces_ref",
                            "learning_service_ref",
                        ),
                        error_prefix="learning_service_contract:learning_service_evidence_ref",
                    )
                )
    promotion_evaluation_path = output_dir / "learning" / "promotion_evaluation.json"
    if promotion_evaluation_path.exists():
        promotion_evaluation_errors = validate_promotion_evaluation_path(promotion_evaluation_path)
        for token in promotion_evaluation_errors:
            errors.append(f"promotion_evaluation_contract:{token}")
        if not promotion_evaluation_errors:
            promotion_evaluation_body, promotion_evaluation_read_error = _read_json_file(
                promotion_evaluation_path
            )
            if promotion_evaluation_read_error is None and promotion_evaluation_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=promotion_evaluation_body,
                        required_keys=(
                            "promotion_package_ref",
                            "review_ref",
                            "traces_ref",
                            "promotion_evaluation_ref",
                        ),
                        error_prefix="promotion_evaluation_contract:promotion_evaluation_evidence_ref",
                    )
                )
                promotion_signals = promotion_evaluation_body.get("signals")
                if isinstance(promotion_signals, dict):
                    promotion_review_pass = promotion_signals.get("review_pass")
                    evidence = promotion_evaluation_body.get("evidence")
                    review_ref = evidence.get("review_ref") if isinstance(evidence, dict) else None
                    if isinstance(review_ref, str) and review_ref.strip():
                        review_body, review_ref_error = _read_json_file(output_dir / review_ref.strip())
                        if review_ref_error is None and review_body is not None:
                            expected_review_pass = review_body.get("status") == "completed_review_pass"
                            if isinstance(promotion_review_pass, bool) and promotion_review_pass != expected_review_pass:
                                errors.append(
                                    "promotion_evaluation_contract:promotion_evaluation_review_pass_mismatch"
                                )
    regression_testing_surface_path = output_dir / "learning" / "regression_testing_surface.json"
    if regression_testing_surface_path.exists():
        regression_testing_surface_errors = validate_regression_testing_surface_path(
            regression_testing_surface_path
        )
        for token in regression_testing_surface_errors:
            errors.append(f"regression_testing_surface_contract:{token}")
        if not regression_testing_surface_errors:
            regression_testing_surface_body, regression_testing_surface_read_error = _read_json_file(
                regression_testing_surface_path
            )
            if (
                regression_testing_surface_read_error is None
                and regression_testing_surface_body is not None
            ):
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=regression_testing_surface_body,
                        required_keys=(
                            "promotion_evaluation_ref",
                            "online_evaluation_ref",
                            "summary_ref",
                            "surface_ref",
                        ),
                        error_prefix=(
                            "regression_testing_surface_contract:"
                            "regression_testing_surface_evidence_ref"
                        ),
                    )
                )
    evaluation_service_path = output_dir / "evaluation" / "service_runtime.json"
    if evaluation_service_path.exists():
        evaluation_service_errors = validate_evaluation_service_path(evaluation_service_path)
        for token in evaluation_service_errors:
            errors.append(f"evaluation_service_contract:{token}")
        if not evaluation_service_errors:
            evaluation_service_body, evaluation_service_read_error = _read_json_file(evaluation_service_path)
            if evaluation_service_read_error is None and evaluation_service_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=evaluation_service_body,
                        required_keys=(
                            "summary_ref",
                            "online_eval_ref",
                            "promotion_eval_ref",
                            "evaluation_service_ref",
                        ),
                        error_prefix="evaluation_service_contract:evaluation_service_evidence_ref",
                    )
                )
    practice_engine_path = output_dir / "practice" / "practice_engine.json"
    if practice_engine_path.exists():
        practice_engine_errors = validate_practice_engine_path(practice_engine_path)
        for token in practice_engine_errors:
            errors.append(f"practice_engine_contract:{token}")
        if not practice_engine_errors:
            practice_engine_body, practice_engine_read_error = _read_json_file(practice_engine_path)
            if practice_engine_read_error is None and practice_engine_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=practice_engine_body,
                        required_keys=("task_spec_ref", "evaluation_result_ref"),
                        error_prefix="practice_engine_contract:practice_engine_evidence_ref",
                    )
                )
    self_learning_loop_body: dict[str, Any] = {}
    self_learning_loop_path = output_dir / "learning" / "self_learning_loop.json"
    self_learning_loop_errors = validate_self_learning_loop_path(self_learning_loop_path)
    for token in self_learning_loop_errors:
        errors.append(f"self_learning_loop_contract:{token}")
    if not self_learning_loop_errors:
        self_learning_loop_body, self_learning_loop_read_error = _read_json_file(self_learning_loop_path)
        if self_learning_loop_read_error:
            errors.append(f"self_learning_loop_contract:{self_learning_loop_read_error}")
        else:
            evidence = self_learning_loop_body.get("evidence", {})
            for key in (
                "traces_ref",
                "skill_nodes_ref",
                "practice_engine_ref",
                "transfer_learning_metrics_ref",
                "capability_growth_metrics_ref",
                "self_learning_candidates_ref",
                "self_learning_loop_ref",
            ):
                evidence_ref = evidence.get(key)
                if isinstance(evidence_ref, str) and evidence_ref.strip():
                    if not (output_dir / evidence_ref.strip()).is_file():
                        errors.append(f"self_learning_loop_contract:self_learning_loop_evidence_ref_missing:{key}")
            candidates_ref = evidence.get("self_learning_candidates_ref")
            if isinstance(candidates_ref, str) and candidates_ref.strip():
                candidate_path = output_dir / candidates_ref.strip()
                for token in validate_self_learning_candidates_path(candidate_path):
                    errors.append(f"self_learning_loop_contract:{token}")
    readiness_path = output_dir / "program" / "production_readiness.json"
    if readiness_path.exists():
        readiness_errors = validate_production_readiness_program_path(readiness_path)
        for token in readiness_errors:
            errors.append(f"production_readiness_program_contract:{token}")
        if not readiness_errors:
            readiness_body, readiness_read_error = _read_json_file(readiness_path)
            if readiness_read_error is None and readiness_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=readiness_body,
                        required_keys=("summary_ref", "review_ref", "readiness_ref"),
                        error_prefix=(
                            "production_readiness_program_contract:"
                            "production_readiness_program_evidence_ref"
                        ),
                    )
                )
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
        if not production_pipeline_plan_artifact_errors:
            plan_artifact_body, plan_artifact_read_error = _read_json_file(
                production_pipeline_plan_artifact_path
            )
            if plan_artifact_read_error is None and plan_artifact_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=plan_artifact_body,
                        required_keys=(
                            "project_plan_ref",
                            "progress_ref",
                            "work_batch_ref",
                            "discovery_ref",
                            "verification_bundle_ref",
                            "production_pipeline_plan_artifact_ref",
                        ),
                        error_prefix=(
                            "production_pipeline_plan_artifact_contract:"
                            "production_pipeline_plan_artifact_evidence_ref"
                        ),
                    )
                )
    dual_control_path = output_dir / "program" / "dual_control_runtime.json"
    if dual_control_path.exists():
        dual_control_errors = validate_dual_control_path(dual_control_path)
        for token in dual_control_errors:
            errors.append(f"dual_control_contract:{token}")
        if not dual_control_errors:
            dual_control_body, dual_control_read_error = _read_json_file(dual_control_path)
            if dual_control_read_error is None and dual_control_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=dual_control_body,
                        required_keys=("doc_review_ref", "dual_control_ack_ref", "dual_control_runtime_ref"),
                        error_prefix="dual_control_contract:dual_control_evidence_ref",
                    )
                )
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
        if not closure_plan_errors:
            closure_plan_body, closure_plan_read_error = _read_json_file(closure_plan_path)
            if closure_plan_read_error is None and closure_plan_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=closure_plan_body,
                        required_keys=("summary_ref", "review_ref", "readiness_ref"),
                        error_prefix=(
                            "closure_security_reliability_scalability_plans_contract:"
                            "closure_security_reliability_scalability_plans_evidence_ref"
                        ),
                    )
                )
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
        if not scalability_errors:
            scalability_body, scalability_read_error = _read_json_file(scalability_path)
            if scalability_read_error is None and scalability_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=scalability_body,
                        required_keys=("summary_ref", "review_ref"),
                        error_prefix="scalability_strategy_contract:scalability_strategy_evidence_ref",
                    )
                )
    full_build_order_path = output_dir / "strategy" / "full_build_order_progression.json"
    if full_build_order_path.exists():
        full_build_order_errors = validate_full_build_order_progression_path(full_build_order_path)
        for token in full_build_order_errors:
            errors.append(f"full_build_order_progression_contract:{token}")
        if not full_build_order_errors:
            full_build_order_body, full_build_order_read_error = _read_json_file(full_build_order_path)
            if full_build_order_read_error is None and full_build_order_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=full_build_order_body,
                        required_keys=(
                            "run_manifest_ref",
                            "orchestration_ref",
                            "progression_ref",
                        ),
                        error_prefix=(
                            "full_build_order_progression_contract:"
                            "full_build_order_progression_evidence_ref"
                        ),
                    )
                )
    service_boundaries_path = output_dir / "strategy" / "service_boundaries.json"
    if service_boundaries_path.exists():
        service_boundaries_errors = validate_service_boundaries_path(service_boundaries_path)
        for token in service_boundaries_errors:
            errors.append(f"service_boundaries_contract:{token}")
        if not service_boundaries_errors:
            service_boundaries_body, service_boundaries_read_error = _read_json_file(service_boundaries_path)
            if service_boundaries_read_error is None and service_boundaries_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=service_boundaries_body,
                        required_keys=("review_ref", "boundaries_ref"),
                        error_prefix="service_boundaries_contract:service_boundaries_evidence_ref",
                    )
                )
    storage_architecture_path = output_dir / "storage" / "storage_architecture.json"
    if storage_architecture_path.exists():
        storage_architecture_errors = validate_storage_architecture_path(storage_architecture_path)
        for token in storage_architecture_errors:
            errors.append(f"{_STORAGE_CONTRACT_ERROR_PREFIX}{token}")
    production_observability_path = output_dir / "observability" / "production_observability.json"
    if production_observability_path.exists():
        production_observability_errors = validate_production_observability_path(
            production_observability_path
        )
        for token in production_observability_errors:
            errors.append(f"production_observability_contract:{token}")
        if not production_observability_errors:
            production_observability_body, production_observability_read_error = _read_json_file(
                production_observability_path
            )
            if (
                production_observability_read_error is None
                and production_observability_body is not None
            ):
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=production_observability_body,
                        required_keys=(
                            "traces_ref",
                            "orchestration_ref",
                            "run_log_ref",
                            "observability_ref",
                        ),
                        error_prefix=(
                            "production_observability_contract:"
                            "production_observability_evidence_ref"
                        ),
                    )
                )
    observability_component_path = output_dir / "observability" / _COMPONENT_RUNTIME_FILENAME
    if observability_component_path.exists():
        observability_component_errors = validate_observability_component_path(observability_component_path)
        for token in observability_component_errors:
            errors.append(f"observability_component_contract:{token}")
        if not observability_component_errors:
            observability_component_body, observability_component_read_error = _read_json_file(
                observability_component_path
            )
            if observability_component_read_error is None and observability_component_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=observability_component_body,
                        required_keys=(
                            "production_observability_ref",
                            "run_log_ref",
                            "traces_ref",
                            "orchestration_ref",
                            "component_ref",
                        ),
                        error_prefix=(
                            "observability_component_contract:"
                            "observability_component_evidence_ref"
                        ),
                    )
                )
    production_orchestration_path = output_dir / "orchestration" / "production_orchestration.json"
    if production_orchestration_path.exists():
        production_orchestration_errors = validate_production_orchestration_path(
            production_orchestration_path
        )
        for token in production_orchestration_errors:
            errors.append(f"production_orchestration_contract:{token}")
        if not production_orchestration_errors:
            production_orchestration_body, production_orchestration_read_error = _read_json_file(
                production_orchestration_path
            )
            if (
                production_orchestration_read_error is None
                and production_orchestration_body is not None
            ):
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=production_orchestration_body,
                        required_keys=("lease_table_ref", "shard_map_ref"),
                        error_prefix=(
                            "production_orchestration_contract:"
                            "production_orchestration_evidence_ref"
                        ),
                    )
                )
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
        if not career_strategy_errors:
            career_strategy_body, career_strategy_read_error = _read_json_file(career_strategy_path)
            if career_strategy_read_error is None and career_strategy_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=career_strategy_body,
                        required_keys=(
                            "summary_ref",
                            "review_ref",
                            "promotion_package_ref",
                            "career_strategy_ref",
                        ),
                        error_prefix="career_strategy_layer_contract:career_strategy_layer_evidence_ref",
                    )
                )
    identity_authz_plane_path = output_dir / "iam" / "identity_authz_plane.json"
    if identity_authz_plane_path.exists():
        identity_authz_plane_errors = validate_identity_authz_plane_path(identity_authz_plane_path)
        for token in identity_authz_plane_errors:
            errors.append(f"identity_authz_plane_contract:{token}")
        if not identity_authz_plane_errors:
            identity_authz_body, identity_authz_read_error = _read_json_file(identity_authz_plane_path)
            if identity_authz_read_error is None and identity_authz_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=identity_authz_body,
                        required_keys=("permission_matrix_ref", "action_audit_ref", "lease_table_ref"),
                        error_prefix="identity_authz_plane_contract:identity_authz_plane_evidence_ref",
                    )
                )
    production_identity_authz_path = output_dir / "iam" / "production_identity_authorization.json"
    if production_identity_authz_path.exists():
        production_identity_authz_errors = validate_production_identity_authorization_path(
            production_identity_authz_path
        )
        for token in production_identity_authz_errors:
            errors.append(f"production_identity_authorization_contract:{token}")
        if not production_identity_authz_errors:
            production_identity_authz_body, production_identity_authz_read_error = _read_json_file(
                production_identity_authz_path
            )
            if production_identity_authz_read_error is None and production_identity_authz_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=production_identity_authz_body,
                        required_keys=("permission_matrix_ref", "action_audit_ref", "strategy_proposal_ref"),
                        error_prefix=(
                            "production_identity_authorization_contract:"
                            "production_identity_authorization_evidence_ref"
                        ),
                    )
                )
    role_agents_path = output_dir / "capability" / "role_agents.json"
    if role_agents_path.exists():
        role_agents_errors = validate_role_agents_path(role_agents_path)
        for token in role_agents_errors:
            errors.append(f"role_agents_contract:{token}")
        if not role_agents_errors:
            role_agents_body, role_agents_read_error = _read_json_file(role_agents_path)
            if role_agents_read_error is None and role_agents_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=role_agents_body,
                        required_keys=("summary_ref", "traces_ref", "skill_nodes_ref", "role_agents_ref"),
                        error_prefix="role_agents_contract:role_agents_evidence_ref",
                    )
                )
    memory_architecture_path = output_dir / "memory" / "runtime_memory_architecture.json"
    if memory_architecture_path.exists():
        memory_architecture_errors = validate_memory_architecture_in_runtime_path(
            memory_architecture_path
        )
        for token in memory_architecture_errors:
            errors.append(f"memory_architecture_in_runtime_contract:{token}")
        if not memory_architecture_errors:
            memory_architecture_body, memory_architecture_read_error = _read_json_file(
                memory_architecture_path
            )
            if memory_architecture_read_error is None and memory_architecture_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=memory_architecture_body,
                        required_keys=(
                            "retrieval_bundle_ref",
                            "quality_metrics_ref",
                            "quarantine_ref",
                            "memory_architecture_ref",
                        ),
                        error_prefix=(
                            "memory_architecture_in_runtime_contract:"
                            "memory_architecture_in_runtime_evidence_ref"
                        ),
                    )
                )
    memory_system_path = output_dir / "memory" / "memory_system.json"
    if memory_system_path.exists():
        memory_system_errors = validate_memory_system_path(memory_system_path)
        for token in memory_system_errors:
            errors.append(f"memory_system_contract:{token}")
        if not memory_system_errors:
            memory_system_body, memory_system_read_error = _read_json_file(memory_system_path)
            if memory_system_read_error is None and memory_system_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=memory_system_body,
                        required_keys=(
                            "retrieval_bundle_ref",
                            "quality_metrics_ref",
                            "quarantine_ref",
                            "memory_system_ref",
                        ),
                        error_prefix="memory_system_contract:memory_system_evidence_ref",
                    )
                )
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
        if not risk_budgets_permission_matrix_errors:
            risk_budgets_permission_matrix_body, risk_budgets_permission_matrix_read_error = _read_json_file(
                risk_budgets_permission_matrix_path
            )
            if (
                risk_budgets_permission_matrix_read_error is None
                and risk_budgets_permission_matrix_body is not None
            ):
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=risk_budgets_permission_matrix_body,
                        required_keys=("summary_ref", "review_ref", "runtime_ref"),
                        error_prefix=(
                            "risk_budgets_permission_matrix_contract:"
                            "risk_budgets_permission_matrix_evidence_ref"
                        ),
                    )
                )
    autonomy_boundaries_path = output_dir / "safety" / "autonomy_boundaries_tokens_expiry.json"
    if autonomy_boundaries_path.exists():
        autonomy_boundaries_errors = validate_autonomy_boundaries_runtime_path(autonomy_boundaries_path)
        for token in autonomy_boundaries_errors:
            errors.append(f"{_AUTONOMY_BOUNDARIES_CONTRACT_ERROR_PREFIX}{token}")
        if not autonomy_boundaries_errors:
            autonomy_body, autonomy_read_error = _read_json_file(autonomy_boundaries_path)
            if autonomy_read_error is not None or autonomy_body is None:
                autonomy_body = {}
            evidence = autonomy_body.get("evidence") if isinstance(autonomy_body, dict) else {}
            token_context_ref = evidence.get("token_context_ref") if isinstance(evidence, dict) else None
            if isinstance(token_context_ref, str) and token_context_ref.strip():
                token_context_path = output_dir / token_context_ref.strip()
                if not token_context_path.is_file():
                    errors.append(
                        f"{_AUTONOMY_BOUNDARIES_CONTRACT_ERROR_PREFIX}"
                        "autonomy_boundaries_evidence_ref_missing:token_context_ref"
                    )
                else:
                    token_context_body, token_context_read_error = _read_json_file(token_context_path)
                    autonomy_token_context = autonomy_body.get("token_context")
                    if token_context_read_error is None and token_context_body is not None:
                        if autonomy_token_context != token_context_body:
                            errors.append(
                                f"{_AUTONOMY_BOUNDARIES_CONTRACT_ERROR_PREFIX}"
                                "autonomy_boundaries_token_context_mismatch"
                            )
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
        if not event_store_semantics_errors:
            event_store_semantics_body, event_store_semantics_read_error = _read_json_file(
                event_store_semantics_path
            )
            if event_store_semantics_read_error is None and event_store_semantics_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=event_store_semantics_body,
                        required_keys=(
                            "replay_manifest_ref",
                            "run_events_ref",
                            "traces_ref",
                            "semantics_ref",
                        ),
                        error_prefix="event_store_semantics_contract:event_store_semantics_evidence_ref",
                    )
                )
    replay_fail_closed_path = output_dir / "replay" / "fail_closed.json"
    replay_fail_closed_errors = validate_replay_fail_closed_path(replay_fail_closed_path)
    for token in replay_fail_closed_errors:
        errors.append(f"replay_fail_closed_contract:{token}")
    if not replay_fail_closed_errors:
        replay_fail_closed_body, replay_fail_closed_read_error = _read_json_file(replay_fail_closed_path)
        if replay_fail_closed_read_error is None and replay_fail_closed_body is not None:
            errors.extend(
                _append_missing_evidence_ref_errors(
                    output_dir=output_dir,
                    body=replay_fail_closed_body,
                    required_keys=(
                        "replay_manifest_ref",
                        "traces_ref",
                        "run_events_ref",
                        "replay_fail_closed_ref",
                    ),
                    error_prefix="replay_fail_closed_contract:replay_fail_closed_evidence_ref",
                )
            )
    failure_path_artifacts_path = output_dir / "replay" / "failure_path_artifacts.json"
    if failure_path_artifacts_path.exists():
        failure_path_artifacts_errors = validate_failure_path_artifacts_path(failure_path_artifacts_path)
        for token in failure_path_artifacts_errors:
            errors.append(f"failure_path_artifacts_contract:{token}")
        if not failure_path_artifacts_errors:
            failure_path_artifacts_body, failure_path_artifacts_read_error = _read_json_file(
                failure_path_artifacts_path
            )
            if failure_path_artifacts_read_error is None and failure_path_artifacts_body is not None:
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=failure_path_artifacts_body,
                        required_keys=(
                            "summary_ref",
                            "replay_manifest_ref",
                            "failure_path_artifacts_ref",
                        ),
                        error_prefix=(
                            "failure_path_artifacts_contract:"
                            "failure_path_artifacts_evidence_ref"
                        ),
                    )
                )
                failure_path_run_id = failure_path_artifacts_body.get("run_id")
                evidence = failure_path_artifacts_body.get("evidence")
                if isinstance(failure_path_run_id, str) and failure_path_run_id.strip() and isinstance(evidence, dict):
                    summary_ref = evidence.get("summary_ref")
                    if isinstance(summary_ref, str) and summary_ref.strip():
                        summary_body, summary_ref_error = _read_json_file(output_dir / summary_ref.strip())
                        if summary_ref_error is None and summary_body is not None:
                            summary_run_id = summary_body.get("runId")
                            if not isinstance(summary_run_id, str):
                                summary_run_id = summary_body.get("run_id")
                            if (
                                isinstance(summary_run_id, str)
                                and summary_run_id.strip()
                                and summary_run_id.strip() != failure_path_run_id.strip()
                            ):
                                errors.append(
                                    "failure_path_artifacts_contract:"
                                    "failure_path_artifacts_run_id_mismatch:summary"
                                )
                    replay_manifest_ref = evidence.get("replay_manifest_ref")
                    if isinstance(replay_manifest_ref, str) and replay_manifest_ref.strip():
                        replay_manifest_body, replay_manifest_ref_error = _read_json_file(
                            output_dir / replay_manifest_ref.strip()
                        )
                        if replay_manifest_ref_error is None and replay_manifest_body is not None:
                            replay_run_id = replay_manifest_body.get("run_id")
                            if not isinstance(replay_run_id, str):
                                replay_run_id = replay_manifest_body.get("runId")
                            if (
                                isinstance(replay_run_id, str)
                                and replay_run_id.strip()
                                and replay_run_id.strip() != failure_path_run_id.strip()
                            ):
                                errors.append(
                                    "failure_path_artifacts_contract:"
                                    "failure_path_artifacts_run_id_mismatch:replay_manifest"
                                )
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
        if not strategy_overlay_runtime_errors:
            strategy_overlay_runtime_body, strategy_overlay_runtime_read_error = _read_json_file(
                strategy_overlay_runtime_path
            )
            if (
                strategy_overlay_runtime_read_error is None
                and strategy_overlay_runtime_body is not None
            ):
                errors.extend(
                    _append_missing_evidence_ref_errors(
                        output_dir=output_dir,
                        body=strategy_overlay_runtime_body,
                        required_keys=("proposal_ref", "overlay_ref", "traces_ref"),
                        error_prefix="strategy_overlay_runtime_contract:strategy_overlay_runtime_evidence_ref",
                    )
                )
    errors.extend(validate_policy_bundle_rollback(output_dir))
    errors.extend(_validate_policy_bundle_rollback_coherence(output_dir))
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
    self_learning_decision = {}
    if isinstance(self_learning_loop_body, dict):
        maybe_decision = self_learning_loop_body.get("decision")
        if isinstance(maybe_decision, dict):
            self_learning_decision = maybe_decision
    for hs_id in failed_hard_stop_ids:
        errors.append(f"hard_stop_failed:{hs_id}")
    if (
        failed_hard_stop_ids
        and self_learning_decision.get("decision") == "promote"
    ):
        errors.append("self_learning_loop_contract:self_learning_loop_promote_with_active_hard_stop")
    ready = validation_ready(summary["balanced_gates"]) if summary.get("balanced_gates") else False
    strict_ok = ready and not errors and len(failed_hard_stop_ids) == 0
    return {"ok": strict_ok, "errors": errors, "hard_stops": hard, "validation_ready": ready}
