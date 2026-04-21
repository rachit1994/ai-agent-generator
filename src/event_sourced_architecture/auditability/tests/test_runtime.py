from __future__ import annotations

from event_sourced_architecture.auditability import build_auditability, validate_auditability_dict


def test_build_auditability_is_deterministic() -> None:
    events = [
        {"payload": {"sha256": "abc123"}},
        {"payload": {"sha256": "abc123"}},
    ]
    one = build_auditability(
        run_id="rid-audit",
        mode="guarded_pipeline",
        replay_manifest={"chain_root": "abc123"},
        run_events=events,
        kill_switch_state={"latched": False},
        review={"status": "completed_review_pass"},
    )
    two = build_auditability(
        run_id="rid-audit",
        mode="guarded_pipeline",
        replay_manifest={"chain_root": "abc123"},
        run_events=events,
        kill_switch_state={"latched": False},
        review={"status": "completed_review_pass"},
    )
    assert one == two
    assert validate_auditability_dict(one) == []


def test_validate_auditability_fail_closed() -> None:
    errs = validate_auditability_dict({"schema": "bad"})
    assert "auditability_schema" in errs
    assert "auditability_schema_version" in errs


def test_validate_auditability_rejects_status_semantics_mismatch() -> None:
    payload = build_auditability(
        run_id="rid-audit",
        mode="guarded_pipeline",
        replay_manifest={"chain_root": "abc123"},
        run_events=[{"payload": {"sha256": "abc123"}}],
        kill_switch_state={"latched": False},
        review={"status": "completed_review_pass"},
    )
    payload["status"] = "inconsistent"
    errs = validate_auditability_dict(payload)
    assert "auditability_status_semantics_mismatch" in errs


def test_validate_auditability_rejects_non_canonical_evidence_ref() -> None:
    payload = build_auditability(
        run_id="rid-audit",
        mode="guarded_pipeline",
        replay_manifest={"chain_root": "abc123"},
        run_events=[{"payload": {"sha256": "abc123"}}],
        kill_switch_state={"latched": False},
        review={"status": "completed_review_pass"},
    )
    payload["evidence"]["event_store_ref"] = "event_store/events.jsonl"
    errs = validate_auditability_dict(payload)
    assert "auditability_evidence_ref_mismatch:event_store_ref" in errs
