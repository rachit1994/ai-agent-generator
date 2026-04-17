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
    report_lines = [
        "# MVP Decision Report",
        f"- run_id: {summary['runId']}",
        f"- provider: {summary['provider']}",
        f"- mode: {summary['mode']}",
        f"- implementation_model: {summary['models']['implementation']}",
        f"- support_model: {summary['models']['support']}",
        f"- suite: {summary['suitePath']}",
        f"- suite_version: {summary['suiteVersion']}",
        f"- budgets: tokens={summary['budgets']['max_tokens']}, retries={summary['budgets']['max_retries']}, timeout_ms={summary['budgets']['timeout_ms']}",
        f"- verdict: {verdict}",
        f"- recommendation: {recommendation}",
        f"- pass_rate_delta_points: {summary['passRateDeltaPoints']}",
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
    report = "\n".join(report_lines)
    write_json(base / "report-meta.json", {"recommendation": recommendation})
    (base / "report.md").write_text(report, encoding="utf-8")
    return report
