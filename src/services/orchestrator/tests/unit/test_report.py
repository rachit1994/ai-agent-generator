from pathlib import Path

from agent_mvp.report import generate_report
from agent_mvp.storage import ensure_dir, write_json


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
            "model": "qwen2.5:7b-instruct",
            "metrics": {"passRate": 0, "reliability": 0},
        },
    )
    report = generate_report(run_id)
    assert "MVP Run Report" in report


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
            "suitePath": "./data/mvp-tasks.jsonl",
            "suiteVersion": "v1",
            "budgets": {"max_tokens": 1, "max_retries": 1, "timeout_ms": 1},
            "verdict": "supported",
            "passRateDeltaPoints": 10,
            "medianLatencyDeltaPercent": 0,
            "baselineMetrics": {"passRate": 0},
            "guardedMetrics": {"passRate": 1},
            "perTaskDeltas": [],
        },
    )
    report = generate_report(run_id)
    assert "MVP Decision Report" in report


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
            "suitePath": "./data/mvp-tasks.jsonl",
            "suiteVersion": "v1",
            "budgets": {"max_tokens": 1, "max_retries": 1, "timeout_ms": 1},
            "verdict": "inconclusive",
            "passRateDeltaPoints": 5,
            "medianLatencyDeltaPercent": 0,
            "baselineMetrics": {"passRate": 0},
            "guardedMetrics": {"passRate": 0.05},
            "perTaskDeltas": [],
        },
    )
    generate_report(run_id)
    assert (base / "report-meta.json").read_text(encoding="utf-8").find("continue") >= 0
