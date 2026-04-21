from __future__ import annotations

from event_sourced_architecture.event_store.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "event_sourced_architecture/event_store"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "event_sourced_architecture.event_store.runtime" in refs
