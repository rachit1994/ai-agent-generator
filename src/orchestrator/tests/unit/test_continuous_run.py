from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator.api.continuous_run import run_continuous_until


def test_run_continuous_until_never_runs_n_times(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[int] = []

    def fake_execute(task: str, mode: str, *, repeat: int = 1) -> dict:
        calls.append(1)
        rid = f"r{len(calls)}"
        d = tmp_path / rid
        d.mkdir()
        return {"run_id": rid, "output_dir": str(d), "output": "{}"}

    monkeypatch.setattr(
        "orchestrator.api.continuous_run.execute_single_task",
        fake_execute,
    )
    out = run_continuous_until(
        task="t",
        mode="baseline",
        max_iterations=4,
        stop_when="never",
    )
    assert out["exit_code"] == 0
    assert out["stopped_reason"] == "max_iterations"
    assert len(out["iterations"]) == 4
    assert len(calls) == 4


def test_run_continuous_until_definition_of_done_stops_early(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    n = {"i": 0}

    def fake_execute(task: str, mode: str, *, repeat: int = 1) -> dict:
        n["i"] += 1
        rid = f"r{n['i']}"
        d = tmp_path / rid
        d.mkdir()
        dod = {"schema_version": "1.0", "all_required_passed": n["i"] >= 2}
        (d / "review.json").write_text(
            json.dumps({"definition_of_done": dod}),
            encoding="utf-8",
        )
        return {"run_id": rid, "output_dir": str(d), "output": "{}"}

    monkeypatch.setattr(
        "orchestrator.api.continuous_run.execute_single_task",
        fake_execute,
    )
    out = run_continuous_until(
        task="t",
        mode="guarded_pipeline",
        max_iterations=10,
        stop_when="definition_of_done",
    )
    assert out["exit_code"] == 0
    assert out["stopped_reason"] == "definition_of_done"
    assert len(out["iterations"]) == 2


def test_run_continuous_until_validation_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    n = {"i": 0}

    def fake_execute(task: str, mode: str, *, repeat: int = 1) -> dict:
        n["i"] += 1
        return {"run_id": f"r{n['i']}", "output_dir": "/tmp/fake", "output": "{}"}

    def fake_validate(_path: Path, *, mode: str) -> dict:
        return {"ok": n["i"] >= 3, "validation_ready": n["i"] >= 3, "errors": []}

    monkeypatch.setattr(
        "orchestrator.api.continuous_run.execute_single_task",
        fake_execute,
    )
    monkeypatch.setattr(
        "orchestrator.api.continuous_run.validate_execution_run_directory",
        fake_validate,
    )
    out = run_continuous_until(
        task="t",
        mode="baseline",
        max_iterations=10,
        stop_when="validation_ready",
    )
    assert out["exit_code"] == 0
    assert out["stopped_reason"] == "validation_ready"
    assert len(out["iterations"]) == 3


def test_run_continuous_until_pipeline_error_stops(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "orchestrator.api.continuous_run.execute_single_task",
        lambda *_a, **_k: {"error": {"type": "E", "message": "m"}},
    )
    out = run_continuous_until(
        task="t",
        mode="baseline",
        max_iterations=5,
        stop_when="never",
    )
    assert out["exit_code"] == 1
    assert out["stopped_reason"] == "pipeline_error"


def test_run_continuous_until_max_without_match(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_execute(task: str, mode: str, *, repeat: int = 1) -> dict:
        return {"run_id": "r1", "output_dir": "/x", "output": "{}"}

    monkeypatch.setattr(
        "orchestrator.api.continuous_run.execute_single_task",
        fake_execute,
    )
    monkeypatch.setattr(
        "orchestrator.api.continuous_run.validate_execution_run_directory",
        lambda *_a, **_k: {"ok": False, "validation_ready": False, "errors": ["e"]},
    )
    out = run_continuous_until(
        task="t",
        mode="baseline",
        max_iterations=2,
        stop_when="validation_ready",
    )
    assert out["exit_code"] == 1
    assert out["stopped_reason"] == "max_iterations_without_match"
