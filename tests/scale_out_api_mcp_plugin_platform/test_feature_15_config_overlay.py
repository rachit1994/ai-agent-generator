from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_15_local_prod_config_overlay_invariant_semantics import (
    build_config_overlay_contract,
    evaluate_config_overlay_gate,
    update_config_overlay_history,
    validate_config_overlay_report_dict,
)


def _base() -> dict[str, object]:
    return {"shared_schema_present": True, "config_schema_version": "2026.04.1"}


def _overlay() -> dict[str, object]:
    return {
        "override_allowlist_enforced": True,
        "override_allowlist_hash": "sha256:allowlist-v1",
        "config_schema_version": "2026.04.1",
    }


def _resolved() -> dict[str, object]:
    return {
        "config_schema_version": "2026.04.1",
        "applied_precedence": ["base", "env_overlay", "runtime_override_allowlist"],
        "override_allowlist_hash": "sha256:allowlist-v1",
        "overlay_merge_deterministic": True,
        "invariants_fail_fast_enforced": True,
        "drift_detection_present": True,
        "secret_redaction_consistent": True,
        "versioned_migrations_supported": True,
        "adapter_overlay_tests_present": True,
    }


def test_config_overlay_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_config_overlay_gate(
        run_id="run-feature-15-pass",
        mode="ci",
        base_config=_base(),
        overlay_config=_overlay(),
        resolved_config=_resolved(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_config_overlay_report_dict(report) == []


def test_config_overlay_gate_fail_closes_on_invariant_violation() -> None:
    resolved = _resolved()
    resolved["invariants_fail_fast_enforced"] = False
    report = evaluate_config_overlay_gate(
        run_id="run-feature-15-invariant-fail",
        mode="preflight",
        base_config=_base(),
        overlay_config=_overlay(),
        resolved_config=resolved,
    )
    assert report["status"] == "fail"
    assert "invariants_fail_fast_enforced" in report["failed_gates"]


def test_config_overlay_gate_fail_closes_on_schema_version_drift() -> None:
    overlay = _overlay()
    overlay["config_schema_version"] = "2026.04.2"
    report = evaluate_config_overlay_gate(
        run_id="run-feature-15-schema-version-drift",
        mode="preflight",
        base_config=_base(),
        overlay_config=overlay,
        resolved_config=_resolved(),
    )
    assert report["status"] == "fail"
    assert "shared_schema_present" in report["failed_gates"]


def test_config_overlay_gate_fail_closes_on_precedence_order_drift() -> None:
    resolved = _resolved()
    resolved["applied_precedence"] = ["env_overlay", "base", "runtime_override_allowlist"]
    report = evaluate_config_overlay_gate(
        run_id="run-feature-15-precedence-order-drift",
        mode="preflight",
        base_config=_base(),
        overlay_config=_overlay(),
        resolved_config=resolved,
    )
    assert report["status"] == "fail"
    assert "overlay_merge_deterministic" in report["failed_gates"]


def test_config_overlay_gate_fail_closes_on_override_allowlist_hash_drift() -> None:
    resolved = _resolved()
    resolved["override_allowlist_hash"] = "sha256:allowlist-v2"
    report = evaluate_config_overlay_gate(
        run_id="run-feature-15-override-allowlist-hash-drift",
        mode="preflight",
        base_config=_base(),
        overlay_config=_overlay(),
        resolved_config=resolved,
    )
    assert report["status"] == "fail"
    assert "override_allowlist_enforced" in report["failed_gates"]


def test_config_overlay_contract_is_deterministic() -> None:
    assert build_config_overlay_contract() == build_config_overlay_contract()


def test_config_overlay_history_appends_snapshot() -> None:
    report = evaluate_config_overlay_gate(
        run_id="run-feature-15-history",
        mode="ci",
        base_config=_base(),
        overlay_config=_overlay(),
        resolved_config=_resolved(),
    )
    history = update_config_overlay_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-15-history"

