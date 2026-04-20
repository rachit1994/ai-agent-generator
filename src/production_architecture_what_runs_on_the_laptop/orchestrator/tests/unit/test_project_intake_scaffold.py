from __future__ import annotations

import json
from pathlib import Path

from orchestrator.api import scaffold_project_intake
from orchestrator.runtime.cli.main import build_parser


def test_scaffold_project_intake_writes_intake_dir(tmp_path: Path) -> None:
    session = tmp_path / "sess"
    session.mkdir()
    out = scaffold_project_intake(session, goal="ship feature X", repo_label="demo-repo")
    assert out["ok"] is True
    intake = session / "intake"
    assert (intake / "discovery.json").is_file()
    assert (intake / "planner_identity.json").is_file()
    assert (intake / "reviewer_identity.json").is_file()
    disc = json.loads((intake / "discovery.json").read_text(encoding="utf-8"))
    assert disc["goal_excerpt"] == "ship feature X"
    assert disc["repo_id"] == "demo-repo"
    assert (intake / "research_digest.md").is_file()
    assert (intake / "doc_review.json").is_file()
    assert (intake / "question_workbook.jsonl").is_file()
    assert (intake / "README.txt").is_file()


def test_scaffold_project_intake_rejects_empty_goal(tmp_path: Path) -> None:
    session = tmp_path / "sess2"
    session.mkdir()
    out = scaffold_project_intake(session, goal="   ")
    assert out["ok"] is False
    assert out["error"] == "goal_empty"


def test_scaffold_project_intake_rejects_missing_dir(tmp_path: Path) -> None:
    missing = tmp_path / "nope"
    out = scaffold_project_intake(missing, goal="x")
    assert out["ok"] is False
    assert out["error"] == "session_dir_not_a_directory"


def test_cli_project_scaffold_intake_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "scaffold-intake",
            "--session-dir",
            "/tmp/sde-session",
            "--goal",
            "hello",
            "--repo-label",
            "acme",
        ]
    )
    assert args.command == "project"
    assert args.project_cmd == "scaffold-intake"
    assert args.intake_session_dir == "/tmp/sde-session"
    assert args.goal == "hello"
    assert args.repo_label == "acme"


def test_cli_project_intake_revise_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "intake-revise",
            "--session-dir",
            "/tmp/sde-session",
            "--max-retries",
            "3",
        ]
    )
    assert args.command == "project"
    assert args.project_cmd == "intake-revise"
    assert args.intake_session_dir == "/tmp/sde-session"
    assert args.max_retries == 3
