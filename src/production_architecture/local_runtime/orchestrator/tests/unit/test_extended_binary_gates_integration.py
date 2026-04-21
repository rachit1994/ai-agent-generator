from __future__ import annotations

import json
from pathlib import Path

from success_criteria.extended_binary_gates import validate_extended_binary_gates_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)


def test_extended_binary_gates_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-extended-binary"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    skill_nodes = write_memory_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events
    )
    write_evolution_artifacts(
        output_dir=run_dir, run_id=run_id, parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    metrics_path = run_dir / "learning" / "extended_binary_gates.json"
    assert validate_extended_binary_gates_path(metrics_path) == []
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == run_id
    expected_overall_pass = all(payload["gates"].values())
    assert payload["overall_pass"] is expected_overall_pass


def test_validate_extended_binary_gates_path_rejects_missing_evidence_refs(tmp_path: Path) -> None:
    run_id = "run-extended-binary-bad-evidence"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True)
    path = run_dir / "learning" / "extended_binary_gates.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.extended_binary_gates.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "overall_pass": True,
                "gates": {
                    "reliability_gate": True,
                    "delivery_gate": True,
                    "governance_gate": True,
                    "learning_gate": True,
                },
                "evidence": {
                    "traces_ref": "traces.jsonl",
                    "checks_ref": "",
                    "skill_nodes_ref": "capability/skill_nodes.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_extended_binary_gates_path(path)
    assert "extended_binary_gates_evidence_ref:checks_ref" in errs


def test_validate_extended_binary_gates_path_rejects_non_canonical_evidence_refs(
    tmp_path: Path,
) -> None:
    run_id = "run-extended-binary-bad-canonical-evidence"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True)
    path = run_dir / "learning" / "extended_binary_gates.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.extended_binary_gates.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "overall_pass": True,
                "gates": {
                    "reliability_gate": True,
                    "delivery_gate": True,
                    "governance_gate": True,
                    "learning_gate": True,
                },
                "evidence": {
                    "traces_ref": "learning/traces.jsonl",
                    "checks_ref": "summary.json",
                    "skill_nodes_ref": "capability/skill_nodes.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_extended_binary_gates_path(path)
    assert "extended_binary_gates_evidence_ref:traces_ref_canonical" in errs
