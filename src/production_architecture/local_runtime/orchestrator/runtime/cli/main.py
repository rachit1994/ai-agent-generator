from __future__ import annotations

import argparse
import json
import os
import sys

from pathlib import Path

from orchestrator.api import (
    apply_intake_doc_review_result,
    append_roadmap_learning_line,
    evaluate_remaining_work,
    evaluate_project_plan_lock_readiness,
    describe_project_session,
    execute_single_task,
    generate_report,
    load_remaining_work_rules,
    replay_run,
    render_remaining_work_markdown,
    roadmap_review,
    run_benchmark,
    run_bounded_evolve_loop,
    run_continuous_project_session,
    run_continuous_until,
    run_project_session,
    scaffold_project_intake,
    validate_project_session,
    validate_run,
    write_project_plan_lock,
    write_project_stage1_observability_export,
)


def _env_require_non_stub_reviewer() -> bool:
    """True when ``SDE_REQUIRE_NON_STUB_REVIEWER`` requests strict reviewer policy (CLI only)."""
    raw = os.environ.get("SDE_REQUIRE_NON_STUB_REVIEWER", "").strip().lower()
    return raw in ("1", "true", "yes", "on")


def _strict_reviewer_when_enforcing_project_lock(args: object) -> bool:
    """Strict reviewer policy when ``--enforce-plan-lock`` is set (``project run`` / ``continuous`` project modes)."""
    if not bool(getattr(args, "enforce_plan_lock", False)):
        return False
    return bool(getattr(args, "require_non_stub_reviewer", False)) or _env_require_non_stub_reviewer()


