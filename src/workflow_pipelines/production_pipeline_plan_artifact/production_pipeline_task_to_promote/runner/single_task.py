"""Single-task CLI path: run mode, persist traces, CTO artifacts, report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.config import DEFAULT_CONFIG
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.run_logging import (
    log_cto_gate_layer,
    log_orchestration_persisted,
    log_run_banner,
    log_run_end,
    log_run_error,
    log_run_failure_context,
    log_structured_output_summary,
    log_success_artifact_layer,
    log_traces_persisted,
    setup_run_logger,
    shutdown_run_logger,
)
from production_architecture.storage.storage.storage import append_jsonl, ensure_dir, write_json
from core_components.orchestrator.common.utils import create_run_id, outputs_base
from guardrails_and_safety import validate_execution_run_directory

from workflow_pipelines.retry_repeat_profile.retry_pipeline_contract import (
    RETRY_PIPELINE_REPEAT_CONTRACT,
    validate_repeat_profile_result,
)
from workflow_pipelines.run_manifest.run_manifest_contract import (
    RUN_MANIFEST_CONTRACT,
    validate_run_manifest_dict,
)

from .cto_publish import write_cto_gate_layer
from .completion_layer import write_completion_artifacts
from .career_strategy_layer import write_career_strategy_layer_artifact
from .closure_security_reliability_scalability_plans_layer import (
    write_closure_security_reliability_scalability_plans_artifact,
)
from .consolidated_improvements_layer import write_consolidated_improvements_artifact
from .auditability_layer import write_auditability_artifact
from .dual_control_layer import write_dual_control_artifact
from .event_lineage_layer import write_event_lineage_artifacts
from .event_store_component_layer import write_event_store_component_artifact
from .event_store_semantics_layer import write_event_store_semantics_artifact
from .evaluation_service_layer import write_evaluation_service_artifact
from .evolution_layer import write_evolution_artifacts
from .failure_path_artifacts_layer import write_failure_path_artifacts
from .memory_artifact_layer import write_memory_artifacts
from .organization_layer import write_organization_artifacts
from .failure_summary import write_failure_summary
from .identity_authz_plane_layer import write_identity_authz_plane_artifact
from .local_runtime_spine_layer import write_local_runtime_spine_artifact
from .implementation_roadmap_layer import write_implementation_roadmap_artifact
from .learning_lineage_layer import write_learning_lineage_artifact
from .learning_service_layer import write_learning_service_artifact
from .memory_architecture_runtime_layer import write_memory_architecture_in_runtime_artifact
from .memory_system_layer import write_memory_system_artifact
from .orchestration_run_error_contract import validate_orchestration_run_error_dict
from .online_evaluation_shadow_canary_layer import write_online_evaluation_shadow_canary_artifact
from .observability_layer import write_production_observability_artifact
from .observability_component_layer import write_observability_component_artifact
from .objective_policy_engine_layer import write_objective_policy_engine_artifact
from .orchestration_run_start_layer import write_orchestration_run_start_runtime_artifact
from .orchestration_run_end_layer import write_orchestration_run_end_runtime_artifact
from .orchestration_run_error_layer import write_orchestration_run_error_runtime_artifact
from .orchestration_stage_event_layer import write_orchestration_stage_event_runtime_artifact
from .orchestrator_component_layer import write_orchestrator_component_artifact
from .persist_traces import (
    append_orchestration_run_start,
    append_orchestration_stage_events,
    persist_traces,
)
from .replay_fail_closed_layer import write_replay_fail_closed_artifact
from .production_readiness_layer import write_production_readiness_artifact
from .production_orchestration_layer import write_production_orchestration_artifact
from .production_pipeline_plan_artifact_layer import write_production_pipeline_plan_artifact
from .practice_engine_layer import write_practice_engine_artifact
from .production_identity_authorization_layer import write_production_identity_authorization_artifact
from .promotion_evaluation_layer import write_promotion_evaluation_artifact
from .regression_testing_surface_layer import write_regression_testing_surface_artifact
from .retry_repeat_profile_layer import write_retry_repeat_profile_runtime_artifact
from .rollback_rules_policy_bundle_layer import write_rollback_rules_policy_bundle_artifact
from .role_agents_layer import write_role_agents_artifact
from .run_manifest_runtime_layer import write_run_manifest_runtime_artifact
from .risk_budgets_permission_matrix_layer import write_risk_budgets_permission_matrix_artifact
from .safety_controller_layer import write_safety_controller_artifact
from .self_learning_loop_layer import write_self_learning_loop_artifact
from .service_boundaries_layer import write_service_boundaries_artifact
from .scalability_strategy_layer import write_scalability_strategy_artifact
from .strategy_overlay_layer import write_strategy_overlay_runtime_artifact
from .full_build_order_progression_layer import write_full_build_order_progression_artifact
from .storage_layer import write_storage_architecture_artifact
from .topology_and_repository_layout_layer import write_topology_and_repository_layout_artifact
from .traces_jsonl_event_row_layer import write_traces_jsonl_event_row_runtime_artifact
from .success_artifacts import write_success_artifact_layer as write_success_disk_layer


def _run_single_attempt(
    task: str,
    mode: str,
    *,
    project_step_id: str | None = None,
    project_session_dir: str | None = None,
) -> dict:
    import workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner as runner_pkg

    run_id = create_run_id()
    output_dir = outputs_base() / "runs" / run_id
    ensure_dir(output_dir)
    manifest: dict[str, Any] = {
        "schema": RUN_MANIFEST_CONTRACT,
        "run_id": run_id,
        "mode": mode,
        "task": task,
    }
    if project_step_id is not None and str(project_step_id).strip():
        manifest["project_step_id"] = str(project_step_id)
    if project_session_dir is not None and str(project_session_dir).strip():
        manifest["project_session_dir"] = str(project_session_dir)
    rm_errs = validate_run_manifest_dict(manifest)
    if rm_errs:
        raise ValueError(f"run_manifest_contract:{','.join(rm_errs)}")
    write_json(output_dir / "run-manifest.json", manifest)
    write_run_manifest_runtime_artifact(output_dir=output_dir)
    orchestration = output_dir / "orchestration.jsonl"
    run_logger = setup_run_logger(run_id, output_dir)
    log_run_banner(
        run_logger,
        run_id=run_id,
        mode=mode,
        task=task,
        provider=DEFAULT_CONFIG.provider,
        model=DEFAULT_CONFIG.implementation_model,
    )
    events: list[dict] = []
    output = ""
    try:
        if mode == "baseline":
            output, events = runner_pkg.run_baseline(run_id, "manual-task", task, DEFAULT_CONFIG)
        elif mode == "phased_pipeline":
            output, events = runner_pkg.run_phased(run_id, "manual-task", task, DEFAULT_CONFIG)
        else:
            output, events = runner_pkg.run_guarded(run_id, "manual-task", task, DEFAULT_CONFIG)
    except Exception as exc:
        log_run_error(run_logger, "Pipeline raised before trace write", exc)
        err_line = {
            "run_id": run_id,
            "type": "run_error",
            "mode": mode,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
        err_line_errs = validate_orchestration_run_error_dict(err_line)
        if err_line_errs:
            raise ValueError(f"orchestration_run_error_contract:{','.join(err_line_errs)}")
        append_jsonl(orchestration, err_line)
        write_orchestration_run_error_runtime_artifact(output_dir=output_dir, run_id=run_id)
        write_orchestration_run_end_runtime_artifact(output_dir=output_dir, run_id=run_id)
        write_traces_jsonl_event_row_runtime_artifact(output_dir=output_dir, run_id=run_id)
        write_local_runtime_spine_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
        write_failure_summary(output_dir, run_id, mode, exc, partial=False)
        log_run_failure_context(
            run_logger,
            detail="No trace lines were written because the pipeline failed immediately.",
        )
        log_run_end(run_logger, artifacts={}, output_dir=str(output_dir))
        shutdown_run_logger(run_logger)
        return {
            "run_id": run_id,
            "output_dir": str(output_dir),
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }

    persist_traces(output_dir, events, run_logger)
    write_traces_jsonl_event_row_runtime_artifact(output_dir=output_dir, run_id=run_id)
    log_traces_persisted(
        run_logger,
        event_count=len(events),
        traces_path=str(output_dir / "traces.jsonl"),
    )
    append_orchestration_run_start(orchestration, run_id, mode)
    write_orchestration_run_start_runtime_artifact(output_dir=output_dir, run_id=run_id)
    append_orchestration_stage_events(orchestration, run_id, events)
    write_orchestration_stage_event_runtime_artifact(output_dir=output_dir, run_id=run_id)
    log_orchestration_persisted(
        run_logger,
        orchestration_path=str(orchestration),
        stage_event_lines=len(events),
    )

    try:
        parsed = json.loads(output)
    except (json.JSONDecodeError, TypeError) as exc:
        log_run_error(run_logger, "Final output is not valid JSON", exc)
        parse_err_line = {
            "run_id": run_id,
            "type": "run_error",
            "mode": mode,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "detail": "output_parse_failed",
        }
        parse_errs = validate_orchestration_run_error_dict(parse_err_line)
        if parse_errs:
            raise ValueError(f"orchestration_run_error_contract:{','.join(parse_errs)}")
        append_jsonl(orchestration, parse_err_line)
        write_orchestration_run_error_runtime_artifact(output_dir=output_dir, run_id=run_id)
        write_orchestration_run_end_runtime_artifact(output_dir=output_dir, run_id=run_id)
        write_traces_jsonl_event_row_runtime_artifact(output_dir=output_dir, run_id=run_id)
        write_local_runtime_spine_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
        write_failure_summary(output_dir, run_id, mode, exc, partial=True)
        log_run_failure_context(
            run_logger,
            detail="Traces were written, but the model output string was not valid JSON.",
        )
        log_run_end(run_logger, artifacts={}, output_dir=str(output_dir))
        shutdown_run_logger(run_logger)
        return {
            "run_id": run_id,
            "output_dir": str(output_dir),
            "error": {"type": type(exc).__name__, "message": str(exc), "detail": "output_parse_failed"},
        }

    log_structured_output_summary(run_logger, parsed)

    artifacts = write_success_disk_layer(
        parsed=parsed,
        events=events,
        output_dir=output_dir,
        run_id=run_id,
        mode=mode,
        orchestration=orchestration,
    )
    write_production_observability_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    write_observability_component_artifact(output_dir=output_dir, run_id=run_id)
    refusal = parsed.get("refusal")
    is_safety_refusal = isinstance(refusal, dict) and refusal.get("code") == "unsafe_action_refused"
    phased_plan = parsed.get("phased_plan") if mode == "phased_pipeline" else None
    if isinstance(phased_plan, dict) and not is_safety_refusal:
        ensure_dir(output_dir / "program")
        write_json(output_dir / "program" / "phased_plan.json", phased_plan)
    if mode in ("guarded_pipeline", "phased_pipeline") and not is_safety_refusal:
        write_completion_artifacts(
            output_dir=output_dir,
            run_id=run_id,
            task=task,
            parsed=parsed,
            events=events,
        )
        write_dual_control_artifact(output_dir=output_dir, run_id=run_id)
        write_rollback_rules_policy_bundle_artifact(output_dir=output_dir, run_id=run_id)
        write_production_pipeline_plan_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    write_event_lineage_artifacts(output_dir=output_dir, run_id=run_id)
    write_replay_fail_closed_artifact(output_dir=output_dir, run_id=run_id)
    write_failure_path_artifacts(output_dir=output_dir, run_id=run_id)
    write_orchestrator_component_artifact(output_dir=output_dir, run_id=run_id)
    write_event_store_semantics_artifact(output_dir=output_dir, run_id=run_id)
    write_event_store_component_artifact(output_dir=output_dir, run_id=run_id)
    write_auditability_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    skill_nodes = write_memory_artifacts(output_dir=output_dir, run_id=run_id, parsed=parsed, events=events)
    write_memory_system_artifact(output_dir=output_dir, run_id=run_id)
    write_memory_architecture_in_runtime_artifact(output_dir=output_dir, run_id=run_id)
    write_role_agents_artifact(
        output_dir=output_dir,
        run_id=run_id,
        parsed=parsed if isinstance(parsed, dict) else {},
        events=events if isinstance(events, list) else [],
        skill_nodes=skill_nodes,
    )
    write_evolution_artifacts(
        output_dir=output_dir,
        run_id=run_id,
        mode=mode,
        parsed=parsed,
        events=events,
        skill_nodes=skill_nodes,
    )
    write_learning_service_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    write_promotion_evaluation_artifact(output_dir=output_dir, run_id=run_id)
    write_learning_lineage_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    write_online_evaluation_shadow_canary_artifact(output_dir=output_dir, run_id=run_id)
    write_regression_testing_surface_artifact(output_dir=output_dir, run_id=run_id)
    write_evaluation_service_artifact(output_dir=output_dir, run_id=run_id)
    write_practice_engine_artifact(output_dir=output_dir, run_id=run_id)
    write_self_learning_loop_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    write_organization_artifacts(output_dir=output_dir, run_id=run_id)
    write_production_orchestration_artifact(output_dir=output_dir, run_id=run_id)
    write_identity_authz_plane_artifact(output_dir=output_dir, run_id=run_id)
    write_production_identity_authorization_artifact(output_dir=output_dir, run_id=run_id)
    write_strategy_overlay_runtime_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    log_success_artifact_layer(run_logger, artifacts=artifacts)

    cto = write_cto_gate_layer(
        run_id=run_id,
        mode=mode,
        parsed=parsed,
        events=events,
        output_dir=output_dir,
    )
    write_risk_budgets_permission_matrix_artifact(output_dir=output_dir, run_id=run_id, cto=cto)
    write_safety_controller_artifact(output_dir=output_dir, run_id=run_id, cto=cto)
    write_objective_policy_engine_artifact(output_dir=output_dir, run_id=run_id, mode=mode, cto=cto)
    write_service_boundaries_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    write_scalability_strategy_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode=mode,
        parsed=parsed if isinstance(parsed, dict) else {},
        events=events if isinstance(events, list) else [],
        cto=cto,
    )
    write_full_build_order_progression_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    write_storage_architecture_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    write_career_strategy_layer_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    write_topology_and_repository_layout_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    write_consolidated_improvements_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    write_production_readiness_artifact(output_dir=output_dir, run_id=run_id, mode=mode, cto=cto)
    write_closure_security_reliability_scalability_plans_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode=mode,
        policy_bundle_valid=not any(not bool(row.get("passed")) for row in cto.get("hard_stops", [])),
    )
    write_implementation_roadmap_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    log_cto_gate_layer(run_logger, cto=cto)

    write_orchestration_run_error_runtime_artifact(output_dir=output_dir, run_id=run_id)
    write_orchestration_run_end_runtime_artifact(output_dir=output_dir, run_id=run_id)
    write_local_runtime_spine_artifact(output_dir=output_dir, run_id=run_id, mode=mode)
    log_run_end(run_logger, artifacts=artifacts, output_dir=str(output_dir))
    shutdown_run_logger(run_logger)
    return {"run_id": run_id, "output": output, "output_dir": str(output_dir)}


def execute_single_task(
    task: str,
    mode: str,
    *,
    repeat: int = 1,
    project_step_id: str | None = None,
    project_session_dir: str | None = None,
) -> dict:
    """Run one or more isolated attempts (V1 RepeatProfile when ``repeat`` >= 2).

    When invoked from the project driver, pass ``project_step_id`` and ``project_session_dir``
    so each run's ``run-manifest.json`` links back to the session plan (Phase 1 contract).
    """
    if repeat < 1:
        raise ValueError("repeat must be >= 1")
    if repeat == 1:
        attempt = _run_single_attempt(
            task,
            mode,
            project_step_id=project_step_id,
            project_session_dir=project_session_dir,
        )
        out_dir = attempt.get("output_dir")
        if isinstance(out_dir, str) and out_dir.strip():
            validation_ready = False
            if "error" not in attempt:
                verdict = validate_execution_run_directory(Path(out_dir), mode=mode)
                validation_ready = bool(verdict.get("ok") and verdict.get("validation_ready"))
            write_retry_repeat_profile_runtime_artifact(
                output_dir=Path(out_dir),
                run_id=str(attempt.get("run_id") or ""),
                repeat=1,
                attempts=[attempt],
                all_runs_no_pipeline_error=("error" not in attempt),
                validation_ready_all=validation_ready,
            )
        return attempt
    attempts: list[dict] = []
    for _ in range(repeat):
        attempts.append(
            _run_single_attempt(
                task,
                mode,
                project_step_id=project_step_id,
                project_session_dir=project_session_dir,
            )
        )
    gates_ok: list[bool] = []
    for attempt in attempts:
        out_dir = attempt.get("output_dir")
        if not out_dir or attempt.get("error"):
            gates_ok.append(False)
            continue
        verdict = validate_execution_run_directory(Path(out_dir), mode=mode)
        gates_ok.append(bool(verdict.get("ok") and verdict.get("validation_ready")))
    result = {
        "schema": RETRY_PIPELINE_REPEAT_CONTRACT,
        "repeat": repeat,
        "task": task,
        "mode": mode,
        "runs": attempts,
        "all_runs_no_pipeline_error": all("error" not in r for r in attempts),
        "validation_ready_all": all(gates_ok) if gates_ok else False,
    }
    rp_errs = validate_repeat_profile_result(result, repeat=repeat)
    if rp_errs:
        raise ValueError(f"retry_pipeline_contract:{','.join(rp_errs)}")
    for attempt in attempts:
        out_dir = attempt.get("output_dir")
        run_id = attempt.get("run_id")
        if not isinstance(out_dir, str) or not out_dir.strip():
            continue
        if not isinstance(run_id, str) or not run_id.strip():
            continue
        write_retry_repeat_profile_runtime_artifact(
            output_dir=Path(out_dir),
            run_id=run_id,
            repeat=repeat,
            attempts=attempts,
            all_runs_no_pipeline_error=bool(result["all_runs_no_pipeline_error"]),
            validation_ready_all=bool(result["validation_ready_all"]),
        )
    return result
