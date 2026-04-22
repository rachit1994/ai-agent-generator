from __future__ import annotations

from typing import Any

from .contracts import IDEMPOTENCY_SCHEMA, IDEMPOTENCY_SCHEMA_VERSION


def build_idempotency_contract() -> dict[str, object]:
    return {
        "invocation_path_idempotency": True,
        "global_dedupe_ledger_services_plugins": True,
        "api_key_validation_replay_semantics": True,
        "concurrent_duplicate_write_safety": True,
        "external_side_effect_deduplication_outbox": True,
        "conflict_response_semantics": True,
        "ttl_replay_policy": True,
        "idempotency_metrics_alerts": True,
    }


def _valid_status(value: Any) -> bool:
    return value in {"hit", "miss", "conflict"}


def _valid_metrics(metrics: Any) -> bool:
    if not isinstance(metrics, dict):
        return False
    hits = metrics.get("hits")
    misses = metrics.get("misses")
    conflicts = metrics.get("conflicts")
    total_requests = metrics.get("total_requests")
    return (
        isinstance(hits, int)
        and hits >= 0
        and isinstance(misses, int)
        and misses >= 0
        and isinstance(conflicts, int)
        and conflicts >= 0
        and isinstance(total_requests, int)
        and total_requests == (hits + misses + conflicts)
    )


def _lock_duration_within_ttl(ledger_state: dict[str, Any]) -> bool:
    dedupe_lock_held_ms = ledger_state.get("dedupe_lock_held_ms")
    ttl_seconds = ledger_state.get("ttl_seconds")
    return (
        isinstance(dedupe_lock_held_ms, int)
        and dedupe_lock_held_ms >= 0
        and isinstance(ttl_seconds, int)
        and ttl_seconds > 0
        and dedupe_lock_held_ms <= ttl_seconds * 1000
    )


def summarize_idempotency_health(*, api_state: dict[str, Any], ledger_state: dict[str, Any], side_effects_state: dict[str, Any]) -> dict[str, bool]:
    return {
        "invocation_path_idempotency": api_state.get("invocation_path_idempotency") is True
        and isinstance(api_state.get("idempotency_key"), str)
        and api_state.get("idempotency_key").strip() != "",
        "global_dedupe_ledger_services_plugins": ledger_state.get("global_dedupe_ledger_services_plugins") is True
        and isinstance(ledger_state.get("ledger_partition"), str)
        and ledger_state.get("ledger_partition").strip() != "",
        "api_key_validation_replay_semantics": api_state.get("api_key_validation_replay_semantics") is True
        and _valid_status(api_state.get("replay_status")),
        "concurrent_duplicate_write_safety": ledger_state.get("concurrent_duplicate_write_safety") is True
        and _lock_duration_within_ttl(ledger_state),
        "external_side_effect_deduplication_outbox": side_effects_state.get("external_side_effect_deduplication_outbox") is True
        and isinstance(side_effects_state.get("outbox_events"), list)
        and len(side_effects_state.get("outbox_events")) > 0,
        "conflict_response_semantics": api_state.get("conflict_response_semantics") is True
        and isinstance(api_state.get("conflict_code"), str)
        and api_state.get("conflict_code").strip() != "",
        "ttl_replay_policy": ledger_state.get("ttl_replay_policy") is True
        and isinstance(ledger_state.get("ttl_seconds"), int)
        and ledger_state.get("ttl_seconds") > 0,
        "idempotency_metrics_alerts": side_effects_state.get("idempotency_metrics_alerts") is True
        and _valid_metrics(side_effects_state.get("metrics")),
    }


def evaluate_idempotency_gate(*, run_id: str, mode: str, api_state: dict[str, Any], ledger_state: dict[str, Any], side_effects_state: dict[str, Any]) -> dict[str, Any]:
    checks = summarize_idempotency_health(api_state=api_state, ledger_state=ledger_state, side_effects_state=side_effects_state)
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": IDEMPOTENCY_SCHEMA,
        "schema_version": IDEMPOTENCY_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "failed_gates": failed_gates,
        "idempotency_contract": build_idempotency_contract(),
        "evidence": {
            "api_ref": "data/idempotency/api_state.json",
            "ledger_ref": "data/idempotency/ledger_state.json",
            "effects_ref": "data/idempotency/side_effects_state.json",
            "history_ref": "data/idempotency/trend_history.jsonl",
        },
    }


def update_idempotency_history(*, existing: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
    }
    return [*existing, row]
