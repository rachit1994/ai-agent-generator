"""§13 offline eval: JSONL suite structural contract before ``validate_task_payload``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from workflow_pipelines.production_pipeline_task_to_promote.benchmark.offline_eval_contract import (
    OFFLINE_EVAL_SUITE_CONTRACT,
    validate_suite_document,
    validate_suite_jsonl,
)
from workflow_pipelines.production_pipeline_task_to_promote.benchmark.suite import read_suite


def test_offline_eval_contract_constant_is_stable() -> None:
    assert OFFLINE_EVAL_SUITE_CONTRACT == "sde.offline_eval_suite.v1"


def test_validate_suite_document_empty_fails() -> None:
    assert validate_suite_document("") == ["offline_eval_suite_empty"]
    assert validate_suite_document("\n\n") == ["offline_eval_suite_empty"]


def test_validate_suite_document_bad_json_line(tmp_path: Path) -> None:
    text = '{"taskId":"a","prompt":"x","difficulty":"medium"}\nnot-json\n'
    assert any("line_2_json" in e for e in validate_suite_document(text))


def test_validate_suite_jsonl_missing_file(tmp_path: Path) -> None:
    assert validate_suite_jsonl(tmp_path / "nope.jsonl") == ["offline_eval_suite_file_missing"]


def test_read_suite_raises_on_contract_violation(tmp_path: Path) -> None:
    p = tmp_path / "bad.jsonl"
    p.write_text(json.dumps({"taskId": "x", "prompt": "y"}), encoding="utf-8")
    with pytest.raises(ValueError, match="offline_eval_suite_contract"):
        read_suite(str(p))
