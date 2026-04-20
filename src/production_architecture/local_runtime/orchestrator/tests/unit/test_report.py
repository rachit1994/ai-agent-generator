from pathlib import Path

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.report import generate_report
from production_architecture.storage.storage.storage import ensure_dir, write_json


def test_single_run_report_support(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    run_id = "r-single"
    base = Path("outputs") / "runs" / run_id
    ensure_dir(base)
    write_json(
        base / "summary.json",
        {
            "runId": run_id,
            "mode": "baseline",
            "provider": "ollama",
            "model": "qwen3:14b",
            "metrics": {"passRate": 0, "reliability": 0},
        },
    )
    report = generate_report(run_id)
    assert "SDE run report" in report


def test_benchmark_report_support(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    run_id = "r-bench"
    base = Path("outputs") / "runs" / run_id
    ensure_dir(base)
    write_json(
        base / "summary.json",
        {
            "runId": run_id,
            "provider": "ollama",
            "mode": "both",
            "models": {"implementation": "q", "support": "g"},
            "suitePath": "./data/medium-hard-sde-suite.jsonl",
            "suiteVersion": "medium-hard-sde",
            "budgets": {"max_tokens": 1, "max_retries": 1, "timeout_ms": 1},
            "verdict": "supported",
            "passRateDeltaPoints": 10,
            "medianLatencyDeltaPercent": 0,
            "baselineMetrics": {"passRate": 0},
            "guardedMetrics": {"passRate": 1},
            "reliabilityDeltaPoints": 10,
            "perTaskDeltas": [],
            "rootCauseDistribution": {"baseline": {"quality_check_fail": 1}, "guarded_pipeline": {}},
            "stageLatencyBreakdownMs": {"baseline": {"finalize": 10}, "guarded_pipeline": {"finalize": 12}},
            "incrementalRoi": {"conservative": -1, "baseCase": 1, "aggressive": 2},
            "gateDecision": {"decision": "continue_and_scale", "checks": {"passRateDelta": True}},
        },
    )
    report = generate_report(run_id)
    assert "SDE decision report" in report


def test_benchmark_report_inconclusive_recommends_continue(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    run_id = "r-bench-inconclusive"
    base = Path("outputs") / "runs" / run_id
    ensure_dir(base)
    write_json(
        base / "summary.json",
        {
            "runId": run_id,
            "provider": "ollama",
            "mode": "both",
            "models": {"implementation": "q", "support": "g"},
            "suitePath": "./data/medium-hard-sde-suite.jsonl",
            "suiteVersion": "medium-hard-sde",
            "budgets": {"max_tokens": 1, "max_retries": 1, "timeout_ms": 1},
            "verdict": "inconclusive",
            "passRateDeltaPoints": 5,
            "medianLatencyDeltaPercent": 0,
            "baselineMetrics": {"passRate": 0},
            "guardedMetrics": {"passRate": 0.05},
            "reliabilityDeltaPoints": 5,
            "perTaskDeltas": [],
            "rootCauseDistribution": {"baseline": {"quality_check_fail": 20}, "guarded_pipeline": {"quality_check_fail": 19}},
            "stageLatencyBreakdownMs": {"baseline": {"finalize": 200}, "guarded_pipeline": {"finalize": 210}},
            "incrementalRoi": {"conservative": -2, "baseCase": -1, "aggressive": 0},
            "gateDecision": {"decision": "stop", "checks": {"passRateDelta": False}},
        },
    )
    generate_report(run_id)
    assert (base / "report-meta.json").read_text(encoding="utf-8").find("continue") >= 0
