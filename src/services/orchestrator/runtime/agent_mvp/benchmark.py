from __future__ import annotations

import json
from pathlib import Path

from agent_mvp.config import DEFAULT_CONFIG, config_snapshot
from agent_mvp.eval import aggregate_metrics, root_cause_distribution, stage_latency_breakdown, strict_gate_decision, verdict_for
from agent_mvp.modes.baseline import run_baseline
from agent_mvp.modes.guarded import run_guarded
from agent_mvp.safeguards import validate_task_payload
from agent_mvp.storage import append_jsonl, ensure_dir, write_json
from agent_mvp.utils import create_run_id


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
    out = Path("outputs") / "runs" / run_id
    ensure_dir(out)
    baseline_events: list[dict] = []
    guarded_events: list[dict] = []
    for task in tasks:
        if mode in ("baseline", "both"):
            _, events = run_baseline(run_id, task["taskId"], task["prompt"], DEFAULT_CONFIG)
            baseline_events.extend(events)
        if mode in ("guarded_pipeline", "both"):
            _, events = run_guarded(run_id, task["taskId"], task["prompt"], DEFAULT_CONFIG)
            guarded_events.extend(events)
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
            median_latency_delta_percent = ((guarded_metrics["p50Latency"] - baseline_metrics["p50Latency"]) / baseline_metrics["p50Latency"]) * 100
    verdict = verdict_for(baseline_metrics, guarded_metrics) if mode == "both" and baseline_metrics and guarded_metrics else "inconclusive"
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
        # Value proxy uses reliability + pass-rate lift; cost proxy uses latency overhead.
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
    return {"runId": run_id, "verdict": verdict}
