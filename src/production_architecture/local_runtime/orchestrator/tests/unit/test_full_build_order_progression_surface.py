from __future__ import annotations

from scalability_strategy.full_build_order_progression.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "scalability_strategy/full_build_order_progression"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "scalability_strategy.full_build_order_progression.runtime" in refs

