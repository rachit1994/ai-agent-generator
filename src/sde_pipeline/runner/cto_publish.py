"""Token context, review.json, hard-stops, balanced summary v2, second report."""

from __future__ import annotations

from pathlib import Path

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
    write_json(output_dir / "review.json", review)
    hard_stops = evaluate_hard_stops(output_dir, events, token_ctx, run_status="ok")
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
