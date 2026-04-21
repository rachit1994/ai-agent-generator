from __future__ import annotations

from implementation_roadmap.implementation_roadmap.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "implementation_roadmap/implementation_roadmap"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "implementation_roadmap.implementation_roadmap.runtime" in refs
