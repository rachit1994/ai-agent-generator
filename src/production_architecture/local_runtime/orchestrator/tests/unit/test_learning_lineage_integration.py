from __future__ import annotations

import json
from pathlib import Path

import pytest

from event_sourced_architecture.learning_lineage import validate_learning_lineage_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_lineage_layer import (
    write_event_lineage_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.learning_lineage_layer import (
    write_learning_lineage_artifact,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)


def test_learning_lineage_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-learning-lineage"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "traces.jsonl").write_text(
        '{"stage":"finalize","score":{"passed":true,"reliability":0.9}}\n',
        encoding="utf-8",
    )
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    write_event_lineage_artifacts(output_dir=run_dir, run_id=run_id)
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    write_evolution_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        skill_nodes=skill_nodes,
    )
    payload = write_learning_lineage_artifact(
        output_dir=run_dir, run_id=run_id, mode="guarded_pipeline"
    )
    assert payload["run_id"] == run_id
    lineage_path = run_dir / "learning" / "learning_lineage.json"
    assert validate_learning_lineage_path(lineage_path) == []
    body = json.loads(lineage_path.read_text(encoding="utf-8"))
    assert body["status"] in {"aligned", "partial", "broken"}


def test_learning_lineage_fails_closed_on_non_object_reflection_bundle(tmp_path: Path) -> None:
    run_id = "run-learning-lineage-fail-closed"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True, exist_ok=True)
    (run_dir / "replay_manifest.json").write_text(
        json.dumps({"chain_root": "abc"}), encoding="utf-8"
    )
    (run_dir / "event_store").mkdir(parents=True, exist_ok=True)
    (run_dir / "event_store" / "run_events.jsonl").write_text(
        json.dumps({"event_id": "evt-1"}) + "\n", encoding="utf-8"
    )
    (run_dir / "learning" / "reflection_bundle.json").write_text(
        json.dumps(["not", "an", "object"]), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="learning_lineage_upstream_not_object"):
        write_learning_lineage_artifact(
            output_dir=run_dir, run_id=run_id, mode="guarded_pipeline"
        )


def test_learning_lineage_fails_closed_on_non_object_event_row(tmp_path: Path) -> None:
    run_id = "run-learning-lineage-fail-closed-events"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True, exist_ok=True)
    (run_dir / "replay_manifest.json").write_text(
        json.dumps({"chain_root": "abc"}), encoding="utf-8"
    )
    (run_dir / "event_store").mkdir(parents=True, exist_ok=True)
    (run_dir / "event_store" / "run_events.jsonl").write_text(
        json.dumps({"event_id": "evt-1"}) + "\n" + json.dumps(["bad-row"]) + "\n",
        encoding="utf-8",
    )
    (run_dir / "learning" / "reflection_bundle.json").write_text(
        json.dumps({"linked_event_ids": ["evt-1"]}), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="learning_lineage_event_row_not_object"):
        write_learning_lineage_artifact(
            output_dir=run_dir, run_id=run_id, mode="guarded_pipeline"
        )


def test_validate_learning_lineage_path_rejects_status_coverage_mismatch(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "runs" / "run-learning-lineage-status-mismatch"
    (run_dir / "learning").mkdir(parents=True, exist_ok=True)
    (run_dir / "learning" / "learning_lineage.json").write_text(
        json.dumps(
            {
                "schema": "sde.learning_lineage.v1",
                "schema_version": "1.0",
                "run_id": "run-learning-lineage-status-mismatch",
                "mode": "guarded_pipeline",
                "status": "broken",
                "checks": {
                    "manifest_has_chain_root": True,
                    "event_store_present": True,
                    "reflection_linked": True,
                },
                "coverage": 0.0,
                "evidence": {
                    "replay_manifest_ref": "replay_manifest.json",
                    "event_store_ref": "event_store/run_events.jsonl",
                    "reflection_bundle_ref": "learning/reflection_bundle.json",
                    "learning_lineage_ref": "learning/learning_lineage.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_learning_lineage_path(run_dir / "learning" / "learning_lineage.json")
    assert "learning_lineage_status_semantics" in errs
    assert "learning_lineage_coverage_semantics" in errs
