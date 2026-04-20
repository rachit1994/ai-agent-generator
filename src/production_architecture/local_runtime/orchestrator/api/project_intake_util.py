"""Shared ``intake/`` checks for driver/status/context-pack intake merge rules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json_dict(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, json.JSONDecodeError):
        return None
    return body if isinstance(body, dict) else None


def _valid_discovery_anchor(path: Path) -> bool:
    disc = _read_json_dict(path)
    if not disc:
        return False
    ge = disc.get("goal_excerpt")
    return isinstance(ge, str) and bool(ge.strip())


def _valid_doc_review_anchor(path: Path) -> bool:
    doc = _read_json_dict(path)
    if not doc:
        return False
    return len(_doc_review_schema_errors(doc)) == 0


def _doc_review_schema_errors(doc: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if not isinstance(doc.get("passed"), bool):
        errs.append("doc_review_passed_not_bool")
    findings = doc.get("findings")
    if not (isinstance(findings, list) or isinstance(findings, dict)):
        errs.append("doc_review_findings_bad_type")
    return errs


def intake_doc_review_errors(session_dir: Path) -> list[str]:
    """Return schema errors for ``intake/doc_review.json`` (empty list when file missing or valid)."""
    path = session_dir / "intake" / "doc_review.json"
    doc = _read_json_dict(path)
    if doc is None:
        return []
    return _doc_review_schema_errors(doc)


def intake_merge_anchor_present(session_dir: Path) -> bool:
    """True when ``intake/`` has schema-valid discovery/doc-review anchor content."""
    intake = session_dir / "intake"
    if not intake.is_dir():
        return False
    return _valid_discovery_anchor(intake / "discovery.json") or _valid_doc_review_anchor(
        intake / "doc_review.json"
    )
