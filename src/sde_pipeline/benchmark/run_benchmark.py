"""Benchmark suite driver: load tasks, run modes, write traces and summary."""

from __future__ import annotations

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
from sde_foundations.storage import append_jsonl, ensure_dir, write_json
from sde_foundations.utils import create_run_id, outputs_base

from .summary_payload import build_summary
from .suite import read_suite
from .task_loop import run_suite_tasks


def run_benchmark(suite_path: str, mode: str = "both") -> dict:
    tasks = read_suite(suite_path)
    run_id = create_run_id()
    out = outputs_base() / "runs" / run_id
    ensure_dir(out)
    run_logger = setup_run_logger(run_id, out)
    log_benchmark_banner(
        run_logger,
        run_id=run_id,
        suite_path=suite_path,
        mode=mode,
        task_count=len(tasks),
    )
    baseline_events: list[dict] = []
    guarded_events: list[dict] = []
    try:
        try:
            baseline_events, guarded_events = run_suite_tasks(run_logger, run_id, mode, tasks)
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
                out / "summary.json",
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
        for event in combined:
            append_jsonl(out / "traces.jsonl", event)
        log_benchmark_traces_written(
            run_logger,
            event_count=len(combined),
            traces_path=str(out / "traces.jsonl"),
        )
        summary = build_summary(
            run_id=run_id,
            suite_path=suite_path,
            mode=mode,
            tasks=tasks,
            baseline_events=baseline_events,
            guarded_events=guarded_events,
        )
        verdict = summary["verdict"]
        write_json(out / "config-snapshot.json", config_snapshot())
        write_json(out / "summary.json", summary)
        log_benchmark_verdict(
            run_logger,
            verdict=verdict,
            summary_path=str(out / "summary.json"),
        )
        log_run_end(
            run_logger,
            artifacts={"traces_jsonl": str(out / "traces.jsonl"), "summary_json": str(out / "summary.json")},
            output_dir=str(out),
        )
        return {"runId": run_id, "verdict": verdict}
    finally:
        shutdown_run_logger(run_logger)
