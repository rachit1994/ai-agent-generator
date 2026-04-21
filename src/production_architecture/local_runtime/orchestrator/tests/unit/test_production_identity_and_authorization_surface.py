from __future__ import annotations

from production_architecture.identity_and_authorization.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "production_architecture/identity_and_authorization"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "production_architecture.identity_and_authorization.runtime" in refs
