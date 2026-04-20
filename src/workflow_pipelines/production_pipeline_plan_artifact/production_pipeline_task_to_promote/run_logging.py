from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

_LOG_MAX_FIELD = 8000
_LOG_EXCERPT = 500
_LOG_RULE = "=" * 80
_LOG_RULE_THIN = "-" * 80
_LOG_RULE_ERR = "!" * 80

_STAGE_SUMMARY: dict[str, str] = {
    "executor": "Executor: model produced candidate output for the task.",
    "executor_fix": "Executor (fix pass): model revised output after a failed verifier.",
    "repair": "Repair: model produced a corrected JSON response after checks failed.",
    "planner_doc": "Planner: wrote the planning document (markdown).",
    "planner_prompt": "Planner: produced the prompt that will be sent to the executor.",
    "verifier": "Verifier: evaluated the output against quality/policy checks.",
    "verifier_fix": "Verifier (post-fix): re-evaluated output after the fix pass.",
    "finalize": "Finalize: consolidated scores, failure reason, and run outcome.",
}


def setup_run_logger(run_id: str, output_dir: Path) -> logging.Logger:
    """Attach a file logger for this run to ``output_dir / run.log``."""
    name = f"orchestrator.run.{run_id}"
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    for h in tuple(logger.handlers):
        logger.removeHandler(h)
        h.close()
    log_path = output_dir / "run.log"
    handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def shutdown_run_logger(logger: logging.Logger) -> None:
    for h in tuple(logger.handlers):
        logger.removeHandler(h)
        h.flush()
        h.close()


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [truncated, {len(text) - limit} more chars]"


def log_run_banner(
    logger: logging.Logger,
    *,
    run_id: str,
    mode: str,
    task: str,
    provider: str,
    model: str,
) -> None:
    logger.info("")
    logger.info(_LOG_RULE)
    logger.info("SDE SINGLE TASK RUN — human-readable narrative (newest sections at bottom)")
    logger.info(_LOG_RULE)
    logger.info("Run id: %s", run_id)
    logger.info("Mode: %s  (baseline = one-shot JSON; guarded_pipeline = planner + executor + verifier)", mode)
    logger.info("Provider: %s  Implementation model: %s", provider, model)
    logger.info("What happens next: the pipeline runs, then each step is logged below in order.")
    logger.info(_LOG_RULE_THIN)
    logger.info("TASK TEXT")
    logger.info(_LOG_RULE_THIN)
    logger.info("%s", _clip(task.strip(), _LOG_MAX_FIELD))
    logger.info(_LOG_RULE_THIN)


def log_benchmark_banner(
    logger: logging.Logger,
    *,
    run_id: str,
    suite_path: str,
    mode: str,
    task_count: int,
) -> None:
    logger.info("")
    logger.info(_LOG_RULE)
    logger.info("SDE BENCHMARK RUN — human-readable narrative")
    logger.info(_LOG_RULE)
    logger.info("run_id=%s", run_id)
    logger.info("suite_path=%s", suite_path)
    logger.info("mode=%s  (baseline / guarded_pipeline / both)", mode)
    logger.info("task_count=%s", task_count)
    logger.info("Per-task traces appear below in execution order; then files on disk are summarized.")
    logger.info(_LOG_RULE_THIN)


def log_benchmark_traces_written(logger: logging.Logger, *, event_count: int, traces_path: str) -> None:
    logger.info("")
    logger.info("Wrote %d combined trace events (all tasks, selected branches) -> %s", event_count, traces_path)


def log_benchmark_verdict(logger: logging.Logger, *, verdict: str, summary_path: str) -> None:
    logger.info("")
    logger.info("Benchmark verdict: %s", verdict)
    logger.info("Full metrics and deltas: %s", summary_path)


def log_task_scope(logger: logging.Logger, *, task_id: str, prompt: str, branch: str) -> None:
    logger.info("")
    logger.info(">>> Benchmark task task_id=%s branch=%s", task_id, branch)
    logger.info("Prompt:\n%s", _clip(prompt.strip(), _LOG_MAX_FIELD))
    logger.info("<<< end task header")


def _agent_line(meta: dict[str, Any]) -> str:
    agent = meta.get("agent")
    if isinstance(agent, dict):
        return (
            f"agent name={agent.get('name')} type={agent.get('type')} role={agent.get('role')}"
            f" model={meta.get('model')!r}"
        )
    return f"agent={agent!r} model={meta.get('model')!r}"


