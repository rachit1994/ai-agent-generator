"""Artifact path lists and manifest rows for review.json."""

from __future__ import annotations

from pathlib import Path
from typing import Any

EVENT_LINEAGE_MANIFEST_PATHS = [
    "replay_manifest.json",
    "kill_switch_state.json",
    "event_store/run_events.jsonl",
]

MEMORY_MANIFEST_PATHS = [
    "memory/retrieval_bundle.json",
    "memory/quarantine.jsonl",
    "memory/quality_metrics.json",
    "capability/skill_nodes.json",
]

EVOLUTION_MANIFEST_PATHS = [
    "learning/reflection_bundle.json",
    "learning/canary_report.json",
    "lifecycle/promotion_package.json",
    "practice/task_spec.json",
    "practice/evaluation_result.json",
]

ORGANIZATION_MANIFEST_PATHS = [
    "coordination/lease_table.json",
    "iam/permission_matrix.json",
    "iam/action_audit.jsonl",
    "orchestration/shard_map.json",
    "strategy/proposal.json",
]

GUARDED_CORE_PATHS = [
    "planner_doc.md",
    "executor_prompt.txt",
    "verifier_report.json",
]

PHASED_PLAN_PATH = "program/phased_plan.json"

GUARDED_COMPLETION_PATHS = [
    "program/project_plan.json",
    "program/progress.json",
    "program/work_batch.json",
    "program/discovery.json",
    "program/research_digest.md",
    "program/doc_review.json",
    "program/dual_control_ack.json",
    "program/question_workbook.jsonl",
    "program/learning_events.jsonl",
    "program/doc_pack_manifest.json",
    "program/plan_lock.json",
    "program/policy_bundle_rollback.json",
    "product_brief.md",
    "architecture_sketch.md",
    "test_plan_stub.md",
    "step_reviews/step_planner.json",
    "step_reviews/step_implement.json",
    "step_reviews/step_verify.json",
    "verification_bundle.json",
]


def manifest_paths_for_review(mode: str, *, include_guarded_completion: bool = False) -> list[str]:
    """Paths checked in ``review.json`` artifact_manifest (before review file itself exists)."""
    base = [
        "traces.jsonl",
        "orchestration.jsonl",
        "report.md",
        "run.log",
        "answer.txt",
        "static_gates_report.json",
        "outputs/README.txt",
        "outputs/manifest.json",
        *EVENT_LINEAGE_MANIFEST_PATHS,
        *MEMORY_MANIFEST_PATHS,
        *EVOLUTION_MANIFEST_PATHS,
        *ORGANIZATION_MANIFEST_PATHS,
    ]
    if mode in ("guarded_pipeline", "phased_pipeline"):
        base.extend(GUARDED_CORE_PATHS)
        if include_guarded_completion:
            base.extend(GUARDED_COMPLETION_PATHS)
        if mode == "phased_pipeline":
            base.append(PHASED_PLAN_PATH)
    return base


def all_required_execution_paths(mode: str, output_dir: Path | None = None) -> list[str]:
    include_completion = False
    if mode in ("guarded_pipeline", "phased_pipeline") and output_dir is not None:
        include_completion = (output_dir / "program" / "project_plan.json").is_file()
    return [
        "summary.json",
        "review.json",
        "token_context.json",
        *manifest_paths_for_review(mode, include_guarded_completion=include_completion),
    ]


def manifest_entries(output_dir: Path, relative_paths: list[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for rel in relative_paths:
        p = output_dir / rel
        entries.append({"path": rel, "present": p.is_file() or p.is_dir()})
    return entries
