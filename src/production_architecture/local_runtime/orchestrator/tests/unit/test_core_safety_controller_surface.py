from __future__ import annotations

from core_components.safety_controller.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "core_components/safety_controller"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "core_components.safety_controller.runtime" in refs
