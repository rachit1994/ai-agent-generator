"""Heuristic verification and JSON helpers for verifier stages."""

from __future__ import annotations

import json


def heuristic_verify(_task: str, _planning_doc: str, code: str) -> tuple[bool, list[str], dict]:
    issues: list[str] = []
    normalized = code.strip()
    if not normalized:
        issues.append("empty_output")
    passed = len(issues) == 0
    report = {"passed": passed, "issues": issues, "notes": "heuristic_general_verifier"}
    return passed, issues, report


def extract_json_object(text: str) -> dict:
    stripped = text.strip()
    try:
        return json.loads(stripped)
    except Exception:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return json.loads(stripped[start : end + 1])
    raise ValueError("no_json")


def finalize_failure_reason(refusal: dict | None, passed: bool, issues: list[str]) -> str:
    if refusal:
        return "refusal_expected"
    if passed:
        return "none"
    if "timeout" in " ".join(issues).lower():
        return "pipeline_timeout"
    return "quality_check_fail"
