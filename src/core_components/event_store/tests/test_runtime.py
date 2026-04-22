from __future__ import annotations

from core_components.event_store import (
    build_event_store_component,
    execute_event_store_runtime,
    validate_event_store_component_dict,
)


def test_build_event_store_component_is_deterministic() -> None:
    one = build_event_store_component(
        run_id="rid-event-store",
        replay_manifest={"passed": True},
        run_events=[{"event_id": "evt-1"}],
        trace_events=[{"type": "stage_event"}],
        kill_switch_state={"latched": False},
    )
    two = build_event_store_component(
        run_id="rid-event-store",
        replay_manifest={"passed": True},
        run_events=[{"event_id": "evt-1"}],
        trace_events=[{"type": "stage_event"}],
        kill_switch_state={"latched": False},
    )
    assert one == two
    assert validate_event_store_component_dict(one) == []
    assert one["execution"]["run_events_processed"] == 1


def test_validate_event_store_component_fail_closed() -> None:
    errs = validate_event_store_component_dict({"schema": "bad"})
    assert "event_store_component_schema" in errs
    assert "event_store_component_schema_version" in errs


def test_execute_event_store_runtime_detects_missing_manifest_signal() -> None:
    execution = execute_event_store_runtime(
        replay_manifest={"status": "ok"},
        run_events=[{"event_id": "evt-1"}],
        trace_events=[{"type": "stage_event"}],
    )
    assert execution["run_events_processed"] == 1
    assert execution["trace_events_processed"] == 1
    assert execution["missing_manifest_signal"] is True
