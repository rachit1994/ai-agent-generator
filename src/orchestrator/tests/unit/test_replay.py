from __future__ import annotations

import json
import pytest

from sde_foundations.eval import aggregate_metrics
from sde_pipeline.benchmark.task_loop import synthetic_finalize_failure_event
from sde_pipeline.config import DEFAULT_CONFIG
from sde_pipeline.replay import replay_run


def test_replay_narrative_json(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / "outputs" / "runs" / "run-a"
    run_dir.mkdir(parents=True)
    (run_dir / "run-manifest.json").write_text(
        json.dumps(
            {
                "schema": "sde.run_manifest.v1",
                "run_id": "run-a",
                "mode": "baseline",
                "task": "hello world",
            }
        ),
        encoding="utf-8",
    )
    ev = {
        "run_id": "run-a",
        "task_id": "manual-task",
        "mode": "baseline",
        "stage": "finalize",
        "latency_ms": 3,
        "errors": [],
        "score": {"passed": True, "reliability": 1.0, "validity": 1.0},
    }
    (run_dir / "traces.jsonl").write_text(json.dumps(ev) + "\n", encoding="utf-8")
    out = replay_run("run-a", output_format="json", rerun=False)
    data = json.loads(out)
    assert data["event_count"] == 1
    assert data["manifest"]["task"] == "hello world"


def test_write_trajectory_html_creates_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / "outputs" / "runs" / "r-html"
    run_dir.mkdir(parents=True)
    (run_dir / "run-manifest.json").write_text(
        json.dumps({"schema": "sde.run_manifest.v1", "run_id": "r-html", "mode": "baseline", "task": "t"}),
        encoding="utf-8",
    )
    ev = {
        "run_id": "r-html",
        "task_id": "manual-task",
        "mode": "baseline",
        "stage": "finalize",
        "latency_ms": 2,
        "errors": [],
        "score": {"passed": True, "reliability": 1.0, "validity": 1.0},
    }
    (run_dir / "traces.jsonl").write_text(json.dumps(ev) + "\n", encoding="utf-8")
    from sde_pipeline.replay import write_trajectory_html

    path = write_trajectory_html("r-html")
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    assert "<table>" in body and "finalize" in body


def test_replay_run_rejects_html_with_rerun() -> None:
    from sde_pipeline.replay import replay_run

    with pytest.raises(ValueError, match="html"):
        replay_run("any", output_format="html", rerun=True)


def test_replay_rerun_invokes_execute(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / "outputs" / "runs" / "prior"
    run_dir.mkdir(parents=True)
    (run_dir / "run-manifest.json").write_text(
        json.dumps(
            {
                "schema": "sde.run_manifest.v1",
                "run_id": "prior",
                "mode": "baseline",
                "task": "x",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "traces.jsonl").write_text("{}\n", encoding="utf-8")

    def _fake_execute(task: str, mode: str, **kwargs: object) -> dict:  # type: ignore[no-untyped-def]
        return {"run_id": "new-run", "output_dir": str(tmp_path / "outputs" / "runs" / "new-run"), "stub": True}

    monkeypatch.setattr("sde_pipeline.runner.execute_single_task", _fake_execute)
    text = replay_run("prior", output_format="text", rerun=True)
    assert "new-run" in text


def test_replay_rerun_passes_project_manifest_fields(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / "outputs" / "runs" / "prior2"
    run_dir.mkdir(parents=True)
    (run_dir / "run-manifest.json").write_text(
        json.dumps(
            {
                "schema": "sde.run_manifest.v1",
                "run_id": "prior2",
                "mode": "baseline",
                "task": "x",
                "project_step_id": "step_z",
                "project_session_dir": "/tmp/sde_sess",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "traces.jsonl").write_text("{}\n", encoding="utf-8")
    captured: dict[str, object] = {}

    def _fake_execute(task: str, mode: str, **kwargs: object) -> dict:
        captured.update(kwargs)
        return {"run_id": "n2", "output_dir": str(tmp_path / "outputs" / "runs" / "n2"), "stub": True}

    monkeypatch.setattr("sde_pipeline.runner.execute_single_task", _fake_execute)
    replay_run("prior2", output_format="text", rerun=True)
    assert captured.get("project_step_id") == "step_z"
    assert captured.get("project_session_dir") == "/tmp/sde_sess"


def test_synthetic_failure_event_metrics() -> None:
    ev = synthetic_finalize_failure_event("r", "t1", "baseline", ValueError("boom"), DEFAULT_CONFIG)
    m = aggregate_metrics([ev])
    assert m["passRate"] == 0.0
