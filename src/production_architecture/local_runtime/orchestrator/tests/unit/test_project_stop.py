from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator.api.project_driver import run_project_session
from orchestrator.api.project_stop import (
    EXIT_SESSION_BLOCKED_OR_BUDGET,
    EXIT_SESSION_INVALID,
    EXIT_SESSION_OK,
    exit_code_ci_meaning,
    write_stop_report,
)


def test_exit_code_ci_meaning() -> None:
    assert exit_code_ci_meaning(EXIT_SESSION_OK) == "session_completed_verified"
    assert "blocked" in exit_code_ci_meaning(EXIT_SESSION_BLOCKED_OR_BUDGET)
    assert "invalid" in exit_code_ci_meaning(EXIT_SESSION_INVALID)


def test_write_stop_report_roundtrip(tmp_path: Path) -> None:
    body = write_stop_report(
        tmp_path,
        exit_code=1,
        stopped_reason="test",
        driver_status="blocked_human",
        max_steps=10,
        steps_used=3,
        block_detail="x",
        extra={"k": "v"},
    )
    assert body["exit_code"] == 1
    raw = json.loads((tmp_path / "stop_report.json").read_text(encoding="utf-8"))
    assert raw["ci"]["exit_code_meaning"] == exit_code_ci_meaning(1)
    assert raw["extra"]["k"] == "v"


def test_write_stop_report_rejects_invalid_numeric_inputs(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="exit_code must be an int"):
        write_stop_report(
            tmp_path,
            exit_code=True,  # type: ignore[arg-type]
            stopped_reason="test",
            driver_status="blocked_human",
            max_steps=10,
            steps_used=3,
        )
    with pytest.raises(ValueError, match="max_steps must be a non-negative int"):
        write_stop_report(
            tmp_path,
            exit_code=1,
            stopped_reason="test",
            driver_status="blocked_human",
            max_steps=-1,
            steps_used=3,
        )
    with pytest.raises(ValueError, match="steps_used must be a non-negative int"):
        write_stop_report(
            tmp_path,
            exit_code=1,
            stopped_reason="test",
            driver_status="blocked_human",
            max_steps=10,
            steps_used=-1,
        )


def test_run_project_session_invalid_plan_emits_stop(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text(
        json.dumps({"schema_version": "0.9", "steps": []}),
        encoding="utf-8",
    )
    out = run_project_session(sess, repo_root=tmp_path, max_steps=5, mode="baseline")
    assert out["exit_code"] == 2
    assert (sess / "stop_report.json").is_file()


def test_run_project_session_plan_lock_gate_blocks(tmp_path: Path) -> None:
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
            }
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    out = run_project_session(
        sess,
        repo_root=tmp_path,
        max_steps=5,
        mode="baseline",
        enforce_plan_lock=True,
    )
    assert out["exit_code"] == 1
    assert out["stopped_reason"] == "blocked_human"
    assert out["detail"] == "plan_lock_not_ready"
    assert (sess / "stop_report.json").is_file()


def test_run_project_session_rejects_non_int_or_non_positive_concurrency(tmp_path: Path) -> None:
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
            }
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")

    with pytest.raises(ValueError, match="max_concurrent_agents"):
        run_project_session(
            sess,
            repo_root=tmp_path,
            max_steps=5,
            mode="baseline",
            max_concurrent_agents=True,
        )
    with pytest.raises(ValueError, match="max_concurrent_agents"):
        run_project_session(
            sess,
            repo_root=tmp_path,
            max_steps=5,
            mode="baseline",
            max_concurrent_agents=0,
        )
