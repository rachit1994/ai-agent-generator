import sys

import pytest

import orchestrator.runtime.cli.main as cli_main
from orchestrator.runtime.cli.main import build_parser, main


def test_cli_continuous_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "continuous",
            "--task",
            "build the thing",
            "--mode",
            "baseline",
            "--max-iterations",
            "50",
            "--stop-when",
            "never",
        ]
    )
    assert args.command == "continuous"
    assert args.task == "build the thing"
    assert args.mode == "baseline"
    assert args.max_iterations == 50
    assert args.stop_when == "never"
    assert args.continue_on_pipeline_error is False


def test_cli_run_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(["run", "--task", "hello", "--mode", "baseline"])
    assert args.command == "run"
    assert args.task == "hello"
    assert args.mode == "baseline"
    assert args.repeat == 1


def test_cli_run_repeat_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(["run", "--task", "hello", "--mode", "baseline", "--repeat", "3"])
    assert args.repeat == 3


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


def test_cli_validate_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(["validate", "--run-id", "abc-123", "--mode", "baseline"])
    assert args.command == "validate"
    assert args.run_id == "abc-123"
    assert args.mode == "baseline"


def test_cli_validate_parse_default_mode() -> None:
    parser = build_parser()
    args = parser.parse_args(["validate", "--run-id", "x"])
    assert args.mode is None


def test_cli_validate_exit_zero_when_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["sde", "validate", "--run-id", "r"])
    monkeypatch.setattr(cli_main, "validate_run", lambda *_args, **_kwargs: {"ok": True, "validation_ready": True})
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


def test_cli_validate_exit_one_when_not_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["sde", "validate", "--run-id", "r"])
    monkeypatch.setattr(cli_main, "validate_run", lambda *_args, **_kwargs: {"ok": False, "validation_ready": False})
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1


def test_cli_validate_benchmark_aggregate_exit_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["sde", "validate", "--run-id", "bench"])
    monkeypatch.setattr(
        cli_main,
        "validate_run",
        lambda *_args, **_kwargs: {
            "ok": True,
            "validation_ready": False,
            "execution_gates_applied": False,
            "errors": [],
            "hard_stops": [],
            "run_kind": "benchmark_aggregate",
        },
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


def test_cli_replay_html_and_write_html() -> None:
    parser = build_parser()
    args = parser.parse_args(["replay", "--run-id", "x", "--format", "html", "--write-html"])
    assert args.format == "html"
    assert args.write_html is True


def test_cli_project_remaining_work_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "remaining-work",
            "--repo-root",
            "/tmp/repo",
            "--rules",
            "docs/rules.json",
            "--format",
            "json",
        ]
    )
    assert args.command == "project"
    assert args.project_cmd == "remaining-work"
    assert args.repo_root == "/tmp/repo"
    assert args.rules == "docs/rules.json"
    assert args.format == "json"
