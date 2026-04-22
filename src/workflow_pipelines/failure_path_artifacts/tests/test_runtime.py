from __future__ import annotations

from workflow_pipelines.failure_path_artifacts import (
    build_failure_path_artifacts,
    validate_failure_path_artifacts_dict,
)


def test_build_failure_path_artifacts_deterministic() -> None:
    summary = {
        "runId": "rid-fail",
        "mode": "baseline",
        "runStatus": "failed",
        "partial": False,
        "error": {"type": "RuntimeError", "message": "boom"},
        "provider": "p",
        "model": "m",
    }
    replay_manifest = {
        "schema_version": "1.0",
        "run_id": "rid-fail",
        "contract_version": "sde.replay_manifest.v1",
        "sources": [{"path": "traces.jsonl", "sha256": "a" * 64}],
        "chain_root": "b" * 64,
    }
    one = build_failure_path_artifacts(run_id="rid-fail", summary=summary, replay_manifest=replay_manifest)
    two = build_failure_path_artifacts(run_id="rid-fail", summary=summary, replay_manifest=replay_manifest)
    assert one == two
    assert one["status"] == "failed"
    assert validate_failure_path_artifacts_dict(one) == []


def test_validate_failure_path_artifacts_fail_closed() -> None:
    errs = validate_failure_path_artifacts_dict({"schema": "bad"})
    assert "failure_path_artifacts_schema" in errs
    assert "failure_path_artifacts_schema_version" in errs


def test_build_failure_path_artifacts_fails_closed_when_summary_or_replay_invalid() -> None:
    payload = build_failure_path_artifacts(
        run_id="rid-fail",
        summary={"runStatus": "ok"},
        replay_manifest={},
    )
    assert payload["status"] == "failed"
    assert payload["checks"]["summary_contract_valid"] is False
    assert payload["checks"]["replay_manifest_contract_valid"] is False


def test_validate_failure_path_artifacts_rejects_ok_status_when_contract_checks_fail() -> None:
    payload = {
        "schema": "sde.failure_path_artifacts.v1",
        "schema_version": "1.0",
        "run_id": "rid",
        "status": "ok",
        "checks": {
            "summary_present": True,
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
    errs = validate_failure_path_artifacts_dict(payload)
    assert "failure_path_artifacts_status_ok_requires_valid_contracts" in errs


def test_validate_failure_path_artifacts_rejects_missing_evidence() -> None:
    payload = {
        "schema": "sde.failure_path_artifacts.v1",
        "schema_version": "1.0",
        "run_id": "rid",
        "status": "failed",
        "checks": {
            "summary_present": True,
            "summary_contract_valid": False,
            "replay_manifest_present": True,
            "replay_manifest_contract_valid": True,
        },
    }
    errs = validate_failure_path_artifacts_dict(payload)
    assert "failure_path_artifacts_evidence" in errs


def test_validate_failure_path_artifacts_rejects_bad_evidence_refs() -> None:
    payload = {
        "schema": "sde.failure_path_artifacts.v1",
        "schema_version": "1.0",
        "run_id": "rid",
        "status": "failed",
        "checks": {
            "summary_present": True,
            "summary_contract_valid": False,
            "replay_manifest_present": True,
            "replay_manifest_contract_valid": True,
        },
        "evidence": {
            "summary_ref": "../summary.json",
            "replay_manifest_ref": "/tmp/replay_manifest.json",
            "failure_path_artifacts_ref": "replay/other.json",
        },
    }
    errs = validate_failure_path_artifacts_dict(payload)
    assert "failure_path_artifacts_evidence_ref:summary_ref" in errs
    assert "failure_path_artifacts_evidence_ref:replay_manifest_ref" in errs
    assert "failure_path_artifacts_evidence_ref:failure_path_artifacts_ref" in errs
