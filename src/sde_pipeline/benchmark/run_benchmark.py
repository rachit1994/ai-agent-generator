"""Benchmark suite driver: load tasks, run modes, write traces and summary."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sde_pipeline.config import config_snapshot
from sde_pipeline.run_logging import (
    log_benchmark_banner,
    log_benchmark_traces_written,
    log_benchmark_verdict,
    log_run_end,
    log_run_error,
    log_run_failure_context,
    setup_run_logger,
    shutdown_run_logger,
)
from sde_foundations.storage import append_jsonl, ensure_dir, read_json, read_jsonl, write_json
from sde_foundations.utils import create_run_id, outputs_base

from .summary_payload import build_summary
from .suite import read_suite
from .task_loop import run_suite_tasks

CHECKPOINT_SCHEMA = "sde.benchmark_checkpoint.v1"
_BENCHMARK_MANIFEST = "benchmark-manifest.json"
_BENCHMARK_CHECKPOINT = "benchmark-checkpoint.json"
_TRACES_JSONL = "traces.jsonl"
_SUMMARY_JSON = "summary.json"


def _partition_traces_by_mode(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    baseline = [e for e in events if e.get("mode") == "baseline"]
    guarded = [e for e in events if e.get("mode") == "guarded_pipeline"]
    return baseline, guarded


def _ordered_tasks_for_manifest(manifest: dict[str, Any], suite_path: str) -> list[dict[str, Any]]:
    rows_by_id = {r["taskId"]: r for r in read_suite(suite_path)}
    ordered: list[dict[str, Any]] = []
    for spec in manifest["tasks"]:
        tid = spec["taskId"]
        if tid not in rows_by_id:
            raise ValueError(f"suite has no row for taskId {tid!r} referenced by benchmark manifest")
        ordered.append(rows_by_id[tid])
    return ordered


def _checkpoint_body(
    *,
    run_id: str,
    suite_path: str,
    mode: str,
    max_tasks: int | None,
    continue_on_error: bool,
    completed_task_ids: list[str],
    finished: bool,
) -> dict[str, Any]:
    return {
        "schema": CHECKPOINT_SCHEMA,
        "run_id": run_id,
        "suite_path": suite_path,
        "mode": mode,
        "max_tasks": max_tasks,
        "continue_on_error": continue_on_error,
        "completed_task_ids": completed_task_ids,
        "finished": finished,
        "updated_at_ms": int(time.time() * 1000),
    }


@dataclass
class _BenchCtx:
    out: Path
    run_id: str
    suite_path: str
    mode: str
    max_tasks: int | None
    continue_on_error: bool
    tasks: list[dict[str, Any]]
    full_tasks: list[dict[str, Any]]
    baseline_events: list[dict[str, Any]]
    guarded_events: list[dict[str, Any]]
    completed_ids: list[str]
    ck_path: Path


def _bench_ctx_resume(resume_run_id: str, suite_path: str | None, mode: str) -> _BenchCtx:
    out = outputs_base() / "runs" / resume_run_id
    if not out.is_dir():
        raise FileNotFoundError(f"resume run directory not found: {out}")
    manifest = read_json(out / _BENCHMARK_MANIFEST)
    ck_path = out / _BENCHMARK_CHECKPOINT
    if not ck_path.is_file():
        raise FileNotFoundError(f"benchmark-checkpoint.json missing under {out}; cannot resume")
    prior_ck = read_json(ck_path)
    if prior_ck.get("finished"):
        raise ValueError(f"benchmark run {resume_run_id!r} already finished (checkpoint.finished)")
    manifest_suite = str(Path(manifest["suite_path"]).resolve())
    if suite_path is not None and Path(suite_path).resolve() != Path(manifest_suite).resolve():
        raise ValueError("--suite does not match benchmark-manifest suite_path for this resume")
    resolved_suite = manifest_suite
    if mode != manifest["mode"]:
        raise ValueError(f"--mode {mode!r} does not match manifest mode {manifest['mode']!r}")
    run_mode = manifest["mode"]
    run_id = manifest["run_id"]
    max_m = manifest.get("max_tasks")
    coe = bool(manifest.get("continue_on_error", False))
    full_tasks = _ordered_tasks_for_manifest(manifest, resolved_suite)
    completed_ids = list(prior_ck.get("completed_task_ids") or [])
    done = set(completed_ids)
    pending = [t for t in full_tasks if t["taskId"] not in done]
    existing = read_jsonl(out / _TRACES_JSONL)
    baseline_events, guarded_events = _partition_traces_by_mode(existing)
    return _BenchCtx(
        out=out,
        run_id=run_id,
        suite_path=resolved_suite,
        mode=run_mode,
        max_tasks=max_m,
        continue_on_error=coe,
        tasks=pending,
        full_tasks=full_tasks,
        baseline_events=baseline_events,
        guarded_events=guarded_events,
        completed_ids=completed_ids,
        ck_path=ck_path,
    )


def _bench_ctx_fresh(
    suite_path: str,
    mode: str,
    max_tasks: int | None,
    continue_on_error: bool,
) -> _BenchCtx:
    tasks = read_suite(suite_path)
    if max_tasks is not None and max_tasks > 0:
        tasks = tasks[:max_tasks]
    run_id = create_run_id()
    out = outputs_base() / "runs" / run_id
    ensure_dir(out)
    (out / _TRACES_JSONL).write_text("", encoding="utf-8")
    resolved = str(Path(suite_path).resolve())
    write_json(
        out / _BENCHMARK_MANIFEST,
        {
            "schema": "sde.benchmark_manifest.v1",
            "run_id": run_id,
            "suite_path": resolved,
            "mode": mode,
            "tasks": [{"taskId": t["taskId"], "prompt": t["prompt"]} for t in tasks],
            "max_tasks": max_tasks,
            "continue_on_error": continue_on_error,
        },
    )
    ck_path = out / _BENCHMARK_CHECKPOINT
    completed_ids: list[str] = []
    write_json(
        ck_path,
        _checkpoint_body(
            run_id=run_id,
            suite_path=resolved,
            mode=mode,
            max_tasks=max_tasks,
            continue_on_error=continue_on_error,
            completed_task_ids=[],
            finished=False,
        ),
    )
    return _BenchCtx(
        out=out,
        run_id=run_id,
        suite_path=resolved,
        mode=mode,
        max_tasks=max_tasks,
        continue_on_error=continue_on_error,
        tasks=tasks,
        full_tasks=tasks,
        baseline_events=[],
        guarded_events=[],
        completed_ids=completed_ids,
        ck_path=ck_path,
    )


def run_benchmark(
    suite_path: str | None = None,
    mode: str = "both",
    *,
    max_tasks: int | None = None,
    continue_on_error: bool = False,
    resume_run_id: str | None = None,
) -> dict:
    resume = resume_run_id is not None and str(resume_run_id).strip() != ""
    if not resume and not suite_path:
        raise ValueError("suite_path is required unless resume_run_id is set")

    if resume:
        ctx = _bench_ctx_resume(resume_run_id, suite_path, mode)
    else:
        assert suite_path is not None
        ctx = _bench_ctx_fresh(suite_path, mode, max_tasks, continue_on_error)

    out = ctx.out
    run_id = ctx.run_id
    suite_path = ctx.suite_path
    mode = ctx.mode
    max_tasks = ctx.max_tasks
    continue_on_error = ctx.continue_on_error
    tasks = ctx.tasks
    full_tasks = ctx.full_tasks
    baseline_events = ctx.baseline_events
    guarded_events = ctx.guarded_events
    completed_ids = ctx.completed_ids
    ck_path = ctx.ck_path

    def on_task_events(tid: str, baseline_chunk: list[dict], guarded_chunk: list[dict]) -> None:
        for ev in baseline_chunk:
            append_jsonl(out / _TRACES_JSONL, ev)
        for ev in guarded_chunk:
            append_jsonl(out / _TRACES_JSONL, ev)
        completed_ids.append(tid)
        write_json(
            ck_path,
            _checkpoint_body(
                run_id=run_id,
                suite_path=suite_path,
                mode=mode,
                max_tasks=max_tasks,
                continue_on_error=continue_on_error,
                completed_task_ids=list(completed_ids),
                finished=False,
            ),
        )

    benchmark_started_ms = int(time.time() * 1000)
    run_logger = setup_run_logger(run_id, out)
    log_benchmark_banner(
        run_logger,
        run_id=run_id,
        suite_path=suite_path,
        mode=mode,
        task_count=len(tasks),
    )
    if resume:
        append_jsonl(
            out / "orchestration.jsonl",
            {
                "run_id": run_id,
                "type": "benchmark_resume",
                "pending_task_count": len(tasks),
            },
        )
    try:
        try:
            new_baseline, new_guarded = run_suite_tasks(
                run_logger,
                run_id,
                mode,
                tasks,
                continue_on_error=continue_on_error,
                on_task_events=on_task_events,
            )
            baseline_events = baseline_events + new_baseline
            guarded_events = guarded_events + new_guarded
        except Exception as exc:
            log_run_error(run_logger, "Benchmark aborted", exc)
            append_jsonl(
                out / "orchestration.jsonl",
                {
                    "run_id": run_id,
                    "type": "benchmark_error",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                },
            )
            write_json(
                out / _SUMMARY_JSON,
                {
                    "runId": run_id,
                    "suitePath": suite_path,
                    "mode": mode,
                    "runStatus": "failed",
                    "error": {"type": type(exc).__name__, "message": str(exc)},
                },
            )
            write_json(out / "config-snapshot.json", config_snapshot())
            log_run_failure_context(run_logger, detail="Benchmark loop raised; see error above.")
            log_run_end(run_logger, artifacts={}, output_dir=str(out))
            return {"runId": run_id, "verdict": "failed", "error": {"type": type(exc).__name__, "message": str(exc)}}
        combined = [*baseline_events, *guarded_events]
        log_benchmark_traces_written(
            run_logger,
            event_count=len(combined),
            traces_path=str(out / _TRACES_JSONL),
        )
        summary = build_summary(
            run_id=run_id,
            suite_path=suite_path,
            mode=mode,
            tasks=full_tasks,
            baseline_events=baseline_events,
            guarded_events=guarded_events,
        )
        summary["benchmarkStartedAtMs"] = benchmark_started_ms
        summary["benchmarkFinishedAtMs"] = int(time.time() * 1000)
        summary["taskCount"] = len(full_tasks)
        summary["continueOnError"] = continue_on_error
        summary["resumed"] = bool(resume)
        verdict = summary["verdict"]
        write_json(out / "config-snapshot.json", config_snapshot())
        write_json(out / _SUMMARY_JSON, summary)
        write_json(
            ck_path,
            _checkpoint_body(
                run_id=run_id,
                suite_path=suite_path,
                mode=mode,
                max_tasks=max_tasks,
                continue_on_error=continue_on_error,
                completed_task_ids=[t["taskId"] for t in full_tasks],
                finished=True,
            ),
        )
        log_benchmark_verdict(
            run_logger,
            verdict=verdict,
            summary_path=str(out / _SUMMARY_JSON),
        )
        log_run_end(
            run_logger,
            artifacts={"traces_jsonl": str(out / _TRACES_JSONL), "summary_json": str(out / _SUMMARY_JSON)},
            output_dir=str(out),
        )
        return {"runId": run_id, "verdict": verdict}
    finally:
        shutdown_run_logger(run_logger)
