from agent_mvp.cli.main import build_parser


def test_cli_run_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(["run", "--task", "hello", "--mode", "baseline"])
    assert args.command == "run"
    assert args.task == "hello"
    assert args.mode == "baseline"


def test_cli_benchmark_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["benchmark", "--suite", "data/mvp-tasks.jsonl"])
    assert args.command == "benchmark"
    assert args.mode == "both"
