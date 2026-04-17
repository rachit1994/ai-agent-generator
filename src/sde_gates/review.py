"""Build review.json from run outcome and artifact presence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import REVIEW_SCHEMA
from .manifest import manifest_entries, manifest_paths_for_review
from .metrics_helpers import metrics_from_events, reliability_gate
from .time_util import iso_now


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
    paths = manifest_paths_for_review(mode)
    manifest = manifest_entries(output_dir, paths)
    manifest_complete = all(m["present"] for m in manifest)
    met = metrics_from_events(events)
    gate_snapshot = {
        "reliability": "pass" if reliability_gate(met) else "validating",
        "safety": "pass" if status in ("completed_review_pass",) or reasons == ["safety_refusal_terminal"] else "validating",
        "replay": "pass" if len(events) > 0 else "fail",
        "resource_budget": "validating",
        "token_context": "validating",
    }
    fixes: list[str] = []
    if not manifest_complete:
        fixes.append("restore_missing_artifacts")
    if status == "completed_review_fail":
        fixes.append("address_verifier_issues")
    return {
        "schema_version": REVIEW_SCHEMA,
        "run_id": run_id,
        "status": status,
        "reasons": reasons,
        "required_fixes": fixes,
        "gate_snapshot": gate_snapshot,
        "artifact_manifest": manifest,
        "completed_at": iso_now(),
    }
