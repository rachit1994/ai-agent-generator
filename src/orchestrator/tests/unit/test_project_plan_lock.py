from __future__ import annotations

import json
from pathlib import Path

from orchestrator.api import (
    evaluate_project_plan_lock_readiness,
    write_intake_lineage_manifest,
    write_project_plan_lock,
)
from orchestrator.api.project_plan_lock import lineage_manifest_session_event_snapshot


def _ready_session(tmp_path: Path) -> Path:
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
            {
                "step_id": "impl-a",
                "phase": "implementation",
                "title": "Implement",
                "description": "build feature",
                "depends_on": ["contract-a"],
                "path_scope": [],
                "rollback_hint": "revert impl",
            },
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    return sess


def test_evaluate_project_plan_lock_readiness_ready(tmp_path: Path) -> None:
    sess = _ready_session(tmp_path)
    lineage = write_intake_lineage_manifest(sess)
    assert lineage["ok"] is True
    out = evaluate_project_plan_lock_readiness(sess)
    assert out["ok"] is True
    assert out["ready"] is True
    assert out["reasons"] == []
    ps = out.get("reviewer_proof_summary") or {}
    assert ps.get("attestation_type") == "local_stub"
    assert ps.get("attestation_type_allowed") is True
    assert ps.get("attestation_policy_ok") is True
    assert ps.get("reviewer_matches_doc_review") is True
    assert ps.get("reviewer_differs_from_planner") is True


