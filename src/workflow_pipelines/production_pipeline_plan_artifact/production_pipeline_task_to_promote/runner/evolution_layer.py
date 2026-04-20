"""Evolution harness: reflection, promotion, practice, canary."""

from __future__ import annotations

from pathlib import Path

from production_architecture.storage.storage.storage import ensure_dir, write_json
from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import iso_now

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.online_eval_shadow_contract import (
    validate_canary_report_dict,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.promotion_eval_contract import (
    validate_promotion_package_dict,
)


def write_evolution_artifacts(*, output_dir: Path, run_id: str) -> None:
    """Minimal lifecycle + learning artifacts (local SDE default-on)."""
    learn = output_dir / "learning"
    ensure_dir(learn)
    life = output_dir / "lifecycle"
    ensure_dir(life)
    practice = output_dir / "practice"
    ensure_dir(practice)

    event_ref = f"evt-{run_id}-traces"
    write_json(
        learn / "reflection_bundle.json",
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "linked_event_ids": [event_ref],
            "root_causes": ["harness_stub"],
            "evidence_links": [event_ref],
            "blast_radius": "none",
            "proposed_intervention": "none",
            "causal_closure_checklist": {
                "failure_class": True,
                "root_cause_evidence": True,
                "intervention_mapped": True,
                "post_fix_verified": True,
            },
            "completed_at": iso_now(),
        },
    )
    promotion_pkg = {
        "schema_version": "1.0",
        "aggregate_id": run_id,
        "current_stage": "junior",
        "proposed_stage": "junior",
        "independent_evaluator_signal_ids": ["eval-harness-1"],
        "evidence_window": [run_id],
    }
    pkg_errs = validate_promotion_package_dict(promotion_pkg)
    if pkg_errs:
        raise ValueError(f"promotion_eval_package_contract:{','.join(pkg_errs)}")
    write_json(life / "promotion_package.json", promotion_pkg)
    write_json(
        practice / "task_spec.json",
        {
            "schema_version": "1.0",
            "gap_detection_ref": "learning/reflection_bundle.json",
            "task": "harness_stub",
            "acceptance_criteria": [],
        },
    )
    write_json(
        practice / "evaluation_result.json",
        {"schema_version": "1.0", "passed": True, "evaluated_at": iso_now()},
    )
    canary_body = {
        "schema_version": "1.0",
        "shadow_metrics": {"latency_p95_ms": 0},
        "promote": True,
        "recorded_at": iso_now(),
    }
    canary_errs = validate_canary_report_dict(canary_body)
    if canary_errs:
        raise ValueError(f"online_eval_shadow_contract:{','.join(canary_errs)}")
    write_json(learn / "canary_report.json", canary_body)
