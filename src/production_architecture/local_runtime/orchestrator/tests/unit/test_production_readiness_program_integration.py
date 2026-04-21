from __future__ import annotations

from pathlib import Path

from implementation_roadmap.production_readiness_program import validate_production_readiness_program_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.production_readiness_layer import (
    write_production_readiness_artifact,
)


def test_write_production_readiness_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-readiness-layer"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "outputs")
    ensure_dir(output_dir / "memory")
    ensure_dir(output_dir / "capability")
    ensure_dir(output_dir / "learning")
    ensure_dir(output_dir / "lifecycle")
    ensure_dir(output_dir / "practice")
    ensure_dir(output_dir / "coordination")
    ensure_dir(output_dir / "iam")
    ensure_dir(output_dir / "orchestration")
    ensure_dir(output_dir / "strategy")
    ensure_dir(output_dir / "event_store")
    write_json(output_dir / "summary.json", {"runId": run_id, "mode": "guarded_pipeline", "balanced_gates": {"validation_ready": True}, "runStatus": "ok"})
    write_json(output_dir / "review.json", {"schema_version": "1.0", "run_id": run_id, "status": "completed_review_pass", "reasons": [], "required_fixes": [], "review_findings": [], "artifact_manifest": []})
    write_json(output_dir / "token_context.json", {"schema_version": "1.0"})
    (output_dir / "traces.jsonl").write_text("{}", encoding="utf-8")
    (output_dir / "orchestration.jsonl").write_text("{}", encoding="utf-8")
    (output_dir / "report.md").write_text("ok", encoding="utf-8")
    (output_dir / "run.log").write_text("ok", encoding="utf-8")
    (output_dir / "answer.txt").write_text("ok", encoding="utf-8")
    write_json(output_dir / "static_gates_report.json", {"ok": True})
    write_json(output_dir / "outputs" / "manifest.json", {"ok": True})
    (output_dir / "outputs" / "README.txt").write_text("ok", encoding="utf-8")
    write_json(output_dir / "replay_manifest.json", {"ok": True})
    write_json(output_dir / "kill_switch_state.json", {"ok": True})
    (output_dir / "event_store" / "run_events.jsonl").write_text("{}", encoding="utf-8")
    write_json(output_dir / "memory" / "retrieval_bundle.json", {"ok": True})
    (output_dir / "memory" / "quarantine.jsonl").write_text("", encoding="utf-8")
    write_json(output_dir / "memory" / "quality_metrics.json", {"ok": True})
    write_json(output_dir / "capability" / "skill_nodes.json", {"schema_version": "1.0", "nodes": []})
    write_json(output_dir / "learning" / "reflection_bundle.json", {"ok": True})
    write_json(output_dir / "learning" / "canary_report.json", {"ok": True})
    write_json(output_dir / "learning" / "transfer_learning_metrics.json", {"schema": "sde.transfer_learning_metrics.v1", "schema_version": "1.0", "run_id": run_id, "metrics": {"transfer_gain_rate": 0.7, "negative_transfer_rate": 0.1, "retained_success_rate": 0.8, "net_transfer_points": 60.0, "transfer_efficiency_score": 0.75}})
    write_json(output_dir / "learning" / "capability_growth_metrics.json", {"schema": "sde.capability_growth_metrics.v1", "schema_version": "1.0", "run_id": run_id, "metrics": {"capability_growth_rate": 0.7, "capability_stability_rate": 0.8, "promotion_readiness_delta": 0.2, "growth_confidence": 0.75}})
    write_json(output_dir / "learning" / "extended_binary_gates.json", {"schema": "sde.extended_binary_gates.v1", "schema_version": "1.0", "run_id": run_id, "overall_pass": True, "gates": {"reliability_gate": True, "delivery_gate": True, "governance_gate": True, "learning_gate": True}})
    write_json(output_dir / "lifecycle" / "promotion_package.json", {"ok": True})
    write_json(output_dir / "practice" / "task_spec.json", {"ok": True})
    write_json(output_dir / "practice" / "evaluation_result.json", {"ok": True})
    write_json(output_dir / "coordination" / "lease_table.json", {"ok": True})
    (output_dir / "iam" / "action_audit.jsonl").write_text("", encoding="utf-8")
    write_json(output_dir / "iam" / "permission_matrix.json", {"ok": True})
    write_json(output_dir / "orchestration" / "shard_map.json", {"ok": True})
    write_json(output_dir / "strategy" / "proposal.json", {"ok": True})
    write_json(output_dir / "program" / "policy_bundle_rollback.json", {"schema_version": "1.0", "bundles": []})
    payload = write_production_readiness_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        cto={"hard_stops": [{"id": "HS01", "passed": True}]},
    )
    assert payload["run_id"] == run_id
    assert validate_production_readiness_program_path(output_dir / "program" / "production_readiness.json") == []


