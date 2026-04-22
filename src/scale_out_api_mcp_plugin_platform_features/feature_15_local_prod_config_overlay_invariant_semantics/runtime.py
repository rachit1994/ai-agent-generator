"""Runtime for feature 15 local/prod config overlay invariants."""

from __future__ import annotations

from typing import Any

from .contracts import CONFIG_OVERLAY_SCHEMA, CONFIG_OVERLAY_SCHEMA_VERSION


def build_config_overlay_contract() -> dict[str, object]:
    return {
        "shared_schema": True,
        "deterministic_precedence": ["base", "env_overlay", "runtime_override_allowlist"],
        "invariant_fields_enforced": True,
        "startup_fail_fast": True,
        "drift_detection": True,
        "secret_redaction_validation": True,
        "versioned_migrations": True,
    }


def _schema_versions_align(
    *, base_config: dict[str, Any], overlay_config: dict[str, Any], resolved_config: dict[str, Any]
) -> bool:
    base_version = base_config.get("config_schema_version")
    overlay_version = overlay_config.get("config_schema_version")
    resolved_version = resolved_config.get("config_schema_version")
    return (
        isinstance(base_version, str)
        and base_version.strip() != ""
        and base_version == overlay_version
        and base_version == resolved_version
    )


def _valid_overlay_precedence(resolved_config: dict[str, Any]) -> bool:
    applied_precedence = resolved_config.get("applied_precedence")
    expected_precedence = ["base", "env_overlay", "runtime_override_allowlist"]
    return isinstance(applied_precedence, list) and applied_precedence == expected_precedence


def _override_allowlist_hash_aligned(overlay_config: dict[str, Any], resolved_config: dict[str, Any]) -> bool:
    overlay_hash = overlay_config.get("override_allowlist_hash")
    resolved_hash = resolved_config.get("override_allowlist_hash")
    return (
        isinstance(overlay_hash, str)
        and overlay_hash.strip() != ""
        and overlay_hash == resolved_hash
    )


def summarize_config_overlay_health(
    *, base_config: dict[str, Any], overlay_config: dict[str, Any], resolved_config: dict[str, Any]
) -> dict[str, bool]:
    return {
        "shared_schema_present": base_config.get("shared_schema_present") is True
        and _schema_versions_align(
            base_config=base_config,
            overlay_config=overlay_config,
            resolved_config=resolved_config,
        ),
        "overlay_merge_deterministic": resolved_config.get("overlay_merge_deterministic") is True
        and _valid_overlay_precedence(resolved_config),
        "invariants_fail_fast_enforced": resolved_config.get("invariants_fail_fast_enforced") is True,
        "drift_detection_present": resolved_config.get("drift_detection_present") is True,
        "override_allowlist_enforced": overlay_config.get("override_allowlist_enforced") is True
        and _override_allowlist_hash_aligned(overlay_config, resolved_config),
        "secret_redaction_consistent": resolved_config.get("secret_redaction_consistent") is True,
        "versioned_migrations_supported": resolved_config.get("versioned_migrations_supported") is True,
        "adapter_overlay_tests_present": resolved_config.get("adapter_overlay_tests_present") is True,
    }


def evaluate_config_overlay_gate(
    *,
    run_id: str,
    mode: str,
    base_config: dict[str, Any],
    overlay_config: dict[str, Any],
    resolved_config: dict[str, Any],
) -> dict[str, Any]:
    checks = summarize_config_overlay_health(
        base_config=base_config,
        overlay_config=overlay_config,
        resolved_config=resolved_config,
    )
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": CONFIG_OVERLAY_SCHEMA,
        "schema_version": CONFIG_OVERLAY_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "failed_gates": failed_gates,
        "overlay_contract": build_config_overlay_contract(),
        "evidence": {
            "base_ref": "data/config_overlay/base_config.json",
            "overlay_ref": "data/config_overlay/overlay_config.json",
            "resolved_ref": "data/config_overlay/resolved_config.json",
            "history_ref": "data/config_overlay/trend_history.jsonl",
        },
    }


def update_config_overlay_history(
    *, existing: list[dict[str, Any]], report: dict[str, Any]
) -> list[dict[str, Any]]:
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
    }
    return [*existing, row]

