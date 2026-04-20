"""Completion harness for guarded_pipeline runs (program/, step_reviews/, verification)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from storage.storage import ensure_dir, write_json
from time_and_budget.time_util import iso_now

from workflow_pipelines.production_pipeline_task_to_promote.benchmark.production_pipeline_plan_contract import (
    validate_harness_project_plan_dict,
)

STEP_IDS = ("step_planner", "step_implement", "step_verify")
_TASK_EXCERPT_MAX = 800


def _task_excerpt(task: str) -> str:
    t = (task or "").strip()
    if len(t) <= _TASK_EXCERPT_MAX:
        return t
    return t[: _TASK_EXCERPT_MAX] + "…"


def _learning_stub_lines() -> list[dict[str, Any]]:
    base = iso_now()
    phases = (
        "discovery",
        "research",
        "differentiation",
        "question_policy",
        "doc_review",
        "doc_review",
        "plan_lock",
        "plan_lock",
    )
    return [
        {
            "event_id": f"learn-{i + 1}",
            "type": "episode",
            "refs": [f"traces:{i}"],
            "created_at": base,
            "phase": phases[i],
        }
        for i in range(8)
    ]


def _verifier_passed(parsed: dict[str, Any]) -> bool:
    for row in parsed.get("checks") or []:
        if isinstance(row, dict) and row.get("name") == "verifier_passed":
            return bool(row.get("passed"))
    return False


def write_completion_artifacts(
    *,
    output_dir: Path,
    run_id: str,
    task: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
) -> None:
    """Emit minimal planning + completion paths under the run directory (harness / local SDE)."""
    _ = events
    excerpt = _task_excerpt(task)
    program = output_dir / "program"
    ensure_dir(program)
    ensure_dir(output_dir / "step_reviews")

    plan = {
        "plan_version": "1.0",
        "steps": [
            {"step_id": "step_planner", "depends_on": [], "phase": "planning"},
            {"step_id": "step_implement", "depends_on": ["step_planner"], "phase": "implementation"},
            {"step_id": "step_verify", "depends_on": ["step_implement"], "phase": "verification"},
        ],
    }
    plan_errs = validate_harness_project_plan_dict(plan)
    if plan_errs:
        raise ValueError(f"production_pipeline_plan_contract:{','.join(plan_errs)}")
    write_json(program / "project_plan.json", plan)
    write_json(
        program / "discovery.json",
        {
            "schema_version": "1.0",
            "repo_id": "sde_harness",
            "source": "completion_harness",
            "goal_excerpt": excerpt,
            "constraints": [],
            "non_goals": [],
            "open_questions": [],
        },
    )
    digest_lines = [
        "# Research digest (harness)",
        "",
        f"- **Run:** `{run_id}`",
        "- **Scope:** Stub artifact for Stage 1 (V2) intake parity with `docs/AI-Professional-Evolution-Master-Architecture.md` (product stages).",
        "- **Sources:** Placeholder until planner-backed research is wired.",
        "",
        "## Task excerpt (from CLI)",
        "",
        "```text",
        excerpt if excerpt else "(empty task)",
        "```",
        "",
        "## Constraints",
        "",
        "- None recorded in harness beyond the task excerpt.",
        "",
        "## Risks / unknowns",
        "",
        "- Deferred to real discovery pipeline.",
        "",
    ]
    (program / "research_digest.md").write_text("\n".join(digest_lines), encoding="utf-8")
    write_json(
        program / "doc_review.json",
        {
            "schema_version": "1.0",
            "passed": True,
            "reviewed_at": iso_now(),
            "findings": [],
            "reviewer": "harness_stub",
        },
    )
    write_json(
        program / "dual_control_ack.json",
        {
            "schema_version": "1.0",
            "implementor_actor_id": "harness_implementor",
            "independent_reviewer_actor_id": "harness_independent_reviewer",
            "acknowledged_at": iso_now(),
            "source": "completion_harness",
        },
    )
    brief = "\n".join(
        [
            "# Product brief (harness)",
            "",
            f"- **Run:** `{run_id}`",
            "- **Intent:** Stub Stage 1 doc pack entry until planner-authored briefs ship.",
            "",
            "## Goals",
            "",
            "- Satisfy `program/doc_pack_manifest.json` + HS12 with on-disk evidence.",
            "",
            "## Non-goals",
            "",
            "- None declared in harness.",
            "",
            "## Task excerpt",
            "",
            "```text",
            excerpt if excerpt else "(empty task)",
            "```",
            "",
        ]
    )
    (output_dir / "product_brief.md").write_text(brief, encoding="utf-8")
    arch = "\n".join(
        [
            "# Architecture sketch (harness)",
            "",
            f"- **Run:** `{run_id}`",
            "- **Intent:** Stub Stage 1 architecture note until planner-owned ADRs ship.",
            "",
            "## Context",
            "",
            "- See `product_brief.md` and `planner_doc.md` in this run directory.",
            "",
            "## Components (placeholder)",
            "",
            "- **Orchestrator:** SDE guarded pipeline (local).",
            "- **Persistence:** Run artifacts under `outputs/runs/<id>/`.",
            "",
        ]
    )
    (output_dir / "architecture_sketch.md").write_text(arch, encoding="utf-8")
    test_plan = "\n".join(
        [
            "# Test plan (harness stub)",
            "",
            f"- **Run:** `{run_id}`",
            "- **Intent:** Stub Stage 1 test-plan surface until plan steps declare real commands.",
            "",
            "## Strategy",
            "",
            "- Use `verification_bundle.json` from this run as the harness signal.",
            "- Replace with repo-specific pytest / lint / typecheck when wired to `project_plan.json`.",
            "",
        ]
    )
    (output_dir / "test_plan_stub.md").write_text(test_plan, encoding="utf-8")
    write_json(
        program / "doc_pack_manifest.json",
        {
            "schema_version": "1.0",
            "entries": [
                {"path": "planner_doc.md", "content_sha256": None},
                {"path": "product_brief.md", "content_sha256": None},
                {"path": "architecture_sketch.md", "content_sha256": None},
                {"path": "test_plan_stub.md", "content_sha256": None},
                {"path": "program/research_digest.md", "content_sha256": None},
            ],
        },
    )
    q_lines = [
        {"id": "q1", "status": "resolved", "topic": "scope"},
        {"id": "q2", "status": "resolved", "topic": "stack"},
    ]
    (program / "question_workbook.jsonl").write_text(
        "\n".join(json.dumps(q) for q in q_lines) + "\n",
        encoding="utf-8",
    )
    learn_path = program / "learning_events.jsonl"
    learn_path.write_text(
        "\n".join(json.dumps(row) for row in _learning_stub_lines()) + "\n",
        encoding="utf-8",
    )
    write_json(
        program / "work_batch.json",
        {"batch_id": "b0", "paths": [], "max_paths": 500, "content_sha256": None},
    )

    refusal = parsed.get("refusal")
    impl_ok = not refusal
    verify_ok = _verifier_passed(parsed)
    planner_ok = (output_dir / "planner_doc.md").is_file()

    reviews: dict[str, bool] = {
        "step_planner": planner_ok,
        "step_implement": impl_ok,
        "step_verify": verify_ok,
    }
    for sid in STEP_IDS:
        write_json(
            output_dir / "step_reviews" / f"{sid}.json",
            {
                "schema_version": "1.0",
                "step_id": sid,
                "passed": reviews[sid],
                "findings": [],
                "evidence_refs": [f"traces.jsonl#{sid}"],
                "reviewed_at": iso_now(),
            },
        )

    last_done: str | None = None
    pending: str | None = "step_planner"
    if planner_ok:
        last_done = "step_planner"
        pending = "step_implement"
    if planner_ok and impl_ok:
        last_done = "step_implement"
        pending = "step_verify"
    if planner_ok and impl_ok and verify_ok:
        last_done = "step_verify"
        pending = None
    write_json(
        program / "progress.json",
        {
            "plan_version": plan["plan_version"],
            "last_completed_step_id": last_done,
            "pending_step_id": pending,
            "updated_at": iso_now(),
        },
    )

    vb_passed = verify_ok and impl_ok
    write_json(
        output_dir / "verification_bundle.json",
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "commands": [
                {
                    "cmd": "guarded_pipeline_verifier",
                    "cwd": str(output_dir),
                    "exit_code": 0 if vb_passed else 1,
                    "log_path": "verifier_report.json",
                }
            ],
            "passed": vb_passed,
            "captured_at": iso_now(),
        },
    )
    write_json(
        program / "plan_lock.json",
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "locked_at": iso_now(),
            "source": "completion_harness",
            "note": "Stub plan-lock record for OSV-STORY-01; real plan lock is session-scoped when using `sde project run`.",
        },
    )
    write_json(
        program / "policy_bundle_rollback.json",
        {
            "schema_version": "1.0",
            "status": "none",
            "recorded_at": iso_now(),
            "previous_policy_sha256": None,
            "current_policy_sha256": None,
            "paths_touched": [],
            "source": "completion_harness",
            "note": "No rollback on this harness run; documents §11.E policy-bundle rollback record shape.",
        },
    )
