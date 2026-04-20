from __future__ import annotations

import json
from pathlib import Path

from orchestrator.api.project_aggregate import (
    write_project_definition_of_done,
    write_verification_aggregate,
)


def test_write_verification_aggregate_all_pass(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    vdir = sess / "verification"
    vdir.mkdir()
    (vdir / "a.json").write_text(
        json.dumps({"schema_version": "1.0", "step_id": "a", "passed": True, "commands": []}),
        encoding="utf-8",
    )
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "x", "depends_on": [], "path_scope": []},
        ],
    }
    agg = write_verification_aggregate(sess, plan)
    assert agg["all_steps_verification_passed"] is True
    assert agg["missing_step_bundles"] == []
    body = json.loads((sess / "verification_aggregate.json").read_text(encoding="utf-8"))
    assert body["steps"]["a"]["passed"] is True


def test_write_verification_aggregate_missing_file(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "x", "phase": "p", "title": "X", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    agg = write_verification_aggregate(sess, plan)
    assert agg["all_steps_verification_passed"] is False
    assert "x" in agg["missing_step_bundles"]


def test_write_project_definition_of_done_blocked(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "x", "depends_on": [], "path_scope": []},
        ],
    }
    dod = write_project_definition_of_done(
        sess,
        plan,
        completed_step_ids=[],
        driver_status="blocked_human",
        aggregate=write_verification_aggregate(sess, plan),
    )
    assert dod["all_required_passed"] is False
    assert dod["checks"][0]["passed"] is False
