"""Which hard-stop IDs are evaluated for a given mode + on-disk layout.

Must stay aligned with ``evaluate_hard_stops`` in ``hard_stops.py`` (ordering
and gating only — pass/fail is evaluated separately).
"""

from __future__ import annotations

import json
from pathlib import Path


def _coding_only(output_dir: Path) -> bool:
    path = output_dir / "summary.json"
    if not path.is_file():
        return False
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return body.get("run_class") == "coding_only"


def expected_hard_stop_ids(mode: str, output_dir: Path) -> list[str]:
    out: list[str] = []
    out.extend(f"HS{i:02d}" for i in range(1, 7))
    if mode in ("guarded_pipeline", "phased_pipeline"):
        if (output_dir / "program" / "project_plan.json").is_file():
            out.extend(f"HS{i:02d}" for i in range(7, 17))
    if _coding_only(output_dir):
        return out
    if (output_dir / "replay_manifest.json").is_file():
        out.extend(f"HS{i:02d}" for i in range(17, 21))
    if (output_dir / "memory" / "retrieval_bundle.json").is_file():
        out.extend(f"HS{i:02d}" for i in range(21, 25))
    if (output_dir / "learning" / "reflection_bundle.json").is_file():
        out.extend(f"HS{i:02d}" for i in range(25, 29))
    if (output_dir / "coordination" / "lease_table.json").is_file():
        out.extend(f"HS{i:02d}" for i in range(29, 33))
    return out
