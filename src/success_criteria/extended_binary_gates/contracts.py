"""Contracts for extended binary gates artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EXTENDED_BINARY_GATES_CONTRACT = "sde.extended_binary_gates.v1"
EXTENDED_BINARY_GATES_SCHEMA_VERSION = "1.0"


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
    gates = body.get("gates")
    if not isinstance(gates, dict):
        errs.append("extended_binary_gates_gates")
        return errs
    required = ("reliability_gate", "delivery_gate", "governance_gate", "learning_gate")
    for key in required:
        value = gates.get(key)
        if not isinstance(value, bool):
            errs.append(f"extended_binary_gates_gate_type:{key}")
    return errs


def validate_extended_binary_gates_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["extended_binary_gates_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["extended_binary_gates_json"]
    return validate_extended_binary_gates_dict(body)

