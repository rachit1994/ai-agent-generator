"""Assemble benchmark summary.json body and verdict."""

from __future__ import annotations

from pathlib import Path

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.config import DEFAULT_CONFIG, config_snapshot
from evaluation_framework.offline_evaluation.sde_eval.eval import (
    aggregate_metrics,
    root_cause_distribution,
    stage_latency_breakdown,
    strict_gate_decision,
    verdict_for,
)


def build_summary(
    *,
    run_id: str,
    suite_path: str,
    mode: str,
    tasks: list[dict],
    baseline_events: list[dict],
    guarded_events: list[dict],
) -> dict:
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
        if b is None or g is None:
            pass_delta = None
            latency_delta_ms = None
        else:
            pass_delta = (1 if g["score"]["passed"] else 0) - (1 if b["score"]["passed"] else 0)
            latency_delta_ms = g["latency_ms"] - b["latency_ms"]
        per_task.append(
            {
                "taskId": task["taskId"],
                "baselinePassed": None if b is None else b["score"]["passed"],
                "guardedPassed": None if g is None else g["score"]["passed"],
                "baselineLatencyMs": None if b is None else b["latency_ms"],
                "guardedLatencyMs": None if g is None else g["latency_ms"],
                "passDelta": pass_delta,
                "latencyDeltaMs": latency_delta_ms,
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
    return {
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
