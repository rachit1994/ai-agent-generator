"""Evolution harness: reflection, promotion, practice, canary."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from human_professional_evolution_model import (
    build_canary_report,
    build_evolution_decision,
    build_mentorship_plan,
    build_promotion_package,
    build_practice_evaluation_result,
    build_practice_task_spec,
    build_reflection_bundle,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json
from success_criteria.capability_growth_metrics import (
    build_capability_growth_metrics,
    validate_capability_growth_metrics_dict,
)
from success_criteria.extended_binary_gates import (
    build_extended_binary_gates,
    validate_extended_binary_gates_dict,
)
from success_criteria.error_reduction_metrics import (
    build_error_reduction_metrics,
    validate_error_reduction_metrics_dict,
)
from success_criteria.hard_release_gates import (
    build_hard_release_gates,
    validate_hard_release_gates_dict,
)
from success_criteria.stability_metrics import (
    build_stability_metrics,
    validate_stability_metrics_dict,
)
from success_criteria.transfer_learning_metrics import (
    build_transfer_learning_metrics,
    validate_transfer_learning_metrics_dict,
)
from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import iso_now

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.online_eval_shadow_contract import (
    validate_canary_report_dict,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.promotion_eval_contract import (
    validate_promotion_package_dict,
)


def _sanitize_skill_nodes(skill_nodes: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(skill_nodes, dict):
        return {"schema_version": "1.0", "nodes": []}
    raw_nodes = skill_nodes.get("nodes")
    if not isinstance(raw_nodes, list):
        return {"schema_version": "1.0", "nodes": []}
    nodes: list[dict[str, Any]] = []
    for item in raw_nodes:
        if not isinstance(item, dict):
            continue
        normalized = dict(item)
        score = normalized.get("score")
        if isinstance(score, (int, float)) and not isinstance(score, bool):
            normalized["score"] = float(score) if math.isfinite(float(score)) else 0.0
        nodes.append(normalized)
    return {"schema_version": str(skill_nodes.get("schema_version") or "1.0"), "nodes": nodes}


def write_evolution_artifacts(
    *,
    output_dir: Path,
    run_id: str,
    mode: str = "guarded_pipeline",
    parsed: dict[str, Any] | None = None,
    events: list[dict[str, Any]] | None = None,
    skill_nodes: dict[str, Any] | None = None,
) -> None:
    """Minimal lifecycle + learning artifacts (local SDE default-on)."""
    safe_parsed = parsed if isinstance(parsed, dict) else {}
    safe_events = events if isinstance(events, list) else []
    safe_nodes = _sanitize_skill_nodes(skill_nodes)
    learn = output_dir / "learning"
    ensure_dir(learn)
    life = output_dir / "lifecycle"
    ensure_dir(life)
    practice = output_dir / "practice"
    ensure_dir(practice)

    event_ref = f"evt-{run_id}-traces"
    decision = build_evolution_decision(
        run_id=run_id,
        parsed=safe_parsed,
        events=safe_events,
        skill_nodes=safe_nodes,
    )
    reflection_bundle = build_reflection_bundle(run_id=run_id, decision=decision, event_ref=event_ref)
    reflection_bundle["completed_at"] = iso_now()
    write_json(learn / "reflection_bundle.json", reflection_bundle)
    write_json(learn / "mentorship_plan.json", build_mentorship_plan(run_id=run_id, decision=decision))
    promotion_pkg = build_promotion_package(run_id=run_id, decision=decision)
    pkg_errs = validate_promotion_package_dict(promotion_pkg)
    if pkg_errs:
        raise ValueError(f"promotion_eval_package_contract:{','.join(pkg_errs)}")
    write_json(life / "promotion_package.json", promotion_pkg)
    write_json(practice / "task_spec.json", build_practice_task_spec(decision=decision))
    eval_result = build_practice_evaluation_result(decision=decision)
    eval_result["evaluated_at"] = iso_now()
    write_json(practice / "evaluation_result.json", eval_result)
    canary_body = build_canary_report(decision=decision)
    canary_body["recorded_at"] = iso_now()
    canary_errs = validate_canary_report_dict(canary_body)
    if canary_errs:
        raise ValueError(f"online_eval_shadow_contract:{','.join(canary_errs)}")
    write_json(learn / "canary_report.json", canary_body)
    transfer_metrics = build_transfer_learning_metrics(
        run_id=run_id, parsed=safe_parsed, events=safe_events, skill_nodes=safe_nodes
    )
    transfer_errs = validate_transfer_learning_metrics_dict(transfer_metrics)
    if transfer_errs:
        raise ValueError(f"transfer_learning_metrics_contract:{','.join(transfer_errs)}")
    write_json(learn / "transfer_learning_metrics.json", transfer_metrics)
    capability_growth = build_capability_growth_metrics(
        run_id=run_id, parsed=safe_parsed, events=safe_events, skill_nodes=safe_nodes
    )
    capability_growth_errs = validate_capability_growth_metrics_dict(capability_growth)
    if capability_growth_errs:
        raise ValueError(f"capability_growth_metrics_contract:{','.join(capability_growth_errs)}")
    write_json(learn / "capability_growth_metrics.json", capability_growth)
    extended_binary = build_extended_binary_gates(
        run_id=run_id, parsed=safe_parsed, events=safe_events, skill_nodes=safe_nodes
    )
    extended_binary_errs = validate_extended_binary_gates_dict(extended_binary)
    if extended_binary_errs:
        raise ValueError(f"extended_binary_gates_contract:{','.join(extended_binary_errs)}")
    write_json(learn / "extended_binary_gates.json", extended_binary)
    error_reduction = build_error_reduction_metrics(
        run_id=run_id, parsed=safe_parsed, events=safe_events, skill_nodes=safe_nodes
    )
    error_reduction_errs = validate_error_reduction_metrics_dict(error_reduction)
    if error_reduction_errs:
        raise ValueError(f"error_reduction_metrics_contract:{','.join(error_reduction_errs)}")
    write_json(learn / "error_reduction_metrics.json", error_reduction)
    hard_release_gates = build_hard_release_gates(
        run_id=run_id,
        mode=mode,
        parsed=safe_parsed,
        events=safe_events,
    )
    hard_release_gates_errs = validate_hard_release_gates_dict(hard_release_gates)
    if hard_release_gates_errs:
        raise ValueError(f"hard_release_gates_contract:{','.join(hard_release_gates_errs)}")
    write_json(learn / "hard_release_gates.json", hard_release_gates)
    stability_metrics = build_stability_metrics(run_id=run_id, events=safe_events)
    stability_metrics_errs = validate_stability_metrics_dict(stability_metrics)
    if stability_metrics_errs:
        raise ValueError(f"stability_metrics_contract:{','.join(stability_metrics_errs)}")
    write_json(learn / "stability_metrics.json", stability_metrics)
