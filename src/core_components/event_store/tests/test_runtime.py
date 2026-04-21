from __future__ import annotations

from core_components.event_store import (
    build_event_store_component,
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


def test_validate_event_store_component_fail_closed() -> None:
    errs = validate_event_store_component_dict({"schema": "bad"})
    assert "event_store_component_schema" in errs
    assert "event_store_component_schema_version" in errs
