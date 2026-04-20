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
from .event_lineage_layer import write_event_lineage_artifacts
from .evolution_layer import write_evolution_artifacts
from .memory_artifact_layer import write_memory_artifacts
from .organization_layer import write_organization_artifacts
from .failure_summary import write_failure_summary
from .orchestration_run_error_contract import validate_orchestration_run_error_dict
from .persist_traces import (
    append_orchestration_run_start,
    append_orchestration_stage_events,
    persist_traces,
)
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
    log_traces_persisted(
        run_logger,
        event_count=len(events),
        traces_path=str(output_dir / "traces.jsonl"),
    )
    append_orchestration_run_start(orchestration, run_id, mode)
    append_orchestration_stage_events(orchestration, run_id, events)
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
    write_event_lineage_artifacts(output_dir=output_dir, run_id=run_id)
    write_memory_artifacts(output_dir=output_dir, run_id=run_id)
    write_evolution_artifacts(output_dir=output_dir, run_id=run_id)
    write_organization_artifacts(output_dir=output_dir, run_id=run_id)
    log_success_artifact_layer(run_logger, artifacts=artifacts)

    cto = write_cto_gate_layer(
        run_id=run_id,
        mode=mode,
        parsed=parsed,
        events=events,
        output_dir=output_dir,
    )
    log_cto_gate_layer(run_logger, cto=cto)

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
        return _run_single_attempt(
            task,
            mode,
            project_step_id=project_step_id,
            project_session_dir=project_session_dir,
        )
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
    return result
