"""Finding composition for reviewer/evaluator runtime."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STATIC_GATES_REPORT = "static_gates_report.json"


def normalize_severity(raw: str | None) -> str:
    sev = (raw or "").lower()
    if sev in ("blocker", "error", "critical", "high"):
        return "blocker"
    if sev in ("warn", "warning", "medium"):
        return "warn"
    return "info"


def _from_static_gates(output_dir: Path) -> list[dict[str, Any]]:
    path = output_dir / STATIC_GATES_REPORT
    if not path.is_file():
        return []
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [{"severity": "warn", "code": "static_gates_unreadable", "message": f"{STATIC_GATES_REPORT} is not valid JSON", "evidence_ref": STATIC_GATES_REPORT}]
    out: list[dict[str, Any]] = []
    for key, default in (("blockers", "static_blocker"), ("warnings", "static_warning")):
        for row in body.get(key) or []:
            if not isinstance(row, dict):
                continue
            code = str(row.get("id") or default)
            detail = row.get("detail") or row.get("pattern") or ""
            out.append({"severity": normalize_severity(str(row.get("severity"))) if key == "blockers" else "warn", "code": code, "message": f"{code}:{detail}" if detail else code, "evidence_ref": STATIC_GATES_REPORT})
    return out


def _from_manifest(manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in manifest:
        if isinstance(row, dict) and not row.get("present"):
            rel = str(row.get("path") or "unknown")
            out.append({"severity": "warn", "code": "artifact_manifest_missing", "message": f"missing:{rel}", "evidence_ref": rel})
    return out


def _from_terminal(status: str, reasons: list[str]) -> list[dict[str, Any]]:
    if status == "completed_review_fail":
        return [{"severity": "blocker", "code": "verifier_or_checks_failed", "message": "Verifier or structured checks did not pass (see traces / verifier_report).", "evidence_ref": "traces.jsonl"}]
    if status == "incomplete":
        reason = reasons[0] if reasons else "unknown"
        return [{"severity": "warn", "code": "run_incomplete", "message": f"Run did not finish cleanly ({reason}).", "evidence_ref": "summary.json"}]
    if reasons == ["safety_refusal_terminal"]:
        return [{"severity": "info", "code": "safety_refusal_terminal", "message": "Task refused as unsafe; terminal safety outcome.", "evidence_ref": "review.json#refusal"}]
    return []


def compose_review_findings(
    output_dir: Path, manifest: list[dict[str, Any]], status: str, reasons: list[str]
) -> list[dict[str, Any]]:
    return _from_static_gates(output_dir) + _from_manifest(manifest) + _from_terminal(status, reasons)
