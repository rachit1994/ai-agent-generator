from __future__ import annotations

import json
from pathlib import Path

from orchestrator.runtime.config import DEFAULT_CONFIG, config_snapshot
from orchestrator.runtime.cto_gates import (
    build_review,
    build_token_context,
    compute_balanced_gates,
    evaluate_hard_stops,
    metrics_from_events,
    validation_ready,
)
from orchestrator.runtime.eval import aggregate_metrics
from orchestrator.runtime.artifacts import extract_python_code
from orchestrator.runtime.modes.baseline import run_baseline
from orchestrator.runtime.modes.guarded import run_guarded
from orchestrator.runtime.run_logging import (
    log_run_banner,
    log_run_end,
    log_run_error,
    log_trace_narrative,
    setup_run_logger,
    shutdown_run_logger,
)
from orchestrator.runtime.report import generate_report
from orchestrator.runtime.storage import append_jsonl, ensure_dir, write_json
from orchestrator.runtime.utils import create_run_id, outputs_base


def _harvest_pipeline_artifacts(events: list[dict], output_dir: Path) -> dict[str, str]:
    artifacts: dict[str, str] = {}
    planner_doc = ""
    executor_prompt = ""
    verifier_report: dict | None = None
    for event in events:
        meta = event.get("metadata") or {}
        if isinstance(meta.get("planner_doc"), str) and meta.get("planner_doc"):
            planner_doc = meta["planner_doc"]
        if isinstance(meta.get("executor_prompt"), str) and meta.get("executor_prompt"):
            executor_prompt = meta["executor_prompt"]
        if isinstance(meta.get("verifier_report"), dict):
            verifier_report = meta["verifier_report"]
    if planner_doc:
        doc_path = output_dir / "planner_doc.md"
        doc_path.write_text(planner_doc + "\n", encoding="utf-8")
        artifacts["planner_doc_md"] = str(doc_path)
    if executor_prompt:
        prompt_path = output_dir / "executor_prompt.txt"
        prompt_path.write_text(executor_prompt + "\n", encoding="utf-8")
        artifacts["executor_prompt_txt"] = str(prompt_path)
    if verifier_report is not None:
        report_path = output_dir / "verifier_report.json"
        write_json(report_path, verifier_report)
        artifacts["verifier_report_json"] = str(report_path)
    return artifacts


def _write_failure_summary(
    output_dir: Path,
    run_id: str,
    mode: str,
    exc: BaseException,
    *,
    partial: bool,
) -> None:
    write_json(
        output_dir / "summary.json",
        {
            "runId": run_id,
            "mode": mode,
            "runStatus": "failed",
            "partial": partial,
            "error": {"type": type(exc).__name__, "message": str(exc)},
            "provider": DEFAULT_CONFIG.provider,
            "model": DEFAULT_CONFIG.implementation_model,
        },
    )
    write_json(output_dir / "config-snapshot.json", config_snapshot())


