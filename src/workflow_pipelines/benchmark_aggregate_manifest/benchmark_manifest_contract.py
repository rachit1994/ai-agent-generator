"""Contract for benchmark aggregate ``benchmark-manifest.json`` (resume / validate / replay)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

BENCHMARK_MANIFEST_CONTRACT: Final = "sde.benchmark_manifest.v1"

_BENCHMARK_MODES: Final = frozenset({"baseline", "guarded_pipeline", "both"})


def _errs_benchmark_core(b: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if b.get("schema") != BENCHMARK_MANIFEST_CONTRACT:
        errs.append("benchmark_manifest_schema")
    rid = b.get("run_id")
    if not isinstance(rid, str) or not rid.strip():
        errs.append("benchmark_manifest_run_id")
    sp = b.get("suite_path")
    if not isinstance(sp, str) or not sp.strip():
        errs.append("benchmark_manifest_suite_path")
    mode = b.get("mode")
    if mode not in _BENCHMARK_MODES:
        errs.append("benchmark_manifest_mode")
    return errs


def _errs_benchmark_tasks_list(tasks: Any) -> list[str]:
    if not isinstance(tasks, list):
        return ["benchmark_manifest_tasks"]
    errs: list[str] = []
    for idx, row in enumerate(tasks):
        if not isinstance(row, dict):
            errs.append(f"benchmark_manifest_task_not_object:{idx}")
            continue
        tid = row.get("taskId", row.get("task_id"))
        if not isinstance(tid, str) or not tid.strip():
            errs.append(f"benchmark_manifest_task_id:{idx}")
        pr = row.get("prompt")
        if not isinstance(pr, str):
            errs.append(f"benchmark_manifest_task_prompt:{idx}")
    return errs


def _errs_benchmark_tail(b: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if "max_tasks" in b:
        mt = b.get("max_tasks")
        if mt is not None and (not isinstance(mt, int) or mt < 0):
            errs.append("benchmark_manifest_max_tasks")
    if "continue_on_error" not in b or not isinstance(b.get("continue_on_error"), bool):
        errs.append("benchmark_manifest_continue_on_error")
    return errs


def validate_benchmark_manifest_dict(body: Any) -> list[str]:
    """Return stable error tokens for ``run_benchmark`` manifest shape."""
    if not isinstance(body, dict):
        return ["benchmark_manifest_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_benchmark_core(b))
    errs.extend(_errs_benchmark_tasks_list(b.get("tasks")))
    errs.extend(_errs_benchmark_tail(b))
    return errs


def validate_benchmark_manifest_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["benchmark_manifest_file_missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ["benchmark_manifest_unreadable"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return ["benchmark_manifest_json"]
    return validate_benchmark_manifest_dict(parsed)
