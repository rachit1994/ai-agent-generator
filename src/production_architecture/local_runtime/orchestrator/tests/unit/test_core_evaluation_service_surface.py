from __future__ import annotations

from core_components.evaluation_service.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "core_components/evaluation_service"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "core_components.evaluation_service.runtime" in refs
