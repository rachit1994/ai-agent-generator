"""Run baseline and/or guarded modes per task and collect trace events."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from sde_modes.modes.baseline import run_baseline
from sde_modes.modes.guarded import run_guarded
from sde_pipeline.config import DEFAULT_CONFIG
from sde_pipeline.run_logging import log_task_scope, log_trace_narrative
from sde_foundations.utils import ms_to_iso


def synthetic_finalize_failure_event(
    run_id: str,
    task_id: str,
    branch_mode: str,
    exc: Exception,
    config: Any,
) -> dict[str, Any]:
    t0 = int(time.time() * 1000)
    return {
        "run_id": run_id,
        "task_id": task_id,
        "mode": branch_mode,
        "model": config.implementation_model,
        "provider": config.provider,
        "stage": "finalize",
        "started_at": ms_to_iso(t0),
        "ended_at": ms_to_iso(t0),
        "latency_ms": 0,
        "token_input": 0,
        "token_output": 0,
        "estimated_cost_usd": 0.0,
        "retry_count": 0,
        "errors": ["task_run_exception"],
        "score": {"passed": False, "reliability": 0.0, "validity": 0.0},
        "metadata": {
            "agent": {"name": "system", "type": "error", "role": "finalize"},
            "failure_reason": "task_run_exception",
            "error": {"type": type(exc).__name__, "message": str(exc)[:500]},
        },
    }


def _collect_branch_events(
    run_logger: Any,
    run_id: str,
    tid: str,
    prompt: str,
    branch_mode: str,
    runner,
    *,
    continue_on_error: bool,
) -> list[dict]:
    log_task_scope(run_logger, task_id=tid, prompt=prompt, branch=branch_mode)
    try:
        _, events = runner(run_id, tid, prompt, DEFAULT_CONFIG)
    except Exception as exc:
        if not continue_on_error:
            raise
        events = [synthetic_finalize_failure_event(run_id, tid, branch_mode, exc, DEFAULT_CONFIG)]
    for ev in events:
        log_trace_narrative(run_logger, ev)
    return events


def run_suite_tasks(
    run_logger: Any,
    run_id: str,
    mode: str,
    tasks: list[dict],
    *,
    continue_on_error: bool = False,
    on_task_events: Callable[[str, list[dict[str, Any]], list[dict[str, Any]]], None] | None = None,
) -> tuple[list[dict], list[dict]]:
    baseline_events: list[dict] = []
    guarded_events: list[dict] = []
    for task in tasks:
        tid = task["taskId"]
        prompt = task["prompt"]
        baseline_chunk: list[dict] = []
        guarded_chunk: list[dict] = []
        if mode in ("baseline", "both"):
            baseline_chunk = _collect_branch_events(
                run_logger, run_id, tid, prompt, "baseline", run_baseline, continue_on_error=continue_on_error
            )
            baseline_events.extend(baseline_chunk)
        if mode in ("guarded_pipeline", "both"):
            guarded_chunk = _collect_branch_events(
                run_logger,
                run_id,
                tid,
                prompt,
                "guarded_pipeline",
                run_guarded,
                continue_on_error=continue_on_error,
            )
            guarded_events.extend(guarded_chunk)
        if on_task_events is not None:
            on_task_events(tid, baseline_chunk, guarded_chunk)
    return baseline_events, guarded_events
