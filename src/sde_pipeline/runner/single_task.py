"""Single-task CLI path: run mode, persist traces, CTO artifacts, report."""

from __future__ import annotations

import json

from sde_pipeline.config import DEFAULT_CONFIG
from sde_pipeline.run_logging import (
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
from sde_foundations.storage import append_jsonl, ensure_dir, write_json
from sde_foundations.utils import create_run_id, outputs_base

from .cto_publish import write_cto_gate_layer
from .failure_summary import write_failure_summary
from .persist_traces import (
    append_orchestration_run_start,
    append_orchestration_stage_events,
    persist_traces,
)
from .success_artifacts import write_success_artifact_layer as write_success_disk_layer


def execute_single_task(task: str, mode: str) -> dict:
    import sde_pipeline.runner as runner_pkg

    run_id = create_run_id()
    output_dir = outputs_base() / "runs" / run_id
    ensure_dir(output_dir)
    write_json(
        output_dir / "run-manifest.json",
        {
            "schema": "sde.run_manifest.v1",
            "run_id": run_id,
            "mode": mode,
            "task": task,
        },
    )
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
        else:
            output, events = runner_pkg.run_guarded(run_id, "manual-task", task, DEFAULT_CONFIG)
    except Exception as exc:
        log_run_error(run_logger, "Pipeline raised before trace write", exc)
        append_jsonl(
            orchestration,
            {
                "run_id": run_id,
                "type": "run_error",
                "mode": mode,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
        )
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
        append_jsonl(
            orchestration,
            {
                "run_id": run_id,
                "type": "run_error",
                "mode": mode,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "detail": "output_parse_failed",
            },
        )
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
