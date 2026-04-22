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
    build_benchmark_aggregate_summary_runtime,
    validate_benchmark_aggregate_summary_runtime_path,
)
from workflow_pipelines.benchmark_aggregate_manifest.benchmark_manifest_contract import (
    validate_benchmark_manifest_path,
)
from workflow_pipelines.benchmark_aggregate_manifest import (
    build_benchmark_aggregate_manifest_runtime,
    validate_benchmark_aggregate_manifest_runtime_path,
)
from workflow_pipelines.benchmark_checkpoint.benchmark_checkpoint_contract import (
    validate_benchmark_checkpoint_path,
)
from workflow_pipelines.benchmark_checkpoint import (
    build_benchmark_checkpoint_runtime,
    validate_benchmark_checkpoint_runtime_path,
)
from workflow_pipelines.benchmark_orchestration_jsonl import (
    build_benchmark_orchestration_jsonl_runtime,
    validate_benchmark_orchestration_jsonl_runtime_path,
)
from workflow_pipelines.traces_jsonl import (
    build_traces_jsonl_event_row_runtime,
    validate_traces_jsonl_event_row_runtime_path,
)
from evaluation_framework.offline_evaluation import (
    build_offline_evaluation_runtime,
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
        except (OSError, json.JSONDecodeError):
            body = {}
        return str(body.get("mode") or "baseline")
    benchmark_manifest = output_dir / "benchmark-manifest.json"
    if benchmark_manifest.is_file():
        try:
            body = json.loads(benchmark_manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
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
    except OSError:
        return [bad_json], {}
    except json.JSONDecodeError:
        return [bad_json], {}


def _benchmark_checkpoint_cross_contract_errors(output_dir: Path) -> list[str]:
    checkpoint_errors, checkpoint_body = _json_errors(
        output_dir / _BENCHMARK_CHECKPOINT,
        missing="missing_benchmark_checkpoint_json",
        bad_json="benchmark_checkpoint_invalid_json",
    )
    runtime_errors, runtime_body = _json_errors(
        output_dir / _BENCHMARK_CHECKPOINT_RUNTIME,
        missing="missing_benchmark_checkpoint_runtime_json",
        bad_json="benchmark_checkpoint_runtime_invalid_json",
    )
    if checkpoint_errors or runtime_errors or not isinstance(checkpoint_body, dict) or not isinstance(runtime_body, dict):
        return []
    expected = build_benchmark_checkpoint_runtime(checkpoint=checkpoint_body)
    if runtime_body.get("run_id") != expected.get("run_id"):
        return ["benchmark_checkpoint_cross_contract:run_id_mismatch"]
    if runtime_body.get("status") != expected.get("status"):
        return ["benchmark_checkpoint_cross_contract:status_mismatch"]
    if runtime_body.get("checks") != expected.get("checks"):
        return ["benchmark_checkpoint_cross_contract:checks_mismatch"]
    return []


def _benchmark_manifest_checkpoint_coherence_errors(output_dir: Path) -> list[str]:
    manifest_errors, manifest_body = _json_errors(
        output_dir / _BENCHMARK_MANIFEST,
        missing="missing_benchmark_manifest_json",
        bad_json="benchmark_manifest_invalid_json",
    )
    checkpoint_errors, checkpoint_body = _json_errors(
        output_dir / _BENCHMARK_CHECKPOINT,
        missing="missing_benchmark_checkpoint_json",
        bad_json="benchmark_checkpoint_invalid_json",
    )
    if (
        manifest_errors
        or checkpoint_errors
        or not isinstance(manifest_body, dict)
        or not isinstance(checkpoint_body, dict)
    ):
        return []
    if manifest_body.get("run_id") != checkpoint_body.get("run_id"):
        return ["benchmark_manifest_checkpoint_coherence:run_id_mismatch"]
    if manifest_body.get("suite_path") != checkpoint_body.get("suite_path"):
        return ["benchmark_manifest_checkpoint_coherence:suite_path_mismatch"]
    if manifest_body.get("mode") != checkpoint_body.get("mode"):
        return ["benchmark_manifest_checkpoint_coherence:mode_mismatch"]
    if manifest_body.get("continue_on_error") != checkpoint_body.get("continue_on_error"):
        return ["benchmark_manifest_checkpoint_coherence:continue_on_error_mismatch"]
    if manifest_body.get("max_tasks") != checkpoint_body.get("max_tasks"):
        return ["benchmark_manifest_checkpoint_coherence:max_tasks_mismatch"]
    return []


def _benchmark_manifest_runtime_cross_contract_errors(output_dir: Path) -> list[str]:
    manifest_errors, manifest_body = _json_errors(
        output_dir / _BENCHMARK_MANIFEST,
        missing="missing_benchmark_manifest_json",
        bad_json="benchmark_manifest_invalid_json",
    )
    checkpoint_errors, checkpoint_body = _json_errors(
        output_dir / _BENCHMARK_CHECKPOINT,
        missing="missing_benchmark_checkpoint_json",
        bad_json="benchmark_checkpoint_invalid_json",
    )
    runtime_errors, runtime_body = _json_errors(
        output_dir / _BENCHMARK_MANIFEST_RUNTIME,
        missing="missing_benchmark_manifest_runtime_json",
        bad_json="benchmark_manifest_runtime_invalid_json",
    )
    if (
        manifest_errors
        or checkpoint_errors
        or runtime_errors
        or not isinstance(manifest_body, dict)
        or not isinstance(checkpoint_body, dict)
        or not isinstance(runtime_body, dict)
    ):
        return []
    expected = build_benchmark_aggregate_manifest_runtime(manifest=manifest_body, checkpoint=checkpoint_body)
    if runtime_body.get("run_id") != expected.get("run_id"):
        return ["benchmark_manifest_runtime_cross_contract:run_id_mismatch"]
    if runtime_body.get("status") != expected.get("status"):
        return ["benchmark_manifest_runtime_cross_contract:status_mismatch"]
    if runtime_body.get("checks") != expected.get("checks"):
        return ["benchmark_manifest_runtime_cross_contract:checks_mismatch"]
    return []


def _benchmark_summary_runtime_cross_contract_errors(output_dir: Path) -> list[str]:
    summary_errors, summary_body = _json_errors(
        output_dir / "summary.json",
        missing="missing_summary_json",
        bad_json="summary_invalid_json",
    )
    runtime_errors, runtime_body = _json_errors(
        output_dir / _BENCHMARK_SUMMARY_RUNTIME,
        missing="missing_benchmark_summary_runtime_json",
        bad_json="benchmark_summary_runtime_invalid_json",
    )
    if summary_errors or runtime_errors or not isinstance(summary_body, dict) or not isinstance(runtime_body, dict):
        return []
    expected = build_benchmark_aggregate_summary_runtime(summary=summary_body)
    summary_run_id = str(summary_body.get("runId") or summary_body.get("run_id") or "").strip()
    if summary_run_id and runtime_body.get("run_id") != summary_run_id:
        return ["benchmark_summary_runtime_cross_contract:run_id_mismatch"]
    run_manifest_errors, run_manifest_body = _json_errors(
        output_dir / _BENCHMARK_MANIFEST,
        missing="missing_benchmark_manifest_json",
        bad_json="benchmark_manifest_invalid_json",
    )
    expected_run_id = (
        str(run_manifest_body.get("run_id") or "").strip()
        if not run_manifest_errors and isinstance(run_manifest_body, dict)
        else ""
    )
    if expected_run_id and runtime_body.get("run_id") != expected_run_id:
        return ["benchmark_summary_runtime_cross_contract:run_id_mismatch"]
    if runtime_body.get("status") != expected.get("status"):
        return ["benchmark_summary_runtime_cross_contract:status_mismatch"]
    if runtime_body.get("checks") != expected.get("checks"):
        return ["benchmark_summary_runtime_cross_contract:checks_mismatch"]
    return []


def _benchmark_orchestration_cross_contract_errors(output_dir: Path) -> list[str]:
    runtime_errors, runtime_body = _json_errors(
        output_dir / _BENCHMARK_ORCHESTRATION_RUNTIME,
        missing="missing_benchmark_orchestration_runtime_json",
        bad_json="benchmark_orchestration_runtime_invalid_json",
    )
    if runtime_errors or not isinstance(runtime_body, dict):
        return []
    orchestration_rows, parse_errors = _read_orchestration_rows(output_dir / "orchestration.jsonl")
    if parse_errors:
        return [parse_errors[0]]
    expected = build_benchmark_orchestration_jsonl_runtime(
        run_id=str(runtime_body.get("run_id") or "").strip(),
        orchestration_rows=orchestration_rows,
    )
    run_manifest_errors, run_manifest_body = _json_errors(
        output_dir / _BENCHMARK_MANIFEST,
        missing="missing_benchmark_manifest_json",
        bad_json="benchmark_manifest_invalid_json",
    )
    expected_run_id = (
        str(run_manifest_body.get("run_id") or "").strip()
        if not run_manifest_errors and isinstance(run_manifest_body, dict)
        else ""
    )
    if expected_run_id and runtime_body.get("run_id") != expected_run_id:
        return ["benchmark_orchestration_cross_contract:run_id_mismatch"]
    if runtime_body.get("status") != expected.get("status"):
        return ["benchmark_orchestration_cross_contract:status_mismatch"]
    if runtime_body.get("checks") != expected.get("checks"):
        return ["benchmark_orchestration_cross_contract:checks_mismatch"]
    if runtime_body.get("counts") != expected.get("counts"):
        return ["benchmark_orchestration_cross_contract:counts_mismatch"]
    return []


def _traces_event_row_cross_contract_errors(output_dir: Path) -> list[str]:
    runtime_errors, runtime_body = _json_errors(
        output_dir / _TRACES_EVENT_ROW_RUNTIME,
        missing="missing_traces_event_row_runtime_json",
        bad_json="traces_event_row_runtime_invalid_json",
    )
    if runtime_errors or not isinstance(runtime_body, dict):
        return []
    traces_rows = _read_traces_rows(output_dir / "traces.jsonl")
    expected = build_traces_jsonl_event_row_runtime(
        run_id=str(runtime_body.get("run_id") or "").strip(),
        trace_rows=traces_rows,
    )
    run_manifest_errors, run_manifest_body = _json_errors(
        output_dir / _BENCHMARK_MANIFEST,
        missing="missing_benchmark_manifest_json",
        bad_json="benchmark_manifest_invalid_json",
    )
    expected_run_id = (
        str(run_manifest_body.get("run_id") or "").strip()
        if not run_manifest_errors and isinstance(run_manifest_body, dict)
        else ""
    )
    if expected_run_id and runtime_body.get("run_id") != expected_run_id:
        return ["traces_event_row_cross_contract:run_id_mismatch"]
    if runtime_body.get("status") != expected.get("status"):
        return ["traces_event_row_cross_contract:status_mismatch"]
    if runtime_body.get("checks") != expected.get("checks"):
        return ["traces_event_row_cross_contract:checks_mismatch"]
    if runtime_body.get("counts") != expected.get("counts"):
        return ["traces_event_row_cross_contract:counts_mismatch"]
    return []


def _offline_evaluation_cross_contract_errors(output_dir: Path) -> list[str]:
    runtime_errors, runtime_body = _json_errors(
        output_dir / _OFFLINE_EVALUATION_RUNTIME,
        missing="missing_offline_evaluation_runtime_json",
        bad_json="offline_evaluation_runtime_invalid_json",
    )
    if runtime_errors or not isinstance(runtime_body, dict):
        return []
    run_manifest_errors, run_manifest_body = _json_errors(
        output_dir / _BENCHMARK_MANIFEST,
        missing="missing_benchmark_manifest_json",
        bad_json="benchmark_manifest_invalid_json",
    )
    expected_run_id = (
        str(run_manifest_body.get("run_id") or "").strip()
        if not run_manifest_errors and isinstance(run_manifest_body, dict)
        else ""
    )
    if expected_run_id and runtime_body.get("run_id") != expected_run_id:
        return ["offline_evaluation_cross_contract:run_id_mismatch"]
    checkpoint_errors, checkpoint_body = _json_errors(
        output_dir / _BENCHMARK_CHECKPOINT,
        missing="missing_benchmark_checkpoint_json",
        bad_json="benchmark_checkpoint_invalid_json",
    )
    checkpoint_finished = bool(checkpoint_body.get("finished")) if not checkpoint_errors else False
    summary_present = (output_dir / "summary.json").is_file()
    traces_present = (output_dir / "traces.jsonl").is_file()
    expected = build_offline_evaluation_runtime(
        run_id=str(runtime_body.get("run_id") or "").strip(),
        suite_errors=[],
        traces_present=traces_present,
        summary_present=summary_present,
        checkpoint_finished=checkpoint_finished,
    )
    if runtime_body.get("status") != expected.get("status"):
        return ["offline_evaluation_cross_contract:status_mismatch"]
    if runtime_body.get("checks") != expected.get("checks"):
        return ["offline_evaluation_cross_contract:checks_mismatch"]
    return []


def _read_orchestration_rows(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.is_file():
        return [], []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return [], []
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            errors.append("benchmark_orchestration_cross_contract:malformed_jsonl_line")
            continue
        if not isinstance(row, dict):
            errors.append("benchmark_orchestration_cross_contract:non_object_row")
            continue
        row_type = row.get("type")
        if row_type not in ("benchmark_resume", "benchmark_error"):
            errors.append("benchmark_orchestration_cross_contract:unknown_row_type")
            continue
        rows.append(row)
    return rows, errors


def _read_traces_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    rows: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


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
        if err == "benchmark_checkpoint_runtime_unreadable":
            out.append("benchmark_checkpoint_runtime_unreadable")
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
        if err == "benchmark_aggregate_manifest_runtime_unreadable":
            out.append("benchmark_manifest_runtime_unreadable")
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
        if err == "benchmark_aggregate_summary_runtime_unreadable":
            out.append("benchmark_summary_runtime_unreadable")
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
        if err == "benchmark_orchestration_jsonl_runtime_unreadable":
            out.append("benchmark_orchestration_runtime_unreadable")
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
        if err == "traces_jsonl_event_row_runtime_unreadable":
            out.append("traces_event_row_runtime_unreadable")
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
        *_benchmark_manifest_checkpoint_coherence_errors(output_dir),
        *_benchmark_checkpoint_cross_contract_errors(output_dir),
        *_benchmark_manifest_runtime_cross_contract_errors(output_dir),
        *_benchmark_summary_runtime_cross_contract_errors(output_dir),
        *_benchmark_orchestration_cross_contract_errors(output_dir),
        *_traces_event_row_cross_contract_errors(output_dir),
        *_offline_evaluation_cross_contract_errors(output_dir),
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
