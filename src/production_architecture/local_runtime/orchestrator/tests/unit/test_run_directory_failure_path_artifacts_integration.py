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


def test_run_directory_surfaces_invalid_failure_path_artifacts_contract(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "replay").mkdir(parents=True, exist_ok=True)
    (out / "replay" / "failure_path_artifacts.json").write_text(
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
    assert "failure_path_artifacts_contract:failure_path_artifacts_schema" in result["errors"]


def test_run_directory_surfaces_invalid_failure_path_artifacts_evidence_refs(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "replay").mkdir(parents=True, exist_ok=True)
    (out / "replay" / "failure_path_artifacts.json").write_text(
        json.dumps(
            {
                "schema": "sde.failure_path_artifacts.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "status": "failed",
                "checks": {
                    "summary_present": True,
                    "summary_contract_valid": False,
                    "replay_manifest_present": True,
                    "replay_manifest_contract_valid": True,
                },
                "evidence": {
                    "summary_ref": "../summary.json",
                    "replay_manifest_ref": "replay_manifest.json",
                    "failure_path_artifacts_ref": "replay/failure_path_artifacts.json",
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
        "failure_path_artifacts_contract:failure_path_artifacts_evidence_ref:summary_ref"
        in result["errors"]
    )


def test_run_directory_surfaces_missing_failure_path_artifacts_summary_ref_file(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "replay").mkdir(parents=True, exist_ok=True)
    (out / "replay_manifest.json").write_text("{}", encoding="utf-8")
    (out / "replay" / "failure_path_artifacts.json").write_text(
        json.dumps(
            {
                "schema": "sde.failure_path_artifacts.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "status": "failed",
                "checks": {
                    "summary_present": False,
                    "summary_contract_valid": False,
                    "replay_manifest_present": True,
                    "replay_manifest_contract_valid": True,
                },
                "evidence": {
                    "summary_ref": "summary.json",
                    "replay_manifest_ref": "replay_manifest.json",
                    "failure_path_artifacts_ref": "replay/failure_path_artifacts.json",
                },
            }
        ),
        encoding="utf-8",
    )
    (out / "summary.json").unlink()
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
        "failure_path_artifacts_contract:failure_path_artifacts_evidence_ref:summary_ref_missing"
        in result["errors"]
    )


def test_run_directory_surfaces_failure_path_artifacts_run_id_mismatch(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "replay").mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "runId": "rid-summary",
                "mode": "baseline",
                "runStatus": "failed",
                "partial": True,
                "error": {"type": "x", "message": "y"},
                "provider": "p",
                "model": "m",
            }
        ),
        encoding="utf-8",
    )
    (out / "replay_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "rid-replay",
                "contract_version": "sde.replay_manifest.v1",
                "sources": [{"path": "summary.json", "sha256": "0" * 64}],
                "chain_root": "f" * 64,
            }
        ),
        encoding="utf-8",
    )
    (out / "replay" / "failure_path_artifacts.json").write_text(
        json.dumps(
            {
                "schema": "sde.failure_path_artifacts.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "status": "partial_failure",
                "checks": {
                    "summary_present": True,
                    "summary_contract_valid": True,
                    "replay_manifest_present": True,
                    "replay_manifest_contract_valid": True,
                },
                "evidence": {
                    "summary_ref": "summary.json",
                    "replay_manifest_ref": "replay_manifest.json",
                    "failure_path_artifacts_ref": "replay/failure_path_artifacts.json",
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
    assert "failure_path_artifacts_contract:failure_path_artifacts_run_id_mismatch:summary" in result["errors"]
    assert (
        "failure_path_artifacts_contract:failure_path_artifacts_run_id_mismatch:replay_manifest"
        in result["errors"]
    )
