"""Heuristic verification and JSON helpers for verifier stages."""

from __future__ import annotations

import json

from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.static_analysis import blocking_ids, run_static_code_gates


def heuristic_verify(_task: str, _planning_doc: str, code: str) -> tuple[bool, list[str], dict]:
    issues: list[str] = []
    hints: list[str] = []
    normalized = code.strip()
    if not normalized:
        issues.append("empty_output")
    static_report = run_static_code_gates(extracted_python=normalized or None)
    for bid in blocking_ids(static_report):
        issues.append(f"static_gate:{bid}")
    if "eval(" in code and "static_gate:eval_call" not in issues:
        hints.append("hint_contains_eval")
    if "exec(" in code and "static_gate:exec_call" not in issues:
        hints.append("hint_contains_exec")
    for w in static_report.get("warnings") or []:
        if isinstance(w, dict) and w.get("id"):
            hints.append(f"hint_pattern:{w['id']}")
    line_len = max((len(line) for line in code.splitlines()), default=0)
    if line_len > 4000:
        hints.append("hint_very_long_line")
    passed = len(issues) == 0
    report = {
        "passed": passed,
        "issues": issues,
        "hints": hints,
        "notes": "heuristic_general_verifier",
        "static_gates": static_report,
    }
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
