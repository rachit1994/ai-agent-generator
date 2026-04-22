"""Contracts for extended binary gates artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EXTENDED_BINARY_GATES_CONTRACT = "sde.extended_binary_gates.v1"
EXTENDED_BINARY_GATES_SCHEMA_VERSION = "1.0"


def _validate_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["extended_binary_gates_execution"]
    errs: list[str] = []
    int_fields = (
        "events_processed",
        "finalize_events_processed",
        "malformed_event_rows",
        "checks_processed",
    )
    for field in int_fields:
        value = execution.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errs.append(f"extended_binary_gates_execution_type:{field}")
    if not isinstance(execution.get("strict_boolean_violations"), list):
        errs.append("extended_binary_gates_execution_type:strict_boolean_violations")
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["extended_binary_gates_evidence"]
    errs: list[str] = []
    for key in ("traces_ref", "checks_ref", "skill_nodes_ref"):
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"extended_binary_gates_evidence_ref:{key}")
    if evidence.get("traces_ref") != "traces.jsonl":
        errs.append("extended_binary_gates_evidence_ref:traces_ref_canonical")
    if evidence.get("checks_ref") != "summary.json":
        errs.append("extended_binary_gates_evidence_ref:checks_ref_canonical")
    if evidence.get("skill_nodes_ref") != "capability/skill_nodes.json":
        errs.append("extended_binary_gates_evidence_ref:skill_nodes_ref_canonical")
    return errs


def _validate_gates(gates: Any, overall_pass: Any) -> list[str]:
    if not isinstance(gates, dict):
        return ["extended_binary_gates_gates"]
    errs: list[str] = []
    required = ("reliability_gate", "delivery_gate", "governance_gate", "learning_gate")
    for key in required:
        value = gates.get(key)
        if not isinstance(value, bool):
            errs.append(f"extended_binary_gates_gate_type:{key}")
    if isinstance(overall_pass, bool):
        gate_values = [gates.get(key) for key in required]
        if all(isinstance(value, bool) for value in gate_values):
            expected_overall_pass = all(gate_values)
            if overall_pass != expected_overall_pass:
                errs.append("extended_binary_gates_overall_pass_mismatch")
    return errs


def validate_extended_binary_gates_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["extended_binary_gates_not_object"]
    errs: list[str] = []
    if body.get("schema") != EXTENDED_BINARY_GATES_CONTRACT:
        errs.append("extended_binary_gates_schema")
    if body.get("schema_version") != EXTENDED_BINARY_GATES_SCHEMA_VERSION:
        errs.append("extended_binary_gates_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("extended_binary_gates_run_id")
    overall_pass = body.get("overall_pass")
    if not isinstance(overall_pass, bool):
        errs.append("extended_binary_gates_overall_pass")
    errs.extend(_validate_execution(body.get("execution")))
    errs.extend(_validate_gates(body.get("gates"), overall_pass))
    errs.extend(_validate_evidence(body.get("evidence")))
    return errs


def validate_extended_binary_gates_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["extended_binary_gates_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["extended_binary_gates_json"]
    return validate_extended_binary_gates_dict(body)

