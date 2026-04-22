"""Contracts for benchmark checkpoint runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BENCHMARK_CHECKPOINT_RUNTIME_CONTRACT = "sde.benchmark_checkpoint_runtime.v1"
BENCHMARK_CHECKPOINT_RUNTIME_SCHEMA_VERSION = "1.0"
_CANONICAL_EVIDENCE_REFS = {
    "benchmark_checkpoint_ref": "benchmark-checkpoint.json",
    "benchmark_checkpoint_runtime_ref": "benchmark-checkpoint-runtime.json",
}


def _validate_core_fields(body: dict[str, Any]) -> tuple[list[str], Any]:
    errs: list[str] = []
    if body.get("schema") != BENCHMARK_CHECKPOINT_RUNTIME_CONTRACT:
        errs.append("benchmark_checkpoint_runtime_schema")
    if body.get("schema_version") != BENCHMARK_CHECKPOINT_RUNTIME_SCHEMA_VERSION:
        errs.append("benchmark_checkpoint_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("benchmark_checkpoint_runtime_run_id")
    status = body.get("status")
    if status not in ("in_progress", "finished"):
        errs.append("benchmark_checkpoint_runtime_status")
    return errs, status


def _validate_checks_fields(checks: Any) -> list[str]:
    if not isinstance(checks, dict):
        return ["benchmark_checkpoint_runtime_checks"]
    errs: list[str] = []
    for key in ("checkpoint_present", "finished", "has_completed_tasks"):
        if not isinstance(checks.get(key), bool):
            errs.append(f"benchmark_checkpoint_runtime_check_type:{key}")
    return errs


def _validate_status_checks_coherence(checks: dict[str, Any], status: Any) -> list[str]:
    errs: list[str] = []
    if not checks.get("checkpoint_present") and (checks.get("finished") or checks.get("has_completed_tasks")):
        errs.append("benchmark_checkpoint_runtime_checks_mismatch")
    if checks.get("finished") and not checks.get("has_completed_tasks"):
        errs.append("benchmark_checkpoint_runtime_checks_mismatch")
    if status == "finished" and not checks.get("finished"):
        errs.append("benchmark_checkpoint_runtime_status_checks_mismatch")
    if status == "in_progress" and checks.get("finished"):
        errs.append("benchmark_checkpoint_runtime_status_checks_mismatch")
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if evidence is None:
        return []
    if not isinstance(evidence, dict):
        return ["benchmark_checkpoint_runtime_evidence"]
    if not evidence:
        return []
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        if key not in evidence:
            continue
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"benchmark_checkpoint_runtime_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized.startswith("/") or ".." in normalized.split("/") or normalized != expected:
            errs.append(f"benchmark_checkpoint_runtime_evidence_ref:{key}")
    return errs


def validate_benchmark_checkpoint_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["benchmark_checkpoint_runtime_not_object"]
    errs, status = _validate_core_fields(body)
    checks = body.get("checks")
    check_errs = _validate_checks_fields(checks)
    errs.extend(check_errs)
    errs.extend(_validate_evidence(body.get("evidence")))
    if not errs and isinstance(checks, dict):
        errs.extend(_validate_status_checks_coherence(checks, status))
    return errs


def validate_benchmark_checkpoint_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["benchmark_checkpoint_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return ["benchmark_checkpoint_runtime_unreadable"]
    except json.JSONDecodeError:
        return ["benchmark_checkpoint_runtime_json"]
    return validate_benchmark_checkpoint_runtime_dict(body)
