"""Token context, review.json, hard-stops, balanced summary v2, second report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sde_pipeline.config import DEFAULT_CONFIG
from sde_gates import (
    build_review,
    build_token_context,
    compute_balanced_gates,
    evaluate_hard_stops,
    metrics_from_events,
    validation_ready,
)
from sde_pipeline.report import generate_report
from sde_foundations.storage import write_json


def _guarded_definition_of_done(output_dir: Path, review_status: str) -> dict[str, Any]:
    step_ok = True
    for fname in ("step_planner.json", "step_implement.json", "step_verify.json"):
        path = output_dir / "step_reviews" / fname
        if not path.is_file():
            step_ok = False
            break
        body = json.loads(path.read_text(encoding="utf-8"))
        if not body.get("passed"):
            step_ok = False
            break
    vb_passed = False
    vb_path = output_dir / "verification_bundle.json"
    if vb_path.is_file():
        vb_passed = bool(json.loads(vb_path.read_text(encoding="utf-8")).get("passed"))
    checks: list[dict[str, Any]] = [
        {
            "id": "step_reviews",
            "description": "Plan steps reviewed",
            "required": True,
            "passed": step_ok,
            "evidence_ref": "step_reviews/",
        },
        {
            "id": "verification",
            "description": "Verifier evidence",
            "required": True,
            "passed": vb_passed,
            "evidence_ref": "verification_bundle.json",
        },
    ]
    all_req = all(c["passed"] for c in checks if c["required"])
    dod_pass = all_req and review_status == "completed_review_pass"
    return {"schema_version": "1.0", "checks": checks, "all_required_passed": dod_pass}


def write_cto_gate_layer(
    *,
    run_id: str,
    mode: str,
    parsed: dict,
    events: list[dict],
    output_dir: Path,
) -> dict[str, object]:
    token_ctx = build_token_context(
        run_id,
        events,
        max_tokens=DEFAULT_CONFIG.budgets.max_tokens,
    )
    write_json(output_dir / "token_context.json", token_ctx)
    review = build_review(
        run_id,
        mode,
        parsed,
        output_dir,
        events,
        run_status="ok",
    )
    refusal = parsed.get("refusal")
    is_safety_refusal = isinstance(refusal, dict) and refusal.get("code") == "unsafe_action_refused"
    if mode in ("guarded_pipeline", "phased_pipeline") and not is_safety_refusal:
        review["definition_of_done"] = _guarded_definition_of_done(output_dir, review["status"])
    write_json(output_dir / "review.json", review)
    hard_stops = evaluate_hard_stops(output_dir, events, token_ctx, run_status="ok", mode=mode)
    manifest_complete = all(m["present"] for m in review["artifact_manifest"])
    met = metrics_from_events(events)
    balanced = compute_balanced_gates(
        met,
        hard_stops,
        review_status=review["status"],
        manifest_complete=manifest_complete,
    )
    vr = validation_ready(balanced)
    write_json(
        output_dir / "summary.json",
        {
            "runId": run_id,
            "mode": mode,
            "runStatus": "ok",
            "provider": DEFAULT_CONFIG.provider,
            "model": DEFAULT_CONFIG.implementation_model,
            "metrics": met,
            "balanced_gates": balanced,
            "quality": {
                "validation_ready": vr,
                "strict_threshold_profile": balanced.get("threshold_profile"),
            },
        },
    )
    generate_report(run_id)
    return {
        "validation_ready": vr,
        "review_status": review["status"],
        "manifest_complete": manifest_complete,
        "balanced_gates": balanced,
        "hard_stops": hard_stops,
    }
