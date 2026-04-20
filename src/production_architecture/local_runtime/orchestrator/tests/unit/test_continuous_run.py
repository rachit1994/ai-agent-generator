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


def test_run_continuous_project_session_forwards_enforce_plan_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict[str, object]] = []

    def fake_run_project_session(
        session_dir: Path,
        *,
        repo_root: Path,
        max_steps: int,
        mode: str,
        max_concurrent_agents: int = 1,
        progress_file: Path | None = None,
        parallel_worktrees: bool = False,
        lease_stale_sec: int | None = None,
        enforce_plan_lock: bool = False,
        require_non_stub_reviewer: bool = False,
    ) -> dict:
        calls.append(
            {
                "session_dir": session_dir,
                "repo_root": repo_root,
                "max_steps": max_steps,
                "mode": mode,
                "enforce_plan_lock": enforce_plan_lock,
                "require_non_stub_reviewer": require_non_stub_reviewer,
            }
        )
        return {"exit_code": 0, "stopped_reason": "completed_review_pass"}

    monkeypatch.setattr(
        "orchestrator.api.continuous_run.run_project_session",
        fake_run_project_session,
    )
    from orchestrator.api.continuous_run import run_continuous_project_session

    out = run_continuous_project_session(
        session_dir=tmp_path / "s",
        repo_root=tmp_path,
        max_iterations=3,
        mode="baseline",
        enforce_plan_lock=True,
    )
    assert out["driver"] == "project_session"
    assert calls and calls[0]["enforce_plan_lock"] is True
    assert calls[0]["require_non_stub_reviewer"] is False


def test_run_continuous_project_session_forwards_require_non_stub_reviewer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict[str, object]] = []

    def fake_run_project_session(
        session_dir: Path,
        *,
        repo_root: Path,
        max_steps: int,
        mode: str,
        max_concurrent_agents: int = 1,
        progress_file: Path | None = None,
        parallel_worktrees: bool = False,
        lease_stale_sec: int | None = None,
        enforce_plan_lock: bool = False,
        require_non_stub_reviewer: bool = False,
    ) -> dict:
        calls.append({"require_non_stub_reviewer": require_non_stub_reviewer})
        return {"exit_code": 0, "stopped_reason": "completed_review_pass"}

    monkeypatch.setattr(
        "orchestrator.api.continuous_run.run_project_session",
        fake_run_project_session,
    )
    from orchestrator.api.continuous_run import run_continuous_project_session

    out = run_continuous_project_session(
        session_dir=tmp_path / "s",
        repo_root=tmp_path,
        max_iterations=2,
        mode="baseline",
        enforce_plan_lock=True,
        require_non_stub_reviewer=True,
    )
    assert out["exit_code"] == 0
    assert calls == [{"require_non_stub_reviewer": True}]
