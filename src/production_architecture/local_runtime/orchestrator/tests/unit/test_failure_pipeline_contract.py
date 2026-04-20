"""§10.D — ``replay_manifest.json`` + harness ``summary.json`` shapes (failure path contracts)."""

from __future__ import annotations

import json
from pathlib import Path

from workflow_pipelines.failure_path_artifacts.failure_pipeline_contract import (
    FAILURE_PIPELINE_SUMMARY_CONTRACT,
    REPLAY_MANIFEST_CONTRACT,
    validate_failure_summary_dict,
    validate_failure_summary_path,
    validate_replay_manifest_dict,
    validate_replay_manifest_path,
)


def test_replay_manifest_contract_id() -> None:
    assert REPLAY_MANIFEST_CONTRACT == "sde.replay_manifest.v1"


def test_failure_summary_contract_id() -> None:
    assert FAILURE_PIPELINE_SUMMARY_CONTRACT == "sde.failure_pipeline_summary.v1"


def test_validate_replay_manifest_minimal_hs18_shape_ok() -> None:
    body = {
        "schema_version": "1.0",
        "run_id": "r1",
        "contract_version": REPLAY_MANIFEST_CONTRACT,
        "sources": [{"path": "traces.jsonl", "sha256": "a" * 64}],
        "chain_root": "b" * 64,
    }
    assert validate_replay_manifest_dict(body) == []


def test_validate_replay_manifest_full_harness_optional_fields_ok() -> None:
    body = {
        "schema_version": "1.0",
        "run_id": "r1",
        "contract_version": REPLAY_MANIFEST_CONTRACT,
        "window": {"first_line": 1, "last_line": 3},
        "sources": [{"path": "traces.jsonl", "sha256": "c" * 64}],
        "chain_root": "d" * 64,
        "projection_version": "1.0",
        "passed": True,
        "built_at": "2026-01-01T00:00:00+00:00",
    }
    assert validate_replay_manifest_dict(body) == []


def test_validate_replay_manifest_wrong_contract() -> None:
    body = {
        "schema_version": "1.0",
        "run_id": "r1",
        "contract_version": "other",
        "sources": [{"path": "traces.jsonl", "sha256": "e" * 64}],
        "chain_root": "f" * 64,
    }
    assert "replay_manifest_contract_version" in validate_replay_manifest_dict(body)


def test_validate_replay_manifest_rejects_non_sha_hashes() -> None:
    body = {
        "schema_version": "1.0",
        "run_id": "r1",
        "contract_version": REPLAY_MANIFEST_CONTRACT,
        "sources": [{"path": "traces.jsonl", "sha256": "bad"}],
        "chain_root": "not-a-sha",
    }
    errs = validate_replay_manifest_dict(body)
    assert "replay_manifest_source_sha256:0" in errs
    assert "replay_manifest_chain_root" in errs


def test_validate_replay_manifest_bad_passed_type_when_present() -> None:
    body = {
        "schema_version": "1.0",
        "run_id": "r1",
        "contract_version": REPLAY_MANIFEST_CONTRACT,
        "sources": [{"path": "traces.jsonl", "sha256": "a" * 64}],
        "chain_root": "b" * 64,
        "passed": "yes",
    }
    assert "replay_manifest_passed_type" in validate_replay_manifest_dict(body)


def test_validate_replay_manifest_path_ok(tmp_path: Path) -> None:
    p = tmp_path / "replay_manifest.json"
    p.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "r1",
                "contract_version": REPLAY_MANIFEST_CONTRACT,
                "sources": [{"path": "traces.jsonl", "sha256": "a" * 64}],
                "chain_root": "b" * 64,
            }
        ),
        encoding="utf-8",
    )
    assert validate_replay_manifest_path(p) == []


def test_validate_replay_manifest_path_missing(tmp_path: Path) -> None:
    assert validate_replay_manifest_path(tmp_path / "missing.json") == ["replay_manifest_file_missing"]


def test_validate_failure_summary_ok() -> None:
    body = {
        "runId": "r1",
        "mode": "baseline",
        "runStatus": "failed",
        "partial": False,
        "error": {"type": "RuntimeError", "message": "boom"},
        "provider": "p",
        "model": "m",
    }
    assert validate_failure_summary_dict(body) == []


def test_validate_failure_summary_not_failed() -> None:
    body = {
        "runId": "r1",
        "mode": "baseline",
        "runStatus": "ok",
        "partial": False,
        "error": {"type": "X", "message": "m"},
        "provider": "p",
        "model": "m",
    }
    assert "failure_summary_run_status" in validate_failure_summary_dict(body)


def test_validate_failure_summary_rejects_blank_message() -> None:
    body = {
        "runId": "r1",
        "mode": "baseline",
        "runStatus": "failed",
        "partial": False,
        "error": {"type": "RuntimeError", "message": " "},
        "provider": "p",
        "model": "m",
    }
    assert "failure_summary_error_message_type" in validate_failure_summary_dict(body)


def test_validate_failure_summary_path_ok(tmp_path: Path) -> None:
    p = tmp_path / "summary.json"
    p.write_text(
        json.dumps(
            {
                "runId": "r1",
                "mode": "baseline",
                "runStatus": "failed",
                "partial": True,
                "error": {"type": "ValueError", "message": "x"},
                "provider": "openai",
                "model": "gpt",
            }
        ),
        encoding="utf-8",
    )
    assert validate_failure_summary_path(p) == []
