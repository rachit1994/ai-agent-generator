from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from orchestrator.runtime.cli.main import build_parser


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _runbook_path() -> Path:
    return _repo_root() / "docs" / "runbooks" / "stage1-intake-failures.md"


def test_stage1_runbook_exists_and_references_current_cli_surface() -> None:
    path = _runbook_path()
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


def test_generate_plans_index_only_does_not_touch_plan_files() -> None:
    root = _repo_root()
    story = root / "docs" / "versioning" / "plans" / "story-01-stage1-intake.md"
    assert story.is_file()
    before = story.read_bytes()
    proc = subprocess.run(
        [sys.executable, str(root / "docs" / "versioning" / "_generate_plans.py"), "--index-only"],
        cwd=str(root),
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr.decode()
    assert story.read_bytes() == before


def test_versioning_index_has_milestone_footer() -> None:
    index = _repo_root() / "docs" / "versioning" / "INDEX.md"
    assert index.is_file()
    body = index.read_text(encoding="utf-8")
    assert "## In-repo milestone pointers" in body
    assert "company-os-path-to-100-percent.md" in body
    assert "story-01-stage1-intake.md" in body


def test_s1a_adrs_exist_and_indexed() -> None:
    root = _repo_root()
    assert (root / "docs" / "adrs" / "README.md").is_file()
    assert (root / "docs" / "adrs" / "0001-s1a-reviewer-attestation-policy.md").is_file()
    assert (root / "docs" / "adrs" / "0002-s1a-model-assisted-revise-deferred.md").is_file()
    index = (root / "docs" / "adrs" / "README.md").read_text(encoding="utf-8")
    assert "0001-s1a-reviewer-attestation-policy.md" in index
    assert "0002-s1a-model-assisted-revise-deferred.md" in index
