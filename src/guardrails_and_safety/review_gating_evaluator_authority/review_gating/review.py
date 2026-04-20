"""Build review.json from run outcome and artifact presence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from guardrails_and_safety.risk_budgets_permission_matrix.gates_constants.constants import (
    REQUIRED_REVIEW_KEYS,
    REVIEW_SCHEMA,
)
from guardrails_and_safety.risk_budgets_permission_matrix.gates_manifest.manifest import manifest_entries, manifest_paths_for_review
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.metrics_helpers import metrics_from_events, reliability_gate
from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import iso_now

_STATIC_GATES_REPORT = "static_gates_report.json"
_REVIEW_FINDING_REQUIRED_KEYS = ("severity", "code", "message", "evidence_ref")
_REVIEW_FINDING_SEVERITIES = frozenset({"blocker", "warn", "info"})


def _normalize_review_severity(raw: str | None) -> str:
    s = (raw or "").lower()
    if s in ("blocker", "error", "critical", "high"):
        return "blocker"
    if s in ("warn", "warning", "medium"):
        return "warn"
    return "info"


def _review_findings_from_static_gates(output_dir: Path) -> list[dict[str, Any]]:
    path = output_dir / _STATIC_GATES_REPORT
    if not path.is_file():
        return []
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [
            {
                "severity": "warn",
                "code": "static_gates_unreadable",
                "message": f"{_STATIC_GATES_REPORT} is not valid JSON",
                "evidence_ref": _STATIC_GATES_REPORT,
            }
        ]
    out: list[dict[str, Any]] = []
    for b in body.get("blockers") or []:
        if not isinstance(b, dict):
            continue
        bid = str(b.get("id") or "static_blocker")
        detail = b.get("detail") or b.get("pattern") or ""
        msg = f"{bid}:{detail}" if detail else bid
        out.append(
            {
                "severity": _normalize_review_severity(str(b.get("severity"))),
                "code": bid,
                "message": msg[:2000],
                "evidence_ref": _STATIC_GATES_REPORT,
            }
        )
    for w in body.get("warnings") or []:
        if not isinstance(w, dict):
            continue
        wid = str(w.get("id") or "static_warning")
        detail = w.get("pattern") or w.get("detail") or ""
        msg = f"{wid}:{detail}" if detail else wid
        out.append(
            {
                "severity": "warn",
                "code": wid,
                "message": msg[:2000],
                "evidence_ref": _STATIC_GATES_REPORT,
            }
        )
    return out


def _terminal_review_findings(status: str, reasons: list[str]) -> list[dict[str, Any]]:
    if status == "completed_review_fail":
        return [
            {
                "severity": "blocker",
                "code": "verifier_or_checks_failed",
                "message": "Verifier or structured checks did not pass (see traces / verifier_report).",
                "evidence_ref": "traces.jsonl",
            }
        ]
    if status == "incomplete":
        return [
            {
                "severity": "warn",
                "code": "run_incomplete",
                "message": f"Run did not finish cleanly ({reasons[0] if reasons else 'unknown'}).",
                "evidence_ref": "summary.json",
            }
        ]
    if reasons == ["safety_refusal_terminal"]:
        return [
            {
                "severity": "info",
                "code": "safety_refusal_terminal",
                "message": "Task refused as unsafe; terminal safety outcome.",
                "evidence_ref": "review.json#refusal",
            }
        ]
    return []


def _review_findings_from_manifest(manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in manifest:
        if not isinstance(row, dict) or row.get("present"):
            continue
        rel = str(row.get("path") or "unknown")
        out.append(
            {
                "severity": "warn",
                "code": "artifact_manifest_missing",
                "message": f"missing:{rel}",
                "evidence_ref": rel,
            }
        )
    return out


def is_evaluator_pass_eligible(review: dict[str, Any]) -> bool:
    """Evaluator authority: only pass terminal reviews without blocker findings."""
    if str(review.get("status") or "") != "completed_review_pass":
        return False
    findings = review.get("review_findings")
    if not isinstance(findings, list):
        return False
    for item in findings:
        if not isinstance(item, dict):
            return False
        if str(item.get("severity") or "").lower() == "blocker":
            return False
    return True


def validate_review_payload(review: dict[str, Any]) -> list[str]:
    """Validate review.json contract needed by review-gating evaluator authority."""
    errors: list[str] = []
    for key in REQUIRED_REVIEW_KEYS:
        if key not in review:
            errors.append(f"missing_review_key:{key}")
    if review.get("schema_version") != REVIEW_SCHEMA:
        errors.append("invalid_review_schema_version")
    findings = review.get("review_findings")
    if not isinstance(findings, list):
        errors.append("review_findings_not_list")
        return errors
    for idx, item in enumerate(findings):
        if not isinstance(item, dict):
            errors.append(f"review_finding_not_object:{idx}")
            continue
        for key in _REVIEW_FINDING_REQUIRED_KEYS:
            if key not in item:
                errors.append(f"review_finding_missing_key:{idx}:{key}")
        sev = str(item.get("severity") or "").lower()
        if sev not in _REVIEW_FINDING_SEVERITIES:
            errors.append(f"review_finding_invalid_severity:{idx}:{sev}")
    return errors


def build_review(
    run_id: str,
    mode: str,
    parsed: dict[str, Any],
    output_dir: Path,
    events: list[dict[str, Any]],
    *,
    run_status: str,
) -> dict[str, Any]:
    refusal = parsed.get("refusal")
    finals = [e for e in events if e.get("stage") == "finalize"]
    passed = bool(finals and finals[-1].get("score", {}).get("passed"))
    if run_status != "ok":
        status = "incomplete"
        reasons = [f"run_{run_status}"]
    elif isinstance(refusal, dict) and refusal.get("code") == "unsafe_action_refused":
        status = "completed_review_pass"
        reasons = ["safety_refusal_terminal"]
    elif passed:
        status = "completed_review_pass"
        reasons = []
    else:
        status = "completed_review_fail"
        reasons = ["verifier_or_checks_failed"]
    is_safety_refusal = isinstance(refusal, dict) and refusal.get("code") == "unsafe_action_refused"
    include_completion = mode in ("guarded_pipeline", "phased_pipeline") and not is_safety_refusal
    paths = manifest_paths_for_review(mode, include_guarded_completion=include_completion)
    manifest = manifest_entries(output_dir, paths)
    manifest_complete = all(m["present"] for m in manifest)
    met = metrics_from_events(events)
    static_analysis = "validating"
    sg_path = output_dir / _STATIC_GATES_REPORT
    if sg_path.is_file():
        try:
            sg_body = json.loads(sg_path.read_text(encoding="utf-8"))
            static_analysis = "pass" if sg_body.get("passed_all") else "fail"
        except json.JSONDecodeError:
            static_analysis = "fail"
    gate_snapshot = {
        "reliability": "pass" if reliability_gate(met) else "validating",
        "safety": "pass" if status in ("completed_review_pass",) or reasons == ["safety_refusal_terminal"] else "validating",
        "replay": "pass" if len(events) > 0 else "fail",
        "resource_budget": "validating",
        "token_context": "validating",
        "static_analysis": static_analysis,
    }
    fixes: list[str] = []
    if not manifest_complete:
        fixes.append("restore_missing_artifacts")
    if status == "completed_review_fail":
        fixes.append("address_verifier_issues")
    review_findings = (
        _review_findings_from_static_gates(output_dir)
        + _review_findings_from_manifest(manifest)
        + _terminal_review_findings(status, reasons)
    )
    return {
        "schema_version": REVIEW_SCHEMA,
        "run_id": run_id,
        "status": status,
        "reasons": reasons,
        "required_fixes": fixes,
        "gate_snapshot": gate_snapshot,
        "artifact_manifest": manifest,
        "review_findings": review_findings,
        "completed_at": iso_now(),
    }