def _score_lines(event: dict[str, Any]) -> list[str]:
    score = event.get("score")
    if not isinstance(score, dict):
        return []
    passed = score.get("passed")
    rel = score.get("reliability")
    val = score.get("validity")
    return [
        f"  score: passed={passed!r} reliability={rel!r} validity={val!r}",
    ]


def _token_lines(event: dict[str, Any]) -> list[str]:
    ti = event.get("token_input")
    to = event.get("token_output")
    if ti is None and to is None:
        return []
    return [f"  tokens (approx): input={ti!r} output={to!r}"]


def _metadata_narrative_lines(meta: dict[str, Any], errors: list[Any]) -> list[str]:
    lines: list[str] = []
    if errors:
        lines.append(f"  errors: {errors}")
    model_error = meta.get("model_error")
    if isinstance(model_error, str) and model_error.strip():
        lines.append(f"  model_error: {model_error.strip()[:2000]}")
    if meta.get("fast_path"):
        lines.append("  note: fast_path planner branch (simple task)")
    planner_doc = meta.get("planner_doc")
    if isinstance(planner_doc, str) and planner_doc.strip():
        lines.append("  planner_document:")
        lines.append(_clip(planner_doc.strip(), _LOG_MAX_FIELD))
    executor_prompt = meta.get("executor_prompt")
    if isinstance(executor_prompt, str) and executor_prompt.strip():
        lines.append("  prompt_to_executor:")
        lines.append(_clip(executor_prompt.strip(), _LOG_MAX_FIELD))
    raw_excerpt = meta.get("raw_response_excerpt")
    if isinstance(raw_excerpt, str) and raw_excerpt.strip():
        lines.append(f"  model_output_excerpt:\n{_clip(raw_excerpt.strip(), _LOG_EXCERPT)}")
    verifier_report = meta.get("verifier_report")
    if isinstance(verifier_report, dict):
        lines.append(f"  verifier_report: {json.dumps(verifier_report, indent=2)[:4000]}")
    check_pass = meta.get("check_pass_map")
    if isinstance(check_pass, dict):
        lines.append(f"  check_pass_map: {check_pass}")
    failure_reason = meta.get("failure_reason")
    if isinstance(failure_reason, str) and failure_reason:
        lines.append(f"  failure_reason: {failure_reason}")
    return lines


def log_trace_narrative(logger: logging.Logger, event: dict[str, Any]) -> None:
    """Append a human-readable narrative for one trace/orchestration event."""
    stage = str(event.get("stage", "?"))
    task_id = event.get("task_id", "?")
    mode = event.get("mode", "?")
    started = event.get("started_at", "")
    ended = event.get("ended_at", "")
    latency = event.get("latency_ms")
    retry = event.get("retry_count")
    errors = event.get("errors") or []
    meta = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
    summary = _STAGE_SUMMARY.get(stage, f"Pipeline stage {stage!r}.")
    head = [
        "",
        _LOG_RULE_THIN,
        f"STEP: {stage}",
        f"  {summary}",
        f"  task_id={task_id!r} mode={mode!r}",
        f"  time window: {started} -> {ended}   latency_ms={latency}   retry_count={retry}",
        f"  {_agent_line(meta)}",
    ]
    head.extend(_score_lines(event))
    head.extend(_token_lines(event))
    logger.info("\n".join(head + _metadata_narrative_lines(meta, errors if isinstance(errors, list) else [])))


def log_traces_persisted(logger: logging.Logger, *, event_count: int, traces_path: str) -> None:
    logger.info("")
    logger.info(_LOG_RULE)
    logger.info("TRACES ON DISK")
    logger.info(_LOG_RULE)
    logger.info(
        "Appended %d trace events to %s (same events as machine-readable traces.jsonl).",
        event_count,
        traces_path,
    )


def log_orchestration_persisted(
    logger: logging.Logger,
    *,
    orchestration_path: str,
    stage_event_lines: int,
) -> None:
    logger.info(
        "Appended orchestration stream: run_start + %d stage_event lines -> %s",
        stage_event_lines,
        orchestration_path,
    )
    logger.info("(orchestration.jsonl is a compact audit log; this file is the readable story.)")


