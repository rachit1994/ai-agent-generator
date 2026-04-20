from __future__ import annotations

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.summary_payload import (
    build_summary,
)


def test_build_summary_single_mode_has_no_cross_mode_deltas() -> None:
    summary = build_summary(
        run_id="run-1",
        suite_path="suite.jsonl",
        mode="baseline",
        tasks=[{"taskId": "t1"}],
        baseline_events=[{"task_id": "t1", "stage": "finalize", "score": {"passed": True}, "latency_ms": 10}],
        guarded_events=[],
    )
    row = summary["perTaskDeltas"][0]
    assert row["passDelta"] is None
    assert row["latencyDeltaMs"] is None
    assert summary["verdict"] == "inconclusive"


def test_build_summary_both_mode_has_deltas_when_both_finalize_exist() -> None:
    summary = build_summary(
        run_id="run-1",
        suite_path="suite.jsonl",
        mode="both",
        tasks=[{"taskId": "t1"}],
        baseline_events=[{"task_id": "t1", "stage": "finalize", "score": {"passed": False, "reliability": 0, "validity": 1}, "latency_ms": 10}],
        guarded_events=[{"task_id": "t1", "stage": "finalize", "score": {"passed": True, "reliability": 1, "validity": 1}, "latency_ms": 12}],
    )
    row = summary["perTaskDeltas"][0]
    assert row["passDelta"] == 1
    assert row["latencyDeltaMs"] == 2
