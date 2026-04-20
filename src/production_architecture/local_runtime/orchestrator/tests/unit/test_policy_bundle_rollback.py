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


def test_validate_invalid_json(tmp_path: Path) -> None:
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "policy_bundle_rollback.json").write_text("{", encoding="utf-8")
    assert validate_policy_bundle_rollback(tmp_path) == ["policy_bundle_rollback_invalid_json"]


def test_validate_non_object_json(tmp_path: Path) -> None:
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "policy_bundle_rollback.json").write_text("[]", encoding="utf-8")
    assert validate_policy_bundle_rollback(tmp_path) == ["policy_bundle_rollback_json_not_object"]


def test_validate_schema_version_error(tmp_path: Path) -> None:
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "policy_bundle_rollback.json").write_text(
        json.dumps({"schema_version": "2.0", "status": "none"}),
        encoding="utf-8",
    )
    assert validate_policy_bundle_rollback(tmp_path) == ["policy_bundle_rollback_schema_version"]


def test_validate_invalid_status(tmp_path: Path) -> None:
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "policy_bundle_rollback.json").write_text(
        json.dumps({"schema_version": "1.0", "status": "bad"}),
        encoding="utf-8",
    )
    assert validate_policy_bundle_rollback(tmp_path) == ["policy_bundle_rollback_status_invalid"]


def test_validate_atomic_requires_non_empty_paths(tmp_path: Path) -> None:
    z = "0" * 64
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "policy_bundle_rollback.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "rolled_back_atomic",
                "previous_policy_sha256": z,
                "current_policy_sha256": "f" * 64,
                "paths_touched": [],
            }
        ),
        encoding="utf-8",
    )
    errs = validate_policy_bundle_rollback(tmp_path)
    assert "policy_bundle_rollback_paths_touched_required" in errs


def test_validate_atomic_rejects_blank_paths_and_duplicate_paths(tmp_path: Path) -> None:
    z = "0" * 64
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "policy_bundle_rollback.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "rolled_back_atomic",
                "previous_policy_sha256": z,
                "current_policy_sha256": "f" * 64,
                "paths_touched": ["", "program/a.json", "program/a.json"],
            }
        ),
        encoding="utf-8",
    )
    errs = validate_policy_bundle_rollback(tmp_path)
    assert "policy_bundle_rollback_paths_touched_invalid" in errs
    assert "policy_bundle_rollback_paths_touched_duplicates" in errs


def test_validate_atomic_requires_sha_change(tmp_path: Path) -> None:
    z = "0" * 64
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "policy_bundle_rollback.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "rolled_back_atomic",
                "previous_policy_sha256": z,
                "current_policy_sha256": z,
                "paths_touched": ["program/project_plan.json"],
            }
        ),
        encoding="utf-8",
    )
    errs = validate_policy_bundle_rollback(tmp_path)
    assert "policy_bundle_rollback_sha256_must_change" in errs


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
