from __future__ import annotations

import argparse
import json

from orchestrator.api import execute_single_task, generate_report, replay_run, run_benchmark


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sde")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run")
    run.add_argument("--task", required=True)
    run.add_argument("--mode", required=True, choices=["baseline", "guarded_pipeline"])

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
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "benchmark" and not getattr(args, "resume_run_id", None) and not args.suite:
        parser.error("--suite is required unless --resume-run-id is set")
    if args.command == "run":
        print(json.dumps(execute_single_task(args.task, args.mode), indent=2))
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
    print(generate_report(args.run_id))


if __name__ == "__main__":
    main()
