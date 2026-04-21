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
    (out / "program").mkdir(parents=True)
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0", "stages": []}), encoding="utf-8")
    (out / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    return out


def test_run_directory_surfaces_policy_bundle_invalid_json(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "program" / "policy_bundle_rollback.json").write_text("{", encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "policy_bundle_rollback_invalid_json" in result["errors"]


def test_run_directory_accepts_valid_atomic_policy_bundle(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "program" / "policy_bundle_rollback.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "rolled_back_atomic",
                "previous_policy_sha256": "0" * 64,
                "current_policy_sha256": "f" * 64,
                "paths_touched": ["program/project_plan.json"],
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
    assert not any(err.startswith("policy_bundle_rollback_") for err in result["errors"])


def test_run_directory_surfaces_invalid_rollback_rules_policy_bundle_contract(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "program" / "rollback_rules_policy_bundle.json").write_text(
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
    assert "rollback_rules_policy_bundle_contract:rollback_rules_policy_bundle_schema" in result["errors"]


def test_run_directory_requires_derived_artifact_even_without_source_rollback(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "rollback_rules_policy_bundle_contract:rollback_rules_policy_bundle_file_missing" in result["errors"]


def test_run_directory_requires_derived_artifact_when_source_rollback_present(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "program" / "policy_bundle_rollback.json").write_text(
        json.dumps({"schema_version": "1.0", "status": "none"}),
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
    assert "rollback_rules_policy_bundle_contract:rollback_rules_policy_bundle_file_missing" in result["errors"]


def test_run_directory_surfaces_atomic_source_vs_derived_mismatch(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "program" / "policy_bundle_rollback.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "rolled_back_atomic",
                "previous_policy_sha256": "0" * 64,
                "current_policy_sha256": "f" * 64,
                "paths_touched": ["program/project_plan.json"],
            }
        ),
        encoding="utf-8",
    )
    (out / "program" / "rollback_rules_policy_bundle.json").write_text(
        json.dumps(
            {
                "schema": "sde.rollback_rules_policy_bundle.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "status": "none",
                "rollback_checks": {
                    "record_present": True,
                    "schema_valid": True,
                    "atomic_sha_change": False,
                    "paths_touched_valid": False,
                },
                "evidence": {
                    "policy_bundle_rollback_ref": "program/policy_bundle_rollback.json",
                    "rollback_rules_policy_bundle_ref": "program/rollback_rules_policy_bundle.json",
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
    assert "rollback_rules_policy_bundle_source_atomic_checks_failed" in result["errors"]
