"""Deterministic benchmark checkpoint runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    BENCHMARK_CHECKPOINT_RUNTIME_CONTRACT,
    BENCHMARK_CHECKPOINT_RUNTIME_SCHEMA_VERSION,
)


def build_benchmark_checkpoint_runtime(*, checkpoint: dict[str, Any]) -> dict[str, Any]:
    run_id = str(checkpoint.get("run_id") or "").strip()
    checkpoint_present = bool(checkpoint)
    finished = bool(checkpoint.get("finished")) if checkpoint_present else False
    completed_task_ids = checkpoint.get("completed_task_ids") if checkpoint_present else []
    has_completed_tasks = isinstance(completed_task_ids, list) and len(completed_task_ids) > 0
    status = "finished" if finished else "in_progress"
    return {
        "schema": BENCHMARK_CHECKPOINT_RUNTIME_CONTRACT,
        "schema_version": BENCHMARK_CHECKPOINT_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "checkpoint_present": checkpoint_present,
            "finished": finished,
            "has_completed_tasks": has_completed_tasks,
        },
        "evidence": {
            "benchmark_checkpoint_ref": "benchmark-checkpoint.json",
            "benchmark_checkpoint_runtime_ref": "benchmark-checkpoint-runtime.json",
        },
    }
