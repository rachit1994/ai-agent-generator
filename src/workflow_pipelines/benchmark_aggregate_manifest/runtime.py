"""Deterministic benchmark aggregate manifest runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    BENCHMARK_AGGREGATE_MANIFEST_RUNTIME_CONTRACT,
    BENCHMARK_AGGREGATE_MANIFEST_RUNTIME_SCHEMA_VERSION,
)


def build_benchmark_aggregate_manifest_runtime(
    *,
    manifest: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    run_id = str(manifest.get("run_id") or checkpoint.get("run_id") or "").strip()
    manifest_present = bool(manifest)
    checkpoint_present = bool(checkpoint)
    checkpoint_finished = bool(checkpoint.get("finished")) if checkpoint_present else False
    status = "finished" if checkpoint_finished else "active"
    return {
        "schema": BENCHMARK_AGGREGATE_MANIFEST_RUNTIME_CONTRACT,
        "schema_version": BENCHMARK_AGGREGATE_MANIFEST_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "manifest_present": manifest_present,
            "checkpoint_present": checkpoint_present,
            "checkpoint_finished": checkpoint_finished,
        },
        "evidence": {
            "benchmark_manifest_ref": "benchmark-manifest.json",
            "benchmark_checkpoint_ref": "benchmark-checkpoint.json",
            "benchmark_manifest_runtime_ref": "benchmark-manifest-runtime.json",
        },
    }
