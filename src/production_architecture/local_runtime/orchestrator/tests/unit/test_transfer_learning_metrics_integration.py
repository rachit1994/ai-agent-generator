from __future__ import annotations

import pytest

from success_criteria.transfer_learning_metrics import validate_transfer_learning_metrics_path
from guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory import (
    validate_execution_run_directory,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)


def test_transfer_learning_metrics_artifact_written_and_valid(tmp_path) -> None:
    parsed = {"checks": [{"name": "a", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    nodes = write_memory_artifacts(output_dir=tmp_path, run_id="rid-transfer", parsed=parsed, events=events)
    write_evolution_artifacts(
        output_dir=tmp_path,
        run_id="rid-transfer",
        parsed=parsed,
        events=events,
        skill_nodes=nodes,
    )
    assert validate_transfer_learning_metrics_path(tmp_path / "learning" / "transfer_learning_metrics.json") == []


def test_evolution_writer_fails_closed_for_transfer_learning_contract(monkeypatch, tmp_path) -> None:
    parsed = {"checks": [{"name": "a", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    nodes = write_memory_artifacts(output_dir=tmp_path, run_id="rid-transfer", parsed=parsed, events=events)

    def _malformed_transfer_metrics(**_: object) -> dict[str, object]:
        return {"schema": "wrong"}

    monkeypatch.setattr(
        "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer.build_transfer_learning_metrics",
        _malformed_transfer_metrics,
    )
    with pytest.raises(ValueError, match=r"^transfer_learning_metrics_contract:"):
        write_evolution_artifacts(
            output_dir=tmp_path,
            run_id="rid-transfer",
            parsed=parsed,
            events=events,
            skill_nodes=nodes,
        )


def test_run_directory_reports_transfer_metrics_contract_when_missing(tmp_path, monkeypatch) -> None:
    out = tmp_path / "run"
    (out / "learning").mkdir(parents=True)
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text('{"runStatus":"ok","balanced_gates":{}}', encoding="utf-8")
    (out / "token_context.json").write_text('{"schema_version":"1.0","stages":[]}', encoding="utf-8")
    (out / "review.json").write_text(
        '{"schema_version":"1.1","run_id":"rid-1","status":"completed_review_pass","reasons":[],"required_fixes":[],"gate_snapshot":{},"artifact_manifest":[],"review_findings":[],"completed_at":"2026-01-01T00:00:00Z"}',
        encoding="utf-8",
    )
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "transfer_learning_metrics_contract:transfer_learning_metrics_file_missing" in result["errors"]