def test_evaluate_project_plan_lock_readiness_not_ready(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text(json.dumps({"schema_version": "1.0", "steps": []}), encoding="utf-8")
    out = evaluate_project_plan_lock_readiness(sess)
    assert out["ok"] is True
    assert out["ready"] is False
    assert "intake_dir_missing" in out["reasons"]


def test_write_project_plan_lock_writes_locked_true_when_ready(tmp_path: Path) -> None:
    sess = _ready_session(tmp_path)
    out = write_project_plan_lock(sess)
    assert out["ok"] is True
    assert out["ready"] is True
    assert out["locked"] is True
    lock = json.loads((sess / "project_plan_lock.json").read_text(encoding="utf-8"))
    assert lock["locked"] is True
    assert lock["ready"] is True
    assert lock["allow_local_stub_attestation"] is True
    ps = lock.get("reviewer_proof_summary") or {}
    assert ps.get("attestation_type") == "local_stub"
    assert ps.get("reviewer_matches_doc_review") is True


def test_evaluate_project_plan_lock_readiness_lineage_drift_detected(tmp_path: Path) -> None:
    sess = _ready_session(tmp_path)
    lineage = write_intake_lineage_manifest(sess)
    assert lineage["ok"] is True
    intake = sess / "intake"
    (intake / "research_digest.md").write_text("# changed digest\n", encoding="utf-8")
    out = evaluate_project_plan_lock_readiness(sess)
    assert out["ready"] is False
    assert "lineage_hash_mismatch:intake/research_digest.md" in out["reasons"]


def test_evaluate_project_plan_lock_reviewer_identity_must_differ(tmp_path: Path) -> None:
    sess = _ready_session(tmp_path)
    intake = sess / "intake"
    (intake / "doc_review.json").write_text(
        json.dumps({"passed": True, "findings": [], "reviewer": "planner-a"}),
        encoding="utf-8",
    )
    (intake / "planner_identity.json").write_text(
        json.dumps({"actor_id": "planner-a"}),
        encoding="utf-8",
    )
    (intake / "reviewer_identity.json").write_text(
        json.dumps(
            {
                "actor_id": "planner-a",
                "role": "reviewer",
                "reviewed_at": "2035-01-01T00:00:00+00:00",
                "attestation_type": "local_stub",
                "attestation": "stub-proof",
            }
        ),
        encoding="utf-8",
    )
    out = evaluate_project_plan_lock_readiness(sess)
    assert out["ready"] is False
    assert "reviewer_matches_planner_identity" in out["reasons"]


def test_evaluate_project_plan_lock_reviewer_identity_must_match_doc_review(tmp_path: Path) -> None:
    sess = _ready_session(tmp_path)
    intake = sess / "intake"
    (intake / "reviewer_identity.json").write_text(
        json.dumps(
            {
                "actor_id": "reviewer-b",
                "role": "reviewer",
                "reviewed_at": "2035-01-01T00:00:00+00:00",
                "attestation_type": "local_stub",
                "attestation": "stub-proof",
            }
        ),
        encoding="utf-8",
    )
    out = evaluate_project_plan_lock_readiness(sess)
    assert out["ready"] is False
    assert "doc_review_reviewer_identity_mismatch" in out["reasons"]


def test_evaluate_project_plan_lock_reviewer_identity_attestation_required(tmp_path: Path) -> None:
    sess = _ready_session(tmp_path)
    intake = sess / "intake"
    (intake / "reviewer_identity.json").write_text(
        json.dumps({"actor_id": "reviewer-a", "role": "reviewer"}),
        encoding="utf-8",
    )
    out = evaluate_project_plan_lock_readiness(sess)
    assert out["ready"] is False
    assert "reviewer_identity_attestation_type_missing" in out["reasons"]
    assert "reviewer_identity_attestation_missing" in out["reasons"]
    assert "reviewer_identity_reviewed_at_missing" in out["reasons"]


def test_evaluate_project_plan_lock_reviewer_attestation_type_allowlist(tmp_path: Path) -> None:
    sess = _ready_session(tmp_path)
    intake = sess / "intake"
    (intake / "reviewer_identity.json").write_text(
        json.dumps(
            {
                "actor_id": "reviewer-a",
                "role": "reviewer",
                "reviewed_at": "2035-01-01T00:00:00+00:00",
                "attestation_type": "random_custom_type",
                "attestation": "stub-proof",
            }
        ),
        encoding="utf-8",
    )
    out = evaluate_project_plan_lock_readiness(sess)
    assert out["ready"] is False
    assert "reviewer_identity_attestation_type_invalid" in out["reasons"]
    ps = out.get("reviewer_proof_summary") or {}
    assert ps.get("attestation_type") == "random_custom_type"
    assert ps.get("attestation_type_allowed") is False


def test_evaluate_project_plan_lock_can_disallow_local_stub_attestation(tmp_path: Path) -> None:
    sess = _ready_session(tmp_path)
    lineage = write_intake_lineage_manifest(sess)
    assert lineage["ok"] is True
    out = evaluate_project_plan_lock_readiness(
        sess,
        allow_local_stub_attestation=False,
    )
    assert out["ready"] is False
    assert "reviewer_identity_attestation_stub_disallowed" in out["reasons"]
    ps = out.get("reviewer_proof_summary") or {}
    assert ps.get("attestation_type") == "local_stub"
    assert ps.get("attestation_type_allowed") is True
    assert ps.get("local_stub_allowed") is False
    assert ps.get("attestation_policy_ok") is False


def test_write_project_plan_lock_persists_non_stub_policy(tmp_path: Path) -> None:
    sess = _ready_session(tmp_path)
    out = write_project_plan_lock(
        sess,
        allow_local_stub_attestation=False,
    )
    assert out["ready"] is False
    assert "reviewer_identity_attestation_stub_disallowed" in out["reasons"]
    lock = json.loads((sess / "project_plan_lock.json").read_text(encoding="utf-8"))
    assert lock["allow_local_stub_attestation"] is False
    ps = lock.get("reviewer_proof_summary") or {}
    assert ps.get("attestation_policy_ok") is False


def test_evaluate_project_plan_lock_reviewed_at_skew_enforced(tmp_path: Path) -> None:
    sess = _ready_session(tmp_path)
    intake = sess / "intake"
    (intake / "reviewer_identity.json").write_text(
        json.dumps(
            {
                "actor_id": "reviewer-a",
                "role": "reviewer",
                "reviewed_at": "2035-01-01T00:20:00+00:00",
                "attestation_type": "local_stub",
                "attestation": "stub-proof",
            }
        ),
        encoding="utf-8",
    )
    out = evaluate_project_plan_lock_readiness(sess)
    assert out["ready"] is False
    assert "reviewed_at_mismatch_exceeds_skew" in out["reasons"]


def test_evaluate_project_plan_lock_doc_review_reviewed_at_required(tmp_path: Path) -> None:
    sess = _ready_session(tmp_path)
    intake = sess / "intake"
    (intake / "doc_review.json").write_text(
        json.dumps({"passed": True, "findings": [], "reviewer": "reviewer-a"}),
        encoding="utf-8",
    )
    out = evaluate_project_plan_lock_readiness(sess)
    assert out["ready"] is False
    assert "doc_review_reviewed_at_missing_or_invalid" in out["reasons"]


def test_lineage_manifest_session_event_snapshot_absent(tmp_path: Path) -> None:
    sess = tmp_path / "empty"
    sess.mkdir()
    snap = lineage_manifest_session_event_snapshot(sess)
    assert snap == {"intake_lineage_manifest_present": False}


def test_lineage_manifest_session_event_snapshot_present(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    intake = sess / "intake"
    intake.mkdir(parents=True)
    body = {
        "schema_version": "1.0",
        "created_at": "2035-01-01T00:00:00+00:00",
        "artifacts": {"intake/discovery.json": "abc"},
    }
    (intake / "lineage_manifest.json").write_text(json.dumps(body), encoding="utf-8")
    snap = lineage_manifest_session_event_snapshot(sess)
    assert snap["intake_lineage_manifest_present"] is True
    assert snap["intake_lineage_manifest_schema_version"] == "1.0"
    assert snap["intake_lineage_manifest_artifact_count"] == 1
    assert snap["intake_lineage_manifest_created_at"] == "2035-01-01T00:00:00+00:00"
    assert isinstance(snap.get("intake_lineage_manifest_file_sha256"), str)
    assert len(snap["intake_lineage_manifest_file_sha256"]) == 64


def test_lineage_manifest_session_event_snapshot_unreadable(tmp_path: Path) -> None:
    sess = tmp_path / "s2"
    intake = sess / "intake"
    intake.mkdir(parents=True)
    (intake / "lineage_manifest.json").write_text("{", encoding="utf-8")
    snap = lineage_manifest_session_event_snapshot(sess)
    assert snap["intake_lineage_manifest_present"] is False
    assert snap.get("intake_lineage_manifest_unreadable") is True
