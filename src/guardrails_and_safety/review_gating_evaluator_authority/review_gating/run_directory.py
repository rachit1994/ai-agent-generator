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

def _read_json_file(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, f"missing:{path.name}"
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, f"invalid_json:{path.name}"
    if not isinstance(body, dict):
        return None, f"json_not_object:{path.name}"
    return body, None


def validate_execution_run_directory(output_dir: Path, *, mode: str) -> dict[str, Any]:
    """Quality gate for tests and CI: verify V1 artifact contract on a completed run directory."""
    errors: list[str] = []
    summary, summary_error = _read_json_file(output_dir / "summary.json")
    if summary_error:
        errors.append("missing_summary_json" if summary_error == "missing:summary.json" else summary_error)
        summary = {}
    if "balanced_gates" not in summary:
        errors.append("missing_balanced_gates")
    review: dict[str, Any] = {}
    review_body, review_error = _read_json_file(output_dir / "review.json")
    if review_error:
        errors.append("missing_review_json" if review_error == "missing:review.json" else review_error)
    else:
        review = review_body or {}
        errors.extend(validate_review_payload(review))
        if review.get("status") == "completed_review_pass" and not is_evaluator_pass_eligible(review):
            errors.append("review_pass_not_evaluator_eligible")
    token_ctx_body, token_ctx_error = _read_json_file(output_dir / "token_context.json")
    if token_ctx_error:
        errors.append("missing_token_context_json" if token_ctx_error == "missing:token_context.json" else token_ctx_error)
        token_ctx_body = {}
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
        for idx, line in enumerate(traces.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"invalid_jsonl:traces.jsonl:{idx + 1}")
                continue
            if isinstance(row, dict):
                events.append(row)
            else:
                errors.append(f"jsonl_not_object:traces.jsonl:{idx + 1}")
    hard = evaluate_hard_stops(
        output_dir,
        events,
        token_ctx_body or {},
        run_status=summary.get("runStatus", "ok"),
        mode=mode,
    )
    failed_hard_stop_ids = [str(row.get("id")) for row in hard if not bool(row.get("passed"))]
    for hs_id in failed_hard_stop_ids:
        errors.append(f"hard_stop_failed:{hs_id}")
    ready = validation_ready(summary["balanced_gates"]) if summary.get("balanced_gates") else False
    strict_ok = ready and not errors and len(failed_hard_stop_ids) == 0
    return {"ok": strict_ok, "errors": errors, "hard_stops": hard, "validation_ready": ready}
