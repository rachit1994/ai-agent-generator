"""Run baseline and/or guarded modes per task and collect trace events."""

from __future__ import annotations

from typing import Any

from sde_pipeline.config import DEFAULT_CONFIG
from sde_modes.modes.baseline import run_baseline
from sde_modes.modes.guarded import run_guarded
from sde_pipeline.run_logging import log_task_scope, log_trace_narrative


def run_suite_tasks(
    run_logger: Any,
    run_id: str,
    mode: str,
    tasks: list[dict],
) -> tuple[list[dict], list[dict]]:
    baseline_events: list[dict] = []
    guarded_events: list[dict] = []
    for task in tasks:
        tid = task["taskId"]
        prompt = task["prompt"]
        if mode in ("baseline", "both"):
            log_task_scope(run_logger, task_id=tid, prompt=prompt, branch="baseline")
            _, events = run_baseline(run_id, tid, prompt, DEFAULT_CONFIG)
            for ev in events:
                log_trace_narrative(run_logger, ev)
            baseline_events.extend(events)
        if mode in ("guarded_pipeline", "both"):
            log_task_scope(run_logger, task_id=tid, prompt=prompt, branch="guarded_pipeline")
            _, events = run_guarded(run_id, tid, prompt, DEFAULT_CONFIG)
            for ev in events:
                log_trace_narrative(run_logger, ev)
            guarded_events.extend(events)
    return baseline_events, guarded_events
