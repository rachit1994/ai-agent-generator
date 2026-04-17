from __future__ import annotations

from pathlib import Path

from agent_mvp.storage import read_json, write_json


def generate_report(run_id: str) -> str:
    base = Path("outputs") / "runs" / run_id
    summary = read_json(base / "summary.json")
    if "metrics" in summary:
        report_lines = [
            "# MVP Run Report",
            f"- run_id: {summary['runId']}",
            f"- mode: {summary['mode']}",
            f"- provider: {summary['provider']}",
            f"- model: {summary['model']}",
            "",
            "## Metrics",
        ]
        report_lines.extend([f"- {k}: {v}" for k, v in summary["metrics"].items()])
        report = "\n".join(report_lines)
        write_json(base / "report-meta.json", {"recommendation": "n/a_single_run"})
        (base / "report.md").write_text(report, encoding="utf-8")
        return report
    verdict = summary["verdict"]
    if verdict in {"supported", "inconclusive"}:
        recommendation = "continue"
    elif verdict == "partially supported":
        recommendation = "pivot"
    else:
        recommendation = "stop"
    budgets = summary.get("budgets", {})
    planner_timeout = budgets.get("planner_timeout_ms", budgets.get("timeout_ms", "n/a"))
    verifier_timeout = budgets.get("verifier_timeout_ms", budgets.get("timeout_ms", "n/a"))
    executor_timeout = budgets.get("executor_timeout_ms", budgets.get("timeout_ms", "n/a"))
    report_lines = [
        "# MVP Decision Report",
        f"- run_id: {summary['runId']}",
        f"- provider: {summary['provider']}",
        f"- mode: {summary['mode']}",
        f"- implementation_model: {summary['models']['implementation']}",
        f"- support_model: {summary['models']['support']}",
        f"- suite: {summary['suitePath']}",
        f"- suite_version: {summary['suiteVersion']}",
        f"- budgets: tokens={budgets.get('max_tokens', 'n/a')}, retries={budgets.get('max_retries', 'n/a')}, planner_timeout_ms={planner_timeout}, verifier_timeout_ms={verifier_timeout}, executor_timeout_ms={executor_timeout}",
        f"- verdict: {verdict}",
        f"- recommendation: {recommendation}",
        f"- pass_rate_delta_points: {summary['passRateDeltaPoints']}",
        f"- reliability_delta_points: {summary.get('reliabilityDeltaPoints')}",
        f"- median_latency_delta_percent: {summary['medianLatencyDeltaPercent']}",
        "",
        "## Baseline Metrics",
    ]
    report_lines.extend([f"- {k}: {v}" for k, v in (summary.get("baselineMetrics") or {}).items()])
    report_lines.extend(["", "## Guarded Metrics"])
    report_lines.extend([f"- {k}: {v}" for k, v in (summary.get("guardedMetrics") or {}).items()])
    report_lines.extend(["", "## Per-task deltas"])
    for item in summary["perTaskDeltas"]:
        report_lines.append(
            f"- {item['taskId']}: pass_delta={item['passDelta']}, latency_delta_ms={item['latencyDeltaMs']}, baseline_pass={item['baselinePassed']}, guarded_pass={item['guardedPassed']}"
        )
    root_causes = summary.get("rootCauseDistribution") or {}
    report_lines.extend(["", "## Root-cause distribution"])
    for side, dist in root_causes.items():
        report_lines.append(f"- {side}: {dist}")
    stage_latency = summary.get("stageLatencyBreakdownMs") or {}
    report_lines.extend(["", "## Stage latency breakdown (ms)"])
    for side, dist in stage_latency.items():
        report_lines.append(f"- {side}: {dist}")
    roi = summary.get("incrementalRoi") or {}
    report_lines.extend(
        [
            "",
            "## Incremental ROI",
            f"- conservative: {roi.get('conservative')}",
            f"- base_case: {roi.get('baseCase')}",
            f"- aggressive: {roi.get('aggressive')}",
        ]
    )
    decision_obj = summary.get("gateDecision")
    if decision_obj:
        report_lines.extend(
            [
                "",
                "## Strict gate decision",
                f"- decision: {decision_obj.get('decision')}",
                f"- checks: {decision_obj.get('checks')}",
            ]
        )
    report = "\n".join(report_lines)
    write_json(base / "report-meta.json", {"recommendation": recommendation, "gateDecision": decision_obj})
    (base / "report.md").write_text(report, encoding="utf-8")
    return report
