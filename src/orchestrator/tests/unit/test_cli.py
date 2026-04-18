import sys

import pytest

from orchestrator.runtime.cli.main import build_parser, main


def test_cli_run_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(["run", "--task", "hello", "--mode", "baseline"])
    assert args.command == "run"
    assert args.task == "hello"
    assert args.mode == "baseline"


def test_cli_benchmark_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["benchmark", "--suite", "data/benchmark-tasks.jsonl"])
    assert args.command == "benchmark"
    assert args.mode == "both"
    assert args.max_tasks is None
    assert args.continue_on_error is False


def test_cli_benchmark_resume_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(["benchmark", "--resume-run-id", "run-123"])
    assert args.resume_run_id == "run-123"
    assert args.suite is None


def test_cli_benchmark_missing_suite_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["sde", "benchmark"])
    with pytest.raises(SystemExit):
        main()


def test_cli_benchmark_flags() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "benchmark",
            "--suite",
            "data/benchmark-tasks.jsonl",
            "--max-tasks",
            "3",
            "--continue-on-error",
        ]
    )
    assert args.max_tasks == 3
    assert args.continue_on_error is True


def test_cli_replay_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(["replay", "--run-id", "abc", "--format", "json", "--rerun"])
    assert args.command == "replay"
    assert args.run_id == "abc"
    assert args.format == "json"
    assert args.rerun is True
    assert args.write_html is False


def test_cli_replay_html_and_write_html() -> None:
    parser = build_parser()
    args = parser.parse_args(["replay", "--run-id", "x", "--format", "html", "--write-html"])
    assert args.format == "html"
    assert args.write_html is True
