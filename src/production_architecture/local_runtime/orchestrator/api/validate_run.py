"""Validate an existing run directory (artifacts + hard-stops)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.orchestrator.common.utils import outputs_base
from guardrails_and_safety import validate_execution_run_directory
from workflow_pipelines.benchmark_aggregate_summary.benchmark_aggregate_summary_contract import (
    validate_benchmark_aggregate_summary_path,
)
from workflow_pipelines.benchmark_aggregate_summary import (
    validate_benchmark_aggregate_summary_runtime_path,
)
from workflow_pipelines.benchmark_aggregate_manifest.benchmark_manifest_contract import (
    validate_benchmark_manifest_path,
)
from workflow_pipelines.benchmark_aggregate_manifest import (
    validate_benchmark_aggregate_manifest_runtime_path,
)
from workflow_pipelines.benchmark_checkpoint.benchmark_checkpoint_contract import (
    validate_benchmark_checkpoint_path,
)
from workflow_pipelines.benchmark_checkpoint import (
    validate_benchmark_checkpoint_runtime_path,
)
from workflow_pipelines.benchmark_orchestration_jsonl import (
    validate_benchmark_orchestration_jsonl_runtime_path,
)
from workflow_pipelines.traces_jsonl import (
    validate_traces_jsonl_event_row_runtime_path,
)
from evaluation_framework.offline_evaluation import (
    validate_offline_evaluation_runtime_path,
)

_BENCHMARK_MANIFEST = "benchmark-manifest.json"
_BENCHMARK_MANIFEST_RUNTIME = "benchmark-manifest-runtime.json"
_BENCHMARK_CHECKPOINT = "benchmark-checkpoint.json"
_BENCHMARK_CHECKPOINT_RUNTIME = "benchmark-checkpoint-runtime.json"
_BENCHMARK_SUMMARY_RUNTIME = "benchmark-summary-runtime.json"
_BENCHMARK_ORCHESTRATION_RUNTIME = "benchmark-orchestration-runtime.json"
_TRACES_EVENT_ROW_RUNTIME = "traces-event-row-runtime.json"
_OFFLINE_EVALUATION_RUNTIME = "offline-evaluation-runtime.json"


def _resolve_mode_from_manifests(output_dir: Any) -> str:
    run_manifest = output_dir / "run-manifest.json"
    if run_manifest.is_file():
        try:
            body: dict[str, Any] = json.loads(run_manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            body = {}
        return str(body.get("mode") or "baseline")
    benchmark_manifest = output_dir / "benchmark-manifest.json"
    if benchmark_manifest.is_file():
        try:
            body = json.loads(benchmark_manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            body = {}
        bench_mode = str(body.get("mode") or "")
        if bench_mode in ("baseline", "guarded_pipeline", "phased_pipeline"):
            return bench_mode
        if bench_mode == "both":
            return "benchmark_both"
    return "baseline"


def _json_errors(path: Path, *, missing: str, bad_json: str) -> tuple[list[str], dict[str, Any]]:
    if not path.is_file():
        return [missing], {}
    try:
        return [], json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [bad_json], {}


def _benchmark_manifest_errors(output_dir: Path) -> list[str]:
    errs = validate_benchmark_manifest_path(output_dir / _BENCHMARK_MANIFEST)
    out: list[str] = []
    for err in errs:
        if err == "benchmark_manifest_file_missing":
            out.append("missing_benchmark_manifest_json")
            continue
        if err == "benchmark_manifest_json":
            out.append("benchmark_manifest_invalid_json")
            continue
        out.append(f"benchmark_manifest_contract:{err}")
    return out


def _benchmark_checkpoint_errors(output_dir: Path) -> list[str]:
    errs = validate_benchmark_checkpoint_path(output_dir / _BENCHMARK_CHECKPOINT)
    out: list[str] = []
    for err in errs:
        if err == "benchmark_checkpoint_file_missing":
            out.append("missing_benchmark_checkpoint_json")
            continue
        if err == "benchmark_checkpoint_json":
            out.append("benchmark_checkpoint_invalid_json")
            continue
        out.append(f"benchmark_checkpoint_contract:{err}")
    return out


def _benchmark_checkpoint_runtime_errors(output_dir: Path) -> list[str]:
    errs = validate_benchmark_checkpoint_runtime_path(output_dir / _BENCHMARK_CHECKPOINT_RUNTIME)
    out: list[str] = []
    for err in errs:
        if err == "benchmark_checkpoint_runtime_file_missing":
            out.append("missing_benchmark_checkpoint_runtime_json")
            continue
        if err == "benchmark_checkpoint_runtime_json":
            out.append("benchmark_checkpoint_runtime_invalid_json")
            continue
        out.append(f"benchmark_checkpoint_runtime_contract:{err}")
    return out


def _benchmark_manifest_runtime_errors(output_dir: Path) -> list[str]:
    errs = validate_benchmark_aggregate_manifest_runtime_path(output_dir / _BENCHMARK_MANIFEST_RUNTIME)
    out: list[str] = []
    for err in errs:
        if err == "benchmark_aggregate_manifest_runtime_file_missing":
            out.append("missing_benchmark_manifest_runtime_json")
            continue
        if err == "benchmark_aggregate_manifest_runtime_json":
            out.append("benchmark_manifest_runtime_invalid_json")
            continue
        out.append(f"benchmark_manifest_runtime_contract:{err}")
    return out


def _benchmark_summary_errors(output_dir: Path) -> list[str]:
    errs = validate_benchmark_aggregate_summary_path(output_dir / "summary.json")
    out: list[str] = []
    for err in errs:
        if err == "benchmark_aggregate_summary_file_missing":
            out.append("missing_summary_json")
            continue
        if err == "benchmark_aggregate_summary_json":
            out.append("summary_invalid_json")
            continue
        out.append(f"benchmark_summary_contract:{err}")
    return out


def _benchmark_summary_runtime_errors(output_dir: Path) -> list[str]:
    errs = validate_benchmark_aggregate_summary_runtime_path(output_dir / _BENCHMARK_SUMMARY_RUNTIME)
    out: list[str] = []
    for err in errs:
        if err == "benchmark_aggregate_summary_runtime_file_missing":
            out.append("missing_benchmark_summary_runtime_json")
            continue
        if err == "benchmark_aggregate_summary_runtime_json":
            out.append("benchmark_summary_runtime_invalid_json")
            continue
        out.append(f"benchmark_summary_runtime_contract:{err}")
    return out


def _benchmark_orchestration_runtime_errors(output_dir: Path) -> list[str]:
    errs = validate_benchmark_orchestration_jsonl_runtime_path(output_dir / _BENCHMARK_ORCHESTRATION_RUNTIME)
    out: list[str] = []
    for err in errs:
        if err == "benchmark_orchestration_jsonl_runtime_file_missing":
            out.append("missing_benchmark_orchestration_runtime_json")
            continue
        if err == "benchmark_orchestration_jsonl_runtime_json":
            out.append("benchmark_orchestration_runtime_invalid_json")
            continue
        out.append(f"benchmark_orchestration_runtime_contract:{err}")
    return out


def _traces_event_row_runtime_errors(output_dir: Path) -> list[str]:
    errs = validate_traces_jsonl_event_row_runtime_path(output_dir / _TRACES_EVENT_ROW_RUNTIME)
    out: list[str] = []
    for err in errs:
        if err == "traces_jsonl_event_row_runtime_file_missing":
            out.append("missing_traces_event_row_runtime_json")
            continue
        if err == "traces_jsonl_event_row_runtime_json":
            out.append("traces_event_row_runtime_invalid_json")
            continue
        out.append(f"traces_event_row_runtime_contract:{err}")
    return out


def _offline_evaluation_runtime_errors(output_dir: Path) -> list[str]:
    errs = validate_offline_evaluation_runtime_path(output_dir / _OFFLINE_EVALUATION_RUNTIME)
    out: list[str] = []
    for err in errs:
        if err == "offline_evaluation_runtime_file_missing":
            out.append("missing_offline_evaluation_runtime_json")
            continue
        if err == "offline_evaluation_runtime_json":
            out.append("offline_evaluation_runtime_invalid_json")
            continue
        out.append(f"offline_evaluation_runtime_contract:{err}")
    return out


def _validate_benchmark_aggregate(output_dir: Path) -> dict[str, Any]:
    """Light integrity check for a benchmark suite run (no single-task CTO ladder)."""
    errors = [
        *_benchmark_manifest_errors(output_dir),
        *_benchmark_manifest_runtime_errors(output_dir),
        *_benchmark_checkpoint_errors(output_dir),
        *_benchmark_checkpoint_runtime_errors(output_dir),
        *_benchmark_summary_errors(output_dir),
        *_benchmark_summary_runtime_errors(output_dir),
        *_benchmark_orchestration_runtime_errors(output_dir),
        *_traces_event_row_runtime_errors(output_dir),
        *_offline_evaluation_runtime_errors(output_dir),
    ]
    if not (output_dir / "traces.jsonl").is_file():
        errors.append("missing_traces_jsonl")

    strict_ok = len(errors) == 0
    return {
        "ok": strict_ok,
        "validation_ready": False,
        "execution_gates_applied": False,
        "errors": errors,
        "hard_stops": [],
        "run_kind": "benchmark_aggregate",
    }


def validate_run(run_id: str, *, mode: str | None = None) -> dict[str, Any]:
    """Load ``outputs/runs/<run_id>/`` and validate artifacts.

    Single-task runs (``run-manifest.json``) use :func:`validate_execution_run_directory`.
    Benchmark aggregate directories (``benchmark-manifest.json`` only) use a lighter
    integrity check: manifest, finished checkpoint, summary verdict, and ``traces.jsonl``.

    If ``mode`` is omitted, reads ``run-manifest.json`` when present; otherwise the
    benchmark manifest when present; otherwise ``baseline``.
    """
    output_dir = outputs_base() / "runs" / run_id
    if not output_dir.is_dir():
        return {
            "ok": False,
            "validation_ready": False,
            "execution_gates_applied": True,
            "errors": [f"run_directory_missing:{run_id}"],
            "hard_stops": [],
        }
    resolved = mode
    if resolved is None:
        resolved = _resolve_mode_from_manifests(output_dir)
    if resolved == "benchmark_both":
        return {
            "ok": False,
            "validation_ready": False,
            "execution_gates_applied": True,
            "errors": ["benchmark_manifest_mode_both_requires_mode_override"],
            "hard_stops": [],
        }
    if resolved not in ("baseline", "guarded_pipeline", "phased_pipeline"):
        return {
            "ok": False,
            "validation_ready": False,
            "execution_gates_applied": True,
            "errors": [f"invalid_mode_in_manifest:{resolved}"],
            "hard_stops": [],
        }

    has_run_manifest = (output_dir / "run-manifest.json").is_file()
    has_benchmark_manifest = (output_dir / _BENCHMARK_MANIFEST).is_file()
    bench_only = has_benchmark_manifest and not has_run_manifest
    if bench_only:
        return _validate_benchmark_aggregate(output_dir)

    outcome = validate_execution_run_directory(output_dir, mode=resolved)
    merged: dict[str, Any] = {**outcome, "execution_gates_applied": True, "run_kind": "single_task"}
    return merged
