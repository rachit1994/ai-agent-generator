"""§11.E policy bundle rollback record validated by ``validate_execution_run_directory``."""

from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.rollback_rules_policy_bundle.policy_bundle_rollback import validate_policy_bundle_rollback


def test_validate_skips_when_file_absent(tmp_path: Path) -> None:
    assert validate_policy_bundle_rollback(tmp_path) == []


def test_validate_none_status_ok(tmp_path: Path) -> None:
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "policy_bundle_rollback.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "none",
                "paths_touched": [],
            }
        ),
        encoding="utf-8",
    )
    assert validate_policy_bundle_rollback(tmp_path) == []


def test_validate_atomic_requires_shas_and_paths(tmp_path: Path) -> None:
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "policy_bundle_rollback.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "rolled_back_atomic",
                "previous_policy_sha256": "x",
                "current_policy_sha256": "y",
                "paths_touched": [],
            }
        ),
        encoding="utf-8",
    )
    errs = validate_policy_bundle_rollback(tmp_path)
    assert "policy_bundle_rollback_sha256_invalid" in errs


def test_validate_atomic_ok(tmp_path: Path) -> None:
    z = "0" * 64
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "policy_bundle_rollback.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "rolled_back_atomic",
                "previous_policy_sha256": z,
                "current_policy_sha256": "f" * 64,
                "paths_touched": ["program/project_plan.json"],
            }
        ),
        encoding="utf-8",
    )
    assert validate_policy_bundle_rollback(tmp_path) == []
