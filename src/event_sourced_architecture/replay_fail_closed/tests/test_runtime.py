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
