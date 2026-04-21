from __future__ import annotations

from service_boundaries.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "service_boundaries/service_boundaries"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "service_boundaries.runtime" in refs

