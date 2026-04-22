"""Runtime for feature 16 contract-version negotiation."""

from __future__ import annotations

from typing import Any

from .contracts import VERSION_NEGOTIATION_SCHEMA, VERSION_NEGOTIATION_SCHEMA_VERSION


def build_version_negotiation_contract() -> dict[str, object]:
    return {
        "handshake_defined": True,
        "version_range_advertisement": True,
        "fallback_selection": True,
        "incompatible_hard_reject": True,
        "dual_version_rollback_safe": True,
        "deprecation_window_enforced": True,
        "telemetry_emitted": True,
    }


def summarize_version_negotiation_health(
    *, handshake: dict[str, Any], compatibility: dict[str, Any], telemetry: dict[str, Any]
) -> dict[str, bool]:
    return {
        "handshake_implemented": handshake.get("handshake_implemented") is True,
        "version_ranges_advertised_selected": compatibility.get("version_ranges_advertised_selected") is True,
        "incompatible_rejections_deterministic": compatibility.get("incompatible_rejections_deterministic") is True,
        "dual_version_rollback_safe": compatibility.get("dual_version_rollback_safe") is True,
        "deprecation_windows_enforced_tested": compatibility.get("deprecation_windows_enforced_tested") is True,
        "negotiated_version_telemetry_tracked": telemetry.get("negotiated_version_telemetry_tracked") is True,
        "mixed_version_fleet_scenarios_tested": compatibility.get("mixed_version_fleet_scenarios_tested") is True,
        "rollout_gated_on_compat_failures": compatibility.get("rollout_gated_on_compat_failures") is True,
    }


def evaluate_version_negotiation_gate(
    *,
    run_id: str,
    mode: str,
    handshake: dict[str, Any],
    compatibility: dict[str, Any],
    telemetry: dict[str, Any],
) -> dict[str, Any]:
    checks = summarize_version_negotiation_health(
        handshake=handshake,
        compatibility=compatibility,
        telemetry=telemetry,
    )
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": VERSION_NEGOTIATION_SCHEMA,
        "schema_version": VERSION_NEGOTIATION_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "failed_gates": failed_gates,
        "negotiation_contract": build_version_negotiation_contract(),
        "evidence": {
            "handshake_ref": "data/version_negotiation/handshake.json",
            "compatibility_ref": "data/version_negotiation/compatibility.json",
            "telemetry_ref": "data/version_negotiation/telemetry.json",
            "history_ref": "data/version_negotiation/trend_history.jsonl",
        },
    }


def update_version_negotiation_history(
    *, existing: list[dict[str, Any]], report: dict[str, Any]
) -> list[dict[str, Any]]:
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
    }
    return [*existing, row]

