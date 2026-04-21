"""Deterministic offline-evaluation runtime derivation."""

from __future__ import annotations

from .contracts import (
    OFFLINE_EVALUATION_RUNTIME_CONTRACT,
    OFFLINE_EVALUATION_RUNTIME_SCHEMA_VERSION,
)


def build_offline_evaluation_runtime(
    *,
    run_id: str,
    suite_errors: list[str],
    traces_present: bool,
    summary_present: bool,
    checkpoint_finished: bool,
) -> dict[str, object]:
    suite_contract_valid = len(suite_errors) == 0
    status = (
        "ready"
        if suite_contract_valid and traces_present and summary_present and checkpoint_finished
        else "degraded"
    )
    return {
        "schema": OFFLINE_EVALUATION_RUNTIME_CONTRACT,
        "schema_version": OFFLINE_EVALUATION_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "suite_contract_valid": suite_contract_valid,
            "summary_present": summary_present,
            "traces_present": traces_present,
            "checkpoint_finished": checkpoint_finished,
        },
        "counts": {"suite_error_count": len(suite_errors)},
        "evidence": {
            "suite_ref": "suite.jsonl",
            "summary_ref": "summary.json",
            "traces_ref": "traces.jsonl",
            "checkpoint_ref": "benchmark-checkpoint.json",
            "runtime_ref": "offline-evaluation-runtime.json",
        },
    }
