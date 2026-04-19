"""Programmatic planned-vs-remaining work evaluator."""

from __future__ import annotations

import json
import re

from pathlib import Path
from typing import Any


CHECKBOX_RE = re.compile(r"^\s*-\s*\[[xX ]\]\s+(?P<label>.+?)\s*$")


def load_remaining_work_rules(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema_version") != "1.0":
        raise ValueError("invalid_rules_schema")
    if not isinstance(raw.get("items"), list) or not raw["items"]:
        raise ValueError("rules_items_required")
    return raw


def _checklist_rows(path: Path) -> list[str]:
    rows: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = CHECKBOX_RE.match(line)
        if match:
            rows.append(match.group("label").strip())
    return rows


def _doc_evidence(repo_root: Path, evidence: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for entry in evidence:
        rel = str(entry.get("path", ""))
        text = (repo_root / rel).read_text(encoding="utf-8") if rel and (repo_root / rel).is_file() else ""
        for marker in entry.get("contains", []):
            if marker not in text:
                missing.append(f"{rel}:{marker}")
    return len(missing) == 0, missing


def _code_evidence(repo_root: Path, evidence: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for entry in evidence:
        for rel in entry.get("paths_exist", []):
            if not (repo_root / rel).exists():
                missing.append(str(rel))
    return len(missing) == 0, missing


def evaluate_remaining_work(repo_root: Path, rules: dict[str, Any]) -> dict[str, Any]:
    checklist_path = repo_root / str(rules.get("checklist_path", ""))
    checklist_rows = _checklist_rows(checklist_path)
    markers = [str(item.get("checklist_marker", "")) for item in rules["items"]]
    unmapped = [row for row in checklist_rows if not any(m and m in row for m in markers)]
    if unmapped:
        raise ValueError(f"unmapped_checklist_items:{len(unmapped)}")
    status_values = rules.get("status_values", {"missing": 0.0, "partial": 0.4, "implemented": 1.0})
    items: dict[str, Any] = {}
    item_order: list[str] = []
    weighted = 0.0
    total_weight = 0.0
    for item in rules["items"]:
        item_id = str(item["id"])
        item_order.append(item_id)
        weight = float(item.get("weight", 1.0))
        doc_ok, missing_doc = _doc_evidence(repo_root, item.get("doc_evidence", []))
        code_ok, missing_code = _code_evidence(repo_root, item.get("code_evidence", []))
        if doc_ok and code_ok:
            status = "implemented"
        elif (not doc_ok) and (not code_ok):
            status = "missing"
        else:
            status = "partial"
        weighted += float(status_values[status]) * weight
        total_weight += weight
        items[item_id] = {
            "label": item.get("label"),
            "status": status,
            "weight": weight,
            "missing_doc_markers": missing_doc,
            "missing_code_paths": missing_code,
        }
    completion = (weighted / total_weight * 100.0) if total_weight > 0 else 0.0
    gates: dict[str, Any] = {}
    for gate in rules.get("gates", []):
        req = [str(x) for x in gate.get("required_item_ids", [])]
        gates[str(gate["id"])] = {
            "required_item_ids": req,
            "passed": all(items.get(x, {}).get("status") == "implemented" for x in req),
        }
    return {
        "schema_version": "1.0",
        "completion_pct": round(completion, 2),
        "remaining_pct": round(max(0.0, 100.0 - completion), 2),
        "item_order": item_order,
        "items": items,
        "gates": gates,
        "unmapped_checklist_items": unmapped,
    }


def render_remaining_work_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Programmatic Remaining Work",
        "",
        f"- Completion: {result['completion_pct']:.2f}%",
        f"- Remaining: {result['remaining_pct']:.2f}%",
        "",
        "## Items",
    ]
    for item_id in result.get("item_order", []):
        row = result["items"][item_id]
        lines.append(f"- `{item_id}`: {row['status']} (weight={row['weight']})")
    lines.append("")
    lines.append("## Gates")
    for gate_id in sorted(result.get("gates", {}).keys()):
        lines.append(f"- `{gate_id}`: {'passed' if result['gates'][gate_id]['passed'] else 'failed'}")
    return "\n".join(lines) + "\n"
