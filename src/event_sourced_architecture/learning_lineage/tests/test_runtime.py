from __future__ import annotations

from event_sourced_architecture.learning_lineage import (
    build_learning_lineage,
    validate_learning_lineage_dict,
)


def test_build_learning_lineage_is_deterministic() -> None:
    payload_one = build_learning_lineage(
        run_id="rid-learning-lineage",
        mode="guarded_pipeline",
        replay_manifest={"chain_root": "a" * 64},
        run_events=[{"event_id": "evt-1"}],
        reflection_bundle={"linked_event_ids": ["evt-1"]},
    )
    payload_two = build_learning_lineage(
        run_id="rid-learning-lineage",
        mode="guarded_pipeline",
        replay_manifest={"chain_root": "a" * 64},
        run_events=[{"event_id": "evt-1"}],
        reflection_bundle={"linked_event_ids": ["evt-1"]},
    )
    assert payload_one == payload_two
    assert validate_learning_lineage_dict(payload_one) == []


def test_validate_learning_lineage_fail_closed() -> None:
    errs = validate_learning_lineage_dict({"schema": "bad"})
    assert "learning_lineage_schema" in errs
    assert "learning_lineage_schema_version" in errs


def test_validate_learning_lineage_rejects_status_coverage_mismatch() -> None:
    payload = build_learning_lineage(
        run_id="rid-learning-lineage-mismatch",
        mode="guarded_pipeline",
        replay_manifest={"chain_root": "a" * 64},
        run_events=[{"event_id": "evt-1"}],
        reflection_bundle={"linked_event_ids": ["evt-1"]},
    )
    payload["status"] = "broken"
    payload["coverage"] = 0.0
    errs = validate_learning_lineage_dict(payload)
    assert "learning_lineage_status_semantics" in errs
    assert "learning_lineage_coverage_semantics" in errs


def test_validate_learning_lineage_rejects_non_canonical_evidence_ref() -> None:
    payload = build_learning_lineage(
        run_id="rid-learning-lineage-evidence",
        mode="guarded_pipeline",
        replay_manifest={"chain_root": "a" * 64},
        run_events=[{"event_id": "evt-1"}],
        reflection_bundle={"linked_event_ids": ["evt-1"]},
    )
    payload["evidence"]["event_store_ref"] = "event_store/events.jsonl"
    errs = validate_learning_lineage_dict(payload)
    assert "learning_lineage_evidence_ref:event_store_ref" in errs
