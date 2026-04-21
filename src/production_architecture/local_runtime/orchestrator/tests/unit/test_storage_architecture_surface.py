from __future__ import annotations

from production_architecture.storage.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "production_architecture/storage"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "production_architecture.storage.runtime" in refs

