"""§10.E — ``run-manifest.json`` shape (single-task deterministic run anchor)."""

from __future__ import annotations

import json
from pathlib import Path

from workflow_pipelines.production_pipeline_task_to_promote.benchmark.run_manifest_contract import (
    RUN_MANIFEST_CONTRACT,
    validate_run_manifest_dict,
    validate_run_manifest_path,
)


def test_run_manifest_contract_id() -> None:
    assert RUN_MANIFEST_CONTRACT == "sde.run_manifest.v1"


def test_validate_run_manifest_ok() -> None:
    body = {
        "schema": RUN_MANIFEST_CONTRACT,
        "run_id": "r-1",
        "mode": "baseline",
        "task": "do the thing",
    }
    assert validate_run_manifest_dict(body) == []


def test_validate_run_manifest_with_project_fields_ok() -> None:
    body = {
        "schema": RUN_MANIFEST_CONTRACT,
        "run_id": "r-2",
        "mode": "guarded_pipeline",
        "task": "t",
        "project_step_id": "s1",
        "project_session_dir": "/tmp/sess",
    }
    assert validate_run_manifest_dict(body) == []


def test_validate_run_manifest_bad_schema() -> None:
    body = {
        "schema": "other",
        "run_id": "r",
        "mode": "baseline",
        "task": "t",
    }
    assert "run_manifest_schema" in validate_run_manifest_dict(body)


def test_validate_run_manifest_bad_mode() -> None:
    body = {
        "schema": RUN_MANIFEST_CONTRACT,
        "run_id": "r",
        "mode": "production",
        "task": "t",
    }
    assert "run_manifest_mode" in validate_run_manifest_dict(body)


def test_validate_run_manifest_blank_task() -> None:
    body = {
        "schema": RUN_MANIFEST_CONTRACT,
        "run_id": "r",
        "mode": "baseline",
        "task": "   ",
    }
    assert "run_manifest_task" in validate_run_manifest_dict(body)


def test_validate_run_manifest_project_step_id_present_but_blank() -> None:
    body = {
        "schema": RUN_MANIFEST_CONTRACT,
        "run_id": "r",
        "mode": "baseline",
        "task": "t",
        "project_step_id": "",
    }
    assert "run_manifest_project_step_id" in validate_run_manifest_dict(body)


def test_validate_run_manifest_path_ok(tmp_path: Path) -> None:
    p = tmp_path / "run-manifest.json"
    p.write_text(
        json.dumps(
            {
                "schema": RUN_MANIFEST_CONTRACT,
                "run_id": "rid",
                "mode": "phased_pipeline",
                "task": "hello",
            }
        ),
        encoding="utf-8",
    )
    assert validate_run_manifest_path(p) == []
