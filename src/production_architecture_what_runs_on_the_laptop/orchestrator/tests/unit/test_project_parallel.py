"""Phase 6: optional parallel execution via git worktrees."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator.api.project_driver import run_project_session


def _step(step_id: str, description: str, path_scope: list[str]) -> dict:
    return {
        "step_id": step_id,
        "phase": "p",
        "title": step_id.upper(),
        "description": description,
        "depends_on": [],
        "path_scope": path_scope,
        "verification": {"commands": [{"cmd": "true", "args": []}]},
    }


def test_parallel_worktrees_runs_both_steps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = tmp_path / "sess"
    session.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            _step("a", "da", ["src/**"]),
            _step("b", "db", ["docs/**"]),
        ],
    }
    (session / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    calls: list[tuple[str | None, str | None]] = []

    def fake_execute(
        task: str,
        mode: str,
        *,
        repeat: int = 1,
        project_step_id: str | None = None,
        project_session_dir: str | None = None,
    ) -> dict:
        calls.append((project_step_id, project_session_dir))
        rid = f"r{project_step_id}"
        od = tmp_path / rid
        od.mkdir(exist_ok=True)
        return {
            "run_id": rid,
            "output_dir": str(od),
            "output": '{"answer":"","checks":[{"name":"verifier_passed","passed":true}],"refusal":null}',
        }

    def fake_verify(**kwargs: object) -> dict:
        session_dir = kwargs["session_dir"]
        step_id = str(kwargs["step_id"])
        assert isinstance(session_dir, Path)
        vdir = session_dir / "verification"
        vdir.mkdir(parents=True, exist_ok=True)
        bundle = {"schema_version": "1.0", "step_id": step_id, "passed": True, "commands": []}
        (vdir / f"{step_id}.json").write_text(json.dumps(bundle), encoding="utf-8")
        return bundle

    def fake_git_ok(_repo: Path) -> bool:
        return True

    def fake_add(_repo: Path, wt: Path) -> bool:
        wt.mkdir(parents=True, exist_ok=True)
        (wt / ".gitmarker").write_text("ok", encoding="utf-8")
        return True

    def fake_remove(_repo: Path, _wt: Path) -> None:
        return

    monkeypatch.setattr("orchestrator.api.project_driver.execute_single_task", fake_execute)
    monkeypatch.setattr("orchestrator.api.project_driver.run_step_verification", fake_verify)
    monkeypatch.setattr("orchestrator.api.project_driver.git_worktree_available", fake_git_ok)
    monkeypatch.setattr("orchestrator.api.project_driver.add_detached_worktree", fake_add)
    monkeypatch.setattr("orchestrator.api.project_driver.remove_worktree", fake_remove)

    out = run_project_session(
        session,
        repo_root=tmp_path,
        max_steps=10,
        mode="baseline",
        max_concurrent_agents=2,
        parallel_worktrees=True,
    )
    assert out["exit_code"] == 0
    assert {c[0] for c in calls} == {"a", "b"}
    for _sid, psd in calls:
        assert psd == str(session.resolve())


def test_parallel_disabled_without_git_or_flag_sequential(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = tmp_path / "sess"
    session.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            _step("a", "da", ["src/**"]),
            _step("b", "db", ["docs/**"]),
        ],
    }
    (session / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    order: list[str] = []

    def fake_execute(
        task: str,
        mode: str,
        *,
        repeat: int = 1,
        project_step_id: str | None = None,
        project_session_dir: str | None = None,
    ) -> dict:
        if project_step_id:
            order.append(project_step_id)
        rid = f"r{len(order)}"
        od = tmp_path / rid
        od.mkdir(exist_ok=True)
        return {
            "run_id": rid,
            "output_dir": str(od),
            "output": '{"answer":"","checks":[{"name":"verifier_passed","passed":true}],"refusal":null}',
        }

    def fake_verify(**kwargs: object) -> dict:
        session_dir = kwargs["session_dir"]
        step_id = str(kwargs["step_id"])
        assert isinstance(session_dir, Path)
        vdir = session_dir / "verification"
        vdir.mkdir(parents=True, exist_ok=True)
        bundle = {"schema_version": "1.0", "step_id": step_id, "passed": True, "commands": []}
        (vdir / f"{step_id}.json").write_text(json.dumps(bundle), encoding="utf-8")
        return bundle

    monkeypatch.setattr("orchestrator.api.project_driver.execute_single_task", fake_execute)
    monkeypatch.setattr("orchestrator.api.project_driver.run_step_verification", fake_verify)
    monkeypatch.setattr("orchestrator.api.project_driver.git_worktree_available", lambda _p: False)

    out = run_project_session(
        session,
        repo_root=tmp_path,
        max_steps=10,
        mode="baseline",
        max_concurrent_agents=2,
        parallel_worktrees=True,
    )
    assert out["exit_code"] == 0
    assert order == ["a", "b"]
