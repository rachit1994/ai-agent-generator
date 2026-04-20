"""§10.M — ``run_end`` ``orchestration.jsonl`` line (success path)."""

from __future__ import annotations

from workflow_pipelines.orchestration_run_end.orchestration_run_end_contract import (
    ORCHESTRATION_RUN_END_CONTRACT,
    validate_orchestration_run_end_dict,
)


def test_orchestration_run_end_contract_id() -> None:
    assert ORCHESTRATION_RUN_END_CONTRACT == "sde.orchestration_run_end.v1"


def test_validate_run_end_ok() -> None:
    body = {
        "run_id": "r-1",
        "type": "run_end",
        "artifacts": {"answer_txt": "/tmp/answer.txt"},
        "output_refusal": None,
        "checks": [{"name": "c", "passed": True}],
    }
    assert validate_orchestration_run_end_dict(body) == []


def test_validate_run_end_ok_minimal_checks_absent() -> None:
    body = {
        "run_id": "r-2",
        "type": "run_end",
        "artifacts": {"k": "/p"},
        "output_refusal": None,
        "checks": None,
    }
    assert validate_orchestration_run_end_dict(body) == []


def test_validate_run_end_unknown_key() -> None:
    body = {
        "run_id": "r",
        "type": "run_end",
        "artifacts": {"k": "/p"},
        "mode": "baseline",
    }
    assert "orchestration_run_end_unknown_keys" in validate_orchestration_run_end_dict(body)


def test_validate_run_end_bad_artifacts_value() -> None:
    body = {
        "run_id": "r",
        "type": "run_end",
        "artifacts": {"k": ""},
    }
    assert "orchestration_run_end_artifacts_value" in validate_orchestration_run_end_dict(body)


def test_validate_run_end_bad_output_refusal() -> None:
    body = {
        "run_id": "r",
        "type": "run_end",
        "artifacts": {"k": "/p"},
        "output_refusal": "no",
    }
    assert "orchestration_run_end_output_refusal" in validate_orchestration_run_end_dict(body)


def test_validate_run_end_bad_checks() -> None:
    body = {
        "run_id": "r",
        "type": "run_end",
        "artifacts": {"k": "/p"},
        "checks": {},
    }
    assert "orchestration_run_end_checks" in validate_orchestration_run_end_dict(body)
