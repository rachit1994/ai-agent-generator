from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import orchestrator.runtime.cli.main as cli_main
from orchestrator.api.project_driver import run_project_session
from orchestrator.api.project_plan import detect_dependency_cycle, plan_step_ids, runnable_step_ids
from orchestrator.api.project_schema import validate_project_plan, validate_progress
from orchestrator.api.project_scheduler import select_steps_for_tick
from orchestrator.runtime.cli.main import build_parser, main, _env_require_non_stub_reviewer


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
    intake = session / "intake"
    intake.mkdir()
    (intake / "discovery.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "goal_excerpt": "smoke session goal",
                "constraints": [],
                "non_goals": [],
                "open_questions": [],
            }
        ),
        encoding="utf-8",
    )
    (intake / "lineage_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "created_at": "2035-01-01T00:00:00+00:00",
                "artifacts": {"intake/discovery.json": "not-a-real-hash"},
            }
        ),
        encoding="utf-8",
    )
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
    term_ev = ev_lines[-1]
    assert term_ev["event"] == "session_terminal"
    assert term_ev["payload"].get("intake_merge_anchor_present") is True
    assert term_ev["payload"].get("intake_loaded_last") is True
    assert term_ev["payload"].get("intake_lineage_manifest_present") is True
    assert term_ev["payload"].get("intake_lineage_manifest_artifact_count") == 1
    assert isinstance(term_ev["payload"].get("intake_lineage_manifest_file_sha256"), str)
    start_ev = next(x for x in ev_lines if x["event"] == "session_driver_start")
    assert start_ev["payload"].get("intake_merge_anchor_present") is True
    assert start_ev["payload"].get("intake_loaded_last") is False
    assert start_ev["payload"].get("intake_lineage_manifest_present") is True
    tick_events = [x for x in ev_lines if x["event"] == "tick"]
    assert tick_events[0]["payload"].get("intake_merge_anchor_present") is True
    assert tick_events[0]["payload"].get("intake_loaded_last") is False
    assert tick_events[0]["payload"].get("intake_lineage_manifest_present") is True
    assert tick_events[1]["payload"].get("intake_loaded_last") is True
    assert tick_events[1]["payload"].get("intake_lineage_manifest_present") is True
    prog_final = json.loads((session / "progress.json").read_text(encoding="utf-8"))
    assert prog_final.get("intake_loaded_last") is True
    assert validate_progress(prog_final) == []
    ds_final = json.loads((session / "driver_state.json").read_text(encoding="utf-8"))
    assert ds_final.get("intake_loaded_last") is True


def test_validate_progress_bad() -> None:
    errs = validate_progress({"schema_version": "0.9", "completed_step_ids": [], "pending_step_ids": []})
    assert errs


def test_validate_progress_intake_loaded_last_must_be_bool() -> None:
    body = {
        "schema_version": "1.0",
        "session_id": "s",
        "completed_step_ids": [],
        "pending_step_ids": [],
        "intake_loaded_last": "yes",
    }
    assert validate_progress(body) == ["progress_intake_loaded_last_bad"]


def test_validate_progress_rejects_bad_optional_identity_fields() -> None:
    body = {
        "schema_version": "1.0",
        "session_id": "   ",
        "completed_step_ids": [],
        "pending_step_ids": [],
        "failed_step_id": "",
        "blocked_reason": "   ",
        "last_run_id": "",
        "last_output_dir": "",
    }
    errs = validate_progress(body)
    assert "progress_session_id_bad" in errs
    assert "progress_failed_step_id_bad" in errs
    assert "progress_blocked_reason_bad" in errs
    assert "progress_last_run_id_bad" in errs
    assert "progress_last_output_dir_bad" in errs


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
    assert args.enforce_plan_lock is False
    assert args.require_non_stub_reviewer is False


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
    assert args.enforce_plan_lock is False
    assert args.require_non_stub_reviewer is False


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


def test_validate_project_plan_rejects_blank_verification_command() -> None:
    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d",
                "depends_on": [],
                "path_scope": [],
                "verification": {"commands": [{"cmd": "   ", "args": []}]},
            },
        ],
    }
    errs = validate_project_plan(plan)
    assert "project_plan_verification_cmd_bad:a:0" in errs


def test_validate_project_plan_rejects_non_string_verification_args() -> None:
    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d",
                "depends_on": [],
                "path_scope": [],
                "verification": {"commands": [{"cmd": "pytest", "args": ["-q", 1]}]},
            },
        ],
    }
    errs = validate_project_plan(plan)
    assert "project_plan_verification_args_bad:a:0" in errs


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
    assert args.require_plan_lock is False
    assert args.require_non_stub_reviewer is False


def test_cli_project_validate_require_plan_lock_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "validate",
            "--session-dir",
            "/tmp/s",
            "--require-plan-lock",
        ]
    )
    assert args.project_cmd == "validate"
    assert args.require_plan_lock is True
    assert args.require_non_stub_reviewer is False


def test_cli_project_validate_require_non_stub_reviewer_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "validate",
            "--session-dir",
            "/tmp/s",
            "--require-plan-lock",
            "--require-non-stub-reviewer",
        ]
    )
    assert args.project_cmd == "validate"
    assert args.require_plan_lock is True
    assert args.require_non_stub_reviewer is True


