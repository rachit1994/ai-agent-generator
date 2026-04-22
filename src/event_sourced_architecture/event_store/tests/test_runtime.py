from __future__ import annotations

from event_sourced_architecture.event_store import (
    build_event_store_semantics,
    validate_event_store_semantics_dict,
)


def test_build_event_store_semantics_is_deterministic() -> None:
    replay_manifest = {
        "chain_root": "abc123",
        "sources": [{"path": "traces.jsonl", "sha256": "abc123"}],
    }
    one = build_event_store_semantics(
        run_id="rid-event-semantics",
        replay_manifest=replay_manifest,
        run_events=[{"event_id": "evt-1"}],
        trace_events=[{"type": "stage_event"}],
    )
    two = build_event_store_semantics(
        run_id="rid-event-semantics",
        replay_manifest=replay_manifest,
        run_events=[{"event_id": "evt-1"}],
        trace_events=[{"type": "stage_event"}],
    )
    assert one == two
    assert validate_event_store_semantics_dict(one) == []


def test_validate_event_store_semantics_fail_closed() -> None:
    errs = validate_event_store_semantics_dict({"schema": "bad"})
    assert "event_store_semantics_schema" in errs
    assert "event_store_semantics_schema_version" in errs


def test_validate_event_store_semantics_rejects_noncanonical_evidence_ref() -> None:
    payload = build_event_store_semantics(
        run_id="rid-event-semantics",
        replay_manifest={"chain_root": "abc123", "sources": [{"path": "traces.jsonl", "sha256": "abc123"}]},
        run_events=[{"event_id": "evt-1"}],
        trace_events=[{"type": "stage_event"}],
    )
    payload["evidence"]["semantics_ref"] = "event_store/other_semantics.json"
    errs = validate_event_store_semantics_dict(payload)
    assert "event_store_semantics_evidence_ref:semantics_ref" in errs
