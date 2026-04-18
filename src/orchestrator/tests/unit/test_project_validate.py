"""Phase 9: sde project validate (read-only preflight)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator.api.project_validate import (
    EXIT_VALIDATE_INVALID,
    EXIT_VALIDATE_OK,
    EXIT_VALIDATE_WORKSPACE,
    validate_project_session,
)


def test_validate_project_session_ok_minimal_plan(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d",
                "depends_on": [],
                "path_scope": [],
            },
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    out = validate_project_session(sess, repo_root=tmp_path, check_workspace=False)
    assert out["exit_code"] == EXIT_VALIDATE_OK
    assert out["ok"] is True
    assert out["step_count"] == 1


def test_validate_project_session_missing_plan(tmp_path: Path) -> None:
    sess = tmp_path / "empty"
    sess.mkdir()
    out = validate_project_session(sess, repo_root=tmp_path, check_workspace=False)
    assert out["exit_code"] == EXIT_VALIDATE_INVALID
    assert out["ok"] is False


def test_validate_project_session_cycle(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "x",
                "depends_on": ["b"],
                "path_scope": [],
            },
            {
                "step_id": "b",
                "phase": "p",
                "title": "B",
                "description": "y",
                "depends_on": ["a"],
                "path_scope": [],
            },
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    out = validate_project_session(sess, repo_root=tmp_path, check_workspace=False)
    assert out["exit_code"] == EXIT_VALIDATE_INVALID
    assert out.get("error") == "dependency_cycle"


def test_validate_project_session_workspace_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "workspace": {"branch": "main"},
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d",
                "depends_on": [],
                "path_scope": [],
                "verification": {"commands": [{"cmd": "true", "args": []}]},
            },
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    monkeypatch.setattr(
        "orchestrator.api.project_validate.evaluate_workspace_repo_gates",
        lambda _plan, _root: "workspace_branch_mismatch",
    )
    out = validate_project_session(sess, repo_root=tmp_path, check_workspace=True)
    assert out["exit_code"] == EXIT_VALIDATE_WORKSPACE
    assert out["ok"] is False


def test_validate_project_session_skip_workspace(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "workspace": {"branch": "nonexistent-branch-xyz"},
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d",
                "depends_on": [],
                "path_scope": [],
            },
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    out = validate_project_session(sess, repo_root=tmp_path, check_workspace=False)
    assert out["exit_code"] == EXIT_VALIDATE_OK
