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
    inn = out.get("intake") or {}
    assert inn.get("intake_dir_present") is False
    assert inn.get("merge_anchor_present") is False
    assert inn.get("progress_intake_loaded_last") is None


def test_validate_project_session_intake_block_with_progress(tmp_path: Path) -> None:
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
    intake = sess / "intake"
    intake.mkdir()
    (intake / "discovery.json").write_text(json.dumps({"goal_excerpt": "g"}), encoding="utf-8")
    (sess / "progress.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "session_id": "s",
                "completed_step_ids": [],
                "pending_step_ids": ["a"],
                "failed_step_id": None,
                "blocked_reason": None,
                "last_run_id": None,
                "last_output_dir": None,
                "intake_loaded_last": True,
            }
        ),
        encoding="utf-8",
    )
    out = validate_project_session(sess, repo_root=tmp_path, check_workspace=False)
    assert out["exit_code"] == EXIT_VALIDATE_OK
    inn = out["intake"]
    assert inn["intake_dir_present"] is True
    assert inn["merge_anchor_present"] is True
    assert inn["progress_intake_loaded_last"] is True


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


def test_validate_project_session_rejects_invalid_doc_review_json(tmp_path: Path) -> None:
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
    intake = sess / "intake"
    intake.mkdir()
    (intake / "doc_review.json").write_text(
        json.dumps({"passed": "true", "findings": "bad"}),
        encoding="utf-8",
    )
    out = validate_project_session(sess, repo_root=tmp_path, check_workspace=False)
    assert out["exit_code"] == EXIT_VALIDATE_INVALID
    assert out["ok"] is False
    assert out["error"] == "invalid_doc_review_json"
    assert "doc_review_passed_not_bool" in out["details"]
    assert "doc_review_findings_bad_type" in out["details"]


def test_validate_project_session_require_plan_lock_not_ready(tmp_path: Path) -> None:
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
    out = validate_project_session(
        sess,
        repo_root=tmp_path,
        check_workspace=False,
        require_plan_lock=True,
    )
    assert out["exit_code"] == EXIT_VALIDATE_INVALID
    assert out["ok"] is False
    assert out["error"] == "plan_lock_not_ready"
    assert isinstance(out.get("details"), list)


def test_validate_project_session_require_non_stub_reviewer_enforced(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    intake = sess / "intake"
    intake.mkdir(parents=True)
    (intake / "discovery.json").write_text(
        json.dumps({"goal_excerpt": "ship x", "constraints": []}),
        encoding="utf-8",
    )
    (intake / "research_digest.md").write_text("# digest\n", encoding="utf-8")
    (intake / "question_workbook.jsonl").write_text(json.dumps({"id": "q1"}) + "\n", encoding="utf-8")
    (intake / "doc_review.json").write_text(
        json.dumps(
            {
                "passed": True,
                "findings": [],
                "reviewer": "reviewer-a",
                "reviewed_at": "2035-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    (intake / "planner_identity.json").write_text(
        json.dumps({"actor_id": "planner-a"}),
        encoding="utf-8",
    )
    (intake / "reviewer_identity.json").write_text(
        json.dumps(
            {
                "actor_id": "reviewer-a",
                "role": "reviewer",
                "reviewed_at": "2035-01-01T00:00:00+00:00",
                "attestation_type": "local_stub",
                "attestation": "stub-proof",
            }
        ),
        encoding="utf-8",
    )
    (intake / "revise_state.json").write_text(
        json.dumps({"status": "review_passed"}),
        encoding="utf-8",
    )
    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "contract-a",
                "phase": "planning",
                "title": "Contract step",
                "description": "define contract",
                "depends_on": [],
                "path_scope": [],
                "rollback_hint": "revert contract file",
                "contract_step": True,
            },
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    out = validate_project_session(
        sess,
        repo_root=tmp_path,
        check_workspace=False,
        require_plan_lock=True,
        require_non_stub_reviewer=True,
    )
    assert out["exit_code"] == EXIT_VALIDATE_INVALID
    assert out["ok"] is False
    assert out["error"] == "plan_lock_not_ready"
    details = out.get("details") or []
    assert "reviewer_identity_attestation_stub_disallowed" in details
