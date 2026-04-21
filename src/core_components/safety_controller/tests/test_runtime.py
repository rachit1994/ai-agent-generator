from __future__ import annotations

from core_components.safety_controller import (
    build_safety_controller,
    validate_safety_controller_dict,
)


def test_build_safety_controller_deterministic() -> None:
    cto = {"validation_ready": True, "hard_stops": [{"id": "HS01", "passed": True}]}
    one = build_safety_controller(run_id="rid-safe", cto=cto)
    two = build_safety_controller(run_id="rid-safe", cto=cto)
    assert one == two
    assert one["status"] == "allow"
    assert validate_safety_controller_dict(one) == []


def test_validate_safety_controller_fail_closed() -> None:
    errs = validate_safety_controller_dict({"schema": "bad"})
    assert "safety_controller_schema" in errs
    assert "safety_controller_schema_version" in errs
