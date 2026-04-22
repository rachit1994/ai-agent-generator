from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_16_contract_version_negotiation_mcp_plugins import (
    build_version_negotiation_contract,
    evaluate_version_negotiation_gate,
    update_version_negotiation_history,
    validate_version_negotiation_report_dict,
)


def _handshake() -> dict[str, object]:
    return {"handshake_implemented": True}


def _compatibility() -> dict[str, object]:
    return {
        "version_ranges_advertised_selected": True,
        "incompatible_rejections_deterministic": True,
        "dual_version_rollback_safe": True,
        "deprecation_windows_enforced_tested": True,
        "mixed_version_fleet_scenarios_tested": True,
        "rollout_gated_on_compat_failures": True,
    }


def _telemetry() -> dict[str, object]:
    return {"negotiated_version_telemetry_tracked": True}


def test_version_negotiation_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_version_negotiation_gate(
        run_id="run-feature-16-pass",
        mode="ci",
        handshake=_handshake(),
        compatibility=_compatibility(),
        telemetry=_telemetry(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_version_negotiation_report_dict(report) == []


def test_version_negotiation_gate_fail_closes_on_incompatible_reject_gap() -> None:
    compatibility = _compatibility()
    compatibility["incompatible_rejections_deterministic"] = False
    report = evaluate_version_negotiation_gate(
        run_id="run-feature-16-reject-gap",
        mode="preflight",
        handshake=_handshake(),
        compatibility=compatibility,
        telemetry=_telemetry(),
    )
    assert report["status"] == "fail"
    assert "incompatible_rejections_deterministic" in report["failed_gates"]


def test_version_negotiation_contract_is_deterministic() -> None:
    assert build_version_negotiation_contract() == build_version_negotiation_contract()


def test_version_negotiation_history_appends_snapshot() -> None:
    report = evaluate_version_negotiation_gate(
        run_id="run-feature-16-history",
        mode="ci",
        handshake=_handshake(),
        compatibility=_compatibility(),
        telemetry=_telemetry(),
    )
    history = update_version_negotiation_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-16-history"

