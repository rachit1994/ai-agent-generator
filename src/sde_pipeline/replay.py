"""Load run trajectories and optional narrative / rerun (local CLI only)."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from sde_foundations.storage import read_json, read_jsonl
from sde_foundations.utils import outputs_base

RUN_MANIFEST_SCHEMA = "sde.run_manifest.v1"
BENCHMARK_MANIFEST_SCHEMA = "sde.benchmark_manifest.v1"
_MANIFEST_FILENAMES = ("run-manifest.json", "benchmark-manifest.json")


def run_dir_for_id(run_id: str) -> Path:
    base = outputs_base() / "runs" / run_id
    if not base.is_dir():
        raise FileNotFoundError(f"run directory not found: {base}")
    return base


def load_traces(run_dir: Path) -> list[dict[str, Any]]:
    return read_jsonl(run_dir / "traces.jsonl")


def _load_manifest_from_run_dir(run_dir: Path) -> dict[str, Any] | None:
    for name in _MANIFEST_FILENAMES:
        path = run_dir / name
        if path.is_file():
            return read_json(path)
    return None


def format_timeline_text(events: list[dict[str, Any]], manifest: dict[str, Any] | None) -> str:
    lines: list[str] = ["# SDE trajectory (narrative)", ""]
    if manifest:
        lines.append(f"- manifest: {manifest.get('schema', 'unknown')}")
        if manifest.get("schema") == RUN_MANIFEST_SCHEMA:
            lines.extend(
                [
                    f"- mode: {manifest.get('mode')}",
                    f"- task (excerpt): {str(manifest.get('task', ''))[:200]!r}",
                ]
            )
        elif manifest.get("schema") == BENCHMARK_MANIFEST_SCHEMA:
            lines.extend(
                [
                    f"- suite: {manifest.get('suite_path')}",
                    f"- benchmark_mode: {manifest.get('mode')}",
                    f"- tasks: {len(manifest.get('tasks') or [])}",
                ]
            )
        lines.append("")
    for i, ev in enumerate(events, 1):
        stage = ev.get("stage", "?")
        tid = ev.get("task_id", "?")
        mode = ev.get("mode", "?")
        lat = ev.get("latency_ms", 0)
        passed = (ev.get("score") or {}).get("passed")
        errs = ev.get("errors") or []
        lines.append(f"{i}. [{mode}] task={tid} stage={stage} latency_ms={lat} passed={passed} errors={errs}")
    return "\n".join(lines)


def format_timeline_html(events: list[dict[str, Any]], manifest: dict[str, Any] | None, run_id: str) -> str:
    rows: list[str] = []
    for ev in events:
        stage = html.escape(str(ev.get("stage", "?")))
        tid = html.escape(str(ev.get("task_id", "?")))
        mode = html.escape(str(ev.get("mode", "?")))
        lat = html.escape(str(ev.get("latency_ms", 0)))
        passed = (ev.get("score") or {}).get("passed")
        ptxt = html.escape(str(passed))
        errs = html.escape(json.dumps(ev.get("errors") or []))
        rows.append(f"<tr><td>{mode}</td><td>{tid}</td><td>{stage}</td><td>{lat}</td><td>{ptxt}</td><td><pre>{errs}</pre></td></tr>")
    man_block = ""
    if manifest:
        man_block = f"<pre>{html.escape(json.dumps(manifest, indent=2)[:4000])}</pre>"
    return (
        "<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"/>"
        "<title>SDE trajectory</title>"
        "<style>body{font-family:system-ui,sans-serif;margin:1rem;} table{border-collapse:collapse;width:100%;}"
        "td,th{border:1px solid #ccc;padding:6px;text-align:left;} pre{white-space:pre-wrap;margin:0;}</style></head><body>"
        f"<h1>Trajectory: {html.escape(run_id)}</h1>"
        f"<p>Events: {len(events)}</p>{man_block}"
        "<table><thead><tr><th>mode</th><th>task_id</th><th>stage</th><th>latency_ms</th><th>passed</th><th>errors</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></body></html>"
    )


def write_trajectory_html(run_id: str) -> Path:
    run_dir = run_dir_for_id(run_id)
    events = load_traces(run_dir)
    manifest = _load_manifest_from_run_dir(run_dir)
    out = run_dir / "trajectory.html"
    out.write_text(format_timeline_html(events, manifest, run_id), encoding="utf-8")
    return out


def replay_narrative(run_id: str, *, output_format: str) -> str:
    run_dir = run_dir_for_id(run_id)
    events = load_traces(run_dir)
    manifest = _load_manifest_from_run_dir(run_dir)
    if output_format == "json":
        return json.dumps(
            {"run_id": run_id, "manifest": manifest, "events": events, "event_count": len(events)},
            indent=2,
        )
    if output_format == "html":
        return format_timeline_html(events, manifest, run_id)
    return format_timeline_text(events, manifest)


def replay_rerun(run_id: str, *, output_format: str) -> str:
    run_dir = run_dir_for_id(run_id)
    path = run_dir / "run-manifest.json"
    if not path.is_file():
        raise FileNotFoundError(f"run-manifest.json missing under {run_dir}; cannot --rerun")
    manifest = read_json(path)
    if manifest.get("schema") != RUN_MANIFEST_SCHEMA:
        raise ValueError(f"unsupported manifest schema: {manifest.get('schema')!r}")
    task = manifest.get("task")
    mode = manifest.get("mode")
    if not isinstance(task, str) or not task.strip():
        raise ValueError("run-manifest.json: invalid task")
    if mode not in ("baseline", "guarded_pipeline", "phased_pipeline"):
        raise ValueError("run-manifest.json: mode must be baseline, guarded_pipeline, or phased_pipeline")
    from sde_pipeline.runner import execute_single_task

    psid = manifest.get("project_step_id")
    psdir = manifest.get("project_session_dir")
    result = execute_single_task(
        task,
        mode,
        project_step_id=psid if isinstance(psid, str) else None,
        project_session_dir=psdir if isinstance(psdir, str) else None,
    )
    if output_format == "json":
        return json.dumps({"prior_run_id": run_id, "rerun": result}, indent=2)
    return (
        f"# SDE rerun\n- prior_run_id: {run_id}\n- new_run_id: {result.get('run_id')}\n"
        f"- output_dir: {result.get('output_dir')}\n"
        f"- error: {result.get('error')}\n"
    )


def replay_run(run_id: str, *, output_format: str = "text", rerun: bool = False, write_html: bool = False) -> str:
    fmt = output_format.lower().strip()
    if fmt not in ("text", "json", "html"):
        raise ValueError("output_format must be text, json, or html")
    if rerun and write_html:
        raise ValueError("write_html is not supported with --rerun")
    if rerun:
        if fmt == "html":
            raise ValueError("--format html is not supported with --rerun")
        return replay_rerun(run_id, output_format=fmt)
    if write_html:
        path = write_trajectory_html(run_id)
        return f"Wrote trajectory HTML: {path}\n"
    return replay_narrative(run_id, output_format=fmt)
