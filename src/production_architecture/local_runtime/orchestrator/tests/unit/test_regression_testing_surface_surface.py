from __future__ import annotations

from evaluation_framework.regression_testing_surface.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "evaluation_framework/regression_testing_surface"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "evaluation_framework.regression_testing_surface.runtime" in refs
