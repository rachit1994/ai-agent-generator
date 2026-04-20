"""Phase 10: project session status snapshot."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from orchestrator.api.project_status import describe_project_session


def test_describe_project_session_minimal(tmp_path: Path) -> None:
    sess = tmp_path / "s"
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
    out = describe_project_session(sess, repo_root=tmp_path, max_concurrent_agents=1)
    assert out["exit_code"] == 0
    assert out["plan"]["present"] is True
    assert out["plan"]["next_tick_batch"] == ["a"]
    pr = out["plan_step_rollups"]
    assert pr["present"] is True
    assert pr["step_count"] == 1
    assert pr["steps"] == [
        {
            "step_id": "a",
            "verification_json_present": False,
            "context_pack_present": False,
            "context_pack_intake_loaded_skipped_oversized": False,
            "context_pack_intake_loaded": None,
            "aggregate_passed": None,
        }
    ]
    assert pr["steps_omitted"] is False
    assert out["progress"]["present"] is False
    rs = out["repo_snapshot"]
    assert rs["path"] == str(tmp_path.resolve())
    assert rs["git_dir_present"] is False
    assert rs["git_available"] is False
    se = out.get("session_events") or {}
    assert se.get("present") is False
    assert se.get("line_count") == 0
    assert se.get("intake_lineage_manifest_present") is False
    pw = out.get("parallel_worktrees") or {}
    assert pw.get("present") is False
    assert pw.get("dir_count") == 0
    ws = out["workspace_status"]
    assert ws["present"] is False
    pl = out["plan_lock"]
    assert pl["present"] is False
    assert pl["ready"] is None
    assert pl["locked"] is None
    g = out["status_at_a_glance"]
    assert g["plan_ok"] is True
    assert g["red_flags"] == []
    assert g["next_tick_batch_count"] == 1
    assert g["runnable_step_ids_count"] == 1
    assert g["intake_merge_anchor_present"] is False
    assert g["intake_loaded_last_progress"] is None
    assert g["intake_loaded_last_driver_state"] is None
    assert g["rollup_context_pack_intake_loaded_true_count"] == 0
    assert g["rollup_context_pack_intake_loaded_false_count"] == 0
    assert g["rollup_context_pack_intake_loaded_null_count"] == 1
    assert g["plan_lock_ready"] is None
    assert g["plan_lock_locked"] is None
    assert g["intake_lineage_manifest_present"] is False
    assert g["intake_lineage_manifest_unreadable"] is False
    assert "intake_merge_anchor_present_but_context_pack_intake_loaded_unknown" not in g["red_flags"]


def test_describe_project_session_glance_intake_fields(tmp_path: Path) -> None:
    sess = tmp_path / "s"
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
    intake = sess / "intake"
    intake.mkdir()
    (intake / "discovery.json").write_text(
        json.dumps({"goal_excerpt": "x", "constraints": []}),
        encoding="utf-8",
    )
    (sess / "progress.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "session_id": "s",
                "completed_step_ids": [],
                "pending_step_ids": ["a"],
                "failed_step_id": None,
                "blocked_reason": None,
                "last_run_id": None,
                "last_output_dir": None,
                "intake_loaded_last": True,
            }
        ),
        encoding="utf-8",
    )
    (sess / "driver_state.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "running",
                "budget": {"max_steps": 5, "steps_used": 0},
                "block_detail": None,
                "intake_loaded_last": True,
            }
        ),
        encoding="utf-8",
    )
    out = describe_project_session(sess, repo_root=tmp_path)
    g = out["status_at_a_glance"]
    assert g["intake_merge_anchor_present"] is True
    assert g["intake_loaded_last_progress"] is True
    assert g["intake_loaded_last_driver_state"] is True
    assert "intake_loaded_last_progress_vs_driver_state_mismatch" not in g["red_flags"]
    assert g["rollup_context_pack_intake_loaded_true_count"] == 0
    assert g["rollup_context_pack_intake_loaded_false_count"] == 0
    assert g["rollup_context_pack_intake_loaded_null_count"] == 1
    assert "intake_merge_anchor_present_but_context_pack_intake_loaded_unknown" not in g["red_flags"]


def test_describe_project_session_glance_intake_mismatch_red_flag(tmp_path: Path) -> None:
    sess = tmp_path / "s"
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
    (sess / "progress.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "session_id": "s",
                "completed_step_ids": [],
                "pending_step_ids": ["a"],
                "failed_step_id": None,
                "blocked_reason": None,
                "last_run_id": None,
                "last_output_dir": None,
                "intake_loaded_last": True,
            }
        ),
        encoding="utf-8",
    )
    (sess / "driver_state.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "running",
                "budget": {"max_steps": 5, "steps_used": 0},
                "block_detail": None,
                "intake_loaded_last": False,
            }
        ),
        encoding="utf-8",
    )
    out = describe_project_session(sess, repo_root=tmp_path)
    g = out["status_at_a_glance"]
    assert "intake_loaded_last_progress_vs_driver_state_mismatch" in g["red_flags"]


def test_describe_project_session_status_at_a_glance_dependency_cycle(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d",
                "depends_on": ["b"],
                "path_scope": [],
            },
            {
                "step_id": "b",
                "phase": "p",
                "title": "B",
                "description": "d",
                "depends_on": ["a"],
                "path_scope": [],
            },
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    out = describe_project_session(sess)
    g = out["status_at_a_glance"]
    assert g["plan_ok"] is False
    assert "dependency_cycle" in g["red_flags"]


def test_describe_project_session_repo_snapshot_root_none(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    out = describe_project_session(sess, repo_root=None)
    rs = out["repo_snapshot"]
    assert rs["reason"] == "repo_root_not_provided"
    assert rs["git_available"] is False


def test_describe_project_session_repo_snapshot_git_repo(tmp_path: Path) -> None:
    if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
        pytest.skip("git not installed")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "status-test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "status-test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    out = describe_project_session(sess, repo_root=repo)
    rs = out["repo_snapshot"]
    assert rs["path"] == str(repo.resolve())
    assert rs["git_dir_present"] is True
    assert rs["inside_work_tree"] is True
    assert rs["git_available"] is True
    assert isinstance(rs.get("head"), str) and len(rs["head"]) >= 7
    assert rs.get("head_short")
    assert rs.get("branch") in ("main", "master", "HEAD")


def test_describe_project_session_workspace_status_skipped_no_git(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "workspace": {"branch": "main", "allowed_path_prefixes": ["src/"]},
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d",
                "depends_on": [],
                "path_scope": ["src/**"],
            },
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    out = describe_project_session(sess, repo_root=tmp_path)
    ws = out["workspace_status"]
    assert ws["present"] is True
    assert ws["from_plan"]["branch"] == "main"
    assert ws["branch_commit_check_skipped"] == "git_not_available"
    assert ws["path_prefix_errors"] == []
    assert ws["path_prefixes_configured"] is True
    assert ws["path_prefixes_ok"] is True


def test_describe_project_session_workspace_status_path_prefix_violation(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "workspace": {"allowed_path_prefixes": ["src/"]},
        "steps": [
            {
                "step_id": "a",
                "phase": "p",
                "title": "A",
                "description": "d",
                "depends_on": [],
                "path_scope": ["docs/**"],
            },
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    out = describe_project_session(sess)
    ws = out["workspace_status"]
    assert ws["path_prefixes_configured"] is True
    assert ws["path_prefixes_ok"] is False
    assert any("outside_prefixes" in e for e in ws["path_prefix_errors"])
    assert "workspace_path_prefix_mismatch" in out["status_at_a_glance"]["red_flags"]


def test_describe_project_session_workspace_status_branch_match(tmp_path: Path) -> None:
    if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
        pytest.skip("git not installed")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "ws-test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "ws-test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    br_proc = subprocess.run(
        ["git", "-C", str(repo), "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=False,
    )
    cur = (br_proc.stdout or "").strip() or "main"
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "workspace": {"branch": cur},
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
    out = describe_project_session(sess, repo_root=repo)
    ws = out["workspace_status"]
    assert ws["present"] is True
    assert ws["branch_commit_match"] is True
    assert ws.get("branch_commit_detail") is None
    assert ws["path_prefixes_configured"] is False
    assert ws["path_prefix_errors"] == []
    assert ws["path_prefixes_ok"] is None


def test_describe_project_session_workspace_status_branch_mismatch(tmp_path: Path) -> None:
    if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
        pytest.skip("git not installed")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "ws-test2@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "ws-test2"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "workspace": {"branch": "nonexistent-branch-xyz"},
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
    out = describe_project_session(sess, repo_root=repo)
    ws = out["workspace_status"]
    assert ws["branch_commit_match"] is False
    assert ws.get("branch_commit_detail")
    assert "workspace_branch_mismatch" in out["status_at_a_glance"]["red_flags"]


def test_describe_project_session_with_progress_and_lease(tmp_path: Path) -> None:
    sess = tmp_path / "s"
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
    prog = {
        "schema_version": "1.0",
        "session_id": "s",
        "completed_step_ids": ["a"],
        "pending_step_ids": [],
        "failed_step_id": None,
        "blocked_reason": None,
        "last_run_id": None,
        "last_output_dir": None,
    }
    (sess / "progress.json").write_text(json.dumps(prog), encoding="utf-8")
    (sess / "leases.json").write_text(
        json.dumps({"leases": [{"step_id": "a", "path_scope": []}]}),
        encoding="utf-8",
    )
    out = describe_project_session(sess)
    assert out["plan"]["all_steps_complete"] is True
    assert out["plan"]["runnable_step_ids"] == []
    assert out["progress"]["present"] is True
    assert out["leases"]["active_row_count"] == 1
    assert out["leases"]["body"]["leases"][0]["step_id"] == "a"
    assert out["session_events"]["present"] is False
    assert (out.get("parallel_worktrees") or {}).get("present") is False


def test_describe_project_session_verification_and_runs(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    agg = {"schema_version": "1.0", "steps": [{"step_id": "a", "passed": True}]}
    (sess / "verification_aggregate.json").write_text(json.dumps(agg), encoding="utf-8")
    dod = {"schema_version": "1.0", "all_required_passed": True, "checks": []}
    (sess / "definition_of_done.json").write_text(json.dumps(dod), encoding="utf-8")
    run_row = {"step_id": "a", "run_id": "r1", "output_dir": "/tmp/out"}
    (sess / "step_runs.jsonl").write_text(json.dumps(run_row) + "\n", encoding="utf-8")
    out = describe_project_session(sess)
    assert out["verification_aggregate"]["present"] is True
    assert out["verification_aggregate"]["body"]["steps"][0]["step_id"] == "a"
    assert out["definition_of_done"]["body"]["all_required_passed"] is True
    assert out["step_runs"]["line_count"] == 1
    assert out["step_runs"]["last"]["run_id"] == "r1"
    assert out["step_runs"]["by_step"]["a"]["run_id"] == "r1"
    assert out["step_runs"]["by_step"]["a"]["output_dir"] == "/tmp/out"


def test_describe_project_session_events_tail(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    row = {"schema_version": "1.0", "ts": "2035-01-01T00:00:00+00:00", "event": "tick", "payload": {"batch": ["x"]}}
    (sess / "session_events.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    out = describe_project_session(sess)
    se = out["session_events"]
    assert se["present"] is True
    assert se["line_count"] == 1
    assert se["last"]["event"] == "tick"
    assert se.get("intake_lineage_manifest_present") is False


def test_describe_project_session_lineage_in_status_block(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    intake = sess / "intake"
    intake.mkdir(parents=True)
    body = {
        "schema_version": "1.0",
        "created_at": "2035-01-01T00:00:00+00:00",
        "artifacts": {"intake/discovery.json": "abc"},
    }
    (intake / "lineage_manifest.json").write_text(json.dumps(body), encoding="utf-8")
    out = describe_project_session(sess)
    se = out["session_events"]
    assert se["intake_lineage_manifest_present"] is True
    assert se["intake_lineage_manifest_schema_version"] == "1.0"
    assert se["intake_lineage_manifest_artifact_count"] == 1
    assert isinstance(se.get("intake_lineage_manifest_file_sha256"), str)
    assert len(se["intake_lineage_manifest_file_sha256"]) == 64
    g = out["status_at_a_glance"]
    assert g["intake_lineage_manifest_present"] is True
    assert g["intake_lineage_manifest_unreadable"] is False


def test_describe_project_session_lineage_unreadable_red_flag(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    intake = sess / "intake"
    intake.mkdir(parents=True)
    (intake / "lineage_manifest.json").write_text("{", encoding="utf-8")
    out = describe_project_session(sess)
    se = out["session_events"]
    assert se["intake_lineage_manifest_present"] is False
    assert se.get("intake_lineage_manifest_unreadable") is True
    assert "intake_lineage_manifest_unreadable" in out["status_at_a_glance"]["red_flags"]


def test_describe_project_session_leases_embed_and_parallel_worktrees(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    (sess / "leases.json").write_text(
        json.dumps({"leases": [{"step_id": "x", "path_scope": ["src/**"]}]}),
        encoding="utf-8",
    )
    wt = sess / "_worktrees"
    wt.mkdir()
    (wt / "s1").mkdir()
    (wt / "s2").mkdir()
    out = describe_project_session(sess)
    ls = out["leases"]
    assert ls["body"]["leases"][0]["step_id"] == "x"
    assert ls["active_row_count"] == 1
    assert ls.get("active_row_count_omitted") is not True
    pw = out["parallel_worktrees"]
    assert pw["present"] is True
    assert pw["dir_count"] == 2
    assert pw["step_ids"] == ["s1", "s2"]


def test_describe_project_session_leases_active_row_count_omitted_when_large(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    pad = "p" * 4000
    (sess / "leases.json").write_text(
        json.dumps({"leases": [{"step_id": "a"}], "pad": pad}),
        encoding="utf-8",
    )
    out = describe_project_session(sess, max_status_json_bytes=500)
    ls = out["leases"]
    assert ls["body"] is None
    assert ls["body_omitted"] is True
    assert ls["active_row_count"] is None
    assert ls["active_row_count_omitted"] is True


def test_describe_project_session_json_body_omitted_when_large(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    pad = "x" * 2000
    (sess / "verification_aggregate.json").write_text(
        json.dumps({"schema_version": "1.0", "pad": pad}),
        encoding="utf-8",
    )
    out = describe_project_session(sess, max_status_json_bytes=100)
    agg = out["verification_aggregate"]
    assert agg["present"] is True
    assert agg["body"] is None
    assert agg["body_omitted"] is True
    assert agg["byte_len"] > 100


def test_describe_project_session_context_lineage_and_dirs(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    row = {"step_id": "z", "built_at": "2035-01-01T00:00:00+00:00", "truncated": False}
    (sess / "context_pack_lineage.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    packs = sess / "context_packs"
    packs.mkdir()
    (packs / "a.json").write_text("{}", encoding="utf-8")
    (packs / "m.json").write_text("{}", encoding="utf-8")
    ver = sess / "verification"
    ver.mkdir()
    (ver / "a.json").write_text("{}", encoding="utf-8")
    out = describe_project_session(sess)
    lin = out["context_pack_lineage"]
    assert lin["present"] is True
    assert lin["line_count"] == 1
    assert lin["last"]["step_id"] == "z"
    cp = out["context_packs"]
    assert cp["present"] is True
    assert cp["file_count"] == 2
    assert cp["step_ids"] == ["a", "m"]
    vb = out["verification_bundles"]
    assert vb["present"] is True
    assert vb["file_count"] == 1
    assert vb["step_ids"] == ["a"]


def test_describe_project_session_step_ids_list_cap(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    packs = sess / "context_packs"
    packs.mkdir()
    (packs / "z.json").write_text("{}", encoding="utf-8")
    (packs / "y.json").write_text("{}", encoding="utf-8")
    out = describe_project_session(sess, max_status_listed_step_ids=1)
    cp = out["context_packs"]
    assert cp["file_count"] == 2
    assert cp["step_ids"] == ["y"]
    assert cp["step_ids_omitted"] is True


def test_describe_project_session_plan_step_rollups(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
            {"step_id": "b", "phase": "p", "title": "B", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    ver = sess / "verification"
    ver.mkdir()
    (ver / "a.json").write_text(json.dumps({"passed": True, "schema_version": "1.0"}), encoding="utf-8")
    packs = sess / "context_packs"
    packs.mkdir()
    (packs / "a.json").write_text(
        json.dumps({"schema_version": "1.1", "intake_loaded": True, "markdown": ""}),
        encoding="utf-8",
    )
    (packs / "b.json").write_text(
        json.dumps({"schema_version": "1.1", "intake_loaded": False, "markdown": ""}),
        encoding="utf-8",
    )
    agg = {
        "schema_version": "1.0",
        "steps": {
            "a": {"present": True, "passed": True},
            "b": {"present": False, "passed": None},
        },
    }
    (sess / "verification_aggregate.json").write_text(json.dumps(agg), encoding="utf-8")
    (sess / "step_runs.jsonl").write_text(
        json.dumps({"step_id": "a", "run_id": "r0", "output_dir": "/old"})
        + "\n"
        + json.dumps({"step_id": "a", "run_id": "r1", "output_dir": "/new"})
        + "\n",
        encoding="utf-8",
    )
    out = describe_project_session(sess)
    rollup = out["plan_step_rollups"]
    assert rollup["present"] is True
    assert rollup["step_count"] == 2
    assert len(rollup["steps"]) == 2
    sa = next(s for s in rollup["steps"] if s["step_id"] == "a")
    assert sa["verification_json_present"] is True
    assert sa["context_pack_present"] is True
    assert sa["context_pack_intake_loaded"] is True
    assert sa["context_pack_intake_loaded_skipped_oversized"] is False
    assert sa["aggregate_passed"] is True
    sb = next(s for s in rollup["steps"] if s["step_id"] == "b")
    assert sb["verification_json_present"] is False
    assert sb["context_pack_present"] is True
    assert sb["context_pack_intake_loaded"] is False
    assert sb["context_pack_intake_loaded_skipped_oversized"] is False
    assert sb["aggregate_passed"] is None
    assert sa["latest_run_id"] == "r1"
    assert sa["latest_output_dir"] == "/new"
    assert "latest_run_id" not in sb
    g = out["status_at_a_glance"]
    assert g["rollup_context_pack_intake_loaded_true_count"] == 1
    assert g["rollup_context_pack_intake_loaded_false_count"] == 1
    assert g["rollup_context_pack_intake_loaded_null_count"] == 0


def test_describe_project_session_plan_step_rollups_cap_and_aggregate_omitted(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
            {"step_id": "b", "phase": "p", "title": "B", "description": "d", "depends_on": [], "path_scope": []},
            {"step_id": "c", "phase": "p", "title": "C", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    out = describe_project_session(sess, max_status_listed_step_ids=1)
    rollup = out["plan_step_rollups"]
    assert rollup["step_count"] == 3
    assert len(rollup["steps"]) == 1
    assert rollup["steps_omitted"] is True
    assert rollup["steps"][0]["step_id"] == "a"

    pad = "z" * 6000
    (sess / "verification_aggregate.json").write_text(
        json.dumps({"schema_version": "1.0", "pad": pad, "steps": {"a": {"passed": True}}}),
        encoding="utf-8",
    )
    out2 = describe_project_session(sess, max_status_json_bytes=800)
    r2 = out2["plan_step_rollups"]
    assert r2["steps"][0]["aggregate_passed"] is None


def test_describe_project_session_rollups_context_pack_intake_omitted_when_pack_too_large(
    tmp_path: Path,
) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    packs = sess / "context_packs"
    packs.mkdir()
    big = {"schema_version": "1.1", "intake_loaded": True, "pad": "x" * 800}
    (packs / "a.json").write_text(json.dumps(big), encoding="utf-8")
    out = describe_project_session(sess, max_status_json_bytes=400)
    row = out["plan_step_rollups"]["steps"][0]
    assert row["context_pack_present"] is True
    assert row["context_pack_intake_loaded"] is None
    assert row["context_pack_intake_loaded_skipped_oversized"] is True


def test_describe_project_session_glance_red_flag_anchor_pack_intake_loaded_unknown(
    tmp_path: Path,
) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    intake = sess / "intake"
    intake.mkdir()
    (intake / "discovery.json").write_text(
        json.dumps({"goal_excerpt": "g", "constraints": []}),
        encoding="utf-8",
    )
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    packs = sess / "context_packs"
    packs.mkdir()
    (packs / "a.json").write_text(
        json.dumps({"schema_version": "1.1", "markdown": ""}),
        encoding="utf-8",
    )
    out = describe_project_session(sess)
    g = out["status_at_a_glance"]
    assert g["intake_merge_anchor_present"] is True
    assert "intake_merge_anchor_present_but_context_pack_intake_loaded_unknown" in g["red_flags"]


def test_describe_project_session_glance_no_red_flag_anchor_when_pack_intake_skipped_oversized(
    tmp_path: Path,
) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    intake = sess / "intake"
    intake.mkdir()
    (intake / "discovery.json").write_text(
        json.dumps({"goal_excerpt": "g", "constraints": []}),
        encoding="utf-8",
    )
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    packs = sess / "context_packs"
    packs.mkdir()
    big = {"schema_version": "1.1", "intake_loaded": True, "pad": "x" * 800}
    (packs / "a.json").write_text(json.dumps(big), encoding="utf-8")
    out = describe_project_session(sess, max_status_json_bytes=400)
    row = out["plan_step_rollups"]["steps"][0]
    assert row["context_pack_intake_loaded_skipped_oversized"] is True
    g = out["status_at_a_glance"]
    assert g["intake_merge_anchor_present"] is True
    assert "intake_merge_anchor_present_but_context_pack_intake_loaded_unknown" not in g["red_flags"]


def test_describe_project_session_glance_red_flag_invalid_doc_review(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    intake = sess / "intake"
    intake.mkdir()
    (intake / "doc_review.json").write_text(
        json.dumps({"passed": "nope", "findings": "bad"}),
        encoding="utf-8",
    )
    out = describe_project_session(sess, repo_root=tmp_path)
    g = out["status_at_a_glance"]
    assert "intake_doc_review_invalid" in g["red_flags"]


def test_describe_project_session_plan_lock_status_and_red_flags(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    (sess / "project_plan_lock.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "ready": False,
                "locked": False,
                "reasons": ["x", "y"],
                "reviewer_proof_summary": {
                    "attestation_type": "local_stub",
                    "attestation_type_allowed": True,
                },
            }
        ),
        encoding="utf-8",
    )
    out = describe_project_session(sess, repo_root=tmp_path)
    pl = out["plan_lock"]
    assert pl["present"] is True
    assert pl["ready"] is False
    assert pl["locked"] is False
    assert pl["reasons_count"] == 2
    rps = pl.get("reviewer_proof_summary") or {}
    assert rps.get("attestation_type") == "local_stub"
    assert rps.get("attestation_type_allowed") is True
    g = out["status_at_a_glance"]
    assert g["plan_lock_ready"] is False
    assert g["plan_lock_locked"] is False
    assert "plan_lock_not_ready" in g["red_flags"]
    assert "plan_lock_not_locked" in g["red_flags"]


def test_describe_project_session_revise_metrics_summary(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    intake = sess / "intake"
    intake.mkdir()
    rows = [
        {
            "schema_version": "1.0",
            "event": "intake_revise_result",
            "at": "2035-01-01T00:00:01+00:00",
            "attempt": 1,
            "status": "retry_allowed",
            "blocked_human": False,
            "findings_count": 2,
            "latency_sec": 5,
        },
        {
            "schema_version": "1.0",
            "event": "intake_revise_result",
            "at": "2035-01-01T00:01:01+00:00",
            "attempt": 2,
            "status": "blocked_human",
            "blocked_human": True,
            "findings_count": 1,
            "latency_sec": 7,
        },
    ]
    (intake / "revise_metrics.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n",
        encoding="utf-8",
    )
    out = describe_project_session(sess, repo_root=tmp_path)
    rm = out["revise_metrics"]
    assert rm["present"] is True
    assert rm["line_count"] == 2
    assert rm["last"]["status"] == "blocked_human"
    summary = rm["summary"]
    assert summary["events_count"] == 2
    assert summary["blocked_human_count"] == 1
    assert summary["avg_latency_sec"] == pytest.approx(6.0)
    assert summary["last_status"] == "blocked_human"
    g = out["status_at_a_glance"]
    assert g["revise_metrics_last_status"] == "blocked_human"
    assert g["revise_metrics_blocked_human_count"] == 1
    assert g["revise_metrics_avg_latency_sec"] == pytest.approx(6.0)


def test_describe_project_session_reviewer_proof_summary_and_red_flags(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    intake = sess / "intake"
    intake.mkdir()
    (intake / "doc_review.json").write_text(
        json.dumps(
            {
                "passed": True,
                "findings": [],
                "reviewer": "reviewer-a",
                "reviewed_at": "2035-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    (intake / "planner_identity.json").write_text(
        json.dumps({"actor_id": "planner-a"}),
        encoding="utf-8",
    )
    (intake / "reviewer_identity.json").write_text(
        json.dumps(
            {
                "actor_id": "reviewer-a",
                "role": "reviewer",
                "attestation_type": "invalid_type",
                "attestation": "x",
                "reviewed_at": "2035-01-01T00:20:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    out = describe_project_session(sess, repo_root=tmp_path)
    rp = out["reviewer_proof"]
    assert rp["present"] is True
    assert rp["reviewer_matches_doc_review"] is True
    assert rp["reviewer_differs_from_planner"] is True
    assert rp["attestation_type_allowed"] is False
    assert rp["reviewed_at_skew_ok"] is False
    g = out["status_at_a_glance"]
    assert g["reviewer_matches_doc_review"] is True
    assert g["reviewer_differs_from_planner"] is True
    assert g["reviewer_attestation_type_allowed"] is False
    assert g["reviewer_attestation_policy_ok"] is None
    assert g["reviewer_signal_source"] == "intake"
    assert g["reviewed_at_skew_ok"] is False
    assert "reviewer_attestation_type_invalid" in g["red_flags"]
    assert "reviewed_at_skew_exceeded" in g["red_flags"]


def test_describe_project_session_glance_prefers_plan_lock_reviewer_proof_summary(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    intake = sess / "intake"
    intake.mkdir()
    (intake / "doc_review.json").write_text(
        json.dumps(
            {
                "passed": True,
                "findings": [],
                "reviewer": "reviewer-a",
                "reviewed_at": "2035-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    (intake / "planner_identity.json").write_text(
        json.dumps({"actor_id": "planner-a"}),
        encoding="utf-8",
    )
    (intake / "reviewer_identity.json").write_text(
        json.dumps(
            {
                "actor_id": "reviewer-a",
                "role": "reviewer",
                "attestation_type": "invalid_type",
                "attestation": "x",
                "reviewed_at": "2035-01-01T00:20:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    (sess / "project_plan_lock.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "ready": True,
                "locked": True,
                "reasons": [],
                "reviewer_proof_summary": {
                    "attestation_type": "agent_signature",
                    "attestation_type_allowed": True,
                    "local_stub_allowed": False,
                    "attestation_policy_ok": True,
                    "reviewer_matches_doc_review": True,
                    "reviewer_differs_from_planner": True,
                    "reviewed_at_skew_ok": True,
                },
            }
        ),
        encoding="utf-8",
    )
    out = describe_project_session(sess, repo_root=tmp_path)
    rp = out["reviewer_proof"]
    assert rp["attestation_type_allowed"] is False
    assert rp["reviewed_at_skew_ok"] is False
    g = out["status_at_a_glance"]
    assert g["reviewer_attestation_type"] == "agent_signature"
    assert g["reviewer_attestation_type_allowed"] is True
    assert g["reviewer_local_stub_allowed"] is False
    assert g["reviewer_attestation_policy_ok"] is True
    assert g["reviewer_signal_source"] == "plan_lock"
    assert g["reviewer_matches_doc_review"] is True
    assert g["reviewer_differs_from_planner"] is True
    assert g["reviewed_at_skew_ok"] is True
    assert "reviewer_attestation_type_invalid" not in g["red_flags"]
    assert "reviewed_at_skew_exceeded" not in g["red_flags"]


def test_describe_project_session_glance_red_flag_reviewer_attestation_policy_failed(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    (sess / "project_plan_lock.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "ready": False,
                "locked": False,
                "reasons": ["reviewer_identity_attestation_stub_disallowed"],
                "reviewer_proof_summary": {
                    "attestation_type": "local_stub",
                    "attestation_type_allowed": True,
                    "local_stub_allowed": False,
                    "attestation_policy_ok": False,
                    "reviewer_matches_doc_review": True,
                    "reviewer_differs_from_planner": True,
                    "reviewed_at_skew_ok": True,
                },
            }
        ),
        encoding="utf-8",
    )
    out = describe_project_session(sess, repo_root=tmp_path)
    g = out["status_at_a_glance"]
    assert g["reviewer_signal_source"] == "plan_lock"
    assert g["reviewer_attestation_policy_ok"] is False
    assert "reviewer_attestation_policy_failed" in g["red_flags"]


def test_describe_project_session_step_runs_by_step_omitted_when_large(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    plan = {
        "schema_version": "1.0",
        "steps": [
            {"step_id": "a", "phase": "p", "title": "A", "description": "d", "depends_on": [], "path_scope": []},
        ],
    }
    (sess / "project_plan.json").write_text(json.dumps(plan), encoding="utf-8")
    lines = [json.dumps({"step_id": "a", "run_id": f"r{i}", "output_dir": f"/o{i}"}) for i in range(80)]
    (sess / "step_runs.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    out = describe_project_session(sess, max_status_jsonl_full_scan_bytes=400)
    sr = out["step_runs"]
    assert sr["by_step_omitted"] is True
    assert sr["by_step"] is None
    assert "latest_run_id" not in out["plan_step_rollups"]["steps"][0]


def test_describe_project_session_jsonl_tail_when_large(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "project_plan.json").write_text("{}", encoding="utf-8")
    lines = [json.dumps({"i": i}) for i in range(400)]
    (sess / "step_runs.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    out = describe_project_session(
        sess,
        max_status_jsonl_full_scan_bytes=500,
        max_status_jsonl_tail_bytes=2000,
    )
    sr = out["step_runs"]
    assert sr["present"] is True
    assert sr["line_count_omitted"] is True
    assert sr["line_count"] is None
    assert sr["last"] is not None
    assert sr["last"]["i"] == 399
    assert sr.get("by_step_omitted") is True
    assert sr.get("by_step") is None
