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


def test_build_safety_controller_treats_truthy_non_boolean_inputs_as_blocking() -> None:
    payload = build_safety_controller(
        run_id="rid-safe",
        cto={"validation_ready": "true", "hard_stops": [{"id": "HS01", "passed": "true"}]},
    )
    assert payload["status"] == "block"
    assert payload["metrics"]["validation_ready"] is False
    assert payload["metrics"]["hard_stop_failures"] is True


def test_validate_safety_controller_rejects_status_metrics_mismatch() -> None:
    payload = build_safety_controller(
        run_id="rid-safe",
        cto={"validation_ready": True, "hard_stops": [{"id": "HS01", "passed": True}]},
    )
    payload["status"] = "block"
    errs = validate_safety_controller_dict(payload)
    assert "safety_controller_status_metrics_mismatch" in errs
