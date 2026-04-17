from __future__ import annotations

import json
from pathlib import Path

from orchestrator.runtime.config import DEFAULT_CONFIG, config_snapshot
from orchestrator.runtime.eval import aggregate_metrics, root_cause_distribution, stage_latency_breakdown, strict_gate_decision, verdict_for
from orchestrator.runtime.modes.baseline import run_baseline
from orchestrator.runtime.modes.guarded import run_guarded
from orchestrator.runtime.run_logging import (
    log_benchmark_banner,
    log_run_end,
    log_run_error,
    log_task_scope,
    log_trace_narrative,
    setup_run_logger,
    shutdown_run_logger,
)
from orchestrator.runtime.safeguards import validate_task_payload
from orchestrator.runtime.storage import append_jsonl, ensure_dir, write_json
from orchestrator.runtime.utils import create_run_id, outputs_base


def _read_suite(suite_path: str) -> list[dict]:
    rows: list[dict] = []
    for line in Path(suite_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        payload = {
            "taskId": raw.get("taskId", raw.get("task_id")),
            "prompt": raw["prompt"],
            "expectedChecks": raw.get("expectedChecks", raw.get("expected_checks", [])),
            "difficulty": raw["difficulty"],
        }
        rows.append(validate_task_payload(payload))
    return rows


def run_benchmark(suite_path: str, mode: str = "both") -> dict:
    tasks = _read_suite(suite_path)
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
            for task in tasks:
                tid = task["taskId"]
                prompt = task["prompt"]
                if mode in ("baseline", "both"):
                    log_task_scope(run_logger, task_id=tid, prompt=prompt, branch="baseline")
                    _, events = run_baseline(run_id, tid, prompt, DEFAULT_CONFIG)
                    for ev in events:
                        log_trace_narrative(run_logger, ev)
                    baseline_events.extend(events)
                if mode in ("guarded_pipeline", "both"):
                    log_task_scope(run_logger, task_id=tid, prompt=prompt, branch="guarded_pipeline")
                    _, events = run_guarded(run_id, tid, prompt, DEFAULT_CONFIG)
                    for ev in events:
                        log_trace_narrative(run_logger, ev)
                    guarded_events.extend(events)
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
            log_run_end(run_logger, artifacts={})
            return {"runId": run_id, "verdict": "failed", "error": {"type": type(exc).__name__, "message": str(exc)}}
        for event in [*baseline_events, *guarded_events]:
            append_jsonl(out / "traces.jsonl", event)
        baseline_metrics = aggregate_metrics(baseline_events) if mode in ("baseline", "both") else None
        guarded_metrics = aggregate_metrics(guarded_events) if mode in ("guarded_pipeline", "both") else None
        pass_rate_delta_points = None
        median_latency_delta_percent = None
        if mode == "both" and baseline_metrics and guarded_metrics:
            pass_rate_delta_points = (guarded_metrics["passRate"] - baseline_metrics["passRate"]) * 100
            if baseline_metrics["p50Latency"] == 0:
                median_latency_delta_percent = 0
            else:
                median_latency_delta_percent = (
                    (guarded_metrics["p50Latency"] - baseline_metrics["p50Latency"]) / baseline_metrics["p50Latency"]
                ) * 100
        verdict = (
            verdict_for(baseline_metrics, guarded_metrics)
            if mode == "both" and baseline_metrics and guarded_metrics
            else "inconclusive"
        )
        per_task = []
        for task in tasks:
            b = next((e for e in baseline_events if e["task_id"] == task["taskId"] and e["stage"] == "finalize"), None)
            g = next((e for e in guarded_events if e["task_id"] == task["taskId"] and e["stage"] == "finalize"), None)
            per_task.append(
                {
                    "taskId": task["taskId"],
                    "baselinePassed": None if b is None else b["score"]["passed"],
                    "guardedPassed": None if g is None else g["score"]["passed"],
                    "baselineLatencyMs": None if b is None else b["latency_ms"],
                    "guardedLatencyMs": None if g is None else g["latency_ms"],
                    "passDelta": (1 if g and g["score"]["passed"] else 0) - (1 if b and b["score"]["passed"] else 0),
                    "latencyDeltaMs": (g["latency_ms"] if g else 0) - (b["latency_ms"] if b else 0),
                }
            )
        decision = None
        roi = {"conservative": None, "baseCase": None, "aggressive": None}
        if mode == "both" and baseline_metrics and guarded_metrics:
            pass_delta_points = (guarded_metrics["passRate"] - baseline_metrics["passRate"]) * 100
            reliability_delta_points = (guarded_metrics["reliability"] - baseline_metrics["reliability"]) * 100
            latency_cost_proxy = max(median_latency_delta_percent or 0, 0)
            base_roi = (pass_delta_points + reliability_delta_points) - latency_cost_proxy
            roi = {"conservative": base_roi - 10, "baseCase": base_roi, "aggressive": base_roi + 10}
            decision = strict_gate_decision(baseline_metrics, guarded_metrics, roi_base_case=base_roi)
        summary = {
            "runId": run_id,
            "suitePath": suite_path,
            "suiteVersion": Path(suite_path).stem,
            "mode": mode,
            "provider": DEFAULT_CONFIG.provider,
            "models": {"implementation": DEFAULT_CONFIG.implementation_model, "support": DEFAULT_CONFIG.support_model},
            "budgets": config_snapshot()["budgets"],
            "baselineMetrics": baseline_metrics,
            "guardedMetrics": guarded_metrics,
            "passRateDeltaPoints": pass_rate_delta_points,
            "reliabilityDeltaPoints": None
            if mode != "both" or not baseline_metrics or not guarded_metrics
            else (guarded_metrics["reliability"] - baseline_metrics["reliability"]) * 100,
            "medianLatencyDeltaPercent": median_latency_delta_percent,
            "rootCauseDistribution": {
                "baseline": root_cause_distribution(baseline_events),
                "guarded_pipeline": root_cause_distribution(guarded_events),
            },
            "stageLatencyBreakdownMs": {
                "baseline": stage_latency_breakdown(baseline_events),
                "guarded_pipeline": stage_latency_breakdown(guarded_events),
            },
            "perTaskDeltas": per_task,
            "incrementalRoi": roi,
            "gateDecision": decision,
            "verdict": verdict,
        }
        write_json(out / "config-snapshot.json", config_snapshot())
        write_json(out / "summary.json", summary)
        log_run_end(
            run_logger,
            artifacts={"traces_jsonl": str(out / "traces.jsonl"), "summary_json": str(out / "summary.json")},
        )
        return {"runId": run_id, "verdict": verdict}
    finally:
        shutdown_run_logger(run_logger)
