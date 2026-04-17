from __future__ import annotations

import argparse
import json

from sde.benchmark import run_benchmark
from sde.report import generate_report
from sde.runner import execute_single_task


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run")
    run.add_argument("--task", required=True)
    run.add_argument("--mode", required=True, choices=["baseline", "guarded_pipeline"])

    bench = sub.add_parser("benchmark")
    bench.add_argument("--suite", required=True)
    bench.add_argument("--mode", default="both", choices=["baseline", "guarded_pipeline", "both"])

    report = sub.add_parser("report")
    report.add_argument("--run-id", required=True)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "run":
        print(json.dumps(execute_single_task(args.task, args.mode), indent=2))
        return
    if args.command == "benchmark":
        print(json.dumps(run_benchmark(args.suite, args.mode), indent=2))
        return
    print(generate_report(args.run_id))


if __name__ == "__main__":
    main()
