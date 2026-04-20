"""Contract for ``execute_single_task(..., repeat>=2)`` aggregate result (§10 retry / repeat profile)."""

from __future__ import annotations

from typing import Any, Final

RETRY_PIPELINE_REPEAT_CONTRACT: Final = "sde.retry_pipeline_repeat_profile.v1"


def _errs_top_fields(body: dict[str, Any], *, repeat: int) -> list[str]:
    errs: list[str] = []
    if body.get("schema") != RETRY_PIPELINE_REPEAT_CONTRACT:
        errs.append("repeat_profile_schema")
    if body.get("repeat") != repeat:
        errs.append("repeat_profile_repeat_mismatch")
    if not isinstance(body.get("task"), str):
        errs.append("repeat_profile_task_type")
    if not isinstance(body.get("mode"), str) or not str(body.get("mode")).strip():
        errs.append("repeat_profile_mode")
    ar = body.get("all_runs_no_pipeline_error")
    if not isinstance(ar, bool):
        errs.append("repeat_profile_all_runs_no_pipeline_error_type")
    vr = body.get("validation_ready_all")
    if not isinstance(vr, bool):
        errs.append("repeat_profile_validation_ready_all_type")
    return errs


def _errs_one_run(row: Any, idx: int) -> list[str]:
    if not isinstance(row, dict):
        return [f"repeat_profile_run_not_object:{idx}"]
    rid = row.get("run_id")
    if not isinstance(rid, str) or not rid.strip():
        return [f"repeat_profile_run_id:{idx}"]
    od = row.get("output_dir")
    if not isinstance(od, str) or not od.strip():
        return [f"repeat_profile_output_dir:{idx}"]
    has_out = "output" in row
    has_err = "error" in row
    if has_out == has_err:
        return [f"repeat_profile_run_outcome:{idx}"]
    if has_err:
        err = row.get("error")
        if not isinstance(err, dict):
            return [f"repeat_profile_error_shape:{idx}"]
        et = err.get("type")
        em = err.get("message")
        if not isinstance(et, str) or not et.strip():
            return [f"repeat_profile_error_type:{idx}"]
        if not isinstance(em, str) or not em.strip():
            return [f"repeat_profile_error_message:{idx}"]
    else:
        if not isinstance(row.get("output"), str):
            return [f"repeat_profile_output_type:{idx}"]
    return []


def _errs_runs(body: dict[str, Any], *, repeat: int) -> list[str]:
    runs = body.get("runs")
    if not isinstance(runs, list):
        return ["repeat_profile_runs_type"]
    if len(runs) != repeat:
        return ["repeat_profile_runs_len"]
    errs: list[str] = []
    for idx, row in enumerate(runs):
        errs.extend(_errs_one_run(row, idx))
    return errs


def _errs_consistency(body: dict[str, Any]) -> list[str]:
    runs = body.get("runs")
    if not isinstance(runs, list):
        return []
    errs: list[str] = []
    has_error = any(isinstance(row, dict) and "error" in row for row in runs)
    all_no_pipeline_error = body.get("all_runs_no_pipeline_error")
    if isinstance(all_no_pipeline_error, bool) and all_no_pipeline_error != (not has_error):
        errs.append("repeat_profile_all_runs_no_pipeline_error_value")
    validation_ready_all = body.get("validation_ready_all")
    if isinstance(validation_ready_all, bool) and has_error and validation_ready_all:
        errs.append("repeat_profile_validation_ready_all_value")
    return errs


def validate_repeat_profile_result(body: Any, *, repeat: int) -> list[str]:
    """Return stable error tokens; empty when ``repeat < 2`` or body matches the V1 repeat envelope."""
    if repeat < 2:
        return []
    if not isinstance(body, dict):
        return ["repeat_profile_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_top_fields(b, repeat=repeat))
    errs.extend(_errs_runs(b, repeat=repeat))
    errs.extend(_errs_consistency(b))
    return errs
