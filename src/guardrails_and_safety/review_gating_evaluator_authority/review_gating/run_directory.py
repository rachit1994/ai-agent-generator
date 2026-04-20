"""Validate a completed run directory against the V1 artifact contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from guardrails_and_safety.risk_budgets_permission_matrix.gates_manifest.manifest import all_required_execution_paths
from guardrails_and_safety.rollback_rules_policy_bundle.policy_bundle_rollback import validate_policy_bundle_rollback
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.balanced_gates import validation_ready
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops import evaluate_hard_stops
from guardrails_and_safety.review_gating_evaluator_authority.review_gating.review import (
    is_evaluator_pass_eligible,
    validate_review_payload,
)


def validate_execution_run_directory(output_dir: Path, *, mode: str) -> dict[str, Any]:
    """Quality gate for tests and CI: verify V1 artifact contract on a completed run directory."""
    errors: list[str] = []
    if not (output_dir / "summary.json").is_file():
        errors.append("missing_summary_json")
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8")) if not errors else {}
    if "balanced_gates" not in summary:
        errors.append("missing_balanced_gates")
    review: dict[str, Any] = {}
    if not (output_dir / "review.json").is_file():
        errors.append("missing_review_json")
    else:
        review = json.loads((output_dir / "review.json").read_text(encoding="utf-8"))
        errors.extend(validate_review_payload(review))
        if review.get("status") == "completed_review_pass" and not is_evaluator_pass_eligible(review):
            errors.append("review_pass_not_evaluator_eligible")
    if not (output_dir / "token_context.json").is_file():
        errors.append("missing_token_context_json")
    if not (output_dir / "outputs").is_dir():
        errors.append("missing_outputs_dir")
    out_files = list((output_dir / "outputs").glob("*")) if (output_dir / "outputs").is_dir() else []
    if len(out_files) < 2:
        errors.append("outputs_dir_needs_at_least_two_entries")
    for rel in all_required_execution_paths(mode, output_dir):
        if not (output_dir / rel).exists():
            errors.append(f"missing:{rel}")
    errors.extend(validate_policy_bundle_rollback(output_dir))
    events: list[dict[str, Any]] = []
    traces = output_dir / "traces.jsonl"
    if traces.is_file():
        events = [json.loads(line) for line in traces.read_text(encoding="utf-8").splitlines() if line.strip()]
    token_path = output_dir / "token_context.json"
    token_ctx = json.loads(token_path.read_text(encoding="utf-8")) if token_path.is_file() else {}
    hard = evaluate_hard_stops(
        output_dir,
        events,
        token_ctx,
        run_status=summary.get("runStatus", "ok"),
        mode=mode,
    )
    ready = validation_ready(summary["balanced_gates"]) if summary.get("balanced_gates") else False
    strict_ok = ready and not errors
    return {"ok": strict_ok, "errors": errors, "hard_stops": hard, "validation_ready": ready}
