"""Run directory profile flags shared across hard-stop extensions."""

from __future__ import annotations

import json
from pathlib import Path


def is_coding_only(output_dir: Path) -> bool:
    path = output_dir / "summary.json"
    if not path.is_file():
        return False
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return body.get("run_class") == "coding_only"
