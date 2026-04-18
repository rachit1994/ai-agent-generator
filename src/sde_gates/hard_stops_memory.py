"""HS21–HS24 memory policy checks (V5 harness)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


from .run_profile import is_coding_only


def _provenance_ids_in_event_store(output_dir: Path) -> set[str]:
    path = output_dir / "event_store" / "run_events.jsonl"
    if not path.is_file():
        return set()
    line = path.read_text(encoding="utf-8").splitlines()
    if not line or not line[0].strip():
        return set()
    try:
        env = json.loads(line[0])
    except json.JSONDecodeError:
        return set()
    eid = env.get("event_id")
    return {str(eid)} if eid else set()


def _hs21_retrieval_provenance(output_dir: Path) -> bool:
    path = output_dir / "memory" / "retrieval_bundle.json"
    if not path.is_file():
        return False
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    allowed = _provenance_ids_in_event_store(output_dir)
    if not allowed:
        return False
    for ch in body.get("chunks") or []:
        if not isinstance(ch, dict):
            return False
        pid = ch.get("provenance_id")
        if not pid or not isinstance(pid, str):
            return False
        if pid not in allowed:
            return False
    return len(body.get("chunks") or []) > 0


def _hs22_quarantine_resolved(output_dir: Path) -> bool:
    path = output_dir / "memory" / "quarantine.jsonl"
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError:
            return False
        if row.get("status") == "unresolved_contradiction":
            return False
    return True


def _hs23_skill_surface(output_dir: Path) -> bool:
    path = output_dir / "capability" / "skill_nodes.json"
    if not path.is_file():
        return False
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return body.get("schema_version") == "1.0" and isinstance(body.get("nodes"), list)


def _hs24_quality_metrics(output_dir: Path) -> bool:
    path = output_dir / "memory" / "quality_metrics.json"
    if not path.is_file():
        return False
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return body.get("schema_version") == "1.0" and "contradiction_rate" in body


def evaluate_memory_hard_stops(output_dir: Path) -> list[dict[str, Any]]:
    if is_coding_only(output_dir):
        return []
    if not (output_dir / "memory" / "retrieval_bundle.json").is_file():
        return []
    return [
        {"id": "HS21", "passed": _hs21_retrieval_provenance(output_dir), "evidence_ref": "memory/retrieval_bundle.json"},
        {"id": "HS22", "passed": _hs22_quarantine_resolved(output_dir), "evidence_ref": "memory/quarantine.jsonl"},
        {"id": "HS23", "passed": _hs23_skill_surface(output_dir), "evidence_ref": "capability/skill_nodes.json"},
        {"id": "HS24", "passed": _hs24_quality_metrics(output_dir), "evidence_ref": "memory/quality_metrics.json"},
    ]
