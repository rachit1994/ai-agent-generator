"""Phase 7: plan workspace.branch + allowed_path_prefixes enforcement."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator.api.project_driver import run_project_session
from orchestrator.api.project_schema import validate_project_plan
from orchestrator.api.project_workspace import (
    evaluate_workspace_repo_gates,
    git_head_matches_branch,
    path_scope_pattern_allowed,
)


def test_path_scope_pattern_allowed_overlap() -> None:
    prefs = ["src/", "docs/"]
    assert path_scope_pattern_allowed("src/**", prefs) is True
    assert path_scope_pattern_allowed("src/orchestrator/**", prefs) is True
    assert path_scope_pattern_allowed("docs/**/*.md", prefs) is True
    assert path_scope_pattern_allowed("vendor/**", prefs) is False
    assert path_scope_pattern_allowed("../src/**", prefs) is False


def test_validate_project_plan_workspace_path_violation() -> None:
    plan = {
        "schema_version": "1.0",
        "workspace": {"branch": "main", "allowed_path_prefixes": ["src/"]},
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d",
                "depends_on": [],
                "path_scope": ["docs/**"],
                "verification": {"commands": [{"cmd": "true", "args": []}]},
            },
        ],
    }
    errs = validate_project_plan(plan)
    assert any("outside_prefixes" in e for e in errs)


def test_validate_project_plan_workspace_empty_prefixes_list() -> None:
    plan = {
        "schema_version": "1.0",
        "workspace": {"allowed_path_prefixes": []},
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d",
                "depends_on": [],
                "path_scope": ["src/**"],
                "verification": {"commands": [{"cmd": "true", "args": []}]},
            },
        ],
    }
    errs = validate_project_plan(plan)
    assert "project_plan_workspace_allowed_path_prefixes_empty" in errs


def test_validate_project_plan_workspace_branch_bad() -> None:
    plan = {
        "schema_version": "1.0",
        "workspace": {"branch": ""},
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
    errs = validate_project_plan(plan)
    assert "project_plan_workspace_branch_bad" in errs


def test_evaluate_workspace_repo_gates_skips_without_branch() -> None:
    plan = {"schema_version": "1.0", "workspace": {}, "steps": []}
    assert evaluate_workspace_repo_gates(plan, Path("/tmp")) is None


def test_run_project_session_workspace_branch_blocked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = tmp_path / "sess"
    session.mkdir()
    plan = {
        "schema_version": "1.0",
        "workspace": {"branch": "release"},
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
    (session / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")

    monkeypatch.setattr(
        "orchestrator.api.project_workspace.git_head_matches_branch",
        lambda _root, _b: (False, "workspace_branch_mismatch:test"),
    )

    out = run_project_session(session, repo_root=tmp_path, max_steps=5, mode="baseline")
    assert out["exit_code"] == 1
    assert "workspace_branch_mismatch" in (out.get("detail") or "")


def test_git_head_matches_branch_requires_git(tmp_path: Path) -> None:
    ok, reason = git_head_matches_branch(tmp_path, "main")
    assert ok is False
    assert reason is not None and "git" in reason.lower()
