from __future__ import annotations

from workflow_pipelines.benchmark_aggregate_summary import (
    build_benchmark_aggregate_summary_runtime,
    validate_benchmark_aggregate_summary_runtime_dict,
)


def test_build_benchmark_aggregate_summary_runtime_deterministic() -> None:
    summary = {
        "schema": "sde.benchmark_aggregate_summary.v1",
        "runId": "bench-sum",
        "suitePath": "/tmp/s.jsonl",
        "mode": "baseline",
        "verdict": "passed",
        "perTaskDeltas": [],
    }
    one = build_benchmark_aggregate_summary_runtime(summary=summary)
    two = build_benchmark_aggregate_summary_runtime(summary=summary)
    assert one == two
    assert one["status"] == "finished"
    assert validate_benchmark_aggregate_summary_runtime_dict(one) == []


def test_validate_benchmark_aggregate_summary_runtime_fail_closed() -> None:
    errs = validate_benchmark_aggregate_summary_runtime_dict({"schema": "bad"})
    assert "benchmark_aggregate_summary_runtime_schema" in errs
    assert "benchmark_aggregate_summary_runtime_schema_version" in errs
