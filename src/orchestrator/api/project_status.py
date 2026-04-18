"""Phase 10–21: read-only project session snapshot (status / observability)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .project_aggregate import VERIFICATION_AGGREGATE_FILENAME
from .project_events import SESSION_EVENTS_FILENAME
from .project_plan import all_steps_complete, detect_dependency_cycle, plan_step_ids, runnable_step_ids
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
    sr = snapshot.get("stop_report") or {}
    sr_body = sr.get("body") if isinstance(sr.get("body"), dict) else None
    dod = snapshot.get("definition_of_done") or {}
    dod_body = dod.get("body") if isinstance(dod.get("body"), dict) else None
    agg = snapshot.get("verification_aggregate") or {}
    agg_body = agg.get("body") if isinstance(agg.get("body"), dict) else None
    ws = snapshot.get("workspace_status") or {}
    runs = snapshot.get("step_runs") or {}
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


def _plan_step_rollups(
    plan: dict[str, Any] | None,
    session_dir: Path,
    *,
    aggregate_body: dict[str, Any] | None,
    max_rows: int,
    latest_by_step: dict[str, dict[str, str]] | None = None,
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
        row: dict[str, Any] = {
            "step_id": sid,
            "verification_json_present": (ver_dir / f"{sid}.json").is_file(),
            "context_pack_present": (pack_dir / f"{sid}.json").is_file(),
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
    as ``parallel_worktrees``. **Phase 16** adds ``plan_step_rollups`` (bounded list of per-step presence
    flags + ``aggregate_passed`` from the embedded aggregate when available). **Phase 17** adds a full
    scan of ``step_runs.jsonl`` for ``latest_by_step`` (and per-row ``latest_run_id`` / ``latest_output_dir``)
    only while the file is under the JSONL full-scan byte cap; otherwise ``by_step_omitted`` is set.
    **Phase 18** adds ``repo_snapshot`` (read-only ``git rev-parse`` for ``HEAD`` / short SHA / branch when
    ``repo_root`` is set and ``.git`` exists). **Phase 19** adds ``workspace_status`` (echo ``workspace`` from
    the parsed plan plus ``branch_commit_match`` via :func:`git_head_matches_branch` when a plan branch and
    git are available). **Phase 20** extends ``workspace_status`` with ``path_prefix_errors`` (from
    :func:`plan_workspace_path_errors`), ``path_prefixes_configured``, and ``path_prefixes_ok``.
    **Phase 21** adds ``status_at_a_glance`` (compact derived fields + ``red_flags``).
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
