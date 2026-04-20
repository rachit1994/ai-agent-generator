"""Repeat ``execute_single_task`` until a stop condition or iteration cap.

Use this when you want SDE to keep driving the same task string across many
isolated runs (e.g. "continue implementing X until gates pass" or a fixed
cadence with ``stop_when=never``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from guardrails_and_safety import validate_execution_run_directory

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner import execute_single_task

from .project_driver import run_project_session

StopWhen = Literal["never", "validation_ready", "definition_of_done"]


def _definition_of_done_passed(output_dir: Path) -> bool:
    path = output_dir / "review.json"
    if not path.is_file():
        return False
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    dod = body.get("definition_of_done")
    if not isinstance(dod, dict):
        return False
    return bool(dod.get("all_required_passed"))


def _pipeline_error_response(
    iterations: list[dict[str, Any]], result: dict[str, Any]
) -> dict[str, Any]:
    return {
        "exit_code": 1,
        "stopped_reason": "pipeline_error",
        "iterations": iterations,
        "last_run_id": result.get("run_id"),
        "last_output_dir": result.get("output_dir"),
    }


def _success_response(
    stopped_reason: str,
    iterations: list[dict[str, Any]],
    result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "exit_code": 0,
        "stopped_reason": stopped_reason,
        "iterations": iterations,
        "last_run_id": result.get("run_id"),
        "last_output_dir": result.get("output_dir"),
    }


def _try_early_exit(
    stop_when: StopWhen,
    output_dir: Path,
    mode: str,
    entry: dict[str, Any],
    result: dict[str, Any],
    iterations: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if stop_when == "validation_ready":
        verdict = validate_execution_run_directory(output_dir, mode=mode)
        entry["validation"] = verdict
        if verdict.get("ok") and verdict.get("validation_ready"):
            return _success_response("validation_ready", iterations, result)
        return None
    if stop_when == "definition_of_done":
        dod_ok = _definition_of_done_passed(output_dir)
        entry["definition_of_done_passed"] = dod_ok
        if dod_ok:
            return _success_response("definition_of_done", iterations, result)
        return None
    return None


def _terminal_after_iteration(
    *,
    result: dict[str, Any],
    entry: dict[str, Any],
    stop_when: StopWhen,
    mode: str,
    iterations: list[dict[str, Any]],
    stop_on_pipeline_error: bool,
) -> dict[str, Any] | None:
    if result.get("error") and stop_on_pipeline_error:
        return _pipeline_error_response(iterations, result)
    out_dir = result.get("output_dir")
    if not out_dir:
        if stop_on_pipeline_error:
            return {
                "exit_code": 1,
                "stopped_reason": "missing_output_dir",
                "iterations": iterations,
            }
        return None
    if stop_when == "never":
        return None
    return _try_early_exit(stop_when, Path(out_dir), mode, entry, result, iterations)


def run_continuous_until(
    *,
    task: str,
    mode: str,
    max_iterations: int,
    stop_when: StopWhen,
    stop_on_pipeline_error: bool = True,
) -> dict[str, Any]:
    """
    Run ``execute_single_task`` up to ``max_iterations`` times.

    Returns a JSON-serializable summary including ``exit_code`` (0 = stopped
    early because the chosen condition was met; 1 = cap reached or pipeline
    error when ``stop_on_pipeline_error``).
    """
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")

    iterations: list[dict[str, Any]] = []
    for i in range(max_iterations):
        result = execute_single_task(task, mode, repeat=1)
        entry: dict[str, Any] = {"index": i + 1, "result": result}
        iterations.append(entry)
        term = _terminal_after_iteration(
            result=result,
            entry=entry,
            stop_when=stop_when,
            mode=mode,
            iterations=iterations,
            stop_on_pipeline_error=stop_on_pipeline_error,
        )
        if term is not None:
            return term

    last = iterations[-1]["result"] if iterations else {}
    tail = {
        "iterations": iterations,
        "last_run_id": last.get("run_id"),
        "last_output_dir": last.get("output_dir"),
    }
    if stop_when == "never":
        return {"exit_code": 0, "stopped_reason": "max_iterations", **tail}
    return {"exit_code": 1, "stopped_reason": "max_iterations_without_match", **tail}


def run_continuous_project_session(
    *,
    session_dir: Path,
    repo_root: Path,
    max_iterations: int,
    mode: str,
    max_concurrent_agents: int = 1,
    progress_file: Path | None = None,
    parallel_worktrees: bool = False,
    lease_stale_sec: int | None = None,
    enforce_plan_lock: bool = False,
    require_non_stub_reviewer: bool = False,
) -> dict[str, Any]:
    """
    Run :func:`run_project_session` with ``max_steps=max_iterations`` (same budget knob as ``continuous``).

    Use when ``--project-session-dir`` or ``--project-plan`` is passed instead of repeating a fixed ``--task``.
    Optional ``progress_file`` overrides the default ``<session-dir>/progress.json`` (Phase 5).
    Optional ``parallel_worktrees`` forwards to :func:`run_project_session` (Phase 6).
    Optional ``lease_stale_sec`` forwards Phase 8 lease TTL / pruning (``0`` disables).
    Optional ``enforce_plan_lock`` requires Stage 1 lock-readiness before project execution.
    Optional ``require_non_stub_reviewer`` applies strict reviewer policy when enforcing the lock.
    """
    summary = run_project_session(
        session_dir,
        repo_root=repo_root,
        max_steps=max_iterations,
        mode=mode,
        max_concurrent_agents=max_concurrent_agents,
        progress_file=progress_file,
        parallel_worktrees=parallel_worktrees,
        lease_stale_sec=lease_stale_sec,
        enforce_plan_lock=enforce_plan_lock,
        require_non_stub_reviewer=require_non_stub_reviewer,
    )
    return {"driver": "project_session", **summary}
