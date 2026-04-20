"""Contract for ``benchmark-checkpoint.json`` (resume progress envelope)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

BENCHMARK_CHECKPOINT_CONTRACT: Final = "sde.benchmark_checkpoint.v1"

_CHECKPOINT_MODES: Final = frozenset({"baseline", "guarded_pipeline", "both"})


def _errs_checkpoint_core(b: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if b.get("schema") != BENCHMARK_CHECKPOINT_CONTRACT:
        errs.append("benchmark_checkpoint_schema")
    rid = b.get("run_id")
    if not isinstance(rid, str) or not rid.strip():
        errs.append("benchmark_checkpoint_run_id")
    sp = b.get("suite_path")
    if not isinstance(sp, str) or not sp.strip():
        errs.append("benchmark_checkpoint_suite_path")
    mode = b.get("mode")
    if mode not in _CHECKPOINT_MODES:
        errs.append("benchmark_checkpoint_mode")
    return errs


def _errs_checkpoint_max_tasks(b: dict[str, Any]) -> list[str]:
    if "max_tasks" not in b:
        return []
    mt = b.get("max_tasks")
    if mt is not None and (not isinstance(mt, int) or mt < 0):
        return ["benchmark_checkpoint_max_tasks"]
    return []


def _errs_checkpoint_ids_and_flags(b: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if "continue_on_error" not in b or not isinstance(b.get("continue_on_error"), bool):
        errs.append("benchmark_checkpoint_continue_on_error")
    cids = b.get("completed_task_ids")
    if not isinstance(cids, list):
        errs.append("benchmark_checkpoint_completed_task_ids")
    else:
        for idx, item in enumerate(cids):
            if not isinstance(item, str) or not item.strip():
                errs.append(f"benchmark_checkpoint_completed_task_id:{idx}")
    if "finished" not in b or not isinstance(b.get("finished"), bool):
        errs.append("benchmark_checkpoint_finished_type")
    ts = b.get("updated_at_ms")
    if not isinstance(ts, int) or ts < 0:
        errs.append("benchmark_checkpoint_updated_at_ms")
    return errs


def validate_benchmark_checkpoint_dict(body: Any) -> list[str]:
    """Return stable error tokens for ``run_benchmark`` checkpoint shape."""
    if not isinstance(body, dict):
        return ["benchmark_checkpoint_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_checkpoint_core(b))
    errs.extend(_errs_checkpoint_max_tasks(b))
    errs.extend(_errs_checkpoint_ids_and_flags(b))
    return errs


def validate_benchmark_checkpoint_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["benchmark_checkpoint_file_missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ["benchmark_checkpoint_unreadable"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return ["benchmark_checkpoint_json"]
    return validate_benchmark_checkpoint_dict(parsed)