def test_write_production_readiness_artifact_requires_non_empty_hard_stops(
    tmp_path: Path,
) -> None:
    run_id = "run-readiness-layer-empty-hard-stops"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "outputs")
    ensure_dir(output_dir / "memory")
    ensure_dir(output_dir / "capability")
    ensure_dir(output_dir / "learning")
    ensure_dir(output_dir / "lifecycle")
    ensure_dir(output_dir / "practice")
    ensure_dir(output_dir / "coordination")
    ensure_dir(output_dir / "iam")
    ensure_dir(output_dir / "orchestration")
    ensure_dir(output_dir / "strategy")
    ensure_dir(output_dir / "event_store")
    write_json(output_dir / "summary.json", {"runId": run_id, "mode": "guarded_pipeline", "balanced_gates": {"validation_ready": True}, "runStatus": "ok"})
    write_json(output_dir / "review.json", {"schema_version": "1.0", "run_id": run_id, "status": "completed_review_pass", "reasons": [], "required_fixes": [], "review_findings": [], "artifact_manifest": []})
    write_json(output_dir / "token_context.json", {"schema_version": "1.0"})
    (output_dir / "traces.jsonl").write_text("{}", encoding="utf-8")
    (output_dir / "orchestration.jsonl").write_text("{}", encoding="utf-8")
    (output_dir / "report.md").write_text("ok", encoding="utf-8")
    (output_dir / "run.log").write_text("ok", encoding="utf-8")
    (output_dir / "answer.txt").write_text("ok", encoding="utf-8")
    write_json(output_dir / "static_gates_report.json", {"ok": True})
    write_json(output_dir / "outputs" / "manifest.json", {"ok": True})
    (output_dir / "outputs" / "README.txt").write_text("ok", encoding="utf-8")
    write_json(output_dir / "replay_manifest.json", {"ok": True})
    write_json(output_dir / "kill_switch_state.json", {"ok": True})
    (output_dir / "event_store" / "run_events.jsonl").write_text("{}", encoding="utf-8")
    write_json(output_dir / "memory" / "retrieval_bundle.json", {"ok": True})
    (output_dir / "memory" / "quarantine.jsonl").write_text("", encoding="utf-8")
    write_json(output_dir / "memory" / "quality_metrics.json", {"ok": True})
    write_json(output_dir / "capability" / "skill_nodes.json", {"schema_version": "1.0", "nodes": []})
    write_json(output_dir / "learning" / "reflection_bundle.json", {"ok": True})
    write_json(output_dir / "learning" / "canary_report.json", {"ok": True})
    write_json(output_dir / "learning" / "transfer_learning_metrics.json", {"schema": "sde.transfer_learning_metrics.v1", "schema_version": "1.0", "run_id": run_id, "metrics": {"transfer_gain_rate": 0.7, "negative_transfer_rate": 0.1, "retained_success_rate": 0.8, "net_transfer_points": 60.0, "transfer_efficiency_score": 0.75}})
    write_json(output_dir / "learning" / "capability_growth_metrics.json", {"schema": "sde.capability_growth_metrics.v1", "schema_version": "1.0", "run_id": run_id, "metrics": {"capability_growth_rate": 0.7, "capability_stability_rate": 0.8, "promotion_readiness_delta": 0.2, "growth_confidence": 0.75}})
    write_json(output_dir / "learning" / "extended_binary_gates.json", {"schema": "sde.extended_binary_gates.v1", "schema_version": "1.0", "run_id": run_id, "overall_pass": True, "gates": {"reliability_gate": True, "delivery_gate": True, "governance_gate": True, "learning_gate": True}})
    write_json(output_dir / "lifecycle" / "promotion_package.json", {"ok": True})
    write_json(output_dir / "practice" / "task_spec.json", {"ok": True})
    write_json(output_dir / "practice" / "evaluation_result.json", {"ok": True})
    write_json(output_dir / "coordination" / "lease_table.json", {"ok": True})
    (output_dir / "iam" / "action_audit.jsonl").write_text("", encoding="utf-8")
    write_json(output_dir / "iam" / "permission_matrix.json", {"ok": True})
    write_json(output_dir / "orchestration" / "shard_map.json", {"ok": True})
    write_json(output_dir / "strategy" / "proposal.json", {"ok": True})
    write_json(output_dir / "program" / "policy_bundle_rollback.json", {"schema_version": "1.0", "bundles": []})
    payload = write_production_readiness_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode="guarded_pipeline",
        cto={"hard_stops": []},
    )
    assert payload["checks"]["hard_stops_passed"] is False
    assert payload["status"] == "not_ready"


def test_validate_production_readiness_path_rejects_unknown_mode(tmp_path: Path) -> None:
    run_id = "run-readiness-unknown-mode"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "program")
    path = output_dir / "program" / "production_readiness.json"
    write_json(
        path,
        {
            "schema": "sde.production_readiness_program.v1",
            "schema_version": "1.0",
            "run_id": run_id,
            "mode": "unknown_mode",
            "status": "ready",
            "checks": {
                "run_manifest_valid": True,
                "review_gate_passed": True,
                "hard_stops_passed": True,
                "balanced_gates_ready": True,
                "required_artifacts_present": True,
                "policy_bundle_valid": True,
            },
            "evidence": {
                "summary_ref": "summary.json",
                "review_ref": "review.json",
                "readiness_ref": "program/production_readiness.json",
            },
        },
    )
    errs = validate_production_readiness_program_path(path)
    assert "production_readiness_program_mode" in errs