def test_cli_project_plan_lock_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "plan-lock",
            "--session-dir",
            "/tmp/sess",
            "--check-only",
            "--allow-missing-revise-state",
        ]
    )
    assert args.project_cmd == "plan-lock"
    assert args.session_dir == "/tmp/sess"
    assert args.check_only is True
    assert args.allow_missing_revise_state is True
    assert args.require_non_stub_reviewer is False


def test_cli_project_plan_lock_require_non_stub_reviewer_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "plan-lock",
            "--session-dir",
            "/tmp/sess",
            "--require-non-stub-reviewer",
        ]
    )
    assert args.project_cmd == "plan-lock"
    assert args.require_non_stub_reviewer is True


def test_env_require_non_stub_reviewer_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SDE_REQUIRE_NON_STUB_REVIEWER", raising=False)
    assert _env_require_non_stub_reviewer() is False
    for v in ("1", "TRUE", "yes", "On"):
        monkeypatch.setenv("SDE_REQUIRE_NON_STUB_REVIEWER", v)
        assert _env_require_non_stub_reviewer() is True
    monkeypatch.setenv("SDE_REQUIRE_NON_STUB_REVIEWER", "0")
    assert _env_require_non_stub_reviewer() is False


def test_cli_plan_lock_check_only_env_strict_calls_readiness(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[bool] = []

    def spy(
        session_dir,
        *,
        require_revise_state=True,
        allow_local_stub_attestation=True,
    ):
        calls.append(allow_local_stub_attestation)
        return {
            "ok": True,
            "ready": False,
            "session_dir": str(session_dir),
            "reasons": ["x"],
            "require_revise_state": require_revise_state,
        }

    monkeypatch.setenv("SDE_REQUIRE_NON_STUB_REVIEWER", "1")
    monkeypatch.setattr(cli_main, "evaluate_project_plan_lock_readiness", spy)
    sess = tmp_path / "sl"
    sess.mkdir()
    (sess / "project_plan.json").write_text(
        json.dumps({"schema_version": "1.0", "steps": []}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["sde", "project", "plan-lock", "--session-dir", str(sess), "--check-only"],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    assert calls == [False]


def test_cli_validate_env_strict_only_when_require_plan_lock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    seq: list[bool | None] = []

    def spy(*_args, **kwargs):
        seq.append(kwargs.get("require_non_stub_reviewer"))
        return {"exit_code": 0, "ok": True}

    monkeypatch.setenv("SDE_REQUIRE_NON_STUB_REVIEWER", "1")
    monkeypatch.setattr(cli_main, "validate_project_session", spy)
    sess = tmp_path / "vsl"
    sess.mkdir()
    (sess / "project_plan.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
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
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sde",
            "project",
            "validate",
            "--session-dir",
            str(sess),
            "--skip-workspace",
            "--require-plan-lock",
        ],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    assert seq == [True]

    seq.clear()
    monkeypatch.setattr(
        sys,
        "argv",
        ["sde", "project", "validate", "--session-dir", str(sess), "--skip-workspace"],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    assert seq == [False]


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


def test_cli_enforce_plan_lock_parse() -> None:
    parser = build_parser()
    pr = parser.parse_args(
        ["project", "run", "--session-dir", "/tmp/s", "--enforce-plan-lock"]
    )
    assert pr.enforce_plan_lock is True
    assert pr.require_non_stub_reviewer is False
    cont = parser.parse_args(
        [
            "continuous",
            "--project-session-dir",
            "/tmp/p",
            "--repo-root",
            "/tmp/r",
            "--enforce-plan-lock",
        ]
    )
    assert cont.enforce_plan_lock is True
    assert cont.require_non_stub_reviewer is False


def test_cli_project_run_enforce_lock_require_non_stub_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "project",
            "run",
            "--session-dir",
            "/tmp/s",
            "--enforce-plan-lock",
            "--require-non-stub-reviewer",
            "--max-steps",
            "3",
            "--mode",
            "baseline",
        ]
    )
    assert args.enforce_plan_lock is True
    assert args.require_non_stub_reviewer is True


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


def test_run_project_session_require_non_stub_forwards_to_lock_readiness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, bool] = {}

    def fake_eval(
        _session_dir,
        *,
        require_revise_state=True,
        allow_local_stub_attestation=True,
    ):
        captured["allow_local_stub"] = allow_local_stub_attestation
        return {
            "ok": True,
            "ready": False,
            "session_dir": str(_session_dir),
            "reasons": ["stub_gate"],
            "require_revise_state": require_revise_state,
        }

    monkeypatch.setattr("orchestrator.api.project_driver.evaluate_project_plan_lock_readiness", fake_eval)
    sess = tmp_path / "plrun"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
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
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    out = run_project_session(
        sess,
        repo_root=tmp_path,
        max_steps=1,
        mode="baseline",
        enforce_plan_lock=True,
        require_non_stub_reviewer=True,
    )
    assert out["exit_code"] == 1
    assert captured.get("allow_local_stub") is False

    captured.clear()
    out2 = run_project_session(
        sess,
        repo_root=tmp_path,
        max_steps=1,
        mode="baseline",
        enforce_plan_lock=True,
        require_non_stub_reviewer=False,
    )
    assert out2["exit_code"] == 1
    assert captured.get("allow_local_stub") is True
