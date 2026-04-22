"""Runtime for feature 14 local vs production semantic parity gates."""

from __future__ import annotations

from typing import Any

from .contracts import LOCAL_PROD_PARITY_SCHEMA, LOCAL_PROD_PARITY_SCHEMA_VERSION


def build_local_prod_parity_contract() -> dict[str, object]:
    return {
        "comparators": ["semantic_outputs", "state_transitions", "errors", "authz", "idempotency"],
        "immutable_artifacts": True,
        "release_block_on_drift": True,
        "diagnostic_hints": True,
        "scheduled_regression": True,
    }


def summarize_local_prod_parity(*, local_results: dict[str, Any], prod_results: dict[str, Any]) -> dict[str, bool]:
    return {
        "semantic_outputs_match": local_results.get("semantic_outputs") == prod_results.get("semantic_outputs"),
        "state_transitions_match": local_results.get("state_transitions") == prod_results.get("state_transitions"),
        "errors_match": local_results.get("errors") == prod_results.get("errors"),
        "authz_match": local_results.get("authz") == prod_results.get("authz"),
        "idempotency_match": local_results.get("idempotency") == prod_results.get("idempotency"),
    }


def evaluate_local_prod_parity_gate(
    *,
    run_id: str,
    mode: str,
    local_results: dict[str, Any],
    prod_results: dict[str, Any],
    diff: dict[str, Any],
) -> dict[str, Any]:
    checks = summarize_local_prod_parity(local_results=local_results, prod_results=prod_results)
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": LOCAL_PROD_PARITY_SCHEMA,
        "schema_version": LOCAL_PROD_PARITY_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "failed_gates": failed_gates,
        "diagnostics": diff.get("diagnostics", []),
        "parity_contract": build_local_prod_parity_contract(),
        "evidence": {
            "local_ref": "data/local_prod_parity/local_results.json",
            "prod_ref": "data/local_prod_parity/prod_results.json",
            "diff_ref": "data/local_prod_parity/diff.json",
            "history_ref": "data/local_prod_parity/trend_history.jsonl",
        },
    }


def update_local_prod_parity_history(
    *, existing: list[dict[str, Any]], report: dict[str, Any]
) -> list[dict[str, Any]]:
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
    }
    return [*existing, row]

