from __future__ import annotations

from event_sourced_architecture.replay_fail_closed import (
    build_replay_fail_closed,
    validate_replay_fail_closed_dict,
)


def test_build_replay_fail_closed_is_deterministic() -> None:
    replay_manifest = {"chain_root": "abc", "sources": [{"sha256": "abc"}]}
    one = build_replay_fail_closed(
        run_id="rid-replay-fc",
        replay_manifest=replay_manifest,
        trace_rows=[{"t": 1}],
        event_rows=[{"e": 1}],
    )
    two = build_replay_fail_closed(
        run_id="rid-replay-fc",
        replay_manifest=replay_manifest,
        trace_rows=[{"t": 1}],
        event_rows=[{"e": 1}],
    )
    assert one == two
    assert validate_replay_fail_closed_dict(one) == []


def test_validate_replay_fail_closed_fail_closed() -> None:
    errs = validate_replay_fail_closed_dict({"schema": "bad"})
    assert "replay_fail_closed_schema" in errs
    assert "replay_fail_closed_schema_version" in errs


def test_validate_replay_fail_closed_rejects_status_checks_mismatch() -> None:
    payload = build_replay_fail_closed(
        run_id="rid-replay-fc",
        replay_manifest={"chain_root": "abc", "sources": [{"sha256": "abc"}]},
        trace_rows=[{"t": 1}],
        event_rows=[{"e": 1}],
    )
    payload["status"] = "fail"
    errs = validate_replay_fail_closed_dict(payload)
    assert "replay_fail_closed_status_checks_mismatch" in errs


def test_validate_replay_fail_closed_rejects_missing_evidence() -> None:
    payload = build_replay_fail_closed(
        run_id="rid-replay-fc",
        replay_manifest={"chain_root": "abc", "sources": [{"sha256": "abc"}]},
        trace_rows=[{"t": 1}],
        event_rows=[{"e": 1}],
    )
    payload.pop("evidence")
    errs = validate_replay_fail_closed_dict(payload)
    assert "replay_fail_closed_evidence" in errs


def test_validate_replay_fail_closed_rejects_noncanonical_evidence_ref() -> None:
    payload = build_replay_fail_closed(
        run_id="rid-replay-fc",
        replay_manifest={"chain_root": "abc", "sources": [{"sha256": "abc"}]},
        trace_rows=[{"t": 1}],
        event_rows=[{"e": 1}],
    )
    payload["evidence"]["replay_fail_closed_ref"] = "replay/other_fail_closed.json"
    errs = validate_replay_fail_closed_dict(payload)
    assert "replay_fail_closed_evidence_ref:replay_fail_closed_ref" in errs