def execute_single_task(task: str, mode: str) -> dict:
    run_id = create_run_id()
    output_dir = outputs_base() / "runs" / run_id
    ensure_dir(output_dir)
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
            output, events = run_baseline(run_id, "manual-task", task, DEFAULT_CONFIG)
        else:
            output, events = run_guarded(run_id, "manual-task", task, DEFAULT_CONFIG)
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
        _write_failure_summary(output_dir, run_id, mode, exc, partial=False)
        log_run_end(run_logger, artifacts={})
        shutdown_run_logger(run_logger)
        return {
            "run_id": run_id,
            "output_dir": str(output_dir),
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }

    traces = output_dir / "traces.jsonl"
    for event in events:
        append_jsonl(traces, event)
        log_trace_narrative(run_logger, event)

    append_jsonl(
        orchestration,
        {
            "run_id": run_id,
            "type": "run_start",
            "mode": mode,
            "provider": DEFAULT_CONFIG.provider,
            "model": DEFAULT_CONFIG.implementation_model,
        },
    )
    for event in events:
        append_jsonl(
            orchestration,
            {
                "run_id": run_id,
                "type": "stage_event",
                "stage": event.get("stage"),
                "retry_count": event.get("retry_count"),
                "errors": event.get("errors"),
                "agent": (event.get("metadata") or {}).get("agent"),
                "model": (event.get("metadata") or {}).get("model"),
                "model_error": (event.get("metadata") or {}).get("model_error"),
                "attempt": (event.get("metadata") or {}).get("attempt"),
                "raw_response_excerpt": (event.get("metadata") or {}).get("raw_response_excerpt"),
                "started_at": event.get("started_at"),
                "ended_at": event.get("ended_at"),
                "latency_ms": event.get("latency_ms"),
            },
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
        _write_failure_summary(output_dir, run_id, mode, exc, partial=True)
        log_run_end(run_logger, artifacts={})
        shutdown_run_logger(run_logger)
        return {
            "run_id": run_id,
            "output_dir": str(output_dir),
            "error": {"type": type(exc).__name__, "message": str(exc), "detail": "output_parse_failed"},
        }

    answer_text = str(parsed.get("answer", ""))
    (output_dir / "answer.txt").write_text(answer_text, encoding="utf-8")
    code = extract_python_code(answer_text)
    artifacts: dict[str, str] = {"answer_txt": str(output_dir / "answer.txt")}
    if code:
        script_path = output_dir / "generated_script.py"
        script_path.write_text(code + "\n", encoding="utf-8")
        artifacts["generated_script_py"] = str(script_path)
    artifacts.update(_harvest_pipeline_artifacts(events, output_dir))
    outputs_sub = output_dir / "outputs"
    ensure_dir(outputs_sub)
    (outputs_sub / "README.txt").write_text(
        "SDE run outputs: generated artifacts and extracted files land here.\n",
        encoding="utf-8",
    )
    write_json(
        outputs_sub / "manifest.json",
        {"run_id": run_id, "mode": mode, "artifacts": list(artifacts.keys())},
    )
    append_jsonl(
        orchestration,
        {
            "run_id": run_id,
            "type": "run_end",
            "artifacts": artifacts,
            "output_refusal": parsed.get("refusal"),
            "checks": parsed.get("checks"),
        },
    )
    write_json(output_dir / "config-snapshot.json", config_snapshot())
    metrics = aggregate_metrics(events)
    write_json(
        output_dir / "summary.json",
        {
            "runId": run_id,
            "mode": mode,
            "runStatus": "ok",
            "provider": DEFAULT_CONFIG.provider,
            "model": DEFAULT_CONFIG.implementation_model,
            "metrics": metrics,
        },
    )
    generate_report(run_id)
    token_ctx = build_token_context(
        run_id,
        events,
        max_tokens=DEFAULT_CONFIG.budgets.max_tokens,
    )
    write_json(output_dir / "token_context.json", token_ctx)
    review = build_review(
        run_id,
        mode,
        parsed,
        output_dir,
        events,
        run_status="ok",
    )
    write_json(output_dir / "review.json", review)
    hard_stops = evaluate_hard_stops(output_dir, events, token_ctx, run_status="ok")
    manifest_complete = all(m["present"] for m in review["artifact_manifest"])
    balanced = compute_balanced_gates(
        metrics_from_events(events),
        hard_stops,
        review_status=review["status"],
        manifest_complete=manifest_complete,
    )
    write_json(
        output_dir / "summary.json",
        {
            "runId": run_id,
            "mode": mode,
            "runStatus": "ok",
            "provider": DEFAULT_CONFIG.provider,
            "model": DEFAULT_CONFIG.implementation_model,
            "metrics": metrics,
            "balanced_gates": balanced,
            "quality": {
                "validation_ready": validation_ready(balanced),
                "strict_threshold_profile": balanced.get("threshold_profile"),
            },
        },
    )
    generate_report(run_id)
    log_run_end(run_logger, artifacts=artifacts)
    shutdown_run_logger(run_logger)
    return {"run_id": run_id, "output": output, "output_dir": str(output_dir)}
