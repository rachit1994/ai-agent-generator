from __future__ import annotations

import subprocess
from pathlib import Path

from orchestrator.runtime.cli.main import build_parser


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _stage1_doc_path() -> Path:
    return _repo_root() / "docs" / "UNDERSTANDING-THE-CODE.md"


def test_stage1_runbook_exists_and_references_current_cli_surface() -> None:
    path = _stage1_doc_path()
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    required_snippets = [
        "sde project status --session-dir",
        "sde project export-stage1-observability",
        "./scripts/stage1-cold-start-demo.sh",
        "sde project validate --session-dir",
        "--require-plan-lock",
        "--require-non-stub-reviewer",
        "sde project plan-lock --session-dir",
        "sde project intake-revise --session-dir",
        "sde project run --session-dir",
        "--enforce-plan-lock",
        "project_plan_lock.json",
        "reviewer_proof_summary",
        "intake/revise_state.json",
        "STAGE1_SUITE_MAX_SECONDS",
        "SDE_REQUIRE_NON_STUB_REVIEWER",
        "sde continuous --project-session-dir",
    ]
    for snippet in required_snippets:
        assert snippet in body


def test_stage1_runbook_commands_parse_with_current_parser() -> None:
    parser = build_parser()
    status = parser.parse_args(["project", "status", "--session-dir", "/tmp/s"])
    assert status.project_cmd == "status"
    validate = parser.parse_args(
        [
            "project",
            "validate",
            "--session-dir",
            "/tmp/s",
            "--skip-workspace",
            "--require-plan-lock",
        ]
    )
    assert validate.project_cmd == "validate"
    assert validate.require_plan_lock is True
    plan_lock = parser.parse_args(
        [
            "project",
            "plan-lock",
            "--session-dir",
            "/tmp/s",
            "--check-only",
        ]
    )
    assert plan_lock.project_cmd == "plan-lock"
    intake_revise = parser.parse_args(
        [
            "project",
            "intake-revise",
            "--session-dir",
            "/tmp/s",
            "--max-retries",
            "2",
        ]
    )
    assert intake_revise.project_cmd == "intake-revise"
    project_run = parser.parse_args(
        [
            "project",
            "run",
            "--session-dir",
            "/tmp/s",
            "--mode",
            "guarded_pipeline",
            "--enforce-plan-lock",
        ]
    )
    assert project_run.project_cmd == "run"
    assert project_run.enforce_plan_lock is True
    project_run_strict = parser.parse_args(
        [
            "project",
            "run",
            "--session-dir",
            "/tmp/s",
            "--mode",
            "guarded_pipeline",
            "--enforce-plan-lock",
            "--require-non-stub-reviewer",
        ]
    )
    assert project_run_strict.require_non_stub_reviewer is True
    cont_strict = parser.parse_args(
        [
            "continuous",
            "--project-session-dir",
            "/tmp/p",
            "--repo-root",
            "/tmp/r",
            "--enforce-plan-lock",
            "--require-non-stub-reviewer",
        ]
    )
    assert cont_strict.enforce_plan_lock is True
    assert cont_strict.require_non_stub_reviewer is True
    export_obs = parser.parse_args(
        [
            "project",
            "export-stage1-observability",
            "--session-dir",
            "/tmp/s",
        ]
    )
    assert export_obs.project_cmd == "export-stage1-observability"


def test_version_index_only_script_exits_zero() -> None:
    root = _repo_root()
    proc = subprocess.run(
        ["bash", str(root / "scripts" / "version-index-only.sh")],
        cwd=str(root),
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr.decode()


def test_s1a_policy_surface_in_understanding_doc() -> None:
    body = _stage1_doc_path().read_text(encoding="utf-8")
    assert "SDE_REQUIRE_NON_STUB_REVIEWER" in body
    assert "reviewer_proof_summary" in body
