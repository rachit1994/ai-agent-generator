from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory import (
    validate_execution_run_directory,
)
from production_architecture.local_runtime import validate_local_runtime_spine_path
from production_architecture.storage.storage.storage import ensure_dir
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.local_runtime_spine_layer import (
    write_local_runtime_spine_artifact,
)


def test_local_runtime_spine_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-local-runtime"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir)
    (run_dir / "run-manifest.json").write_text(
        json.dumps({"schema": "sde.run_manifest.v1", "run_id": run_id, "mode": "baseline", "task": "t"}),
        encoding="utf-8",
    )
    (run_dir / "orchestration.jsonl").write_text("", encoding="utf-8")
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    payload = write_local_runtime_spine_artifact(output_dir=run_dir, run_id=run_id, mode="baseline")
    assert payload["run_id"] == run_id
    assert payload["status"] == "ready"
    assert validate_local_runtime_spine_path(run_dir / "orchestrator" / "local_runtime_spine.json") == []


def test_run_directory_surfaces_invalid_local_runtime_spine_contract(tmp_path: Path, monkeypatch) -> None:
    out = tmp_path / "run"
    (out / "program").mkdir(parents=True)
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(json.dumps({"schema_version": "1.0", "stages": []}), encoding="utf-8")
    (out / "review.json").write_text(
        json.dumps(
            {
                "schema_version": "1.1",
                "run_id": "rid-1",
                "status": "completed_review_pass",
                "reasons": [],
                "required_fixes": [],
                "gate_snapshot": {},
                "artifact_manifest": [],
                "review_findings": [],
                "completed_at": "2026-01-01T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    (out / "orchestrator").mkdir(parents=True, exist_ok=True)
    (out / "orchestrator" / "local_runtime_spine.json").write_text(json.dumps({"schema": "bad"}), encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "local_runtime_spine_contract:local_runtime_spine_schema" in result["errors"]
