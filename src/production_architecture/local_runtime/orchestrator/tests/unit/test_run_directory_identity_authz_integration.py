from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory import (
    validate_execution_run_directory,
)


def _valid_review() -> dict[str, object]:
    return {
        "schema_version": "1.1",
        "run_id": "rid-1",
        "status": "completed_review_pass",
        "reasons": [],
        "required_fixes": [],
        "gate_snapshot": {},
        "artifact_manifest": [],
        "review_findings": [],
        "completed_at": "2026-01-01T00:00:00Z",
    }


def _baseline_dir(tmp_path: Path) -> Path:
    out = tmp_path / "run"
    (out / "iam").mkdir(parents=True)
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0", "stages": []}), encoding="utf-8")
    (out / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    return out


def test_run_directory_invalid_core_identity_authz_surfaces_prefixed_error(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "iam" / "identity_authz_plane.json").write_text(json.dumps({"schema": "bad"}), encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "identity_authz_plane_contract:identity_authz_plane_schema" in result["errors"]


def test_run_directory_invalid_production_identity_authz_surfaces_prefixed_error(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "iam" / "production_identity_authorization.json").write_text(
        json.dumps({"schema": "bad"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "production_identity_authorization_contract:production_identity_authorization_schema" in result["errors"]


def test_run_directory_identity_failure_does_not_fabricate_online_eval_failure(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "learning").mkdir(parents=True)
    (out / "iam" / "identity_authz_plane.json").write_text(json.dumps({"schema": "bad"}), encoding="utf-8")
    (out / "learning" / "online_evaluation_shadow_canary.json").write_text(
        json.dumps(
            {
                "schema": "sde.online_evaluation_shadow_canary.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "decision": {
                    "decision": "hold",
                    "failed_gates": ["min_sample"],
                    "decision_reasons": ["gate_min_sample_unmet"],
                    "min_sample_met": False,
                },
                "metrics": {
                    "sample_size": 0,
                    "coverage": 0.0,
                    "baseline_latency_p50_ms": 0.0,
                    "baseline_latency_p95_ms": 0.0,
                    "candidate_latency_p50_ms": 0.0,
                    "candidate_latency_p95_ms": 0.0,
                    "baseline_error_rate": 0.0,
                    "candidate_error_rate": 0.0,
                    "error_rate_delta": 0.0,
                    "latency_p95_delta_ms": 0.0,
                    "quality_delta": 0.0,
                },
                "evidence": {"online_eval_records_ref": "learning/online_eval_records.jsonl"},
            }
        ),
        encoding="utf-8",
    )
    (out / "learning" / "online_eval_records.jsonl").write_text("", encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "identity_authz_plane_contract:identity_authz_plane_schema" in result["errors"]
    assert not any(
        err.startswith("online_evaluation_shadow_canary_contract:") for err in result["errors"]
    )


def test_run_directory_rejects_missing_identity_evidence_files(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "iam" / "identity_authz_plane.json").write_text(
        json.dumps(
            {
                "schema": "sde.identity_authz_plane.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "status": "enforced",
                "controls": {
                    "permission_matrix_present": True,
                    "lease_bound_audit": True,
                    "high_risk_tokens_valid": True,
                    "authenticated_actor_audit": True,
                    "risk_scope_fields_present": True,
                },
                "coverage": 1.0,
                "evidence": {
                    "permission_matrix_ref": "iam/permission_matrix.json",
                    "action_audit_ref": "iam/action_audit.jsonl",
                    "lease_table_ref": "coordination/lease_table.json",
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "identity_authz_plane_contract:identity_authz_plane_evidence_ref:permission_matrix_ref_missing" in result[
        "errors"
    ]
    assert "identity_authz_plane_contract:identity_authz_plane_evidence_ref:action_audit_ref_missing" in result[
        "errors"
    ]
    assert "identity_authz_plane_contract:identity_authz_plane_evidence_ref:lease_table_ref_missing" in result[
        "errors"
    ]


def test_run_directory_rejects_missing_production_identity_evidence_files(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "iam" / "production_identity_authorization.json").write_text(
        json.dumps(
            {
                "schema": "sde.production_identity_authorization.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "status": "enforced",
                "controls": {
                    "permission_matrix_present": True,
                    "high_risk_approvals_valid": True,
                    "high_risk_dual_control_valid": True,
                    "strategy_self_approval_guarded": True,
                },
                "coverage": 1.0,
                "evidence": {
                    "permission_matrix_ref": "iam/permission_matrix.json",
                    "action_audit_ref": "iam/action_audit.jsonl",
                    "strategy_proposal_ref": "strategy/proposal.json",
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert (
        "production_identity_authorization_contract:"
        "production_identity_authorization_evidence_ref:permission_matrix_ref_missing"
    ) in result["errors"]
    assert (
        "production_identity_authorization_contract:"
        "production_identity_authorization_evidence_ref:action_audit_ref_missing"
    ) in result["errors"]
    assert (
        "production_identity_authorization_contract:"
        "production_identity_authorization_evidence_ref:strategy_proposal_ref_missing"
    ) in result["errors"]
