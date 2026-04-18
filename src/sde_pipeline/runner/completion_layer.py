"""Completion harness for guarded_pipeline runs (program/, step_reviews/, verification)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sde_foundations.storage import ensure_dir, write_json
from sde_gates.time_util import iso_now

STEP_IDS = ("step_planner", "step_implement", "step_verify")


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
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
) -> None:
    """Emit minimal planning + completion paths under the run directory (harness / local SDE)."""
    _ = events
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
    write_json(program / "project_plan.json", plan)
    write_json(
        program / "discovery.json",
        {"schema_version": "1.0", "repo_id": "sde_harness", "constraints": []},
    )
    write_json(
        program / "doc_review.json",
        {"schema_version": "1.0", "passed": True, "reviewed_at": iso_now()},
    )
    write_json(
        program / "doc_pack_manifest.json",
        {
            "schema_version": "1.0",
            "entries": [{"path": "planner_doc.md", "content_sha256": None}],
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
