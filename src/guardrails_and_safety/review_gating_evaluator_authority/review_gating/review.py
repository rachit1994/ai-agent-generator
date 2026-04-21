"""Build review.json from run outcome and artifact presence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_organization.reviewer_evaluator_agents.evaluator import (
    is_review_pass_evaluator_eligible,
    validate_review_payload_contract,
)
from agent_organization.reviewer_evaluator_agents.findings import compose_review_findings
from guardrails_and_safety.risk_budgets_permission_matrix.gates_constants.constants import REVIEW_SCHEMA
from guardrails_and_safety.risk_budgets_permission_matrix.gates_manifest.manifest import manifest_entries, manifest_paths_for_review
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.metrics_helpers import metrics_from_events, reliability_gate
from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import iso_now

_STATIC_GATES_REPORT = "static_gates_report.json"


def _review_findings_from_static_gates(output_dir: Path) -> list[dict[str, Any]]:
    """Compatibility shim for existing tests expecting this helper."""
    return compose_review_findings(output_dir, [], "completed_review_pass", [])


def is_evaluator_pass_eligible(review: dict[str, Any]) -> bool:
    return is_review_pass_evaluator_eligible(review)


def validate_review_payload(review: dict[str, Any]) -> list[str]:
    return validate_review_payload_contract(review)


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
    review_findings = compose_review_findings(output_dir, manifest, status, reasons)
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
