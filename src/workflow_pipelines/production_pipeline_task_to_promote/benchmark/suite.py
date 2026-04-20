"""Load and validate benchmark suite JSONL."""

from __future__ import annotations

import json
from pathlib import Path

from safeguards.safeguards import validate_task_payload

from .offline_eval_contract import validate_suite_document


def read_suite(suite_path: str) -> list[dict]:
    path = Path(suite_path)
    if not path.is_file():
        raise FileNotFoundError(suite_path)
    text = path.read_text(encoding="utf-8")
    pre = validate_suite_document(text)
    if pre:
        raise ValueError("offline_eval_suite_contract: " + "; ".join(pre))
    rows: list[dict] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        payload = {
            "taskId": raw.get("taskId", raw.get("task_id")),
            "prompt": raw["prompt"],
            "expectedChecks": raw.get("expectedChecks", raw.get("expected_checks", [])),
            "difficulty": raw["difficulty"],
        }
        rows.append(validate_task_payload(payload))
    return rows
