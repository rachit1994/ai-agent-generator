"""Contracts for §10 failure path artifacts: ``replay_manifest.json`` + harness ``summary.json`` on failure."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

REPLAY_MANIFEST_CONTRACT: Final = "sde.replay_manifest.v1"
FAILURE_PIPELINE_SUMMARY_CONTRACT: Final = "sde.failure_pipeline_summary.v1"


def _errs_replay_core(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    sv = body.get("schema_version", body.get("schemaVersion"))
    if not isinstance(sv, str) or not sv.strip():
        errs.append("replay_manifest_schema_version")
    rid = body.get("run_id", body.get("runId"))
    if not isinstance(rid, str) or not rid.strip():
        errs.append("replay_manifest_run_id")
    cv = body.get("contract_version", body.get("contractVersion"))
    if cv != REPLAY_MANIFEST_CONTRACT:
        errs.append("replay_manifest_contract_version")
    return errs


def _errs_replay_window_sources(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    win = body.get("window")
    if win is not None:
        if not isinstance(win, dict):
            errs.append("replay_manifest_window")
        else:
            fl = win.get("first_line", win.get("firstLine"))
            ll = win.get("last_line", win.get("lastLine"))
            if not isinstance(fl, int) or not isinstance(ll, int) or fl < 1 or ll < 1:
                errs.append("replay_manifest_window_lines")
    srcs = body.get("sources")
    if not isinstance(srcs, list) or len(srcs) == 0:
        errs.append("replay_manifest_sources")
        return errs
    for idx, row in enumerate(srcs):
        if not isinstance(row, dict):
            errs.append(f"replay_manifest_source_not_object:{idx}")
            continue
        p = row.get("path")
        h = row.get("sha256")
        if not isinstance(p, str) or not p.strip():
            errs.append(f"replay_manifest_source_path:{idx}")
        if not isinstance(h, str) or not h.strip():
            errs.append(f"replay_manifest_source_sha256:{idx}")
    return errs


def _errs_replay_tail(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    cr = body.get("chain_root", body.get("chainRoot"))
    if not isinstance(cr, str) or not cr.strip():
        errs.append("replay_manifest_chain_root")
    pv = body.get("projection_version", body.get("projectionVersion"))
    if pv is not None and (not isinstance(pv, str) or not pv.strip()):
        errs.append("replay_manifest_projection_version")
    if "passed" in body and not isinstance(body.get("passed"), bool):
        errs.append("replay_manifest_passed_type")
    ba = body.get("built_at", body.get("builtAt"))
    if ba is not None and (not isinstance(ba, str) or not ba.strip()):
        errs.append("replay_manifest_built_at")
    return errs


def validate_replay_manifest_dict(body: Any) -> list[str]:
    """Return stable error tokens for **HS18** replay manifest shape (fail-closed replay plane)."""
    if not isinstance(body, dict):
        return ["replay_manifest_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_replay_core(b))
    errs.extend(_errs_replay_window_sources(b))
    errs.extend(_errs_replay_tail(b))
    return errs


def validate_replay_manifest_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["replay_manifest_file_missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ["replay_manifest_unreadable"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return ["replay_manifest_json"]
    return validate_replay_manifest_dict(parsed)


def _errs_failure_summary_top(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    rid = body.get("runId", body.get("run_id"))
    if not isinstance(rid, str) or not rid.strip():
        errs.append("failure_summary_run_id")
    mode = body.get("mode")
    if not isinstance(mode, str) or not mode.strip():
        errs.append("failure_summary_mode")
    rs = body.get("runStatus", body.get("run_status"))
    if rs != "failed":
        errs.append("failure_summary_run_status")
    if "partial" not in body or not isinstance(body.get("partial"), bool):
        errs.append("failure_summary_partial_type")
    return errs


def _errs_failure_summary_error(body: dict[str, Any]) -> list[str]:
    err = body.get("error")
    if not isinstance(err, dict):
        return ["failure_summary_error"]
    if not isinstance(err.get("type"), str) or not str(err.get("type")).strip():
        return ["failure_summary_error_type"]
    if not isinstance(err.get("message"), str):
        return ["failure_summary_error_message_type"]
    return []


def validate_failure_summary_dict(body: Any) -> list[str]:
    """Return stable error tokens for ``write_failure_summary`` ``summary.json`` shape."""
    if not isinstance(body, dict):
        return ["failure_summary_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_failure_summary_top(b))
    errs.extend(_errs_failure_summary_error(b))
    for key in ("provider", "model"):
        val = b.get(key)
        if not isinstance(val, str) or not val.strip():
            errs.append(f"failure_summary_{key}")
    return errs


def validate_failure_summary_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["failure_summary_file_missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ["failure_summary_unreadable"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return ["failure_summary_json"]
    return validate_failure_summary_dict(parsed)