def log_structured_output_summary(logger: logging.Logger, parsed: dict[str, Any]) -> None:
    """Log parsed pipeline JSON (answer / checks / refusal) in plain language."""
    logger.info("")
    logger.info(_LOG_RULE)
    logger.info("PARSED MODEL OUTPUT (JSON)")
    logger.info(_LOG_RULE)
    refusal = parsed.get("refusal")
    if isinstance(refusal, dict):
        logger.info(
            "Refusal object present: code=%r reason=%r",
            refusal.get("code"),
            _clip(str(refusal.get("reason", "")), 800),
        )
    else:
        logger.info("Refusal: none (model did not refuse the task).")
    checks = parsed.get("checks")
    if isinstance(checks, list) and checks:
        logger.info("Structured checks (%d):", len(checks))
        for c in checks:
            if isinstance(c, dict):
                name = c.get("name", "?")
                ok = c.get("passed")
                logger.info("  - %r -> %s", name, "passed" if ok else "FAILED")
    else:
        logger.info("Checks: none or empty list.")
    answer = parsed.get("answer")
    if isinstance(answer, str):
        logger.info("Answer: %d characters.", len(answer))
        logger.info("Answer preview:\n%s", _clip(answer.strip(), _LOG_EXCERPT))
    logger.info(_LOG_RULE_THIN)


def log_success_artifact_layer(logger: logging.Logger, *, artifacts: dict[str, str]) -> None:
    logger.info("")
    logger.info(_LOG_RULE)
    logger.info("ARTIFACT FILES (answer, optional script, outputs/, first summary pass)")
    logger.info(_LOG_RULE)
    for key in sorted(artifacts.keys()):
        logger.info("  %s\n    -> %s", key, artifacts[key])
    logger.info(_LOG_RULE_THIN)


def log_cto_gate_layer(logger: logging.Logger, *, cto: dict[str, Any]) -> None:
    """Readable summary after token_context, review, hard-stops, balanced gates."""
    logger.info("")
    logger.info(_LOG_RULE)
    logger.info("CTO / QUALITY GATE LAYER")
    logger.info(_LOG_RULE)
    logger.info("Review status: %s", cto.get("review_status"))
    logger.info("Artifact manifest complete: %s", cto.get("manifest_complete"))
    logger.info("validation_ready (strict profile): %s", cto.get("validation_ready"))
    bg = cto.get("balanced_gates")
    if isinstance(bg, dict):
        logger.info(
            "Balanced gates: reliability=%s delivery=%s governance=%s composite=%s profile=%r",
            bg.get("reliability"),
            bg.get("delivery"),
            bg.get("governance"),
            bg.get("composite"),
            bg.get("threshold_profile"),
        )
    hs = cto.get("hard_stops")
    if isinstance(hs, list) and hs:
        parts = []
        for item in hs:
            if isinstance(item, dict):
                hid = item.get("id", "?")
                ok = item.get("passed")
                parts.append(f"{hid}={'OK' if ok else 'FAIL'}")
        logger.info("Hard stops: %s", ", ".join(parts))
    logger.info("Second report pass generated (report.md updated with gates).")
    logger.info(_LOG_RULE_THIN)


def log_run_error(logger: logging.Logger, msg: str, exc: BaseException) -> None:
    logger.error("")
    logger.error(_LOG_RULE_ERR)
    logger.error("%s: %s", msg, exc, exc_info=(type(exc), exc, exc.__traceback__))
    logger.error(_LOG_RULE_ERR)


def log_run_failure_context(logger: logging.Logger, *, detail: str) -> None:
    """Short prose when the run stops early (after error already logged)."""
    logger.info("")
    logger.info("Run stopped early: %s", detail)
    logger.info("See messages above for the technical exception / parse error.")


def log_run_end(
    logger: logging.Logger,
    *,
    artifacts: dict[str, str] | None = None,
    output_dir: str | None = None,
) -> None:
    logger.info("")
    logger.info(_LOG_RULE)
    logger.info("RUN COMPLETE")
    logger.info(_LOG_RULE)
    if output_dir:
        logger.info("Output directory: %s", output_dir)
        logger.info("Tip: open run.log (this file), traces.jsonl, summary.json, and report.md together.")
    if artifacts:
        logger.info("Key artifact paths from this run:")
        for key in sorted(artifacts.keys()):
            logger.info("  %s -> %s", key, artifacts[key])
    logger.info(_LOG_RULE)
