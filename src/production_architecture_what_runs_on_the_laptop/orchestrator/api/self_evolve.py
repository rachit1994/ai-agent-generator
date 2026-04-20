"""Bounded self-evolve driver: roadmap review (Gemma) + optional task runs + learning log."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from workflow_pipelines.production_pipeline_task_to_promote.runner import execute_single_task

from .gemma_roadmap_review import append_roadmap_learning_line, roadmap_review


def _overall_pct(review: dict[str, Any] | None) -> int | None:
    if not isinstance(review, dict):
        return None
    raw = review.get("overall_pct")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _maybe_print_evolve_round(verbose: bool, round_idx: int, review_out: dict[str, Any], last_pct: int | None) -> None:
    if not verbose:
        return
    print(
        json.dumps(
            {
                "round": round_idx,
                "roadmap_ok": review_out.get("ok"),
                "overall_pct": last_pct,
                "model_error": review_out.get("model_error"),
            },
            indent=2,
        )
    )


def run_bounded_evolve_loop(
    *,
    repo_root: Path,
    max_rounds: int,
    target_pct: int,
    task: str | None,
    mode: str,
    learning_path: Path,
    emit_task_json: bool = False,
    verbose: bool = False,
) -> tuple[int, dict[str, Any]]:
    """
    Each round: Gemma ``roadmap_review`` → append learning JSONL → optional ``execute_single_task``.

    Returns ``(exit_code, last_roadmap_review_payload)``. ``exit_code`` is ``0`` if
    ``overall_pct >= target_pct`` on a successful parse, else ``1``.
    This does **not** prove "all versions fullest"; it automates the review cadence only.
    """
    if max_rounds < 1:
        raise ValueError("max_rounds must be >= 1")
    last_pct: int | None = None
    last_out: dict[str, Any] = {}
    for i in range(max_rounds):
        review_out = roadmap_review(repo_root=repo_root)
        last_out = review_out
        append_roadmap_learning_line(learning_path, review_out)
        last_pct = _overall_pct(review_out.get("review") if review_out.get("ok") else None)
        _maybe_print_evolve_round(verbose, i + 1, review_out, last_pct)
        if review_out.get("ok") and last_pct is not None and last_pct >= target_pct:
            return 0, last_out
        if task:
            task_result = execute_single_task(task, mode, repeat=1)
            if emit_task_json:
                print(json.dumps({"round_task_result": task_result}, indent=2))
    if last_pct is not None and last_pct >= target_pct:
        return 0, last_out
    return 1, last_out
