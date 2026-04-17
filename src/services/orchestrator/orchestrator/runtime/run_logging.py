from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

_LOG_MAX_FIELD = 8000
_LOG_EXCERPT = 500


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
    logger.info("=== run start ===")
    logger.info("run_id=%s mode=%s provider=%s implementation_model=%s", run_id, mode, provider, model)
    logger.info("task:\n%s", _clip(task.strip(), _LOG_MAX_FIELD))


def log_benchmark_banner(
    logger: logging.Logger,
    *,
    run_id: str,
    suite_path: str,
    mode: str,
    task_count: int,
) -> None:
    logger.info("=== benchmark start ===")
    logger.info(
        "run_id=%s suite_path=%s mode=%s task_count=%s",
        run_id,
        suite_path,
        mode,
        task_count,
    )


def log_task_scope(logger: logging.Logger, *, task_id: str, prompt: str, branch: str) -> None:
    logger.info("--- task_id=%s branch=%s ---", task_id, branch)
    logger.info("prompt:\n%s", _clip(prompt.strip(), _LOG_MAX_FIELD))


def _agent_line(meta: dict[str, Any]) -> str:
    agent = meta.get("agent")
    if isinstance(agent, dict):
        return (
            f"agent name={agent.get('name')} type={agent.get('type')} role={agent.get('role')}"
            f" model={meta.get('model')!r}"
        )
    return f"agent={agent!r} model={meta.get('model')!r}"


def _metadata_narrative_lines(meta: dict[str, Any], errors: list[Any]) -> list[str]:
    lines: list[str] = []
    if errors:
        lines.append(f"  errors: {errors}")
    model_error = meta.get("model_error")
    if isinstance(model_error, str) and model_error.strip():
        lines.append(f"  model_error: {model_error.strip()[:2000]}")
    if meta.get("fast_path"):
        lines.append("  note: fast_path planner branch")
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
    stage = event.get("stage", "?")
    task_id = event.get("task_id", "?")
    mode = event.get("mode", "?")
    started = event.get("started_at", "")
    ended = event.get("ended_at", "")
    latency = event.get("latency_ms")
    retry = event.get("retry_count")
    errors = event.get("errors") or []
    meta = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
    head = [
        f"stage={stage!r} task_id={task_id!r} mode={mode!r}",
        f"  window: {started} -> {ended} latency_ms={latency} retry_count={retry}",
        f"  {_agent_line(meta)}",
    ]
    logger.info("\n".join(head + _metadata_narrative_lines(meta, errors if isinstance(errors, list) else [])))


def log_run_error(logger: logging.Logger, msg: str, exc: BaseException) -> None:
    logger.error("%s: %s", msg, exc, exc_info=(type(exc), exc, exc.__traceback__))


def log_run_end(logger: logging.Logger, *, artifacts: dict[str, str] | None = None) -> None:
    logger.info("=== run end ===")
    if artifacts:
        logger.info("artifacts: %s", artifacts)
