"""OSV-STORY-01 B4: structured Stage 1 observability export schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from orchestrator.api.project_stage1_observability_export import (
    STAGE1_OBSERVABILITY_EXPORT_KIND,
    STAGE1_OBSERVABILITY_EXPORT_SCHEMA_VERSION,
    build_project_stage1_observability_export,
    stage1_observability_export_schema_errors,
    write_project_stage1_observability_export,
)
from orchestrator.runtime.cli.main import build_parser, main


def test_stage1_observability_export_schema_errors_empty_for_built_export(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "steps": [
                    {
                        "step_id": "a",
                        "phase": "p",
                        "title": "A",
                        "description": "d",
                        "depends_on": [],
                        "path_scope": [],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    body = build_project_stage1_observability_export(sess, repo_root=tmp_path)
    assert stage1_observability_export_schema_errors(body) == []
    assert body["schema_version"] == STAGE1_OBSERVABILITY_EXPORT_SCHEMA_VERSION
    assert body["kind"] == STAGE1_OBSERVABILITY_EXPORT_KIND


def test_stage1_observability_export_schema_errors_detect_invalid(tmp_path: Path) -> None:
    assert stage1_observability_export_schema_errors([]) == ["root_not_object"]
    assert "schema_version_invalid" in stage1_observability_export_schema_errors({"kind": STAGE1_OBSERVABILITY_EXPORT_KIND})
    assert "kind_invalid" in stage1_observability_export_schema_errors({"schema_version": "1.0"})
    assert "captured_at_invalid" in stage1_observability_export_schema_errors(
        {
            "schema_version": STAGE1_OBSERVABILITY_EXPORT_SCHEMA_VERSION,
            "kind": STAGE1_OBSERVABILITY_EXPORT_KIND,
            "captured_at": "",
            "session_dir": str(tmp_path),
            "revise_metrics": {},
            "status_at_a_glance": {},
        }
    )
    assert "revise_metrics_invalid" in stage1_observability_export_schema_errors(
        {
            "schema_version": STAGE1_OBSERVABILITY_EXPORT_SCHEMA_VERSION,
            "kind": STAGE1_OBSERVABILITY_EXPORT_KIND,
            "captured_at": "2035-01-01T00:00:00+00:00",
            "session_dir": str(tmp_path),
            "revise_metrics": None,
            "status_at_a_glance": {},
        }
    )


def test_write_project_stage1_observability_export_roundtrip(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    intake = sess / "intake"
    intake.mkdir()
    (intake / "doc_review.json").write_text(
        json.dumps({"passed": True, "findings": []}),
        encoding="utf-8",
    )
    from orchestrator.api import apply_intake_doc_review_result

    apply_intake_doc_review_result(sess, max_retries=2)
    custom = tmp_path / "out.json"
    out = write_project_stage1_observability_export(sess, output_path=custom, repo_root=tmp_path)
    assert out["ok"] is True
    assert out["path"] == str(custom.resolve())
    loaded = json.loads(custom.read_text(encoding="utf-8"))
    assert stage1_observability_export_schema_errors(loaded) == []
    assert loaded["revise_metrics"].get("present") is True


def test_cli_export_stage1_observability_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "export-stage1-observability",
            "--session-dir",
            "/tmp/s",
            "--output",
            "/tmp/m.json",
        ]
    )
    assert args.project_cmd == "export-stage1-observability"
    assert args.output == "/tmp/m.json"


def test_cli_export_stage1_observability_main_writes_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    out_file = tmp_path / "metrics.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["sde", "project", "export-stage1-observability", "--session-dir", str(sess), "--output", str(out_file)],
    )
    with pytest.raises(SystemExit) as ei:
        main()
    assert ei.value.code == 0
    body = json.loads(out_file.read_text(encoding="utf-8"))
    assert stage1_observability_export_schema_errors(body) == []
