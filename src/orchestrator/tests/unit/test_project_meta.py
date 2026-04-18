from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator.api.project_driver import run_project_session
from orchestrator.api.project_plan import detect_dependency_cycle, plan_step_ids, runnable_step_ids
from orchestrator.api.project_schema import validate_project_plan, validate_progress
from orchestrator.api.project_scheduler import select_steps_for_tick
from orchestrator.runtime.cli.main import build_parser


def test_validate_project_plan_ok() -> None:
    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "do a",
                "depends_on": [],
                "path_scope": ["src/**"],
                "verification": {"commands": [{"cmd": "true", "args": []}]},
            }
        ],
    }
    assert validate_project_plan(plan) == []


def test_detect_dependency_cycle() -> None:
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "x", "depends_on": ["b"], "path_scope": []},
            {"step_id": "b", "phase": "p", "title": "B", "description": "y", "depends_on": ["a"], "path_scope": []},
        ],
    }
    cyc = detect_dependency_cycle(plan)
    assert cyc is not None


def test_plan_step_ids_order() -> None:
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "z", "phase": "p", "title": "", "description": "x", "depends_on": [], "path_scope": []},
            {"step_id": "y", "phase": "p", "title": "", "description": "y", "depends_on": [], "path_scope": []},
        ],
    }
    assert plan_step_ids(plan) == ["z", "y"]


def test_runnable_step_ids_order() -> None:
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "", "description": "x", "depends_on": [], "path_scope": []},
            {"step_id": "b", "phase": "p", "title": "", "description": "y", "depends_on": ["a"], "path_scope": []},
        ],
    }
    assert runnable_step_ids(plan, set()) == ["a"]
    assert runnable_step_ids(plan, {"a"}) == ["b"]


def test_select_steps_disjoint() -> None:
    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "",
                "description": "",
                "depends_on": [],
                "path_scope": ["src/**"],
            },
            {
                "step_id": "b",
                "phase": "p",
                "title": "",
                "description": "",
                "depends_on": [],
                "path_scope": ["docs/**"],
            },
        ],
    }
    got = select_steps_for_tick(plan, set(), max_concurrent_agents=2)
    assert "a" in got and "b" in got


def test_run_project_session_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    session = tmp_path / "sess"
    session.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d1",
                "depends_on": [],
                "path_scope": [],
            },
            {
                "step_id": "b",
                "phase": "p",
                "title": "B",
                "description": "d2",
                "depends_on": ["a"],
                "path_scope": [],
            },
        ],
    }
    (session / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    calls: list[str] = []

    def fake_execute(
        task: str,
        mode: str,
        *,
        repeat: int = 1,
        project_step_id: str | None = None,
        project_session_dir: str | None = None,
    ) -> dict:
        calls.append((task[:20], project_step_id, project_session_dir))
        rid = f"r{len(calls)}"
        od = tmp_path / rid
        od.mkdir(exist_ok=True)
        return {"run_id": rid, "output_dir": str(od), "output": '{"answer":"","checks":[{"name":"verifier_passed","passed":true}],"refusal":null}'}

    def fake_verify(**kwargs: object) -> dict:
        session_dir = kwargs["session_dir"]
        step_id = str(kwargs["step_id"])
        assert isinstance(session_dir, Path)
        vdir = session_dir / "verification"
        vdir.mkdir(parents=True, exist_ok=True)
        bundle = {"schema_version": "1.0", "step_id": step_id, "passed": True, "commands": []}
        (vdir / f"{step_id}.json").write_text(json.dumps(bundle), encoding="utf-8")
        return bundle

    monkeypatch.setattr("orchestrator.api.project_driver.execute_single_task", fake_execute)
    monkeypatch.setattr("orchestrator.api.project_driver.run_step_verification", fake_verify)
    out = run_project_session(session, repo_root=tmp_path, max_steps=10, mode="baseline")
    assert out["exit_code"] == 0
    assert out["stopped_reason"] == "completed_review_pass"
    assert len(calls) == 2
    assert calls[0][1] == "a" and calls[1][1] == "b"
    assert calls[0][2] == str(session.resolve())
    dod = out.get("definition_of_done") or {}
    assert dod.get("all_required_passed") is True
    assert (session / "verification_aggregate.json").is_file()
    assert (session / "definition_of_done.json").is_file()
    assert (session / "stop_report.json").is_file()
    assert out.get("stop_report_path")
    ev_path = session / "session_events.jsonl"
    assert ev_path.is_file()
    ev_lines = [json.loads(x) for x in ev_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    ev_names = [x["event"] for x in ev_lines]
    assert "session_driver_start" in ev_names
    assert ev_names.count("tick") >= 2
    assert ev_names[-1] == "session_terminal"


def test_validate_progress_bad() -> None:
    errs = validate_progress({"schema_version": "0.9", "completed_step_ids": [], "pending_step_ids": []})
    assert errs


def test_cli_project_run_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "run",
            "--session-dir",
            "/tmp/sde_sess",
            "--max-steps",
            "12",
            "--mode",
            "baseline",
            "--max-concurrent-agents",
            "2",
        ]
    )
    assert args.command == "project"
    assert args.project_cmd == "run"
    assert args.session_dir == "/tmp/sde_sess"
    assert getattr(args, "project_plan_file", None) is None
    assert args.max_steps == 12
    assert args.max_concurrent_agents == 2


