"""Stage 1 intake revise-loop helper for doc_review outcomes (OSV-STORY-01)."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any

from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import iso_now

from .project_intake_util import intake_doc_review_errors


def _read_doc_review(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None


def _count_revise_attempts(path: Path) -> int:
    if not path.is_file():
        return 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return 0
    count = 0
    for line in lines:
        if not line.strip():
            continue
        count += 1
    return count


def _normalize_findings(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        out: list[dict[str, Any]] = []
        for row in value:
            if isinstance(row, dict):
                out.append(row)
        return out
    if isinstance(value, dict):
        return [value]
    return []


def _autogen_revision_artifacts(intake_dir: Path, *, doc: dict[str, Any], attempt: int) -> dict[str, Any]:
    findings = _normalize_findings(doc.get("findings"))
    finding_count = len(findings)
    summary_line = (
        f"- auto-revise attempt {attempt} at {iso_now()} "
        f"(doc_review findings={finding_count})"
    )
    digest_path = intake_dir / "research_digest.md"
    if digest_path.is_file():
        try:
            existing = digest_path.read_text(encoding="utf-8")
        except OSError:
            existing = ""
    else:
        existing = ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    digest_path.write_text(existing + summary_line + "\n", encoding="utf-8")

    workbook_path = intake_dir / "question_workbook.jsonl"
    row = {
        "id": f"auto-revise-{attempt}",
        "kind": "auto_revise_question",
        "attempt": attempt,
        "at": iso_now(),
        "source": "doc_review",
        "prompt": f"Address {finding_count} doc-review findings before next intake review.",
    }
    with workbook_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")

    autogen_path = intake_dir / "revise_autogen.json"
    body = {
        "schema_version": "1.0",
        "updated_at": iso_now(),
        "last_attempt": attempt,
        "last_finding_count": finding_count,
        "status": "applied",
    }
    autogen_path.write_text(json.dumps(body, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "digest_path": str(digest_path),
        "workbook_path": str(workbook_path),
        "autogen_path": str(autogen_path),
        "finding_count": finding_count,
    }


def _parse_iso_utc_seconds(value: Any) -> int | None:
    if not isinstance(value, str) or not value.strip():
        return None
    txt = value.strip()
    if txt.endswith("Z"):
        txt = txt[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(txt)
    except ValueError:
        return None
    return int(dt.timestamp())


def _append_revise_metric(
    intake_dir: Path,
    *,
    attempt: int,
    status: str,
    blocked_human: bool,
    findings_count: int | None,
    latency_sec: int | None,
) -> str:
    path = intake_dir / "revise_metrics.jsonl"
    row: dict[str, Any] = {
        "schema_version": "1.0",
        "event": "intake_revise_result",
        "at": iso_now(),
        "attempt": attempt,
        "status": status,
        "blocked_human": blocked_human,
        "findings_count": findings_count,
        "latency_sec": latency_sec,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return str(path)


def apply_intake_doc_review_result(
    session_dir: Path,
    *,
    max_retries: int = 2,
) -> dict[str, Any]:
    """
    Process ``intake/doc_review.json`` into bounded revise-loop state.

    On failed review (``passed=False``), increments revise attempts in ``intake/revise_log.jsonl`` and
    writes ``intake/revise_state.json``. Once attempts reach ``max_retries``, state becomes
    ``blocked_human``.
    """
    session_dir = session_dir.resolve()
    if not session_dir.is_dir():
        return {"ok": False, "error": "session_dir_not_a_directory", "session_dir": str(session_dir)}
    if max_retries < 1:
        return {"ok": False, "error": "max_retries_must_be_positive", "session_dir": str(session_dir)}
    intake_dir = session_dir / "intake"
    if not intake_dir.is_dir():
        return {"ok": False, "error": "intake_dir_missing", "session_dir": str(session_dir)}
    doc_path = intake_dir / "doc_review.json"
    doc = _read_doc_review(doc_path)
    if doc is None:
        return {"ok": False, "error": "doc_review_missing_or_unreadable", "session_dir": str(session_dir)}
    schema_errors = intake_doc_review_errors(session_dir)
    if schema_errors:
        return {
            "ok": False,
            "error": "invalid_doc_review_json",
            "details": schema_errors,
            "session_dir": str(session_dir),
        }

    log_path = intake_dir / "revise_log.jsonl"
    state_path = intake_dir / "revise_state.json"
    passed = bool(doc.get("passed"))
    prev_attempts = _count_revise_attempts(log_path)
    findings_count = len(_normalize_findings(doc.get("findings")))
    now_s = _parse_iso_utc_seconds(iso_now())
    reviewed_at_s = _parse_iso_utc_seconds(doc.get("reviewed_at"))
    latency_sec = None
    if now_s is not None and reviewed_at_s is not None:
        latency_sec = max(0, now_s - reviewed_at_s)
    if passed:
        body = {
            "schema_version": "1.0",
            "status": "review_passed",
            "attempts_used": prev_attempts,
            "max_retries": max_retries,
            "updated_at": iso_now(),
        }
        state_path.write_text(json.dumps(body, indent=2), encoding="utf-8")
        metrics_path = _append_revise_metric(
            intake_dir,
            attempt=prev_attempts,
            status="review_passed",
            blocked_human=False,
            findings_count=findings_count,
            latency_sec=latency_sec,
        )
        return {
            "ok": True,
            "state": "review_passed",
            "attempts_used": prev_attempts,
            "max_retries": max_retries,
            "state_path": str(state_path),
            "metrics_path": metrics_path,
        }

    attempt = prev_attempts + 1
    regen = _autogen_revision_artifacts(intake_dir, doc=doc, attempt=attempt)
    row = {
        "attempt": attempt,
        "event": "doc_review_failed",
        "at": iso_now(),
        "auto_regen_applied": bool(regen.get("ok")),
        "auto_regen_finding_count": regen.get("finding_count"),
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    blocked = attempt >= max_retries
    status = "blocked_human" if blocked else "retry_allowed"
    body = {
        "schema_version": "1.0",
        "status": status,
        "attempts_used": attempt,
        "max_retries": max_retries,
        "remaining_retries": max(0, max_retries - attempt),
        "blocked_reason": "doc_review_failed_max_retries" if blocked else None,
        "updated_at": iso_now(),
    }
    state_path.write_text(json.dumps(body, indent=2), encoding="utf-8")
    metrics_path = _append_revise_metric(
        intake_dir,
        attempt=attempt,
        status=status,
        blocked_human=blocked,
        findings_count=findings_count,
        latency_sec=latency_sec,
    )
    return {
        "ok": True,
        "state": status,
        "attempts_used": attempt,
        "max_retries": max_retries,
        "blocked_human": blocked,
        "revise_log_path": str(log_path),
        "state_path": str(state_path),
        "auto_regen": regen,
        "metrics_path": metrics_path,
    }
