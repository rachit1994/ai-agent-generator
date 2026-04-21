from __future__ import annotations

import json
from pathlib import Path

from event_sourced_architecture.auditability import validate_auditability_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.auditability_layer import (
    write_auditability_artifact,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_lineage_layer import (
    write_event_lineage_artifacts,
)


def test_write_auditability_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-auditability"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir)
    (output_dir / "traces.jsonl").write_text(
        '{"event_id":"evt-1","payload":{"sha256":"abc123"}}\n',
        encoding="utf-8",
    )
    write_json(
        output_dir / "review.json",
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "status": "completed_review_pass",
            "review_findings": [],
            "artifact_manifest": [],
        },
    )
    write_event_lineage_artifacts(output_dir=output_dir, run_id=run_id)
    payload = write_auditability_artifact(output_dir=output_dir, run_id=run_id, mode="guarded_pipeline")
    assert payload["run_id"] == run_id
    assert validate_auditability_path(output_dir / "audit" / "auditability.json") == []
    body = json.loads((output_dir / "audit" / "auditability.json").read_text(encoding="utf-8"))
    assert body["status"] == "verifiable"


def test_write_auditability_artifact_fails_closed_on_malformed_run_events_row(
    tmp_path: Path,
) -> None:
    run_id = "run-auditability-malformed-row"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "event_store")
    (output_dir / "event_store" / "run_events.jsonl").write_text('{"payload":{"sha256":"abc123"}}\nnot-json\n', encoding="utf-8")
    write_json(output_dir / "replay_manifest.json", {"chain_root": "abc123"})
    write_json(output_dir / "kill_switch_state.json", {"latched": False})
    write_json(
        output_dir / "review.json",
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "status": "completed_review_pass",
            "review_findings": [],
            "artifact_manifest": [],
        },
    )
    try:
        write_auditability_artifact(output_dir=output_dir, run_id=run_id, mode="guarded_pipeline")
    except ValueError as exc:
        assert "auditability_run_events_jsonl_invalid:" in str(exc)
    else:
        raise AssertionError("expected fail-closed malformed run events error")


def test_write_auditability_artifact_fails_closed_on_non_object_run_events_row(
    tmp_path: Path,
) -> None:
    run_id = "run-auditability-non-object-row"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "event_store")
    (output_dir / "event_store" / "run_events.jsonl").write_text('{"payload":{"sha256":"abc123"}}\n[]\n', encoding="utf-8")
    write_json(output_dir / "replay_manifest.json", {"chain_root": "abc123"})
    write_json(output_dir / "kill_switch_state.json", {"latched": False})
    write_json(
        output_dir / "review.json",
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "status": "completed_review_pass",
            "review_findings": [],
            "artifact_manifest": [],
        },
    )
    try:
        write_auditability_artifact(output_dir=output_dir, run_id=run_id, mode="guarded_pipeline")
    except ValueError as exc:
        assert "auditability_run_events_row_not_object:" in str(exc)
    else:
        raise AssertionError("expected fail-closed non-object run events error")


def test_validate_auditability_path_rejects_status_semantics_mismatch(tmp_path: Path) -> None:
    run_id = "run-auditability-status-mismatch"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "audit")
    (output_dir / "audit" / "auditability.json").write_text(
        json.dumps(
            {
                "schema": "sde.auditability.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "mode": "guarded_pipeline",
                "status": "inconsistent",
                "hash_chain": {
                    "chain_root": "abc123",
                    "latest_hash": "abc123",
                    "event_count": 1,
                    "hash_chain_valid": True,
                },
                "integrity_operations": {
                    "periodic_check_supported": True,
                    "last_check_passed": True,
                    "checks_performed": 1,
                },
                "evidence": {
                    "replay_manifest_ref": "replay_manifest.json",
                    "event_store_ref": "event_store/run_events.jsonl",
                    "kill_switch_ref": "kill_switch_state.json",
                    "review_ref": "review.json",
                    "auditability_ref": "audit/auditability.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_auditability_path(output_dir / "audit" / "auditability.json")
    assert "auditability_status_semantics_mismatch" in errs


def test_validate_auditability_path_rejects_non_canonical_evidence_ref(
    tmp_path: Path,
) -> None:
    run_id = "run-auditability-evidence-mismatch"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "audit")
    (output_dir / "audit" / "auditability.json").write_text(
        json.dumps(
            {
                "schema": "sde.auditability.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "mode": "guarded_pipeline",
                "status": "verifiable",
                "hash_chain": {
                    "chain_root": "abc123",
                    "latest_hash": "abc123",
                    "event_count": 1,
                    "hash_chain_valid": True,
                },
                "integrity_operations": {
                    "periodic_check_supported": True,
                    "last_check_passed": True,
                    "checks_performed": 1,
                },
                "evidence": {
                    "replay_manifest_ref": "replay_manifest.json",
                    "event_store_ref": "event_store/events.jsonl",
                    "kill_switch_ref": "kill_switch_state.json",
                    "review_ref": "review.json",
                    "auditability_ref": "audit/auditability.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_auditability_path(output_dir / "audit" / "auditability.json")
    assert "auditability_evidence_ref_mismatch:event_store_ref" in errs
