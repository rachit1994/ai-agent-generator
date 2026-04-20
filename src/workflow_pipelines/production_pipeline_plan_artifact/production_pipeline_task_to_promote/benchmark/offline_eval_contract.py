"""Structural contract for disk-backed offline benchmark suites (JSONL)."""

from __future__ import annotations

import json
from pathlib import Path

OFFLINE_EVAL_SUITE_CONTRACT = "sde.offline_eval_suite.v1"


def validate_suite_document(text: str) -> list[str]:
    """Return stable error tokens for JSONL **content** (no path I/O)."""
    lines = text.splitlines()
    nonempty = [ln for ln in lines if ln.strip()]
    if not nonempty:
        return ["offline_eval_suite_empty"]
    errs: list[str] = []
    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            errs.append(f"offline_eval_suite_line_{idx}_json")
            continue
        if not isinstance(raw, dict):
            errs.append(f"offline_eval_suite_line_{idx}_not_object")
            continue
        tid = raw.get("taskId", raw.get("task_id"))
        if tid is None or (isinstance(tid, str) and not tid.strip()):
            errs.append(f"offline_eval_suite_line_{idx}_task_id")
        prompt = raw.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            errs.append(f"offline_eval_suite_line_{idx}_prompt")
        if "difficulty" not in raw:
            errs.append(f"offline_eval_suite_line_{idx}_difficulty")
        ec = raw.get("expectedChecks", raw.get("expected_checks"))
        if ec is not None and not isinstance(ec, list):
            errs.append(f"offline_eval_suite_line_{idx}_expected_checks")
    return errs


def validate_suite_jsonl(path: Path) -> list[str]:
    """Return stable error tokens; empty list means the file is structurally acceptable."""
    if not path.is_file():
        return ["offline_eval_suite_file_missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ["offline_eval_suite_unreadable"]
    return validate_suite_document(text)
