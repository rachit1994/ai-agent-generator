from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_07_idempotent_invocation_side_effect_deduplication import (
    build_idempotency_contract,
    evaluate_idempotency_gate,
    update_idempotency_history,
    validate_idempotency_report_dict,
)


def _api() -> dict[str, object]:
    return {
        "invocation_path_idempotency": True,
        "idempotency_key": "idem-tenant-a-order-42",
        "api_key_validation_replay_semantics": True,
        "replay_status": "hit",
        "conflict_response_semantics": True,
        "conflict_code": "IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_PAYLOAD",
    }


def _ledger() -> dict[str, object]:
    return {
        "global_dedupe_ledger_services_plugins": True,
        "ledger_partition": "tenant-a:plugin-orders",
        "concurrent_duplicate_write_safety": True,
        "dedupe_lock_held_ms": 18,
        "ttl_replay_policy": True,
        "ttl_seconds": 86400,
    }


def _effects() -> dict[str, object]:
    return {
        "external_side_effect_deduplication_outbox": True,
        "outbox_events": ["evt-1001"],
        "idempotency_metrics_alerts": True,
        "metrics": {"hits": 24, "misses": 8, "conflicts": 1, "total_requests": 33},
    }


def test_idempotency_gate_passes_for_complete_inputs() -> None:
    report = evaluate_idempotency_gate(
        run_id="run-feature-07-pass",
        mode="ci",
        api_state=_api(),
        ledger_state=_ledger(),
        side_effects_state=_effects(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_idempotency_report_dict(report) == []


def test_idempotency_gate_fail_closes_on_missing_replay_semantics() -> None:
    api_state = _api()
    api_state["api_key_validation_replay_semantics"] = False
    report = evaluate_idempotency_gate(
        run_id="run-feature-07-fail",
        mode="preflight",
        api_state=api_state,
        ledger_state=_ledger(),
        side_effects_state=_effects(),
    )
    assert report["status"] == "fail"
    assert "api_key_validation_replay_semantics" in report["failed_gates"]


def test_idempotency_gate_fail_closes_on_invalid_replay_status() -> None:
    api_state = _api()
    api_state["replay_status"] = "unknown"
    report = evaluate_idempotency_gate(
        run_id="run-feature-07-invalid-replay-status",
        mode="preflight",
        api_state=api_state,
        ledger_state=_ledger(),
        side_effects_state=_effects(),
    )
    assert report["status"] == "fail"
    assert "api_key_validation_replay_semantics" in report["failed_gates"]


def test_idempotency_gate_fail_closes_on_metrics_total_mismatch() -> None:
    side_effects_state = _effects()
    side_effects_state["metrics"]["total_requests"] = 34
    report = evaluate_idempotency_gate(
        run_id="run-feature-07-metrics-total-mismatch",
        mode="preflight",
        api_state=_api(),
        ledger_state=_ledger(),
        side_effects_state=side_effects_state,
    )
    assert report["status"] == "fail"
    assert "idempotency_metrics_alerts" in report["failed_gates"]


def test_idempotency_gate_fail_closes_on_lock_duration_exceeding_ttl_window() -> None:
    ledger_state = _ledger()
    ledger_state["dedupe_lock_held_ms"] = 90_000_000
    report = evaluate_idempotency_gate(
        run_id="run-feature-07-lock-duration-over-ttl",
        mode="preflight",
        api_state=_api(),
        ledger_state=ledger_state,
        side_effects_state=_effects(),
    )
    assert report["status"] == "fail"
    assert "concurrent_duplicate_write_safety" in report["failed_gates"]


def test_idempotency_contract_is_deterministic() -> None:
    assert build_idempotency_contract() == build_idempotency_contract()


def test_idempotency_history_appends_row() -> None:
    report = evaluate_idempotency_gate(
        run_id="run-feature-07-history",
        mode="ci",
        api_state=_api(),
        ledger_state=_ledger(),
        side_effects_state=_effects(),
    )
    history = update_idempotency_history(existing=[], report=report)
    assert history[0]["run_id"] == "run-feature-07-history"