def test_cli_project_run_plan_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["project", "run", "--plan", "/tmp/myproj/project_plan.json", "--max-steps", "3"]
    )
    assert args.project_plan_file == "/tmp/myproj/project_plan.json"
    assert getattr(args, "session_dir", None) is None


def test_cli_continuous_project_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "continuous",
            "--project-session-dir",
            "/tmp/p",
            "--repo-root",
            "/tmp/r",
            "--max-iterations",
            "5",
            "--mode",
            "baseline",
            "--progress-file",
            "/tmp/state/progress.json",
        ]
    )
    assert args.project_session_dir == "/tmp/p"
    assert args.repo_root == "/tmp/r"
    assert args.max_concurrent_agents == 1
    assert args.progress_file == "/tmp/state/progress.json"


def test_cli_continuous_project_plan_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "continuous",
            "--project-plan",
            "/tmp/proj/project_plan.json",
            "--progress-file",
            "/tmp/other/progress.json",
        ]
    )
    assert args.continuous_project_plan == "/tmp/proj/project_plan.json"
    assert args.progress_file == "/tmp/other/progress.json"


def test_validate_project_plan_workspace_lease_ttl_bad() -> None:
    plan = {
        "schema_version": "1.0",
        "workspace": {"lease_ttl_sec": 30},
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d",
                "depends_on": [],
                "path_scope": [],
            },
        ],
    }
    assert "project_plan_workspace_lease_ttl_sec_bad" in validate_project_plan(plan)


def test_cli_parallel_worktrees_flags() -> None:
    parser = build_parser()
    pr = parser.parse_args(
        [
            "project",
            "run",
            "--session-dir",
            "/tmp/s",
            "--parallel-worktrees",
            "--max-concurrent-agents",
            "2",
        ]
    )
    assert pr.parallel_worktrees is True
    cont = parser.parse_args(
        [
            "continuous",
            "--project-session-dir",
            "/tmp/p",
            "--repo-root",
            "/tmp/r",
            "--parallel-worktrees",
        ]
    )
    assert cont.parallel_worktrees is True


def test_cli_project_status_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "status",
            "--session-dir",
            "/tmp/sess",
            "--max-concurrent-agents",
            "2",
            "--status-max-json-bytes",
            "65536",
            "--status-jsonl-full-scan-max-bytes",
            "8192",
            "--status-jsonl-tail-bytes",
            "4096",
            "--status-max-listed-step-ids",
            "128",
        ]
    )
    assert args.project_cmd == "status"
    assert args.session_dir == "/tmp/sess"
    assert args.max_concurrent_agents == 2
    assert args.status_max_json_bytes == 65536
    assert args.status_jsonl_full_scan_max_bytes == 8192
    assert args.status_jsonl_tail_bytes == 4096
    assert args.status_max_listed_step_ids == 128


def test_cli_project_validate_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "validate",
            "--plan",
            "/tmp/x/project_plan.json",
            "--skip-workspace",
            "--progress-file",
            "/tmp/p/progress.json",
        ]
    )
    assert args.project_cmd == "validate"
    assert args.project_plan_file == "/tmp/x/project_plan.json"
    assert args.skip_workspace is True
    assert args.progress_file == "/tmp/p/progress.json"


def test_cli_lease_stale_sec_parse() -> None:
    parser = build_parser()
    pr = parser.parse_args(
        ["project", "run", "--session-dir", "/tmp/s", "--lease-stale-sec", "0"]
    )
    assert pr.lease_stale_sec == 0
    c = parser.parse_args(
        [
            "continuous",
            "--project-session-dir",
            "/tmp/p",
            "--repo-root",
            "/tmp/r",
            "--lease-stale-sec",
            "120",
        ]
    )
    assert c.lease_stale_sec == 120


def test_run_project_session_custom_progress_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    session = tmp_path / "sess"
    session.mkdir()
    alt = tmp_path / "state"
    alt.mkdir()
    prog_path = alt / "progress.json"
    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d1",
                "depends_on": [],
                "path_scope": [],
            },
        ],
    }
    (session / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")

    def fake_execute(
        task: str,
        mode: str,
        *,
        repeat: int = 1,
        project_step_id: str | None = None,
        project_session_dir: str | None = None,
    ) -> dict:
        rid = "r1"
        od = tmp_path / rid
        od.mkdir(exist_ok=True)
        return {"run_id": rid, "output_dir": str(od), "output": '{"answer":"","checks":[{"name":"verifier_passed","passed":true}],"refusal":null}'}

    def fake_verify(**kwargs: object) -> dict:
        session_dir = kwargs["session_dir"]
        step_id = str(kwargs["step_id"])
        vdir = session_dir / "verification"
        vdir.mkdir(parents=True, exist_ok=True)
        bundle = {"schema_version": "1.0", "step_id": step_id, "passed": True, "commands": []}
        (vdir / f"{step_id}.json").write_text(json.dumps(bundle), encoding="utf-8")
        return bundle

    monkeypatch.setattr("orchestrator.api.project_driver.execute_single_task", fake_execute)
    monkeypatch.setattr("orchestrator.api.project_driver.run_step_verification", fake_verify)
    out = run_project_session(session, repo_root=tmp_path, max_steps=10, mode="baseline", progress_file=prog_path)
    assert out["exit_code"] == 0
    assert prog_path.is_file()
    assert not (session / "progress.json").is_file()
