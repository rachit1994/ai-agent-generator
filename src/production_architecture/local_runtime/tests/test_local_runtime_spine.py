from __future__ import annotations

from production_architecture.local_runtime import (
    build_local_runtime_spine,
    validate_local_runtime_spine_dict,
)
from production_architecture.local_runtime.surface import describe_surface


def test_build_local_runtime_spine_deterministic() -> None:
    one = build_local_runtime_spine(
        run_id="rid-local",
        mode="baseline",
        has_run_manifest=True,
        has_orchestration=True,
        has_traces=True,
    )
    two = build_local_runtime_spine(
        run_id="rid-local",
        mode="baseline",
        has_run_manifest=True,
        has_orchestration=True,
        has_traces=True,
    )
    assert one == two
    assert one["status"] == "ready"
    assert validate_local_runtime_spine_dict(one) == []


def test_validate_local_runtime_spine_fail_closed() -> None:
    errs = validate_local_runtime_spine_dict({"schema": "bad"})
    assert "local_runtime_spine_schema" in errs
    assert "local_runtime_spine_schema_version" in errs


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "production_architecture/local_runtime"
    assert payload["status"] == "implemented"
