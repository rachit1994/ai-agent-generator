"""Phase 10–21: read-only project session snapshot (status / observability)."""

from __future__ import annotations

from datetime import datetime
import json
import subprocess
from pathlib import Path
from typing import Any

from .project_aggregate import VERIFICATION_AGGREGATE_FILENAME
from .project_events import SESSION_EVENTS_FILENAME
from .project_intake_util import intake_doc_review_errors, intake_merge_anchor_present
from .project_plan import all_steps_complete, detect_dependency_cycle, plan_step_ids, runnable_step_ids
from .project_plan_lock import lineage_manifest_session_event_snapshot
from .project_scheduler import select_steps_for_tick
from .project_schema import read_json_dict, validate_project_plan
from .project_workspace import git_head_matches_branch, plan_workspace_path_errors


STEP_RUNS_FILENAME = "step_runs.jsonl"
DEFINITION_OF_DONE_FILENAME = "definition_of_done.json"
CONTEXT_PACK_LINEAGE_FILENAME = "context_pack_lineage.jsonl"
CONTEXT_PACKS_DIRNAME = "context_packs"
VERIFICATION_DIRNAME = "verification"
WORKTREES_DIRNAME = "_worktrees"

DEFAULT_STATUS_MAX_JSON_BYTES = 512 * 1024
DEFAULT_STATUS_JSONL_FULL_SCAN_BYTES = 1024 * 1024
DEFAULT_STATUS_JSONL_TAIL_BYTES = 256 * 1024
DEFAULT_STATUS_MAX_LISTED_STEP_IDS = 256
_REVIEWED_AT_SKEW_MAX_SEC = 300
_REVIEWER_ATTESTATION_ALLOWLIST = {"local_stub", "agent_signature", "service_token"}


def _git_stdout(repo_root: Path, *git_args: str) -> tuple[bool, str | None]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), *git_args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, None
    if proc.returncode != 0:
        return False, None
    out = proc.stdout.strip()
    return True, out if out else None


def _repo_git_snapshot(repo_root: Path) -> dict[str, Any]:
    """Read-only ``git rev-parse`` facts for dashboards (no writes)."""
    root = repo_root.resolve()
    block: dict[str, Any] = {"path": str(root), "git_dir_present": (root / ".git").exists()}
    if not block["git_dir_present"]:
        block["git_available"] = False
        return block
    ok, inside = _git_stdout(root, "rev-parse", "--is-inside-work-tree")
    if not ok or inside != "true":
        block["git_available"] = False
        block["read_error"] = "not_a_git_work_tree"
        return block
    block["inside_work_tree"] = True
    ok_head, head = _git_stdout(root, "rev-parse", "HEAD")
    ok_short, short = _git_stdout(root, "rev-parse", "--short", "HEAD")
    ok_br, br = _git_stdout(root, "rev-parse", "--abbrev-ref", "HEAD")
    block["git_available"] = bool(ok_head and head)
    block["head"] = head
    block["head_short"] = short if ok_short else None
    block["branch"] = br if ok_br else None
    if not block["git_available"]:
        block["read_error"] = "git_rev_parse_head_failed"
    return block


