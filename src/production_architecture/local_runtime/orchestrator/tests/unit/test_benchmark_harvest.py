from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from production_architecture.storage.storage.storage import write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark import run_benchmark

run_benchmark_mod = importlib.import_module("workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.run_benchmark")


def _bench_trace_ev(run_id: str, task_id: str) -> dict:
    """Minimal ``TraceEvent``-shaped row for benchmark harness fakes (matches ``traces_jsonl_event_contract``)."""
    return {
        "run_id": run_id,
        "task_id": task_id,
        "mode": "baseline",
        "model": "m",
        "provider": "p",
        "stage": "finalize",
        "started_at": "2026-01-01T00:00:00+00:00",
        "ended_at": "2026-01-01T00:00:01+00:00",
        "latency_ms": 1,
        "token_input": 0,
        "token_output": 0,
        "estimated_cost_usd": 0.0,
        "retry_count": 0,
        "errors": [],
        "score": {"passed": True, "reliability": 1.0, "validity": 1.0},
        "metadata": None,
    }


def test_run_benchmark_max_tasks_slices_before_run(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    def _fake_read(_path: str) -> list[dict]:
        return [
            {"taskId": "a", "prompt": "p0", "expectedChecks": [], "difficulty": "easy"},
            {"taskId": "b", "prompt": "p1", "expectedChecks": [], "difficulty": "easy"},
            {"taskId": "c", "prompt": "p2", "expectedChecks": [], "difficulty": "easy"},
        ]

    captured: dict[str, int] = {}

    def _fake_run_suite(_logger, _rid, _mode, tasks, **kwargs):  # type: ignore[no-untyped-def]
        captured["n"] = len(tasks)
        on_task = kwargs.get("on_task_events")
        baseline_acc: list[dict] = []
        for t in tasks:
            ev = _bench_trace_ev(_rid, t["taskId"])
            baseline_acc.append(ev)
            if on_task:
                on_task(t["taskId"], [ev], [])
        return baseline_acc, []

    monkeypatch.setattr(run_benchmark_mod, "read_suite", _fake_read)
    monkeypatch.setattr(run_benchmark_mod, "run_suite_tasks", _fake_run_suite)

    suite = tmp_path / "suite.jsonl"
    suite.write_text('{"taskId":"x","prompt":"y","difficulty":"easy"}\n', encoding="utf-8")
    run_benchmark(str(suite), "baseline", max_tasks=2)
    assert captured["n"] == 2


def test_benchmark_manifest_written(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    def _fake_read(_path: str) -> list[dict]:
        return [{"taskId": "only", "prompt": "hi", "expectedChecks": [], "difficulty": "easy"}]

    def _fake_run_suite(_logger, _rid, _mode, tasks, **kwargs):  # type: ignore[no-untyped-def]
        on_task = kwargs.get("on_task_events")
        baseline_acc: list[dict] = []
        for t in tasks:
            ev = _bench_trace_ev(_rid, t["taskId"])
            baseline_acc.append(ev)
            if on_task:
                on_task(t["taskId"], [ev], [])
        return baseline_acc, []

    monkeypatch.setattr(run_benchmark_mod, "read_suite", _fake_read)
    monkeypatch.setattr(run_benchmark_mod, "run_suite_tasks", _fake_run_suite)

    suite = tmp_path / "suite.jsonl"
    suite.write_text('{"taskId":"only","prompt":"hi","difficulty":"easy"}\n', encoding="utf-8")
    run_benchmark(str(suite), "baseline", continue_on_error=True)
    runs = list((tmp_path / "outputs" / "runs").iterdir())
    assert len(runs) == 1
    manifest = json.loads((runs[0] / "benchmark-manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "sde.benchmark_manifest.v1"
    assert manifest["continue_on_error"] is True
    summary = json.loads((runs[0] / "summary.json").read_text(encoding="utf-8"))
    assert summary["taskCount"] == 1
    assert "benchmarkStartedAtMs" in summary


def test_resume_runs_only_pending_tasks(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / "outputs" / "runs" / "rid1"
    run_dir.mkdir(parents=True)
    suite = tmp_path / "suite.jsonl"
    suite.write_text(
        '{"taskId":"a","prompt":"p0","expectedChecks":[],"difficulty":"simple"}\n'
        '{"taskId":"b","prompt":"p1","expectedChecks":[],"difficulty":"simple"}\n',
        encoding="utf-8",
    )
    sp = str(suite.resolve())
    write_json(
        run_dir / "benchmark-manifest.json",
        {
            "schema": "sde.benchmark_manifest.v1",
            "run_id": "rid1",
            "suite_path": sp,
            "mode": "baseline",
            "tasks": [{"taskId": "a", "prompt": "p0"}, {"taskId": "b", "prompt": "p1"}],
            "max_tasks": None,
            "continue_on_error": False,
        },
    )
    write_json(
        run_dir / "benchmark-checkpoint.json",
        {
            "schema": "sde.benchmark_checkpoint.v1",
            "run_id": "rid1",
            "suite_path": sp,
            "mode": "baseline",
            "max_tasks": None,
            "continue_on_error": False,
            "completed_task_ids": ["a"],
            "finished": False,
            "updated_at_ms": 0,
        },
    )
    trace_a = _bench_trace_ev("rid1", "a")
    (run_dir / "traces.jsonl").write_text(json.dumps(trace_a) + "\n", encoding="utf-8")

    captured: dict[str, list[str]] = {"ids": []}

    def _fake_run_suite(_logger, _rid, _mode, tasks, **kwargs):  # type: ignore[no-untyped-def]
        on_task = kwargs.get("on_task_events")
        baseline_acc: list[dict] = []
        for t in tasks:
            ev = _bench_trace_ev(_rid, t["taskId"])
            baseline_acc.append(ev)
            captured["ids"].append(t["taskId"])
            if on_task:
                on_task(t["taskId"], [ev], [])
        return baseline_acc, []

    monkeypatch.setattr(run_benchmark_mod, "run_suite_tasks", _fake_run_suite)

    run_benchmark(None, "baseline", resume_run_id="rid1")
    assert captured["ids"] == ["b"]
    ck = json.loads((run_dir / "benchmark-checkpoint.json").read_text(encoding="utf-8"))
    assert ck["finished"] is True
    assert ck["completed_task_ids"] == ["a", "b"]


def test_resume_requires_checkpoint(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / "outputs" / "runs" / "rid2"
    run_dir.mkdir(parents=True)
    suite = tmp_path / "suite.jsonl"
    suite.write_text('{"taskId":"a","prompt":"p0","expectedChecks":[],"difficulty":"simple"}\n', encoding="utf-8")
    write_json(
        run_dir / "benchmark-manifest.json",
        {
            "schema": "sde.benchmark_manifest.v1",
            "run_id": "rid2",
            "suite_path": str(suite.resolve()),
            "mode": "baseline",
            "tasks": [{"taskId": "a", "prompt": "p0"}],
            "max_tasks": None,
            "continue_on_error": False,
        },
    )
    with pytest.raises(FileNotFoundError, match="benchmark-checkpoint"):
        run_benchmark(None, "baseline", resume_run_id="rid2")


def test_resume_rejects_finished_checkpoint(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / "outputs" / "runs" / "rid3"
    run_dir.mkdir(parents=True)
    suite = tmp_path / "suite.jsonl"
    suite.write_text('{"taskId":"a","prompt":"p0","expectedChecks":[],"difficulty":"simple"}\n', encoding="utf-8")
    sp = str(suite.resolve())
    write_json(
        run_dir / "benchmark-manifest.json",
        {
            "schema": "sde.benchmark_manifest.v1",
            "run_id": "rid3",
            "suite_path": sp,
            "mode": "baseline",
            "tasks": [{"taskId": "a", "prompt": "p0"}],
            "max_tasks": None,
            "continue_on_error": False,
        },
    )
    write_json(
        run_dir / "benchmark-checkpoint.json",
        {
            "schema": "sde.benchmark_checkpoint.v1",
            "run_id": "rid3",
            "suite_path": sp,
            "mode": "baseline",
            "max_tasks": None,
            "continue_on_error": False,
            "completed_task_ids": ["a"],
            "finished": True,
            "updated_at_ms": 0,
        },
    )
    with pytest.raises(ValueError, match="already finished"):
        run_benchmark(None, "baseline", resume_run_id="rid3")
