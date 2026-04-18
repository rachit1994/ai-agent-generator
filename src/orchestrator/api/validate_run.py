"""Validate an existing run directory (artifacts + hard-stops)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sde_foundations.utils import outputs_base
from sde_gates import validate_execution_run_directory

_BENCHMARK_MANIFEST = "benchmark-manifest.json"
_BENCHMARK_CHECKPOINT = "benchmark-checkpoint.json"


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
    errs, manifest = _json_errors(
        output_dir / _BENCHMARK_MANIFEST,
        missing="missing_benchmark_manifest_json",
        bad_json="benchmark_manifest_invalid_json",
    )
    if errs:
        return errs
    out: list[str] = []
    if manifest.get("schema") != "sde.benchmark_manifest.v1":
        out.append("benchmark_manifest_unexpected_schema")
    if not manifest.get("run_id"):
        out.append("benchmark_manifest_missing_run_id")
    return out


def _benchmark_checkpoint_errors(output_dir: Path) -> list[str]:
    errs, ck = _json_errors(
        output_dir / _BENCHMARK_CHECKPOINT,
        missing="missing_benchmark_checkpoint_json",
        bad_json="benchmark_checkpoint_invalid_json",
    )
    if errs:
        return errs
    if not ck.get("finished"):
        return ["benchmark_checkpoint_not_finished"]
    return []


def _benchmark_summary_errors(output_dir: Path) -> list[str]:
    errs, summary = _json_errors(
        output_dir / "summary.json",
        missing="missing_summary_json",
        bad_json="summary_invalid_json",
    )
    if errs:
        return errs
    if "verdict" not in summary:
        return ["summary_missing_verdict"]
    return []


def _validate_benchmark_aggregate(output_dir: Path) -> dict[str, Any]:
    """Light integrity check for a benchmark suite run (no single-task CTO ladder)."""
    errors = [
        *_benchmark_manifest_errors(output_dir),
        *_benchmark_checkpoint_errors(output_dir),
        *_benchmark_summary_errors(output_dir),
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
