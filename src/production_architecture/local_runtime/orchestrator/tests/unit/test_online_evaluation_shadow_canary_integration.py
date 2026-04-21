from __future__ import annotations

import json
from pathlib import Path

from evaluation_framework.online_evaluation_shadow_canary_artifact import (
    validate_online_evaluation_shadow_canary_path,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.online_evaluation_shadow_canary_layer import (
    write_online_evaluation_shadow_canary_artifact,
)


def test_online_evaluation_shadow_canary_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-online-shadow"
    run_dir = tmp_path / "runs" / run_id
    parsed = {"checks": [{"name": "shape", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
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
    records = [
        {
            "request_id": f"req-{idx}",
            "cohort": "shadow" if idx % 2 else "canary",
            "baseline_latency_ms": 90.0 + idx,
            "candidate_latency_ms": 95.0 + idx,
            "baseline_outcome": True,
            "candidate_outcome": True,
            "baseline_quality": 0.7,
            "candidate_quality": 0.72,
        }
        for idx in range(6)
    ]
    (run_dir / "learning" / "online_eval_records.jsonl").write_text(
        "\n".join(json.dumps(row) for row in records),
        encoding="utf-8",
    )
    payload = write_online_evaluation_shadow_canary_artifact(
        output_dir=run_dir, run_id=run_id
    )
    assert payload["run_id"] == run_id
    canary_path = run_dir / "learning" / "online_evaluation_shadow_canary.json"
    assert validate_online_evaluation_shadow_canary_path(canary_path) == []
    body = json.loads(canary_path.read_text(encoding="utf-8"))
    assert body["decision"]["decision"] in {"promote", "hold"}
    assert body["evidence"]["online_eval_records_ref"] == "learning/online_eval_records.jsonl"


def test_online_evaluation_shadow_canary_requires_canonical_records(tmp_path: Path) -> None:
    run_id = "run-online-shadow-missing"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True)
    try:
        write_online_evaluation_shadow_canary_artifact(output_dir=run_dir, run_id=run_id)
    except ValueError as exc:
        assert str(exc) == "online_evaluation_shadow_canary_contract:online_eval_records_missing"
        assert not (run_dir / "learning" / "online_evaluation_shadow_canary.json").exists()
    else:
        raise AssertionError("expected missing canonical records to fail closed")


def test_validate_online_evaluation_shadow_canary_path_rejects_coverage_sample_mismatch(
    tmp_path: Path,
) -> None:
    run_id = "run-online-shadow-coverage-mismatch"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "learning").mkdir(parents=True)
    canary_path = run_dir / "learning" / "online_evaluation_shadow_canary.json"
    canary_path.write_text(
        json.dumps(
            {
                "schema": "sde.online_evaluation_shadow_canary.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "decision": {
                    "decision": "hold",
                    "failed_gates": ["gate_min_sample"],
                    "decision_reasons": ["gate_min_sample_unmet"],
                    "min_sample_met": False,
                },
                "metrics": {
                    "sample_size": 0,
                    "coverage": 1.0,
                    "baseline_latency_p50_ms": 0.0,
                    "baseline_latency_p95_ms": 0.0,
                    "candidate_latency_p50_ms": 0.0,
                    "candidate_latency_p95_ms": 0.0,
                    "baseline_error_rate": 0.0,
                    "candidate_error_rate": 0.0,
                    "error_rate_delta": 0.0,
                    "latency_p95_delta_ms": 0.0,
                    "quality_delta": 0.0,
                },
                "evidence": {
                    "online_eval_records_ref": "learning/online_eval_records.jsonl",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_online_evaluation_shadow_canary_path(canary_path)
    assert "online_evaluation_shadow_canary_metrics_coverage_mismatch" in errs
