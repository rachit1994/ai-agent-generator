from __future__ import annotations

import json
import re
from typing import Any


def validate_task_text(task: str) -> str:
    trimmed = task.strip()
    if not trimmed:
        raise ValueError("invalid_input_empty_task")
    return trimmed


def validate_task_payload(payload: dict[str, Any]) -> dict[str, Any]:
    required = ["taskId", "prompt", "expectedChecks", "difficulty"]
    if not all(k in payload for k in required):
        raise ValueError("invalid_task_payload")
    if payload["difficulty"] not in ["simple", "medium", "failure-prone"]:
        raise ValueError("invalid_task_payload")
    return payload


def refusal_for_unsafe(text: str) -> dict[str, Any] | None:
    normalized = text.lower()
    for marker in ["credential", "password dump", "exfiltrate", "rm -rf /"]:
        if marker in normalized:
            return {
                "answer": "",
                "checks": [{"name": "safety", "passed": False}],
                "refusal": {"code": "unsafe_action_refused", "reason": f"blocked_keyword:{marker}"},
            }
    return None


def _extract_json(text: str) -> Any:
    stripped = text.strip()
    if stripped.startswith("```"):
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", stripped, flags=re.IGNORECASE)
        if match:
            return json.loads(match.group(1))
    try:
        return json.loads(stripped)
    except Exception:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return json.loads(stripped[start : end + 1])
    raise ValueError("no_json_object_found")


def validate_structured_output(text: str) -> dict[str, Any]:
    try:
        parsed = _extract_json(text)
        if not isinstance(parsed, dict):
            raise ValueError("malformed")
        answer = parsed.get("answer")
        checks = parsed.get("checks")
        refusal = parsed.get("refusal")
        if not isinstance(answer, str):
            raise ValueError("malformed")
        if not isinstance(checks, list):
            raise ValueError("malformed")
        if len(checks) == 0:
            checks = [{"name": "response_non_empty", "passed": len(answer.strip()) > 0}]
        for check in checks:
            if not isinstance(check, dict) or "name" not in check or "passed" not in check:
                raise ValueError("malformed")
        if isinstance(refusal, list) and len(refusal) == 0:
            refusal = None
        if refusal is not None and (not isinstance(refusal, dict) or "code" not in refusal or "reason" not in refusal):
            raise ValueError("malformed")
        return {"answer": answer, "checks": checks, "refusal": refusal}
    except Exception as exc:
        fallback_answer = text.strip()
        if fallback_answer:
            return {
                "answer": fallback_answer,
                "checks": [
                    {"name": "json_schema", "passed": False},
                    {"name": "response_non_empty", "passed": True},
                ],
                "refusal": None,
            }
        return {
            "answer": "",
            "checks": [{"name": "schema", "passed": False}],
            "refusal": {
                "code": "malformed_output",
                "reason": f"output_schema_validation_failed:{type(exc).__name__}",
            },
        }
