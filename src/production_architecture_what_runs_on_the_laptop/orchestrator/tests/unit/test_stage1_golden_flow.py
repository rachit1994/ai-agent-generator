from __future__ import annotations

import json
from pathlib import Path

from orchestrator.api import (
    apply_intake_doc_review_result,
    scaffold_project_intake,
    validate_project_session,
    write_project_plan_lock,
)


def test_stage1_golden_scaffold_revise_lock_validate(tmp_path: Path) -> None:
    session = tmp_path / "golden"
    session.mkdir()

    scaffold = scaffold_project_intake(
        session,
        goal="Ship Stage 1 intake golden path",
        repo_label="golden-repo",
    )
    assert scaffold["ok"] is True

    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "contract-intake",
                "phase": "planning",
                "title": "Lock contract",
                "description": "Define intake contract",
                "depends_on": [],
                "path_scope": [],
                "rollback_hint": "revert contract",
                "contract_step": True,
            },
            {
                "step_id": "impl-intake",
                "phase": "implementation",
                "title": "Implement intake",
                "description": "Implement Stage 1 intake handlers",
                "depends_on": ["contract-intake"],
                "path_scope": [],
                "rollback_hint": "revert implementation",
            },
        ],
    }
    (session / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")

    revise = apply_intake_doc_review_result(session, max_retries=2)
    assert revise["ok"] is True
    assert revise["state"] == "review_passed"

    lock = write_project_plan_lock(session)
    assert lock["ok"] is True
    assert lock["ready"] is True
    assert lock["locked"] is True

    validate = validate_project_session(
        session,
        repo_root=tmp_path,
        check_workspace=False,
        require_plan_lock=True,
    )
    assert validate["exit_code"] == 0
    assert validate["ok"] is True
    assert validate["step_count"] == 2


def test_stage1_golden_failure_retries_exhausted_blocks_lock_and_validate(tmp_path: Path) -> None:
    session = tmp_path / "golden-fail"
    session.mkdir()

    scaffold = scaffold_project_intake(
        session,
        goal="Stage 1 failure path",
        repo_label="golden-fail-repo",
    )
    assert scaffold["ok"] is True

    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "contract-intake",
                "phase": "planning",
                "title": "Lock contract",
                "description": "Define intake contract",
                "depends_on": [],
                "path_scope": [],
                "rollback_hint": "revert contract",
                "contract_step": True,
            },
            {
                "step_id": "impl-intake",
                "phase": "implementation",
                "title": "Implement intake",
                "description": "Implement Stage 1 intake handlers",
                "depends_on": ["contract-intake"],
                "path_scope": [],
                "rollback_hint": "revert implementation",
            },
        ],
    }
    (session / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")

    intake = session / "intake"
    bad_review = {"passed": False, "findings": [{"severity": "high", "issue": "missing requirement"}]}
    (intake / "doc_review.json").write_text(json.dumps(bad_review), encoding="utf-8")
    (intake / "planner_identity.json").write_text(
        json.dumps({"actor_id": "planner-a"}),
        encoding="utf-8",
    )

    revise1 = apply_intake_doc_review_result(session, max_retries=2)
    assert revise1["ok"] is True
    assert revise1["state"] == "retry_allowed"
    assert revise1["blocked_human"] is False

    revise2 = apply_intake_doc_review_result(session, max_retries=2)
    assert revise2["ok"] is True
    assert revise2["state"] == "blocked_human"
    assert revise2["blocked_human"] is True

    lock = write_project_plan_lock(session)
    assert lock["ok"] is True
    assert lock["ready"] is False
    assert lock["locked"] is False
    reasons = lock.get("reasons") or []
    assert "doc_review_not_passed" in reasons
    assert "revise_state_not_review_passed" in reasons
    assert "doc_review_reviewer_missing" in reasons

    validate = validate_project_session(
        session,
        repo_root=tmp_path,
        check_workspace=False,
        require_plan_lock=True,
    )
    assert validate["exit_code"] == 2
    assert validate["ok"] is False
    assert validate["error"] == "plan_lock_not_ready"
    assert "doc_review_not_passed" in (validate.get("details") or [])
