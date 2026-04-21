from __future__ import annotations

from implementation_roadmap.consolidated_improvements.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "implementation_roadmap/consolidated_improvements"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "implementation_roadmap.consolidated_improvements.runtime" in refs

