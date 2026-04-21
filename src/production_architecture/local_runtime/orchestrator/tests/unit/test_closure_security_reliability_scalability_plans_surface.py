from __future__ import annotations

from implementation_roadmap.closure_security_reliability_scalability_plans.surface import (
    describe_surface,
)


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "implementation_roadmap/closure_security_reliability_scalability_plans"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "implementation_roadmap.closure_security_reliability_scalability_plans.runtime" in refs