def _workspace_status_block(
    plan: dict[str, Any] | None,
    repo_root: Path | None,
    repo_snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Echo ``plan.workspace``, prefix/path_scope checks, and optional ``git_head_matches_branch``."""
    if plan is None:
        return {"present": False}
    ws = plan.get("workspace")
    if not isinstance(ws, dict) or not ws:
        return {"present": False}
    prefix_errs = plan_workspace_path_errors(plan)
    prefs = ws.get("allowed_path_prefixes")
    prefixes_configured = (
        isinstance(prefs, list)
        and bool([p for p in prefs if isinstance(p, str) and p.strip()])
    )
    out_block: dict[str, Any] = {
        "present": True,
        "from_plan": dict(ws),
        "path_prefix_errors": prefix_errs,
        "path_prefixes_configured": prefixes_configured,
        "path_prefixes_ok": (len(prefix_errs) == 0) if prefixes_configured else None,
    }
    br = ws.get("branch")
    if repo_root is None:
        out_block["branch_commit_match"] = None
        out_block["branch_commit_check_skipped"] = "repo_root_not_provided"
        return out_block
    if not isinstance(br, str) or not br.strip():
        out_block["branch_commit_match"] = None
        out_block["branch_commit_check_skipped"] = "plan_branch_not_set"
        return out_block
    if not repo_snapshot.get("git_available"):
        out_block["branch_commit_match"] = None
        out_block["branch_commit_check_skipped"] = "git_not_available"
        return out_block
    ok, detail = git_head_matches_branch(repo_root.resolve(), br)
    out_block["branch_commit_match"] = ok
    out_block["branch_commit_detail"] = detail
    return out_block


def _plan_lock_status_block(session_dir: Path, *, max_bytes: int) -> dict[str, Any]:
    """Embed ``project_plan_lock.json`` and lift core booleans for glance dashboards."""
    lock_path = session_dir / "project_plan_lock.json"
    block = _embed_dict_json_file(lock_path, max_bytes=max_bytes)
    body = block.get("body") if isinstance(block.get("body"), dict) else None
    block["ready"] = body.get("ready") if isinstance(body, dict) else None
    block["locked"] = body.get("locked") if isinstance(body, dict) else None
    reasons = body.get("reasons") if isinstance(body, dict) else None
    block["reasons_count"] = len(reasons) if isinstance(reasons, list) else None
    proof = body.get("reviewer_proof_summary") if isinstance(body, dict) else None
    block["reviewer_proof_summary"] = proof if isinstance(proof, dict) else None
    return block


def _parse_iso_seconds(value: Any) -> int | None:
    if not isinstance(value, str) or not value.strip():
        return None
    txt = value.strip()
    if txt.endswith("Z"):
        txt = txt[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(txt)
    except ValueError:
        return None
    return int(dt.timestamp())


def _reviewer_proof_status_block(session_dir: Path) -> dict[str, Any]:
    intake_dir = session_dir / "intake"
    out: dict[str, Any] = {"present": intake_dir.is_dir()}
    if not intake_dir.is_dir():
        return out
    doc = _read_json_optional(intake_dir / "doc_review.json")
    planner = _read_json_optional(intake_dir / "planner_identity.json")
    reviewer = _read_json_optional(intake_dir / "reviewer_identity.json")
    out["doc_review_present"] = doc is not None
    out["planner_identity_present"] = planner is not None
    out["reviewer_identity_present"] = reviewer is not None
    doc_reviewer = doc.get("reviewer") if isinstance(doc, dict) else None
    reviewer_actor = reviewer.get("actor_id") if isinstance(reviewer, dict) else None
    planner_actor = planner.get("actor_id") if isinstance(planner, dict) else None
    out["doc_review_reviewer"] = doc_reviewer if isinstance(doc_reviewer, str) else None
    out["reviewer_actor_id"] = reviewer_actor if isinstance(reviewer_actor, str) else None
    out["planner_actor_id"] = planner_actor if isinstance(planner_actor, str) else None
    out["reviewer_matches_doc_review"] = (
        isinstance(doc_reviewer, str)
        and doc_reviewer.strip()
        and isinstance(reviewer_actor, str)
        and reviewer_actor.strip()
        and doc_reviewer.strip() == reviewer_actor.strip()
    )
    out["reviewer_differs_from_planner"] = (
        isinstance(reviewer_actor, str)
        and reviewer_actor.strip()
        and isinstance(planner_actor, str)
        and planner_actor.strip()
        and reviewer_actor.strip() != planner_actor.strip()
    )
    att_type = reviewer.get("attestation_type") if isinstance(reviewer, dict) else None
    out["attestation_type"] = att_type if isinstance(att_type, str) else None
    out["attestation_type_allowed"] = isinstance(att_type, str) and att_type.strip() in _REVIEWER_ATTESTATION_ALLOWLIST
    doc_reviewed_at = doc.get("reviewed_at") if isinstance(doc, dict) else None
    reviewer_reviewed_at = reviewer.get("reviewed_at") if isinstance(reviewer, dict) else None
    out["doc_reviewed_at"] = doc_reviewed_at if isinstance(doc_reviewed_at, str) else None
    out["reviewer_reviewed_at"] = reviewer_reviewed_at if isinstance(reviewer_reviewed_at, str) else None
    doc_s = _parse_iso_seconds(doc_reviewed_at)
    reviewer_s = _parse_iso_seconds(reviewer_reviewed_at)
    out["doc_reviewed_at_valid"] = doc_s is not None
    out["reviewer_reviewed_at_valid"] = reviewer_s is not None
    if doc_s is not None and reviewer_s is not None:
        skew = abs(doc_s - reviewer_s)
        out["reviewed_at_skew_sec"] = skew
        out["reviewed_at_skew_ok"] = skew <= _REVIEWED_AT_SKEW_MAX_SEC
    else:
        out["reviewed_at_skew_sec"] = None
        out["reviewed_at_skew_ok"] = None
    return out


def _revise_metrics_status_block(
    session_dir: Path,
    *,
    max_full_scan_bytes: int,
    max_tail_bytes: int,
) -> dict[str, Any]:
    path = session_dir / "intake" / "revise_metrics.jsonl"
    block = {"path": str(path), "present": path.is_file()}
    stats = _jsonl_line_count_and_last(
        path,
        max_full_scan_bytes=max_full_scan_bytes,
        max_tail_bytes=max_tail_bytes,
    )
    block.update(stats)
    if not path.is_file():
        block["summary"] = {
            "events_count": 0,
            "blocked_human_count": 0,
            "avg_latency_sec": None,
            "last_status": None,
        }
        return block
    if stats.get("line_count_omitted"):
        block["summary"] = {
            "events_count": None,
            "blocked_human_count": None,
            "avg_latency_sec": None,
            "last_status": (stats.get("last") or {}).get("status") if isinstance(stats.get("last"), dict) else None,
            "summary_omitted_due_to_size": True,
        }
        return block
    events_count = 0
    blocked_human_count = 0
    latency_total = 0
    latency_count = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        block["summary"] = {"events_count": 0, "blocked_human_count": 0, "avg_latency_sec": None, "last_status": None}
        return block
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        events_count += 1
        if row.get("blocked_human") is True:
            blocked_human_count += 1
        lat = row.get("latency_sec")
        if isinstance(lat, int):
            latency_total += lat
            latency_count += 1
    avg_latency_sec = (latency_total / latency_count) if latency_count > 0 else None
    last_status = (stats.get("last") or {}).get("status") if isinstance(stats.get("last"), dict) else None
    block["summary"] = {
        "events_count": events_count,
        "blocked_human_count": blocked_human_count,
        "avg_latency_sec": avg_latency_sec,
        "last_status": last_status,
    }
    return block


def _status_at_a_glance(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Compact booleans and counts derived from the rest of the snapshot (Phase 21)."""
    plan = snapshot.get("plan") or {}
    schema_errs = plan.get("schema_errors") or []
    plan_ok = bool(
        plan.get("present")
        and not plan.get("read_error")
        and not schema_errs
        and not plan.get("dependency_cycle")
    )
    ds = snapshot.get("driver_state") or {}
    ds_body = ds.get("body") if isinstance(ds.get("body"), dict) else None
    prog = snapshot.get("progress") or {}
    prog_body = prog.get("body") if isinstance(prog.get("body"), dict) else None
    ill_p = prog_body.get("intake_loaded_last") if prog_body else None
    ill_p = ill_p if isinstance(ill_p, bool) else None
    ill_d = ds_body.get("intake_loaded_last") if ds_body else None
    ill_d = ill_d if isinstance(ill_d, bool) else None
    sess_s = snapshot.get("session_dir")
    session_dir = Path(sess_s) if isinstance(sess_s, str) else None
    intake_anchor = intake_merge_anchor_present(session_dir) if session_dir is not None else False
    sr = snapshot.get("stop_report") or {}
    sr_body = sr.get("body") if isinstance(sr.get("body"), dict) else None
    dod = snapshot.get("definition_of_done") or {}
    dod_body = dod.get("body") if isinstance(dod.get("body"), dict) else None
    agg = snapshot.get("verification_aggregate") or {}
    agg_body = agg.get("body") if isinstance(agg.get("body"), dict) else None
    ws = snapshot.get("workspace_status") or {}
    runs = snapshot.get("step_runs") or {}
    pl = snapshot.get("plan_lock") or {}
    rm = snapshot.get("revise_metrics") or {}
    rm_summary = rm.get("summary") if isinstance(rm.get("summary"), dict) else {}
    rp = snapshot.get("reviewer_proof") or {}
    se_lineage = snapshot.get("session_events") or {}
    ilm_present = se_lineage.get("intake_lineage_manifest_present")
    ilm_present_b = ilm_present if isinstance(ilm_present, bool) else False
    ilm_unread = se_lineage.get("intake_lineage_manifest_unreadable")
    ilm_unread_b = ilm_unread if isinstance(ilm_unread, bool) else False
    pl_proof = pl.get("reviewer_proof_summary")
    reviewer_source = pl_proof if isinstance(pl_proof, dict) else rp
    reviewer_source_name = "plan_lock" if isinstance(pl_proof, dict) else "intake"
    runnable = plan.get("runnable_step_ids")
    nxt = plan.get("next_tick_batch")
    runnable_n = len(runnable) if isinstance(runnable, list) else None
    next_n = len(nxt) if isinstance(nxt, list) else None
    if runs.get("by_step_omitted"):
        runs_indexed = False
    elif runs.get("present") and isinstance(runs.get("by_step"), dict):
        runs_indexed = True
    else:
        runs_indexed = False
    roll = snapshot.get("plan_step_rollups") or {}
    roll_steps = roll.get("steps") if isinstance(roll.get("steps"), list) else []
    r_intake_true = 0
    r_intake_false = 0
    r_intake_null = 0
    for s in roll_steps:
        if not isinstance(s, dict):
            continue
        v = s.get("context_pack_intake_loaded")
        if v is True:
            r_intake_true += 1
        elif v is False:
            r_intake_false += 1
        else:
            r_intake_null += 1
    rollup_intake_unknown_with_anchor = False
    if intake_anchor and roll.get("present") is True:
        for s in roll_steps:
            if not isinstance(s, dict):
                continue
            if not s.get("context_pack_present"):
                continue
            if s.get("context_pack_intake_loaded") is not None:
                continue
            if s.get("context_pack_intake_loaded_skipped_oversized") is True:
                continue
            rollup_intake_unknown_with_anchor = True
            break
    glance: dict[str, Any] = {
        "plan_ok": plan_ok,
        "all_plan_steps_complete": plan.get("all_steps_complete"),
        "runnable_step_ids_count": runnable_n,
        "next_tick_batch_count": next_n,
        "driver_status": ds_body.get("status") if ds_body else None,
        "driver_exit_code": ds_body.get("exit_code") if ds_body else None,
        "stop_exit_code": sr_body.get("exit_code") if sr_body else None,
        "dod_all_required_passed": dod_body.get("all_required_passed") if dod_body else None,
        "aggregate_all_steps_verification_passed": (
            agg_body.get("all_steps_verification_passed") if agg_body else None
        ),
        "path_prefixes_ok": ws.get("path_prefixes_ok"),
        "branch_commit_match": ws.get("branch_commit_match"),
        "step_runs_latest_indexed": runs_indexed,
        "plan_lock_ready": pl.get("ready"),
        "plan_lock_locked": pl.get("locked"),
        "revise_metrics_last_status": rm_summary.get("last_status"),
        "revise_metrics_blocked_human_count": rm_summary.get("blocked_human_count"),
        "revise_metrics_avg_latency_sec": rm_summary.get("avg_latency_sec"),
        "reviewer_attestation_type": reviewer_source.get("attestation_type"),
        "reviewer_attestation_type_allowed": reviewer_source.get("attestation_type_allowed"),
        "reviewer_local_stub_allowed": reviewer_source.get("local_stub_allowed"),
        "reviewer_attestation_policy_ok": reviewer_source.get("attestation_policy_ok"),
        "reviewer_matches_doc_review": reviewer_source.get("reviewer_matches_doc_review"),
        "reviewer_differs_from_planner": reviewer_source.get("reviewer_differs_from_planner"),
        "reviewed_at_skew_ok": reviewer_source.get("reviewed_at_skew_ok"),
        "reviewer_signal_source": reviewer_source_name,
        "intake_merge_anchor_present": intake_anchor,
        "intake_loaded_last_progress": ill_p,
        "intake_loaded_last_driver_state": ill_d,
        "rollup_context_pack_intake_loaded_true_count": r_intake_true,
        "rollup_context_pack_intake_loaded_false_count": r_intake_false,
        "rollup_context_pack_intake_loaded_null_count": r_intake_null,
        "intake_lineage_manifest_present": ilm_present_b,
        "intake_lineage_manifest_unreadable": ilm_unread_b,
    }
    red: list[str] = []
    if plan.get("dependency_cycle"):
        red.append("dependency_cycle")
    elif not plan_ok:
        red.append("plan_invalid_or_unreadable_or_schema")
    if ws.get("present") and ws.get("path_prefixes_ok") is False:
        red.append("workspace_path_prefix_mismatch")
    if ws.get("present") and ws.get("branch_commit_match") is False:
        red.append("workspace_branch_mismatch")
    if ill_p is not None and ill_d is not None and ill_p != ill_d:
        red.append("intake_loaded_last_progress_vs_driver_state_mismatch")
    if rollup_intake_unknown_with_anchor:
        red.append("intake_merge_anchor_present_but_context_pack_intake_loaded_unknown")
    if pl.get("present") and pl.get("ready") is False:
        red.append("plan_lock_not_ready")
    if pl.get("present") and pl.get("locked") is False:
        red.append("plan_lock_not_locked")
    sess_s = snapshot.get("session_dir")
    if isinstance(sess_s, str):
        dre = intake_doc_review_errors(Path(sess_s))
        if dre:
            red.append("intake_doc_review_invalid")
    if ilm_unread_b:
        red.append("intake_lineage_manifest_unreadable")
    if isinstance(reviewer_source, dict) and reviewer_source:
        if reviewer_source.get("attestation_type_allowed") is False:
            red.append("reviewer_attestation_type_invalid")
        if reviewer_source.get("reviewer_matches_doc_review") is False:
            red.append("reviewer_identity_doc_review_mismatch")
        if reviewer_source.get("reviewer_differs_from_planner") is False:
            red.append("reviewer_identity_matches_planner")
        if reviewer_source.get("reviewed_at_skew_ok") is False:
            red.append("reviewed_at_skew_exceeded")
        if reviewer_source.get("attestation_policy_ok") is False:
            red.append("reviewer_attestation_policy_failed")
    glance["red_flags"] = red
    return glance


def _read_json_optional(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    return raw if isinstance(raw, dict) else None


def _embed_dict_json_file(path: Path, *, max_bytes: int) -> dict[str, Any]:
    block: dict[str, Any] = {"path": str(path), "present": path.is_file()}
    if not path.is_file():
        return block
    try:
        sz = path.stat().st_size
    except OSError as exc:
        block["read_error"] = str(exc)
        return block
    block["byte_len"] = int(sz)
    if sz > max_bytes:
        block["body"] = None
        block["body_omitted"] = True
        return block
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        block["body"] = None
        block["read_error"] = str(exc)
        return block
    block["body"] = raw if isinstance(raw, dict) else None
    return block


def _jsonl_line_count_and_last(
    path: Path,
    *,
    max_full_scan_bytes: int,
    max_tail_bytes: int,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if not path.is_file():
        out["line_count"] = 0
        out["last"] = None
        return out
    try:
        size = path.stat().st_size
    except OSError:
        out["line_count"] = 0
        out["last"] = None
        return out
    out["byte_len"] = int(size)

    def _scan_text(text: str) -> tuple[int, dict[str, Any] | None]:
        line_count = 0
        last: dict[str, Any] | None = None
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            line_count += 1
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                last = parsed
        return line_count, last

    if size <= max_full_scan_bytes:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            out["line_count"] = 0
            out["last"] = None
            return out
        lc, lst = _scan_text(text)
        out["line_count"] = lc
        out["last"] = lst
        return out

    read_len = min(max_tail_bytes, size)
    try:
        with path.open("rb") as fh:
            fh.seek(size - read_len)
            chunk = fh.read()
    except OSError:
        out["line_count"] = None
        out["line_count_omitted"] = True
        out["last"] = None
        return out
    text = chunk.decode("utf-8", errors="replace")
    if size > read_len and "\n" in text:
        text = text.split("\n", 1)[1]
    _, lst = _scan_text(text)
    out["line_count"] = None
    out["line_count_omitted"] = True
    out["last"] = lst
    return out


def _summarize_child_json_stems(dir_path: Path, *, max_listed: int) -> dict[str, Any]:
    block: dict[str, Any] = {
        "path": str(dir_path),
        "present": dir_path.is_dir(),
        "file_count": 0,
        "step_ids": [],
    }
    if not dir_path.is_dir():
        return block
    stems: list[str] = []
    try:
        for child in dir_path.iterdir():
            if child.is_file() and child.suffix.lower() == ".json":
                stems.append(child.stem)
    except OSError:
        block["read_error"] = "list_failed"
        return block
    stems.sort()
    block["file_count"] = len(stems)
    if len(stems) > max_listed:
        block["step_ids"] = stems[:max_listed]
        block["step_ids_omitted"] = True
    else:
        block["step_ids"] = stems
    return block


def _summarize_child_subdirs(dir_path: Path, *, max_listed: int) -> dict[str, Any]:
    block: dict[str, Any] = {
        "path": str(dir_path),
        "present": dir_path.is_dir(),
        "dir_count": 0,
        "step_ids": [],
    }
    if not dir_path.is_dir():
        return block
    names: list[str] = []
    try:
        for child in dir_path.iterdir():
            if child.is_dir():
                names.append(child.name)
    except OSError:
        block["read_error"] = "list_failed"
        return block
    names.sort()
    block["dir_count"] = len(names)
    if len(names) > max_listed:
        block["step_ids"] = names[:max_listed]
        block["step_ids_omitted"] = True
    else:
        block["step_ids"] = names
    return block


def _leases_active_row_count(leases_embed: dict[str, Any]) -> tuple[int | None, bool]:
    """Return (active_row_count or None if unknown, omitted_flag)."""
    if not leases_embed.get("present"):
        return 0, False
    if leases_embed.get("body_omitted"):
        return None, True
    body = leases_embed.get("body")
    if not isinstance(body, dict):
        return 0, False
    arr = body.get("leases")
    if not isinstance(arr, list):
        return 0, False
    return sum(1 for x in arr if isinstance(x, dict)), False


def _scan_step_runs_text(text: str) -> tuple[int, dict[str, Any] | None, dict[str, dict[str, str]]]:
    """One pass: JSONL line count, last dict line, latest ``run_id``/``output_dir`` per ``step_id``."""
    line_count = 0
    last: dict[str, Any] | None = None
    by_step: dict[str, dict[str, str]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line_count += 1
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        last = row
        sid = row.get("step_id")
        if not isinstance(sid, str) or not sid.strip():
            continue
        cell: dict[str, str] = {}
        od = row.get("output_dir")
        if isinstance(od, str) and od.strip():
            cell["output_dir"] = od
        rid = row.get("run_id")
        if isinstance(rid, str) and rid.strip():
            cell["run_id"] = rid
        if cell:
            by_step[sid] = cell
    return line_count, last, by_step


def _build_step_runs_status(path: Path, *, max_full_scan_bytes: int, max_tail_bytes: int) -> dict[str, Any]:
    """Line stats (Phase 13) plus ``by_step`` latest pointers when the file fits ``max_full_scan_bytes``."""
    block: dict[str, Any] = {"path": str(path), "present": path.is_file()}
    if not path.is_file():
        block["line_count"] = 0
        block["last"] = None
        block["by_step"] = None
        block["by_step_omitted"] = False
        return block
    try:
        size = path.stat().st_size
    except OSError:
        block["line_count"] = 0
        block["last"] = None
        block["by_step"] = None
        block["by_step_omitted"] = False
        return block
    block["byte_len"] = int(size)
    if size <= int(max_full_scan_bytes):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            block["line_count"] = 0
            block["last"] = None
            block["by_step"] = {}
            block["by_step_omitted"] = False
            return block
        lc, lst, by_step = _scan_step_runs_text(text)
        block["line_count"] = lc
        block["last"] = lst
        block["by_step"] = by_step
        block["by_step_omitted"] = False
        return block
    tail_stats = _jsonl_line_count_and_last(
        path,
        max_full_scan_bytes=max_full_scan_bytes,
        max_tail_bytes=max_tail_bytes,
    )
    block.update(tail_stats)
    block["by_step"] = None
    block["by_step_omitted"] = True
    return block


def _context_pack_intake_skipped_oversized(pack_path: Path, *, max_bytes: int) -> bool:
    """True when a pack file exists but is larger than ``max_bytes`` (``intake_loaded`` not read)."""
    if not pack_path.is_file():
        return False
    try:
        return int(pack_path.stat().st_size) > int(max_bytes)
    except OSError:
        return False


def _context_pack_intake_loaded_field(pack_path: Path, *, max_bytes: int) -> bool | None:
    """Read ``intake_loaded`` from ``context_packs/<step_id>.json`` when the file is under ``max_bytes``."""
    if not pack_path.is_file():
        return None
    try:
        sz = pack_path.stat().st_size
    except OSError:
        return None
    if int(sz) > int(max_bytes):
        return None
    try:
        raw = json.loads(pack_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    if not isinstance(raw, dict):
        return None
    v = raw.get("intake_loaded")
    return v if isinstance(v, bool) else None


def _plan_step_rollups(
    plan: dict[str, Any] | None,
    session_dir: Path,
    *,
    aggregate_body: dict[str, Any] | None,
    max_rows: int,
    latest_by_step: dict[str, dict[str, str]] | None = None,
    max_context_pack_json_bytes: int = DEFAULT_STATUS_MAX_JSON_BYTES,
) -> dict[str, Any]:
    """Per-``step_id`` hints: on-disk verification/context-pack presence + aggregate ``passed`` when known."""
    if plan is None:
        return {"present": False, "step_count": 0, "steps": []}
    ids = plan_step_ids(plan)
    total = len(ids)
    cap = max(1, int(max_rows))
    sliced = ids[:cap]
    omitted = total > len(sliced)
    agg_steps: dict[str, Any] | None = None
    if aggregate_body and isinstance(aggregate_body.get("steps"), dict):
        agg_steps = aggregate_body["steps"]
    ver_dir = session_dir / VERIFICATION_DIRNAME
    pack_dir = session_dir / CONTEXT_PACKS_DIRNAME
    rows: list[dict[str, Any]] = []
    for sid in sliced:
        pack_path = pack_dir / f"{sid}.json"
        skipped = _context_pack_intake_skipped_oversized(
            pack_path,
            max_bytes=max_context_pack_json_bytes,
        )
        row: dict[str, Any] = {
            "step_id": sid,
            "verification_json_present": (ver_dir / f"{sid}.json").is_file(),
            "context_pack_present": pack_path.is_file(),
            "context_pack_intake_loaded_skipped_oversized": skipped,
            "context_pack_intake_loaded": _context_pack_intake_loaded_field(
                pack_path,
                max_bytes=max_context_pack_json_bytes,
            ),
        }
        ap: bool | None = None
        if agg_steps is not None:
            cell = agg_steps.get(sid)
            if isinstance(cell, dict) and "passed" in cell:
                raw = cell.get("passed")
                ap = bool(raw) if raw is not None else None
        row["aggregate_passed"] = ap
        if latest_by_step:
            ptr = latest_by_step.get(sid)
            if isinstance(ptr, dict):
                if "run_id" in ptr:
                    row["latest_run_id"] = ptr["run_id"]
                if "output_dir" in ptr:
                    row["latest_output_dir"] = ptr["output_dir"]
        rows.append(row)
    return {
        "present": True,
        "step_count": total,
        "steps": rows,
        "steps_omitted": omitted,
    }


def describe_project_session(
    session_dir: Path,
    *,
    repo_root: Path | None = None,
    progress_file: Path | None = None,
    max_concurrent_agents: int = 1,
    max_status_json_bytes: int | None = None,
    max_status_jsonl_full_scan_bytes: int | None = None,
    max_status_jsonl_tail_bytes: int | None = None,
    max_status_listed_step_ids: int | None = None,
) -> dict[str, Any]:
    """
    Summarize on-disk session artifacts without mutating them.

    Intended for ``sde project status`` and automation. Always returns ``exit_code`` **0**
    (read-only snapshot; inspect ``plan.schema_errors`` / ``plan.dependency_cycle`` for issues).
    Includes **Phase 12** keys ``verification_aggregate``, ``definition_of_done``, and ``step_runs``
    when the corresponding files exist. **Phase 13** bounds JSON / JSONL reads: oversized JSON bodies
    set ``body_omitted`` + ``byte_len``; oversized JSONL may omit ``line_count`` and only scan a tail
    for ``last``. **Phase 14** adds ``context_pack_lineage`` (JSONL tail stats), ``context_packs`` (child
    ``*.json`` stems under ``context_packs/``), and ``verification_bundles`` (child ``*.json`` under
    ``verification/``) with a capped ``step_ids`` list. **Phase 15** embeds ``leases.json`` under the same
    JSON byte cap (with ``active_row_count`` / ``active_row_count_omitted``) and summarizes ``_worktrees/``
    as ``parallel_worktrees``.     **Phase 16** adds ``plan_step_rollups`` (bounded list of per-step presence
    flags + ``aggregate_passed`` from the embedded aggregate when available, plus ``context_pack_intake_loaded``
    read from each ``context_packs/<step_id>.json`` when under the JSON byte cap, with
    ``context_pack_intake_loaded_skipped_oversized`` when the pack file exceeds that cap). **Phase 17** adds a full
    scan of ``step_runs.jsonl`` for ``latest_by_step`` (and per-row ``latest_run_id`` / ``latest_output_dir``)
    only while the file is under the JSONL full-scan byte cap; otherwise ``by_step_omitted`` is set.
    **Phase 18** adds ``repo_snapshot`` (read-only ``git rev-parse`` for ``HEAD`` / short SHA / branch when
    ``repo_root`` is set and ``.git`` exists). **Phase 19** adds ``workspace_status`` (echo ``workspace`` from
    the parsed plan plus ``branch_commit_match`` via :func:`git_head_matches_branch` when a plan branch and
    git are available). **Phase 20** extends ``workspace_status`` with ``path_prefix_errors`` (from
    :func:`plan_workspace_path_errors`), ``path_prefixes_configured``, and ``path_prefixes_ok``.
    **Phase 21** adds ``status_at_a_glance`` (compact derived fields + ``red_flags``). Glance also surfaces
    **intake** hints: ``intake_merge_anchor_present``, ``intake_loaded_last_progress``, and
    ``intake_loaded_last_driver_state`` (with a red flag when both booleans disagree), plus
    ``rollup_context_pack_intake_loaded_{true,false,null}_count`` tallies from ``plan_step_rollups`` steps
    (null counts steps with missing/omitted ``context_pack_intake_loaded``). When ``intake_merge_anchor_present``
    is true, ``red_flags`` may include ``intake_merge_anchor_present_but_context_pack_intake_loaded_unknown`` if
    some in-cap context pack omits a boolean ``intake_loaded`` (oversized packs are excluded via
    ``context_pack_intake_loaded_skipped_oversized``). Status also embeds ``plan_lock`` from
    ``project_plan_lock.json`` (when present) and surfaces ``plan_lock_ready`` / ``plan_lock_locked``
    in ``status_at_a_glance``. **Phase 22** merges ``intake_lineage_manifest_*`` (same contract as
    ``session_events.jsonl`` driver payloads) into the ``session_events`` status block via
    :func:`lineage_manifest_session_event_snapshot`; ``status_at_a_glance`` mirrors presence/unreadable
    and may add ``intake_lineage_manifest_unreadable`` to ``red_flags``.
    """
    session_dir = session_dir.resolve()
    jcap = int(max_status_json_bytes) if max_status_json_bytes is not None else DEFAULT_STATUS_MAX_JSON_BYTES
    jl_full = (
        int(max_status_jsonl_full_scan_bytes)
        if max_status_jsonl_full_scan_bytes is not None
        else DEFAULT_STATUS_JSONL_FULL_SCAN_BYTES
    )
    jl_tail = (
        int(max_status_jsonl_tail_bytes)
        if max_status_jsonl_tail_bytes is not None
        else DEFAULT_STATUS_JSONL_TAIL_BYTES
    )
    list_cap = (
        int(max_status_listed_step_ids)
        if max_status_listed_step_ids is not None
        else DEFAULT_STATUS_MAX_LISTED_STEP_IDS
    )
    out: dict[str, Any] = {
        "exit_code": 0,
        "session_dir": str(session_dir),
        "repo_root": str(repo_root.resolve()) if repo_root is not None else None,
    }
    if repo_root is not None:
        out["repo_snapshot"] = _repo_git_snapshot(repo_root)
    else:
        out["repo_snapshot"] = {
            "path": None,
            "git_dir_present": False,
            "git_available": False,
            "reason": "repo_root_not_provided",
        }

    progress_path = progress_file.resolve() if progress_file is not None else session_dir / "progress.json"
    plan_path = session_dir / "project_plan.json"
    plan_parsed: dict[str, Any] | None = None
    out["plan"] = {"path": str(plan_path), "present": plan_path.is_file()}
    if plan_path.is_file():
        try:
            plan_parsed = read_json_dict(plan_path)
        except (OSError, ValueError, TypeError) as exc:
            out["plan"]["read_error"] = str(exc)
            plan_parsed = None
        if plan_parsed is not None:
            out["plan"]["schema_errors"] = validate_project_plan(plan_parsed)
            cyc = detect_dependency_cycle(plan_parsed)
            out["plan"]["dependency_cycle"] = cyc
            out["plan"]["step_ids"] = plan_step_ids(plan_parsed)
            completed: set[str] = set()
            prog_body = _read_json_optional(progress_path)
            if prog_body and isinstance(prog_body.get("completed_step_ids"), list):
                completed = {str(x) for x in prog_body["completed_step_ids"] if isinstance(x, str)}
            out["plan"]["all_steps_complete"] = all_steps_complete(plan_parsed, completed)
            out["plan"]["runnable_step_ids"] = runnable_step_ids(plan_parsed, completed)
            if not cyc and not out["plan"]["schema_errors"]:
                out["plan"]["next_tick_batch"] = select_steps_for_tick(
                    plan_parsed,
                    completed,
                    max_concurrent_agents=max(1, int(max_concurrent_agents)),
                )

    out["workspace_status"] = _workspace_status_block(plan_parsed, repo_root, out["repo_snapshot"])
    out["plan_lock"] = _plan_lock_status_block(session_dir, max_bytes=jcap)
    out["revise_metrics"] = _revise_metrics_status_block(
        session_dir,
        max_full_scan_bytes=jl_full,
        max_tail_bytes=jl_tail,
    )
    out["reviewer_proof"] = _reviewer_proof_status_block(session_dir)

    out["progress"] = {"path": str(progress_path), "present": progress_path.is_file()}
    if progress_path.is_file():
        pb = _embed_dict_json_file(progress_path, max_bytes=jcap)
        merged = dict(pb)
        merged.pop("path", None)
        merged.pop("present", None)
        out["progress"].update(merged)

    ds_path = session_dir / "driver_state.json"
    out["driver_state"] = _embed_dict_json_file(ds_path, max_bytes=jcap)

    sr_path = session_dir / "stop_report.json"
    out["stop_report"] = _embed_dict_json_file(sr_path, max_bytes=jcap)

    leases_path = session_dir / "leases.json"
    leases_embed = _embed_dict_json_file(leases_path, max_bytes=jcap)
    lc_lease, lc_omitted = _leases_active_row_count(leases_embed)
    leases_embed["active_row_count"] = lc_lease
    if lc_omitted:
        leases_embed["active_row_count_omitted"] = True
    out["leases"] = leases_embed

    wt_dir = session_dir / WORKTREES_DIRNAME
    out["parallel_worktrees"] = _summarize_child_subdirs(wt_dir, max_listed=max(1, list_cap))

    events_path = session_dir / SESSION_EVENTS_FILENAME
    ev_stats = _jsonl_line_count_and_last(
        events_path,
        max_full_scan_bytes=jl_full,
        max_tail_bytes=jl_tail,
    )
    out["session_events"] = {"path": str(events_path), "present": events_path.is_file()}
    out["session_events"].update(ev_stats)
    out["session_events"].update(lineage_manifest_session_event_snapshot(session_dir))

    agg_path = session_dir / VERIFICATION_AGGREGATE_FILENAME
    out["verification_aggregate"] = _embed_dict_json_file(agg_path, max_bytes=jcap)
    agg_embed_body = out["verification_aggregate"].get("body")
    agg_for_rollups = agg_embed_body if isinstance(agg_embed_body, dict) else None

    runs_path = session_dir / STEP_RUNS_FILENAME
    step_runs_block = _build_step_runs_status(
        runs_path,
        max_full_scan_bytes=jl_full,
        max_tail_bytes=jl_tail,
    )
    out["step_runs"] = step_runs_block

    latest_map = step_runs_block.get("by_step")
    latest_for_rollups = latest_map if isinstance(latest_map, dict) else None
    out["plan_step_rollups"] = _plan_step_rollups(
        plan_parsed,
        session_dir,
        aggregate_body=agg_for_rollups,
        max_rows=list_cap,
        latest_by_step=latest_for_rollups,
        max_context_pack_json_bytes=jcap,
    )

    dod_path = session_dir / DEFINITION_OF_DONE_FILENAME
    out["definition_of_done"] = _embed_dict_json_file(dod_path, max_bytes=jcap)

    lineage_path = session_dir / CONTEXT_PACK_LINEAGE_FILENAME
    lineage_stats = _jsonl_line_count_and_last(
        lineage_path,
        max_full_scan_bytes=jl_full,
        max_tail_bytes=jl_tail,
    )
    out["context_pack_lineage"] = {"path": str(lineage_path), "present": lineage_path.is_file()}
    out["context_pack_lineage"].update(lineage_stats)

    packs_dir = session_dir / CONTEXT_PACKS_DIRNAME
    out["context_packs"] = _summarize_child_json_stems(packs_dir, max_listed=max(1, list_cap))

    ver_dir = session_dir / VERIFICATION_DIRNAME
    out["verification_bundles"] = _summarize_child_json_stems(ver_dir, max_listed=max(1, list_cap))

    out["status_at_a_glance"] = _status_at_a_glance(out)
    return out
