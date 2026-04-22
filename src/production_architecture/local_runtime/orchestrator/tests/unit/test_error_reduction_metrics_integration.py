from __future__ import annotations

import json
from pathlib import Path

import pytest

from success_criteria.error_reduction_metrics import validate_error_reduction_metrics_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)


def test_error_reduction_metrics_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-error-reduction"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": False}, {"name": "quality", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    write_evolution_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    metrics_path = run_dir / "learning" / "error_reduction_metrics.json"
    assert validate_error_reduction_metrics_path(metrics_path) == []
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == run_id


def test_validate_error_reduction_metrics_path_rejects_count_arithmetic_mismatch(
    tmp_path: Path,
) -> None:
    run_id = "run-error-reduction-mismatch"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True)
    metrics_path = run_dir / "learning" / "error_reduction_metrics.json"
    metrics_path.write_text(
        json.dumps(
            {
                "schema": "sde.error_reduction_metrics.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "metrics": {
                    "baseline_error_count": 3,
                    "candidate_error_count": 1,
                    "resolved_error_count": 3,
                    "error_reduction_rate": 1.0,
                    "net_error_delta": 0.0,
                },
                "evidence": {"traces_ref": "traces.jsonl", "summary_ref": "summary.json"},
            }
        ),
        encoding="utf-8",
    )
    errs = validate_error_reduction_metrics_path(metrics_path)
    assert "error_reduction_metrics_semantics:resolved_error_count" in errs


def test_error_reduction_metrics_no_finalize_events_fail_close_to_no_improvement(tmp_path: Path) -> None:
    run_id = "run-error-reduction-no-finalize"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": False}]}
    events: list[dict[str, object]] = []
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    write_evolution_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    metrics_path = run_dir / "learning" / "error_reduction_metrics.json"
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert payload["metrics"]["baseline_error_count"] == 1
    assert payload["metrics"]["candidate_error_count"] == 1
    assert payload["metrics"]["resolved_error_count"] == 0
    assert payload["metrics"]["error_reduction_rate"] == pytest.approx(0.0)

