from __future__ import annotations

from workflow_pipelines.run_manifest import (
    build_run_manifest_runtime,
    validate_run_manifest_runtime_dict,
)


def test_build_run_manifest_runtime_deterministic() -> None:
    manifest = {
        "schema": "sde.run_manifest.v1",
        "run_id": "rid-run-manifest",
        "mode": "guarded_pipeline",
        "task": "do thing",
        "project_step_id": "step-1",
        "project_session_dir": "/tmp/session",
    }
    one = build_run_manifest_runtime(run_manifest=manifest)
    two = build_run_manifest_runtime(run_manifest=manifest)
    assert one == two
    assert one["status"] == "linked"
    assert validate_run_manifest_runtime_dict(one) == []


def test_validate_run_manifest_runtime_fail_closed() -> None:
    errs = validate_run_manifest_runtime_dict({"schema": "bad"})
    assert "run_manifest_runtime_schema" in errs
    assert "run_manifest_runtime_schema_version" in errs
