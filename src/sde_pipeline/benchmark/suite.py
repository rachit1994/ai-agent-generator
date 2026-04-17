"""Load and validate benchmark suite JSONL."""

from __future__ import annotations

import json
from pathlib import Path

from sde_foundations.safeguards import validate_task_payload


def read_suite(suite_path: str) -> list[dict]:
    rows: list[dict] = []
    for line in Path(suite_path).read_text(encoding="utf-8").splitlines():
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
