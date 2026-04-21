"""Projection reducer."""

from __future__ import annotations

import json

from production_architecture.storage.types import EventRecord


def apply_events_to_run_state(events: list[EventRecord]) -> dict[str, object]:
    ordered = sorted(events, key=lambda row: row.event_seq)
    event_types = [row.event_type for row in ordered]
    state = {
        "event_count": len(ordered),
        "latest_event_seq": ordered[-1].event_seq if ordered else 0,
        "latest_payload_sha256": ordered[-1].payload_sha256 if ordered else "",
        "event_types": event_types,
    }
    # Normalize ordering/encoding to guarantee deterministic JSON.
    encoded = json.dumps(state, sort_keys=True, separators=(",", ":"))
    return json.loads(encoded)
