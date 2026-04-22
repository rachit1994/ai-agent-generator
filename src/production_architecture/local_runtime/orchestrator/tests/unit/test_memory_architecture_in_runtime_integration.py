from __future__ import annotations

import json
from pathlib import Path

from production_architecture.memory_architecture_in_runtime import (
    validate_memory_architecture_in_runtime_path,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_architecture_runtime_layer import (
    write_memory_architecture_in_runtime_artifact,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)


def test_memory_architecture_in_runtime_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-memory-arch-runtime"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    write_memory_artifacts(output_dir=run_dir, run_id=run_id, parsed=parsed, events=events)
    payload = write_memory_architecture_in_runtime_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    memory_arch_path = run_dir / "memory" / "runtime_memory_architecture.json"
    assert validate_memory_architecture_in_runtime_path(memory_arch_path) == []
    body = json.loads(memory_arch_path.read_text(encoding="utf-8"))
    assert body["status"] in {"healthy", "degraded", "missing"}
    assert body["evidence"]["memory_architecture_ref"] == "memory/runtime_memory_architecture.json"


def test_memory_architecture_in_runtime_fail_closes_malformed_memory_inputs(tmp_path: Path) -> None:
    run_id = "run-memory-arch-runtime-malformed"
    run_dir = tmp_path / "runs" / run_id
    memory_dir = run_dir / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / "retrieval_bundle.json").write_text('{"chunks":[', encoding="utf-8")
    (memory_dir / "quality_metrics.json").write_text('{"contradiction_rate":', encoding="utf-8")
    (memory_dir / "quarantine.jsonl").write_text("bad\nline\n", encoding="utf-8")
    payload = write_memory_architecture_in_runtime_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "missing"
    memory_arch_path = run_dir / "memory" / "runtime_memory_architecture.json"
    assert validate_memory_architecture_in_runtime_path(memory_arch_path) == []


def test_memory_architecture_in_runtime_fail_closes_unreadable_memory_inputs(tmp_path: Path) -> None:
    run_id = "run-memory-arch-runtime-unreadable"
    run_dir = tmp_path / "runs" / run_id
    memory_dir = run_dir / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / "retrieval_bundle.json").write_bytes(b"\xff\xfe\xfd")
    (memory_dir / "quality_metrics.json").write_bytes(b"\xff\xfe\xfd")
    (memory_dir / "quarantine.jsonl").write_bytes(b"\xff\xfe\xfd")
    payload = write_memory_architecture_in_runtime_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "missing"
    memory_arch_path = run_dir / "memory" / "runtime_memory_architecture.json"
    assert validate_memory_architecture_in_runtime_path(memory_arch_path) == []
