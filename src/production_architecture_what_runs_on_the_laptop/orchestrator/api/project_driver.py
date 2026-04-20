"""Meta-orchestrator: plan store, bounded context, per-step verify, stop policy."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from storage.storage import ensure_dir
from workflow_pipelines.production_pipeline_task_to_promote.runner import execute_single_task

from .context_pack import build_context_pack, latest_output_dirs_by_step, task_with_context
from .project_intake_util import intake_merge_anchor_present
from .project_aggregate import (
    VERIFICATION_AGGREGATE_FILENAME,
    write_project_definition_of_done,
    write_verification_aggregate,
)
from .project_events import append_session_event
from .project_plan_lock import evaluate_project_plan_lock_readiness, lineage_manifest_session_event_snapshot
from .project_lease import prune_stale_leases, release, resolve_lease_ttl_sec, touch_lease_heartbeat, try_acquire
from .project_parallel import session_io_lock
from .project_plan import all_steps_complete, detect_dependency_cycle
from .project_schema import (
    PROGRESS_SCHEMA_VERSION,
    default_progress,
    read_json_dict,
    validate_progress,
    validate_project_plan,
)
from .project_scheduler import select_steps_for_tick
from .project_stop import (
    EXIT_SESSION_BLOCKED_OR_BUDGET,
    EXIT_SESSION_INVALID,
    EXIT_SESSION_OK,
    STOP_REPORT_FILENAME,
    write_stop_report,
)
from .project_verify import run_step_verification
from .project_workspace import evaluate_workspace_repo_gates
from .project_worktree import add_detached_worktree, git_worktree_available, remove_worktree


def _write_json(path: Path, body: dict[str, Any]) -> None:
    path.write_text(json.dumps(body, indent=2), encoding="utf-8")


def _append_step_run(session_dir: Path, row: dict[str, Any]) -> None:
    p = session_dir / "step_runs.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def _session_intake_tick_fields(session_dir: Path, progress: dict[str, Any]) -> dict[str, Any]:
    """Snapshot for session_events (matches status ``intake_merge_anchor_present`` + progress bool)."""
    ill = progress.get("intake_loaded_last")
    ill_b: bool | None = ill if isinstance(ill, bool) else None
    snap = lineage_manifest_session_event_snapshot(session_dir)
    base: dict[str, Any] = {
        "intake_merge_anchor_present": intake_merge_anchor_present(session_dir),
        "intake_loaded_last": ill_b,
    }
    base.update(snap)
    return base


def _step_map(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in plan.get("steps") or []:
        if isinstance(row, dict) and isinstance(row.get("step_id"), str):
            out[row["step_id"]] = row
    return out


def _driver_state_path(session_dir: Path) -> Path:
    return session_dir / "driver_state.json"


def _progress_intake_loaded_last(progress_path: Path) -> bool | None:
    if not progress_path.is_file():
        return None
    try:
        data = read_json_dict(progress_path)
    except (OSError, ValueError, TypeError):
        return None
    v = data.get("intake_loaded_last")
    return v if isinstance(v, bool) else None


def _write_driver_state(
    session_dir: Path,
    *,
    status: str,
    max_steps: int,
    steps_used: int,
    block_detail: str | None = None,
    exit_code: int | None = None,
    stopped_reason: str | None = None,
    intake_loaded_last: bool | None = None,
) -> None:
    body: dict[str, Any] = {
        "schema_version": "1.0",
        "status": status,
        "budget": {"max_steps": max_steps, "steps_used": steps_used},
        "block_detail": block_detail,
    }
    if exit_code is not None:
        body["exit_code"] = exit_code
    if stopped_reason is not None:
        body["stopped_reason"] = stopped_reason
    if intake_loaded_last is not None:
        body["intake_loaded_last"] = intake_loaded_last
    _write_json(_driver_state_path(session_dir), body)


def _plan_valid_for_session_artifacts(plan: dict[str, Any] | None) -> bool:
    return plan is not None and not validate_project_plan(plan)


def _emit_stop_and_session_dod(
    session_dir: Path,
    plan: dict[str, Any] | None,
    completed: set[str],
    *,
    exit_code: int,
    stopped_reason: str,
    driver_status: str,
    max_steps: int,
    steps_used: int,
    block_detail: str | None = None,
    extra_for_stop: dict[str, Any] | None = None,
    progress_path: Path | None = None,
) -> dict[str, Any]:
    """Phase 4: ``stop_report.json``, terminal ``driver_state`` fields, optional session DoD + aggregate."""
    pp = progress_path if progress_path is not None else session_dir / "progress.json"
    ill = _progress_intake_loaded_last(pp)
    term_payload: dict[str, Any] = {
        "exit_code": exit_code,
        "stopped_reason": stopped_reason,
        "driver_status": driver_status,
        "max_steps": max_steps,
        "steps_used": steps_used,
        "block_detail": block_detail,
        "completed_step_ids": sorted(completed),
        "intake_merge_anchor_present": intake_merge_anchor_present(session_dir),
        "intake_loaded_last": ill,
    }
    term_payload.update(lineage_manifest_session_event_snapshot(session_dir))
    append_session_event(session_dir, "session_terminal", term_payload)
    write_stop_report(
        session_dir,
        exit_code=exit_code,
        stopped_reason=stopped_reason,
        driver_status=driver_status,
        max_steps=max_steps,
        steps_used=steps_used,
        block_detail=block_detail,
        extra=extra_for_stop,
    )
    _write_driver_state(
        session_dir,
        status=driver_status,
        max_steps=max_steps,
        steps_used=steps_used,
        block_detail=block_detail,
        exit_code=exit_code,
        stopped_reason=stopped_reason,
        intake_loaded_last=ill,
    )
    tail: dict[str, Any] = {"stop_report_path": str(session_dir / STOP_REPORT_FILENAME)}
    if not _plan_valid_for_session_artifacts(plan):
        return tail
    assert plan is not None
    agg = write_verification_aggregate(session_dir, plan)
    dod = write_project_definition_of_done(
        session_dir,
        plan,
        completed_step_ids=sorted(completed),
        driver_status=driver_status,
        aggregate=agg,
    )
    tail["verification_aggregate"] = agg
    tail["definition_of_done"] = dod
    tail["verification_aggregate_path"] = str(session_dir / VERIFICATION_AGGREGATE_FILENAME)
    tail["definition_of_done_path"] = str(session_dir / "definition_of_done.json")
    return tail


def _run_batch_parallel_worktrees(
    session_dir: Path,
    plan: dict[str, Any],
    batch: list[str],
    by_id: dict[str, dict[str, Any]],
    repo_root: Path,
    mode: str,
    failures: list[dict[str, Any]],
    max_steps: int,
    steps_used: int,
    progress_path: Path,
    progress: dict[str, Any],
    completed: set[str],
    max_concurrent_agents: int,
) -> tuple[dict[str, Any] | None, int]:
    """
    Run ``batch`` steps concurrently using detached git worktrees (Phase 6).

    Callers must have acquired leases for every ``step_id`` in ``batch`` already.
    Returns ``(early_return_dict_or_none, new_steps_used)``.
    """
    io_lock = session_io_lock(session_dir)
    worktrees: dict[str, Path] = {}
    for sid in batch:
        wt = session_dir / "_worktrees" / sid
        if not add_detached_worktree(repo_root, wt):
            for _prev_sid, prev_wt in worktrees.items():
                remove_worktree(repo_root, prev_wt)
            for s in batch:
                release(session_dir, s)
            tail = _emit_stop_and_session_dod(
                session_dir,
                plan,
                completed,
                exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
                stopped_reason="worktree_failed",
                driver_status="blocked_human",
                max_steps=max_steps,
                steps_used=steps_used,
                block_detail="git_worktree_add_failed",
                extra_for_stop={"step_id": sid},
                progress_path=progress_path,
            )
            return (
                {
                    "exit_code": 1,
                    "stopped_reason": "blocked_human",
                    "step_id": sid,
                    "detail": "worktree_failed",
                    **tail,
                },
                steps_used,
            )
        worktrees[sid] = wt

    def _worker(sid: str) -> tuple[str, dict[str, Any], dict[str, Any] | None, bool]:
        row = by_id[sid]
        wt_root = worktrees[sid]
        touch_lease_heartbeat(session_dir, sid)
        pack = build_context_pack(
            repo_root=wt_root,
            session_dir=session_dir,
            step=row,
            prior_failures=failures,
            latest_runs_by_step=latest_output_dirs_by_step(session_dir),
        )
        intake_loaded = bool(pack.get("intake_loaded"))
        full_task = task_with_context(
            context_markdown=str(pack.get("markdown", "")),
            step_description=str(row.get("description", "")),
        )
        result = execute_single_task(
            full_task,
            mode,
            repeat=1,
            project_step_id=sid,
            project_session_dir=str(session_dir.resolve()),
        )
        with io_lock:
            _append_step_run(
                session_dir,
                {
                    "step_id": sid,
                    "run_id": result.get("run_id"),
                    "output_dir": result.get("output_dir"),
                    "pipeline_error": result.get("error"),
                },
            )
            touch_lease_heartbeat(session_dir, sid)
        if result.get("error"):
            return sid, result, None, intake_loaded
        ver = row.get("verification")
        vbundle = run_step_verification(
            repo_root=wt_root,
            session_dir=session_dir,
            step_id=sid,
            verification=ver if isinstance(ver, dict) else None,
        )
        return sid, result, vbundle, intake_loaded

    results: dict[str, tuple[dict[str, Any], dict[str, Any] | None, bool]] = {}
    worker_exc: BaseException | None = None
    pool_workers = min(len(batch), max(1, max_concurrent_agents))
    try:
        with ThreadPoolExecutor(max_workers=pool_workers) as pool:
            future_map = {pool.submit(_worker, sid): sid for sid in batch}
            for fut in as_completed(future_map):
                try:
                    sid_done, res, vb, il = fut.result()
                except Exception as exc:
                    worker_exc = exc
                    for pending in future_map:
                        if pending is not fut and not pending.done():
                            pending.cancel()
                    break
                results[sid_done] = (res, vb, il)
    finally:
        for sid in batch:
            remove_worktree(repo_root, worktrees[sid])
            release(session_dir, sid)

    if worker_exc is not None or len(results) != len(batch):
        detail = "worker_exception" if worker_exc is not None else "incomplete_parallel_batch"
        progress["blocked_reason"] = detail
        _write_json(progress_path, progress)
        tail = _emit_stop_and_session_dod(
            session_dir,
            plan,
            completed,
            exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
            stopped_reason="pipeline_error",
            driver_status="blocked_human",
            max_steps=max_steps,
            steps_used=steps_used + len(batch),
            block_detail=detail,
            extra_for_stop={"parallel_batch": True, "error": repr(worker_exc) if worker_exc else None},
            progress_path=progress_path,
        )
        return (
            {
                "exit_code": 1,
                "stopped_reason": "blocked_human",
                "detail": detail,
                **tail,
            },
            steps_used + len(batch),
        )

    new_steps = steps_used + len(batch)
    for sid in batch:
        res, vbundle, intake_il = results[sid]
        if res.get("error"):
            failures.append({"step_id": sid, "detail": str(res.get("error"))})
            progress["failed_step_id"] = sid
            progress["blocked_reason"] = "pipeline_error"
            progress["intake_loaded_last"] = intake_il
            _write_json(progress_path, progress)
            tail = _emit_stop_and_session_dod(
                session_dir,
                plan,
                completed,
                exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
                stopped_reason="pipeline_error",
                driver_status="blocked_human",
                max_steps=max_steps,
                steps_used=new_steps,
                block_detail="pipeline_error",
                extra_for_stop={"step_id": sid, "parallel_batch": True},
                progress_path=progress_path,
            )
            return (
                {
                    "exit_code": 1,
                    "stopped_reason": "blocked_human",
                    "step_id": sid,
                    "result": res,
                    **tail,
                },
                new_steps,
            )
        if vbundle is None or not vbundle.get("passed"):
            failures.append({"step_id": sid, "detail": "verification_failed"})
            progress["failed_step_id"] = sid
            progress["blocked_reason"] = "verification_failed"
            progress["intake_loaded_last"] = intake_il
            _write_json(progress_path, progress)
            tail = _emit_stop_and_session_dod(
                session_dir,
                plan,
                completed,
                exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
                stopped_reason="verification_failed",
                driver_status="blocked_human",
                max_steps=max_steps,
                steps_used=new_steps,
                block_detail="verification_failed",
                extra_for_stop={"step_id": sid, "parallel_batch": True},
                progress_path=progress_path,
            )
            return (
                {
                    "exit_code": 1,
                    "stopped_reason": "blocked_human",
                    "step_id": sid,
                    "verification": vbundle,
                    **tail,
                },
                new_steps,
            )

    last_sid = batch[-1]
    last_res, _, last_intake_il = results[last_sid]
    progress["last_run_id"] = last_res.get("run_id")
    progress["last_output_dir"] = last_res.get("output_dir")
    progress["intake_loaded_last"] = last_intake_il
    for sid in batch:
        completed.add(sid)
    progress["completed_step_ids"] = sorted(completed)
    progress["pending_step_ids"] = [s for s in _step_map(plan) if s not in completed]
    progress["failed_step_id"] = None
    progress["blocked_reason"] = None
    progress["schema_version"] = PROGRESS_SCHEMA_VERSION
    _write_json(progress_path, progress)
    write_verification_aggregate(session_dir, plan)
    _write_driver_state(
        session_dir,
        status="running",
        max_steps=max_steps,
        steps_used=new_steps,
        intake_loaded_last=bool(progress.get("intake_loaded_last", False)),
    )
    return None, new_steps


def run_project_session(
    session_dir: Path,
    *,
    repo_root: Path,
    max_steps: int,
    mode: str,
    max_concurrent_agents: int = 1,
    progress_file: Path | None = None,
    parallel_worktrees: bool = False,
    lease_stale_sec: int | None = None,
    enforce_plan_lock: bool = False,
    require_non_stub_reviewer: bool = False,
) -> dict[str, Any]:
    """
    Load ``project_plan.json`` from ``session_dir`` and ``progress.json`` from ``session_dir``
    (default) or from ``progress_file`` when given (Phase 5: split progress store).

    Returns a JSON-serializable summary with ``exit_code`` (0 = completed_review_pass).

    When ``parallel_worktrees`` is true, a multi-step tick may run in detached git worktrees
    (see Phase 6 in ``docs/UNDERSTANDING-THE-CODE.md``, project driver section); otherwise execution stays on ``repo_root``.
    When the plan declares ``workspace.branch`` / ``workspace.allowed_path_prefixes``, Phase 7
    gates apply (see ``project_workspace`` and the same doc).
    ``lease_stale_sec`` (CLI ``--lease-stale-sec``) overrides plan ``workspace.lease_ttl_sec`` for
    Phase 8 stale lease pruning; use ``0`` to disable pruning.
    ``enforce_plan_lock`` requires Stage 1 lock-readiness before step execution.
    When ``require_non_stub_reviewer`` is true (only meaningful with ``enforce_plan_lock``),
    lock readiness uses the same non-stub reviewer policy as strict plan-lock / validate.
    """
    if max_steps < 1:
        raise ValueError("max_steps must be >= 1")
    ensure_dir(session_dir)
    plan_path = session_dir / "project_plan.json"
    progress_path = progress_file.resolve() if progress_file is not None else session_dir / "progress.json"
    ensure_dir(progress_path.parent)
    if not plan_path.is_file():
        tail = _emit_stop_and_session_dod(
            session_dir,
            None,
            set(),
            exit_code=EXIT_SESSION_INVALID,
            stopped_reason="missing_project_plan_json",
            driver_status="invalid_session",
            max_steps=max_steps,
            steps_used=0,
            block_detail=None,
            extra_for_stop={"session_dir": str(session_dir)},
            progress_path=progress_path,
        )
        return {"exit_code": 2, "error": "missing_project_plan_json", "session_dir": str(session_dir), **tail}
    plan = read_json_dict(plan_path)
    perrs = validate_project_plan(plan)
    if perrs:
        tail = _emit_stop_and_session_dod(
            session_dir,
            plan,
            set(),
            exit_code=EXIT_SESSION_INVALID,
            stopped_reason="invalid_project_plan",
            driver_status="invalid_session",
            max_steps=max_steps,
            steps_used=0,
            block_detail="invalid_project_plan",
            extra_for_stop={"details": perrs},
            progress_path=progress_path,
        )
        return {"exit_code": 2, "error": "invalid_project_plan", "details": perrs, **tail}

    cyc = detect_dependency_cycle(plan)
    if cyc:
        tail = _emit_stop_and_session_dod(
            session_dir,
            plan,
            set(),
            exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
            stopped_reason="dependency_cycle",
            driver_status="dependency_cycle",
            max_steps=max_steps,
            steps_used=0,
            block_detail=f"dependency_cycle:{cyc}",
            extra_for_stop={"cycle": cyc},
            progress_path=progress_path,
        )
        return {"exit_code": 1, "stopped_reason": "dependency_cycle", "cycle": cyc, **tail}

    session_id = session_dir.name
    if progress_path.is_file():
        try:
            progress = read_json_dict(progress_path)
            if validate_progress(progress):
                progress = default_progress(session_id)
        except (OSError, ValueError, TypeError):
            progress = default_progress(session_id)
    else:
        progress = default_progress(session_id)

    completed = {str(x) for x in progress.get("completed_step_ids", []) if isinstance(x, str)}
    ws_gate = evaluate_workspace_repo_gates(plan, repo_root)
    if ws_gate:
        progress["blocked_reason"] = ws_gate
        _write_json(progress_path, progress)
        tail = _emit_stop_and_session_dod(
            session_dir,
            plan,
            completed,
            exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
            stopped_reason="workspace_contract",
            driver_status="blocked_human",
            max_steps=max_steps,
            steps_used=0,
            block_detail=ws_gate,
            extra_for_stop={"workspace_gate": ws_gate},
            progress_path=progress_path,
        )
        return {
            "exit_code": 1,
            "stopped_reason": "blocked_human",
            "detail": ws_gate,
            **tail,
        }
    if enforce_plan_lock:
        lock = evaluate_project_plan_lock_readiness(
            session_dir,
            allow_local_stub_attestation=not require_non_stub_reviewer,
        )
        if not lock.get("ok"):
            detail = str(lock.get("error") or "plan_lock_readiness_error")
            progress["blocked_reason"] = detail
            _write_json(progress_path, progress)
            tail = _emit_stop_and_session_dod(
                session_dir,
                plan,
                completed,
                exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
                stopped_reason="plan_lock_gate_failed",
                driver_status="blocked_human",
                max_steps=max_steps,
                steps_used=0,
                block_detail=detail,
                extra_for_stop={"plan_lock": lock},
                progress_path=progress_path,
            )
            return {
                "exit_code": 1,
                "stopped_reason": "blocked_human",
                "detail": detail,
                **tail,
            }
        if not lock.get("ready"):
            detail = "plan_lock_not_ready"
            progress["blocked_reason"] = detail
            _write_json(progress_path, progress)
            tail = _emit_stop_and_session_dod(
                session_dir,
                plan,
                completed,
                exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
                stopped_reason="plan_lock_gate_failed",
                driver_status="blocked_human",
                max_steps=max_steps,
                steps_used=0,
                block_detail=detail,
                extra_for_stop={"plan_lock": lock},
                progress_path=progress_path,
            )
            return {
                "exit_code": 1,
                "stopped_reason": "blocked_human",
                "detail": detail,
                "plan_lock": lock,
                **tail,
            }

    failures: list[dict[str, Any]] = []
    steps_used = 0
    lease_ttl_sec = resolve_lease_ttl_sec(plan, lease_stale_sec)
    _write_driver_state(
        session_dir,
        status="running",
        max_steps=max_steps,
        steps_used=0,
        intake_loaded_last=bool(progress.get("intake_loaded_last", False)),
    )
    append_session_event(
        session_dir,
        "session_driver_start",
        {
            "max_steps": max_steps,
            "mode": mode,
            "lease_ttl_sec": lease_ttl_sec,
            **_session_intake_tick_fields(session_dir, progress),
        },
    )

    while steps_used < max_steps:
        if lease_ttl_sec > 0:
            prune_stale_leases(session_dir, lease_ttl_sec)
        if all_steps_complete(plan, completed):
            progress["completed_step_ids"] = sorted(completed)
            progress["pending_step_ids"] = []
            progress["blocked_reason"] = None
            _write_json(progress_path, progress)
            tail = _emit_stop_and_session_dod(
                session_dir,
                plan,
                completed,
                exit_code=EXIT_SESSION_OK,
                stopped_reason="completed_review_pass",
                driver_status="completed_review_pass",
                max_steps=max_steps,
                steps_used=steps_used,
                block_detail=None,
                progress_path=progress_path,
            )
            return {
                "exit_code": 0,
                "stopped_reason": "completed_review_pass",
                "steps_executed": steps_used,
                "completed_step_ids": sorted(completed),
                **tail,
            }

        batch = select_steps_for_tick(plan, completed, max_concurrent_agents=max_concurrent_agents)
        if not batch:
            pending = [s for s in _step_map(plan) if s not in completed]
            progress["pending_step_ids"] = pending
            progress["blocked_reason"] = "no_runnable_step"
            _write_json(progress_path, progress)
            tail = _emit_stop_and_session_dod(
                session_dir,
                plan,
                completed,
                exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
                stopped_reason="no_runnable_step",
                driver_status="blocked_human",
                max_steps=max_steps,
                steps_used=steps_used,
                block_detail="deadlock_or_missing_dependency",
                extra_for_stop={"pending_step_ids": pending},
                progress_path=progress_path,
            )
            return {
                "exit_code": 1,
                "stopped_reason": "blocked_human",
                "detail": "no_runnable_step",
                "pending_step_ids": pending,
                **tail,
            }

        by_id = _step_map(plan)
        budget_left = max_steps - steps_used
        if budget_left < len(batch):
            batch = batch[:budget_left]
        if not batch:
            continue

        append_session_event(
            session_dir,
            "tick",
            {
                "steps_used": steps_used,
                "batch": list(batch),
                "completed_step_ids": sorted(completed),
                **_session_intake_tick_fields(session_dir, progress),
            },
        )

        lease_acquired: list[str] = []
        for step_id in batch:
            row = by_id[step_id]
            scopes = row.get("path_scope") or []
            scopes_str = [str(s) for s in scopes if isinstance(s, str)]
            ok_lease, reason = try_acquire(
                session_dir,
                step_id=step_id,
                path_scopes=scopes_str,
                active_step_ids=list(batch),
                plan_steps=by_id,
            )
            if not ok_lease:
                for aid in lease_acquired:
                    release(session_dir, aid)
                progress["blocked_reason"] = reason
                _write_json(progress_path, progress)
                tail = _emit_stop_and_session_dod(
                    session_dir,
                    plan,
                    completed,
                    exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
                    stopped_reason="lease_denied",
                    driver_status="blocked_human",
                    max_steps=max_steps,
                    steps_used=steps_used,
                    block_detail=reason or "lease_denied",
                    extra_for_stop={"step_id": step_id, "detail": reason},
                    progress_path=progress_path,
                )
                return {
                    "exit_code": 1,
                    "stopped_reason": "blocked_human",
                    "detail": reason,
                    "step_id": step_id,
                    **tail,
                }
            lease_acquired.append(step_id)

        use_parallel = (
            parallel_worktrees
            and len(batch) > 1
            and max_concurrent_agents > 1
            and git_worktree_available(repo_root)
        )
        if use_parallel:
            early, steps_used = _run_batch_parallel_worktrees(
                session_dir,
                plan,
                batch,
                by_id,
                repo_root,
                mode,
                failures,
                max_steps,
                steps_used,
                progress_path,
                progress,
                completed,
                max_concurrent_agents,
            )
            if early is not None:
                return early
            continue

        for step_id in batch:
            if steps_used >= max_steps:
                break
            row = by_id[step_id]
            pack = build_context_pack(
                repo_root=repo_root,
                session_dir=session_dir,
                step=row,
                prior_failures=failures,
                latest_runs_by_step=latest_output_dirs_by_step(session_dir),
            )
            progress["intake_loaded_last"] = bool(pack.get("intake_loaded"))
            full_task = task_with_context(
                context_markdown=str(pack.get("markdown", "")),
                step_description=str(row.get("description", "")),
            )
            result = execute_single_task(
                full_task,
                mode,
                repeat=1,
                project_step_id=step_id,
                project_session_dir=str(session_dir.resolve()),
            )
            steps_used += 1
            out_dir = result.get("output_dir")
            run_id = result.get("run_id")
            progress["last_run_id"] = run_id
            progress["last_output_dir"] = out_dir
            _append_step_run(
                session_dir,
                {
                    "step_id": step_id,
                    "run_id": run_id,
                    "output_dir": out_dir,
                    "pipeline_error": result.get("error"),
                },
            )

            if result.get("error"):
                failures.append({"step_id": step_id, "detail": str(result.get("error"))})
                release(session_dir, step_id)
                progress["failed_step_id"] = step_id
                progress["blocked_reason"] = "pipeline_error"
                _write_json(progress_path, progress)
                tail = _emit_stop_and_session_dod(
                    session_dir,
                    plan,
                    completed,
                    exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
                    stopped_reason="pipeline_error",
                    driver_status="blocked_human",
                    max_steps=max_steps,
                    steps_used=steps_used,
                    block_detail="pipeline_error",
                    extra_for_stop={"step_id": step_id},
                    progress_path=progress_path,
                )
                return {
                    "exit_code": 1,
                    "stopped_reason": "blocked_human",
                    "step_id": step_id,
                    "result": result,
                    **tail,
                }

            ver = row.get("verification")
            vbundle = run_step_verification(
                repo_root=repo_root,
                session_dir=session_dir,
                step_id=step_id,
                verification=ver if isinstance(ver, dict) else None,
            )
            release(session_dir, step_id)

            if not vbundle.get("passed"):
                failures.append({"step_id": step_id, "detail": "verification_failed"})
                progress["failed_step_id"] = step_id
                progress["blocked_reason"] = "verification_failed"
                _write_json(progress_path, progress)
                tail = _emit_stop_and_session_dod(
                    session_dir,
                    plan,
                    completed,
                    exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
                    stopped_reason="verification_failed",
                    driver_status="blocked_human",
                    max_steps=max_steps,
                    steps_used=steps_used,
                    block_detail="verification_failed",
                    extra_for_stop={"step_id": step_id},
                    progress_path=progress_path,
                )
                return {
                    "exit_code": 1,
                    "stopped_reason": "blocked_human",
                    "step_id": step_id,
                    "verification": vbundle,
                    **tail,
                }

            completed.add(step_id)
            progress["completed_step_ids"] = sorted(completed)
            progress["pending_step_ids"] = [s for s in _step_map(plan) if s not in completed]
            progress["failed_step_id"] = None
            progress["blocked_reason"] = None
            progress["schema_version"] = PROGRESS_SCHEMA_VERSION
            _write_json(progress_path, progress)
            write_verification_aggregate(session_dir, plan)
            _write_driver_state(
                session_dir,
                status="running",
                max_steps=max_steps,
                steps_used=steps_used,
                intake_loaded_last=bool(progress.get("intake_loaded_last", False)),
            )

        if steps_used >= max_steps and not all_steps_complete(plan, completed):
            progress["completed_step_ids"] = sorted(completed)
            progress["pending_step_ids"] = [s for s in _step_map(plan) if s not in completed]
            _write_json(progress_path, progress)
            tail = _emit_stop_and_session_dod(
                session_dir,
                plan,
                completed,
                exit_code=EXIT_SESSION_BLOCKED_OR_BUDGET,
                stopped_reason="exhausted_budget",
                driver_status="exhausted_budget",
                max_steps=max_steps,
                steps_used=steps_used,
                block_detail="max_steps",
                extra_for_stop={"budget": "max_steps"},
                progress_path=progress_path,
            )
            return {
                "exit_code": 1,
                "stopped_reason": "exhausted_budget",
                "budget": "max_steps",
                "completed_step_ids": sorted(completed),
                **tail,
            }

    tail = _emit_stop_and_session_dod(
        session_dir,
        plan,
        completed,
        exit_code=EXIT_SESSION_INVALID,
        stopped_reason="unexpected_end",
        driver_status="invalid_session",
        max_steps=max_steps,
        steps_used=steps_used,
        block_detail="unexpected_end",
        progress_path=progress_path,
    )
    return {"exit_code": 2, "error": "unexpected_end", "completed_step_ids": sorted(completed), **tail}