def build_parser() -> argparse.ArgumentParser:
    plan_parent_help = "Path to project_plan.json; session directory is its parent"
    parser = argparse.ArgumentParser(prog="sde")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run")
    run.add_argument("--task", required=True)
    run.add_argument(
        "--mode",
        required=True,
        choices=["baseline", "guarded_pipeline", "phased_pipeline"],
    )
    run.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Execute the same task N times with isolated run ids (V1 RepeatProfile; default 1)",
    )

    bench = sub.add_parser("benchmark")
    bench.add_argument("--suite", required=False, default=None)
    bench.add_argument("--mode", default="both", choices=["baseline", "guarded_pipeline", "both"])
    bench.add_argument("--max-tasks", type=int, default=None, help="Run at most the first N suite rows")
    bench.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Record per-task failures and continue the suite instead of aborting",
    )
    bench.add_argument(
        "--resume-run-id",
        default=None,
        help="Continue a benchmark under outputs/runs/<id> (same suite_path and mode as manifest; optional --suite must match)",
    )

    report = sub.add_parser("report")
    report.add_argument("--run-id", required=True)

    replay = sub.add_parser("replay")
    replay.add_argument("--run-id", required=True)
    replay.add_argument("--format", default="text", choices=["text", "json", "html"])
    replay.add_argument(
        "--rerun",
        action="store_true",
        help="Re-execute single-task run from run-manifest.json (new run_id)",
    )
    replay.add_argument(
        "--write-html",
        action="store_true",
        help="Write trajectory.html under the run directory (prints path); not with --rerun",
    )

    validate = sub.add_parser("validate", help="Check outputs/runs/<run-id>/ against artifact + hard-stop contract")
    validate.add_argument("--run-id", required=True)
    validate.add_argument(
        "--mode",
        default=None,
        choices=["baseline", "guarded_pipeline", "phased_pipeline"],
        help="Override mode (default: read from run-manifest.json, else baseline)",
    )

    roadmap = sub.add_parser(
        "roadmap-review",
        help="Ask support_model (default Gemma) for V1–V7 %% estimates, gaps, and a learning note",
    )
    roadmap.add_argument(
        "--repo-root",
        default=None,
        help="Repository root containing docs/ (default: current working directory)",
    )
    roadmap.add_argument(
        "--context-file",
        action="append",
        default=None,
        help="Extra markdown path relative to repo root (repeatable; defaults to core SDE docs)",
    )
    roadmap.add_argument(
        "--append-learning",
        nargs="?",
        const=".agent/sde/learning_events.jsonl",
        default=None,
        help="Append one JSONL learning event to this path (default if flag given: .agent/sde/learning_events.jsonl)",
    )

    evolve = sub.add_parser(
        "evolve",
        help="Bounded loop: roadmap-review each round + optional sde run + learning log until target %% or max rounds",
    )
    evolve.add_argument("--repo-root", default=None, help="Repository root (default: cwd)")
    evolve.add_argument("--max-rounds", type=int, default=5, help="Maximum review rounds (default: 5)")
    evolve.add_argument(
        "--target-pct",
        type=int,
        default=99,
        help="Stop with exit 0 when Gemma overall_pct reaches this (default: 99)",
    )
    evolve.add_argument(
        "--task",
        default=None,
        help="If set, run execute_single_task with this text after each roadmap review (Ollama cost)",
    )
    evolve.add_argument(
        "--mode",
        default="guarded_pipeline",
        choices=["baseline", "guarded_pipeline", "phased_pipeline"],
        help="Mode for optional --task runs (default: guarded_pipeline)",
    )
    evolve.add_argument(
        "--learning-path",
        default=".agent/sde/learning_events.jsonl",
        help="Append-only JSONL for roadmap_review payloads (default: .agent/sde/learning_events.jsonl)",
    )
    evolve.add_argument(
        "--print-task-result",
        action="store_true",
        help="Print execute_single_task JSON envelope when --task is set",
    )
    evolve.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-round roadmap_ok / overall_pct / model_error lines",
    )

    continuous = sub.add_parser(
        "continuous",
        help="Repeat sde run on the same task until a stop condition or --max-iterations; or drive a project session",
    )
    continuous.add_argument(
        "--task",
        default=None,
        help="Task string for each execute_single_task (required unless a project flag is set)",
    )
    continuous.add_argument(
        "--project-session-dir",
        default=None,
        help="Run meta-orchestrator from this session directory (mutually exclusive with --task and --project-plan)",
    )
    continuous.add_argument(
        "--project-plan",
        default=None,
        dest="continuous_project_plan",
        metavar="PATH",
        help="Path to project_plan.json; session directory is its parent (mutually exclusive with --task and --project-session-dir)",
    )
    continuous.add_argument(
        "--progress-file",
        default=None,
        metavar="PATH",
        help="Override progress.json when using --project-session-dir or --project-plan (Phase 5)",
    )
    continuous.add_argument(
        "--parallel-worktrees",
        action="store_true",
        help="When using a project session with max_concurrent_agents>1 and disjoint scopes: run steps in parallel via git worktrees (Phase 6; requires a git repo)",
    )
    continuous.add_argument(
        "--lease-stale-sec",
        type=int,
        default=None,
        metavar="N",
        help="Prune leases.json rows older than N seconds each tick (Phase 8); 0 disables; default from plan or 86400",
    )
    continuous.add_argument(
        "--enforce-plan-lock",
        action="store_true",
        help="When using project session mode, require lock-readiness before running steps",
    )
    continuous.add_argument(
        "--require-non-stub-reviewer",
        action="store_true",
        help=(
            "With --enforce-plan-lock, reject local_stub reviewer in lock readiness; "
            "also when SDE_REQUIRE_NON_STUB_REVIEWER is set (CLI only)"
        ),
    )
    continuous.add_argument(
        "--repo-root",
        default=None,
        help="Repository root when using --project-session-dir (default: cwd)",
    )
    continuous.add_argument(
        "--max-concurrent-agents",
        type=int,
        default=1,
        help="When using a project session: max disjoint path_scope steps considered per tick (default: 1)",
    )
    continuous.add_argument(
        "--mode",
        default="guarded_pipeline",
        choices=["baseline", "guarded_pipeline", "phased_pipeline"],
        help="Pipeline mode (default: guarded_pipeline)",
    )
    continuous.add_argument(
        "--max-iterations",
        type=int,
        default=500,
        help="Hard cap on attempts (default: 500); raise for long repo-wide sessions",
    )
    continuous.add_argument(
        "--stop-when",
        default="validation_ready",
        choices=["never", "validation_ready", "definition_of_done"],
        help="Early exit: strict validate (default), DoD from review.json, or only cap (never)",
    )
    continuous.add_argument(
        "--continue-on-pipeline-error",
        action="store_true",
        help="Keep iterating after execute_single_task errors (default: stop on first error)",
    )

    project = sub.add_parser(
        "project",
        help="Meta-orchestrator: run repo-backed project_plan.json steps with verification",
    )
    p_sub = project.add_subparsers(dest="project_cmd", required=True)
    p_run = p_sub.add_parser("run", help="Execute session until completed_review_pass, block, or budget")
    p_sess = p_run.add_mutually_exclusive_group(required=True)
    p_sess.add_argument(
        "--session-dir",
        help="Directory containing project_plan.json (and progress.json when resuming)",
    )
    p_sess.add_argument(
        "--plan",
        dest="project_plan_file",
        metavar="PATH",
        help=f"{plan_parent_help} (Phase 1: same store as --session-dir)",
    )
    p_run.add_argument(
        "--repo-root",
        default=None,
        help="Repository root for verification cwd and context pack (default: cwd)",
    )
    p_run.add_argument("--max-steps", type=int, default=50, help="Maximum plan steps to attempt (default: 50)")
    p_run.add_argument(
        "--mode",
        default="guarded_pipeline",
        choices=["baseline", "guarded_pipeline", "phased_pipeline"],
        help="Mode for each execute_single_task (default: guarded_pipeline)",
    )
    p_run.add_argument(
        "--max-concurrent-agents",
        type=int,
        default=1,
        help="Max runnable steps per tick with disjoint path_scope (default: 1; still sequential on one worktree)",
    )
    p_run.add_argument(
        "--progress-file",
        default=None,
        metavar="PATH",
        help="Override progress.json path (default: <session-dir>/progress.json)",
    )
    p_run.add_argument(
        "--parallel-worktrees",
        action="store_true",
        help="With max_concurrent_agents>1 and disjoint path_scope: parallel steps via git worktrees (Phase 6)",
    )
    p_run.add_argument(
        "--lease-stale-sec",
        type=int,
        default=None,
        metavar="N",
        help="Stale lease pruning TTL in seconds (Phase 8); 0 disables; overrides plan workspace.lease_ttl_sec",
    )
    p_run.add_argument(
        "--enforce-plan-lock",
        action="store_true",
        help="Require Stage 1 intake lock-readiness before executing project steps",
    )
    p_run.add_argument(
        "--require-non-stub-reviewer",
        action="store_true",
        help=(
            "With --enforce-plan-lock, reject local_stub reviewer in lock readiness; "
            "also when SDE_REQUIRE_NON_STUB_REVIEWER is set (CLI only)"
        ),
    )
    p_val = p_sub.add_parser(
        "validate",
        help="Read-only checks on project_plan.json (schema, cycles, workspace); no steps executed (Phase 9)",
    )
    v_sess = p_val.add_mutually_exclusive_group(required=True)
    v_sess.add_argument(
        "--session-dir",
        help="Directory containing project_plan.json",
    )
    v_sess.add_argument(
        "--plan",
        dest="project_plan_file",
        metavar="PATH",
        help=plan_parent_help,
    )
    p_val.add_argument(
        "--repo-root",
        default=None,
        help="Repository root for workspace branch check (default: cwd)",
    )
    p_val.add_argument(
        "--skip-workspace",
        action="store_true",
        help="Skip git workspace.branch checks (plan + cycle validation only)",
    )
    p_val.add_argument(
        "--progress-file",
        default=None,
        metavar="PATH",
        help="Optional progress.json path for non-fatal conformance warnings",
    )
    p_val.add_argument(
        "--require-plan-lock",
        action="store_true",
        help="Fail validate when Stage 1 plan-lock readiness is not satisfied",
    )
    p_val.add_argument(
        "--require-non-stub-reviewer",
        action="store_true",
        help=(
            "With --require-plan-lock, reject local_stub reviewer attestation_type; "
            "same when SDE_REQUIRE_NON_STUB_REVIEWER is 1/true/yes/on (CLI only)"
        ),
    )
    p_scaffold = p_sub.add_parser(
        "scaffold-intake",
        help="Write intake/ stubs (discovery, research digest, doc review, questions) for Stage 1 alignment; does not edit project_plan.json",
    )
    p_scaffold.add_argument(
        "--session-dir",
        required=True,
        dest="intake_session_dir",
        help="Project session directory (e.g. contains or will contain project_plan.json)",
    )
    p_scaffold.add_argument(
        "--goal",
        required=True,
        help="Non-empty goal text (stored as goal excerpt in discovery.json)",
    )
    p_scaffold.add_argument(
        "--repo-label",
        default="unknown",
        help="Short label stored in discovery.json repo_id (default: unknown)",
    )
    p_revise = p_sub.add_parser(
        "intake-revise",
        help="Apply bounded revise-loop state from intake/doc_review.json (failed -> retry count -> blocked_human)",
    )
    p_revise.add_argument(
        "--session-dir",
        required=True,
        dest="intake_session_dir",
        help="Project session directory containing intake/doc_review.json",
    )
    p_revise.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Max failed doc-review retries before blocked_human (default: 2)",
    )
    p_lock = p_sub.add_parser(
        "plan-lock",
        help="Evaluate Stage 1 intake + plan lock-readiness and write project_plan_lock.json",
    )
    l_sess = p_lock.add_mutually_exclusive_group(required=True)
    l_sess.add_argument(
        "--session-dir",
        help="Project session directory containing project_plan.json and intake/",
    )
    l_sess.add_argument(
        "--plan",
        dest="project_plan_file",
        metavar="PATH",
        help=plan_parent_help,
    )
    p_lock.add_argument(
        "--check-only",
        action="store_true",
        help="Evaluate lock-readiness only; do not write project_plan_lock.json",
    )
    p_lock.add_argument(
        "--allow-missing-revise-state",
        action="store_true",
        help="Do not require intake/revise_state.json with review_passed status",
    )
    p_lock.add_argument(
        "--require-non-stub-reviewer",
        action="store_true",
        help=(
            "Reject local_stub reviewer attestation_type; require service-backed reviewer identity proof; "
            "same when SDE_REQUIRE_NON_STUB_REVIEWER is 1/true/yes/on (CLI only)"
        ),
    )
    p_stat = p_sub.add_parser(
        "status",
        help="Print JSON snapshot of plan, progress, driver_state, stop_report, leases (Phase 10; read-only)",
    )
    s_sess = p_stat.add_mutually_exclusive_group(required=True)
    s_sess.add_argument(
        "--session-dir",
        help="Directory containing project_plan.json",
    )
    s_sess.add_argument(
        "--plan",
        dest="project_plan_file",
        metavar="PATH",
        help=plan_parent_help,
    )
    p_stat.add_argument(
        "--repo-root",
        default=None,
        help="Repository root for repo_snapshot git rev-parse (Phase 18; default: cwd); also recorded in JSON",
    )
    p_stat.add_argument(
        "--progress-file",
        default=None,
        metavar="PATH",
        help="Override progress.json path (default: <session-dir>/progress.json)",
    )
    p_stat.add_argument(
        "--max-concurrent-agents",
        type=int,
        default=1,
        help="For next_tick_batch hint only (default: 1)",
    )
    p_stat.add_argument(
        "--status-max-json-bytes",
        dest="status_max_json_bytes",
        type=int,
        default=None,
        metavar="N",
        help="Max bytes per embedded JSON body (progress, driver_state, stop_report, aggregate, DoD); omit body when larger (Phase 13; default 524288)",
    )
    p_stat.add_argument(
        "--status-jsonl-full-scan-max-bytes",
        dest="status_jsonl_full_scan_max_bytes",
        type=int,
        default=None,
        metavar="N",
        help="If session_events.jsonl / step_runs.jsonl is larger than N bytes, only scan a tail for 'last' and omit exact line_count (Phase 13; default 1048576)",
    )
    p_stat.add_argument(
        "--status-jsonl-tail-bytes",
        dest="status_jsonl_tail_bytes",
        type=int,
        default=None,
        metavar="N",
        help="Tail window when a JSONL file exceeds --status-jsonl-full-scan-max-bytes (Phase 13; default 262144)",
    )
    p_stat.add_argument(
        "--status-max-listed-step-ids",
        dest="status_max_listed_step_ids",
        type=int,
        default=None,
        metavar="N",
        help="Max step_ids listed under context_packs/ and verification/ in status JSON (Phase 14; default 256)",
    )
    p_obs = p_sub.add_parser(
        "export-stage1-observability",
        help="Write intake/stage1_observability_export.json (revise_metrics + status_at_a_glance; OSV-STORY-01 B4)",
    )
    o_sess = p_obs.add_mutually_exclusive_group(required=True)
    o_sess.add_argument(
        "--session-dir",
        help="Directory containing project_plan.json",
    )
    o_sess.add_argument(
        "--plan",
        dest="project_plan_file",
        metavar="PATH",
        help=plan_parent_help,
    )
    p_obs.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help="Destination JSON file (default: <session-dir>/intake/stage1_observability_export.json)",
    )
    p_obs.add_argument(
        "--repo-root",
        default=None,
        help="Repository root for describe_project_session (default: cwd)",
    )
    p_obs.add_argument(
        "--progress-file",
        default=None,
        metavar="PATH",
        help="Override progress.json path (default: <session-dir>/progress.json)",
    )
    p_obs.add_argument(
        "--max-concurrent-agents",
        type=int,
        default=1,
        help="For describe_project_session next_tick_batch hint only (default: 1)",
    )
    p_obs.add_argument(
        "--status-max-json-bytes",
        dest="status_max_json_bytes",
        type=int,
        default=None,
        metavar="N",
        help="Same as project status --status-max-json-bytes",
    )
    p_obs.add_argument(
        "--status-jsonl-full-scan-max-bytes",
        dest="status_jsonl_full_scan_max_bytes",
        type=int,
        default=None,
        metavar="N",
        help="Same as project status --status-jsonl-full-scan-max-bytes",
    )
    p_obs.add_argument(
        "--status-jsonl-tail-bytes",
        dest="status_jsonl_tail_bytes",
        type=int,
        default=None,
        metavar="N",
        help="Same as project status --status-jsonl-tail-bytes",
    )
    p_obs.add_argument(
        "--status-max-listed-step-ids",
        dest="status_max_listed_step_ids",
        type=int,
        default=None,
        metavar="N",
        help="Same as project status --status-max-listed-step-ids",
    )
    p_remaining = p_sub.add_parser(
        "remaining-work",
        help="Evaluate planned-vs-remaining work from repo evidence and explicit rules",
    )
    p_remaining.add_argument("--repo-root", default=None, help="Repository root (default: cwd)")
    p_remaining.add_argument(
        "--rules",
        default="data/company-os-progress-rules.json",
        help="Rules JSON path relative to --repo-root",
    )
    p_remaining.add_argument("--output-json", default=None, help="Optional file path for JSON artifact")
    p_remaining.add_argument("--output-md", default=None, help="Optional file path for markdown summary")
    p_remaining.add_argument("--format", default="text", choices=["text", "json"], help="Stdout format")
    p_remaining.add_argument("--min-completion-pct", type=float, default=None, help="Optional minimum completion")
    p_remaining.add_argument("--require-gates", action="store_true", help="Fail when any configured gate fails")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "benchmark" and not getattr(args, "resume_run_id", None) and not args.suite:
        parser.error("--suite is required unless --resume-run-id is set")
    if args.command == "run":
        if args.repeat < 1:
            parser.error("--repeat must be >= 1")
        print(json.dumps(execute_single_task(args.task, args.mode, repeat=args.repeat), indent=2))
        return
    if args.command == "benchmark":
        print(
            json.dumps(
                run_benchmark(
                    args.suite,
                    args.mode,
                    max_tasks=args.max_tasks,
                    continue_on_error=args.continue_on_error,
                    resume_run_id=args.resume_run_id,
                ),
                indent=2,
            )
        )
        return
    if args.command == "replay":
        print(replay_run(args.run_id, output_format=args.format, rerun=args.rerun, write_html=args.write_html))
        return
    if args.command == "validate":
        verdict = validate_run(args.run_id, mode=args.mode)
        print(json.dumps(verdict, indent=2))
        if verdict.get("execution_gates_applied") is False:
            strict = verdict.get("ok") is True
        else:
            strict = verdict.get("ok") is True and verdict.get("validation_ready") is True
        sys.exit(0 if strict else 1)
    if args.command == "roadmap-review":
        root = Path(args.repo_root).resolve() if args.repo_root else Path.cwd()
        out = roadmap_review(repo_root=root, extra_doc_paths=args.context_file)
        print(json.dumps(out, indent=2))
        if args.append_learning is not None:
            append_roadmap_learning_line(Path(args.append_learning), out)
        sys.exit(0 if out.get("ok") else 2)
    if args.command == "continuous":
        if args.max_iterations < 1:
            parser.error("--max-iterations must be >= 1")
        psd = getattr(args, "project_session_dir", None)
        cpp = getattr(args, "continuous_project_plan", None)
        if sum(1 for x in (args.task, psd, cpp) if x) > 1:
            parser.error("Use only one of --task, --project-session-dir, or --project-plan")
        pf_raw = getattr(args, "progress_file", None)
        if pf_raw and not psd and not cpp:
            parser.error("--progress-file requires --project-session-dir or --project-plan")
        progress_arg = Path(pf_raw).resolve() if pf_raw else None
        if cpp:
            plan_p = Path(cpp).resolve()
            if not plan_p.is_file():
                parser.error("--project-plan must point to an existing project_plan.json file")
            root = Path(args.repo_root).resolve() if args.repo_root else Path.cwd()
            summary = run_continuous_project_session(
                session_dir=plan_p.parent,
                repo_root=root,
                max_iterations=args.max_iterations,
                mode=args.mode,
                max_concurrent_agents=int(getattr(args, "max_concurrent_agents", 1) or 1),
                progress_file=progress_arg,
                parallel_worktrees=bool(getattr(args, "parallel_worktrees", False)),
                lease_stale_sec=getattr(args, "lease_stale_sec", None),
                enforce_plan_lock=bool(getattr(args, "enforce_plan_lock", False)),
                require_non_stub_reviewer=_strict_reviewer_when_enforcing_project_lock(args),
            )
            print(json.dumps(summary, indent=2))
            sys.exit(int(summary.get("exit_code", 1)))
        if psd:
            root = Path(args.repo_root).resolve() if args.repo_root else Path.cwd()
            summary = run_continuous_project_session(
                session_dir=Path(psd).resolve(),
                repo_root=root,
                max_iterations=args.max_iterations,
                mode=args.mode,
                max_concurrent_agents=int(getattr(args, "max_concurrent_agents", 1) or 1),
                progress_file=progress_arg,
                parallel_worktrees=bool(getattr(args, "parallel_worktrees", False)),
                lease_stale_sec=getattr(args, "lease_stale_sec", None),
                enforce_plan_lock=bool(getattr(args, "enforce_plan_lock", False)),
                require_non_stub_reviewer=_strict_reviewer_when_enforcing_project_lock(args),
            )
            print(json.dumps(summary, indent=2))
            sys.exit(int(summary.get("exit_code", 1)))
        if not args.task:
            parser.error("--task is required unless --project-session-dir or --project-plan is set")
        summary = run_continuous_until(
            task=args.task,
            mode=args.mode,
            max_iterations=args.max_iterations,
            stop_when=args.stop_when,
            stop_on_pipeline_error=not args.continue_on_pipeline_error,
        )
        print(json.dumps(summary, indent=2))
        sys.exit(summary.get("exit_code", 1))
    if args.command == "project":
        _rr = getattr(args, "repo_root", None)
        root = Path(_rr).resolve() if _rr else Path.cwd()
        if args.project_cmd == "scaffold-intake":
            out = scaffold_project_intake(
                Path(args.intake_session_dir).resolve(),
                goal=str(getattr(args, "goal", "")),
                repo_label=str(getattr(args, "repo_label", "unknown") or "unknown"),
            )
            print(json.dumps(out, indent=2))
            sys.exit(0 if out.get("ok") else 2)
        if args.project_cmd == "intake-revise":
            out = apply_intake_doc_review_result(
                Path(args.intake_session_dir).resolve(),
                max_retries=int(getattr(args, "max_retries", 2)),
            )
            print(json.dumps(out, indent=2))
            if not out.get("ok"):
                sys.exit(2)
            if out.get("state") == "review_passed":
                sys.exit(0)
            sys.exit(1)
        if args.project_cmd == "remaining-work":
            rr = Path(getattr(args, "repo_root", None)).resolve() if getattr(args, "repo_root", None) else Path.cwd()
            rules_path = (rr / str(getattr(args, "rules", ""))).resolve()
            rules = load_remaining_work_rules(rules_path)
            result = evaluate_remaining_work(rr, rules)
            if getattr(args, "output_json", None):
                Path(args.output_json).resolve().write_text(json.dumps(result, indent=2), encoding="utf-8")
            md = render_remaining_work_markdown(result)
            if getattr(args, "output_md", None):
                Path(args.output_md).resolve().write_text(md, encoding="utf-8")
            print(json.dumps(result, indent=2) if args.format == "json" else md)
            gates = result.get("gates") if isinstance(result.get("gates"), dict) else {}
            gates_ok = all(bool(v.get("passed")) for v in gates.values()) if gates else True
            floor = getattr(args, "min_completion_pct", None)
            completion_ok = float(result.get("completion_pct", 0.0)) >= float(floor) if floor is not None else True
            if completion_ok and (gates_ok or not bool(getattr(args, "require_gates", False))):
                sys.exit(0)
            sys.exit(1)
        plan_file = getattr(args, "project_plan_file", None)
        if plan_file:
            plan_path = Path(plan_file).resolve()
            if not plan_path.is_file():
                parser.error("--plan must point to an existing project_plan.json file")
            session_dir = plan_path.parent
        else:
            if not getattr(args, "session_dir", None):
                parser.error("--session-dir is required when --plan is not set")
            session_dir = Path(args.session_dir).resolve()
        if args.project_cmd == "plan-lock":
            require_revise_state = not bool(getattr(args, "allow_missing_revise_state", False))
            require_non_stub = bool(getattr(args, "require_non_stub_reviewer", False)) or _env_require_non_stub_reviewer()
            allow_local_stub_attestation = not require_non_stub
            if getattr(args, "check_only", False):
                out = evaluate_project_plan_lock_readiness(
                    session_dir,
                    require_revise_state=require_revise_state,
                    allow_local_stub_attestation=allow_local_stub_attestation,
                )
            else:
                out = write_project_plan_lock(
                    session_dir,
                    require_revise_state=require_revise_state,
                    allow_local_stub_attestation=allow_local_stub_attestation,
                )
            print(json.dumps(out, indent=2))
            if not out.get("ok"):
                sys.exit(2)
            sys.exit(0 if out.get("ready") else 1)
        if args.project_cmd == "validate":
            pf_val = getattr(args, "progress_file", None)
            progress_val = Path(pf_val).resolve() if pf_val else None
            require_plan_lock = bool(getattr(args, "require_plan_lock", False))
            require_non_stub = bool(getattr(args, "require_non_stub_reviewer", False)) or _env_require_non_stub_reviewer()
            vout = validate_project_session(
                session_dir,
                repo_root=root,
                check_workspace=not bool(getattr(args, "skip_workspace", False)),
                progress_file=progress_val,
                require_plan_lock=require_plan_lock,
                require_non_stub_reviewer=require_plan_lock and require_non_stub,
            )
            print(json.dumps(vout, indent=2))
            sys.exit(int(vout.get("exit_code", 2)))
        if args.project_cmd == "status":
            pf_st = getattr(args, "progress_file", None)
            progress_st = Path(pf_st).resolve() if pf_st else None
            snap = describe_project_session(
                session_dir,
                repo_root=root,
                progress_file=progress_st,
                max_concurrent_agents=int(getattr(args, "max_concurrent_agents", 1) or 1),
                max_status_json_bytes=getattr(args, "status_max_json_bytes", None),
                max_status_jsonl_full_scan_bytes=getattr(args, "status_jsonl_full_scan_max_bytes", None),
                max_status_jsonl_tail_bytes=getattr(args, "status_jsonl_tail_bytes", None),
                max_status_listed_step_ids=getattr(args, "status_max_listed_step_ids", None),
            )
            print(json.dumps(snap, indent=2))
            sys.exit(0)
        if args.project_cmd == "export-stage1-observability":
            pf_ob = getattr(args, "progress_file", None)
            progress_ob = Path(pf_ob).resolve() if pf_ob else None
            out_dest = getattr(args, "output", None)
            out_path = Path(out_dest).resolve() if out_dest else None
            wout = write_project_stage1_observability_export(
                session_dir,
                output_path=out_path,
                repo_root=root,
                progress_file=progress_ob,
                max_concurrent_agents=int(getattr(args, "max_concurrent_agents", 1) or 1),
                max_status_json_bytes=getattr(args, "status_max_json_bytes", None),
                max_status_jsonl_full_scan_bytes=getattr(args, "status_jsonl_full_scan_max_bytes", None),
                max_status_jsonl_tail_bytes=getattr(args, "status_jsonl_tail_bytes", None),
                max_status_listed_step_ids=getattr(args, "status_max_listed_step_ids", None),
            )
            print(json.dumps(wout, indent=2))
            sys.exit(0 if wout.get("ok") else 2)
        if args.project_cmd != "run":
            parser.error("unknown project subcommand")
        if args.max_steps < 1:
            parser.error("--max-steps must be >= 1")
        pf_run = getattr(args, "progress_file", None)
        progress_run = Path(pf_run).resolve() if pf_run else None
        out = run_project_session(
            session_dir,
            repo_root=root,
            max_steps=args.max_steps,
            mode=args.mode,
            max_concurrent_agents=int(getattr(args, "max_concurrent_agents", 1) or 1),
            progress_file=progress_run,
            parallel_worktrees=bool(getattr(args, "parallel_worktrees", False)),
            lease_stale_sec=getattr(args, "lease_stale_sec", None),
            enforce_plan_lock=bool(getattr(args, "enforce_plan_lock", False)),
            require_non_stub_reviewer=_strict_reviewer_when_enforcing_project_lock(args),
        )
        print(json.dumps(out, indent=2))
        sys.exit(int(out.get("exit_code", 1)))
    if args.command == "evolve":
        root = Path(args.repo_root).resolve() if args.repo_root else Path.cwd()
        code, last = run_bounded_evolve_loop(
            repo_root=root,
            max_rounds=args.max_rounds,
            target_pct=args.target_pct,
            task=args.task,
            mode=args.mode,
            learning_path=Path(args.learning_path),
            emit_task_json=args.print_task_result,
            verbose=args.verbose,
        )
        print(json.dumps({"exit_code": code, "last_roadmap_review": last}, indent=2))
        sys.exit(code)
    print(generate_report(args.run_id))


if __name__ == "__main__":
    main()
