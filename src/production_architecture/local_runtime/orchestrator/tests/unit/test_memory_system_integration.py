from __future__ import annotations

from pathlib import Path

import pytest

from core_components.memory_system import validate_memory_system_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_system_layer import (
    write_memory_system_artifact,
)


def test_memory_system_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-memory-system"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    write_memory_artifacts(output_dir=run_dir, run_id=run_id, parsed=parsed, events=events)
    payload = write_memory_system_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert validate_memory_system_path(run_dir / "memory" / "memory_system.json") == []


def test_memory_system_layer_fails_on_corrupt_retrieval_json(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "run-memory-corrupt"
    ensure_dir(run_dir / "memory")
    (run_dir / "memory" / "retrieval_bundle.json").write_text("{bad", encoding="utf-8")
    with pytest.raises(ValueError, match="memory_system_input_json:retrieval_bundle"):
        write_memory_system_artifact(output_dir=run_dir, run_id="run-memory-corrupt")


def test_memory_system_layer_raises_prefixed_contract_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    run_dir = tmp_path / "runs" / "run-memory-invalid-contract"
    ensure_dir(run_dir / "memory")
    write_json(run_dir / "memory" / "retrieval_bundle.json", {"chunks": [{"text": "x"}]})
    write_json(run_dir / "memory" / "quality_metrics.json", {"contradiction_rate": 0.0, "staleness_p95_hours": 1.0})

    def _invalid_payload(
        *, run_id: str, retrieval_bundle: dict, quality_metrics: dict, quarantine_rows: list[str]
    ) -> dict:
        del run_id, retrieval_bundle, quality_metrics, quarantine_rows
        return {"schema": "bad"}

    monkeypatch.setattr(
        "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_system_layer.build_memory_system",
        _invalid_payload,
    )
    with pytest.raises(ValueError, match=r"^memory_system_contract:"):
        write_memory_system_artifact(output_dir=run_dir, run_id="run-memory-invalid-contract")


def test_memory_system_layer_fails_on_non_object_quality_metrics(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "run-memory-bad-quality-shape"
    ensure_dir(run_dir / "memory")
    write_json(run_dir / "memory" / "retrieval_bundle.json", {"chunks": [{"text": "x"}]})
    write_json(run_dir / "memory" / "quality_metrics.json", ["bad"])
    with pytest.raises(ValueError, match="memory_system_input_not_object:quality_metrics"):
        write_memory_system_artifact(output_dir=run_dir, run_id="run-memory-bad-quality-shape")


def test_validate_memory_system_path_rejects_missing_with_nonzero_quality_score(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "runs" / "run-memory-missing-quality-mismatch"
    ensure_dir(run_dir / "memory")
    write_json(
        run_dir / "memory" / "memory_system.json",
        {
            "schema": "sde.memory_system.v1",
            "schema_version": "1.0",
            "run_id": "run-memory-missing-quality-mismatch",
            "status": "missing",
            "metrics": {
                "retrieval_chunks": 0,
                "quarantine_rows": 0,
                "quality_score": 0.5,
                "contradiction_rate": 0.0,
                "staleness_p95_hours": 1.0,
            },
            "evidence": {
                "retrieval_bundle_ref": "memory/retrieval_bundle.json",
                "quality_metrics_ref": "memory/quality_metrics.json",
                "quarantine_ref": "memory/quarantine.jsonl",
                "memory_system_ref": "memory/memory_system.json",
            },
        },
    )
    errs = validate_memory_system_path(run_dir / "memory" / "memory_system.json")
    assert "memory_system_status_semantics:missing_quality_score" in errs


def test_memory_system_layer_fails_closed_for_out_of_range_quality_metrics(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "run-memory-out-of-range-quality"
    ensure_dir(run_dir / "memory")
    write_json(run_dir / "memory" / "retrieval_bundle.json", {"chunks": [{"text": "x"}]})
    write_json(run_dir / "memory" / "quality_metrics.json", {"contradiction_rate": -0.1, "staleness_p95_hours": -2.0})
    payload = write_memory_system_artifact(output_dir=run_dir, run_id="run-memory-out-of-range-quality")
    assert payload["status"] == "degraded"
    assert payload["metrics"]["quality_score"] == pytest.approx(0.0)
    assert payload["metrics"]["contradiction_rate"] == pytest.approx(1.0)
    assert payload["metrics"]["staleness_p95_hours"] == pytest.approx(999.0)
    assert validate_memory_system_path(run_dir / "memory" / "memory_system.json") == []
