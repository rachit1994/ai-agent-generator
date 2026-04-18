"""Bounded context injection for project driver steps (Category 1, Phase 2)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import uuid
from pathlib import Path
from typing import Any

from sde_gates.time_util import iso_now

from .repo_index import build_repo_index


def latest_output_dirs_by_step(session_dir: Path) -> dict[str, str]:
    """Latest ``output_dir`` per ``step_id`` from ``step_runs.jsonl`` (append order wins)."""
    p = session_dir / "step_runs.jsonl"
    if not p.is_file():
        return {}
    out: dict[str, str] = {}
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        sid = row.get("step_id")
        od = row.get("output_dir")
        if isinstance(sid, str) and isinstance(od, str) and od.strip():
            out[sid] = od
    return out


def _sha256_utf8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git_head(repo_root: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if proc.returncode != 0:
            return None
        return proc.stdout.strip() or None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _excerpt_prior_run(output_dir: Path, *, max_chars: int) -> str:
    chunks: list[str] = []
    budget = max_chars
    summary_path = output_dir / "summary.json"
    if summary_path.is_file() and budget > 80:
        try:
            raw = summary_path.read_text(encoding="utf-8")
            take = min(len(raw), max(budget // 2, 200))
            chunks.append("### summary.json (excerpt)\n```json\n" + raw[:take] + "\n```\n")
            budget -= take + 40
        except OSError:
            pass
    report_path = output_dir / "report.md"
    if report_path.is_file() and budget > 80:
        try:
            raw = report_path.read_text(encoding="utf-8")
            take = min(len(raw), budget)
            chunks.append("### report.md (excerpt)\n" + raw[:take] + "\n")
        except OSError:
            pass
    return "\n".join(chunks) if chunks else ""


def _failure_verification_excerpt(session_dir: Path, step_id: str, *, max_log_chars: int) -> str:
    vp = session_dir / "verification" / f"{step_id}.json"
    if not vp.is_file():
        return ""
    try:
        vb = json.loads(vp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return ""
    lines_out: list[str] = []
    for cmd in (vb.get("commands") or [])[-3:]:
        if not isinstance(cmd, dict):
            continue
        log = str(cmd.get("log", ""))[-max_log_chars:]
        if log.strip():
            lines_out.append(f"- cmd `{cmd.get('cmd')}` exit={cmd.get('exit_code')}\n  ```\n{log}\n  ```")
    return "\n".join(lines_out) if lines_out else ""


def _session_truncation_hs03_ok(truncation_events: list[Any], reductions: list[Any]) -> bool:
    """Same pairing rule as HS03 on ``token_context.json`` (session-level context packs)."""
    trunc = truncation_events or []
    reds = reductions or []
    if len(trunc) == 0:
        return True
    if len(reds) == 0:
        return False
    return all(
        any(isinstance(r, dict) and r.get("provenance_id") == t.get("provenance_id") for r in reds)
        for t in trunc
        if isinstance(t, dict)
    )


def _append_lineage(session_dir: Path, row: dict[str, Any]) -> None:
    path = session_dir / "context_pack_lineage.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, separators=(",", ":")) + "\n")


def _failures_markdown(session_dir: Path, prior_failures: list[dict[str, Any]]) -> str:
    failures_md = ""
    for frow in prior_failures[-5:]:
        sid_f = frow.get("step_id")
        detail = frow.get("detail", "")
        failures_md += f"- step `{sid_f}`: {detail}\n"
        if isinstance(sid_f, str) and ("verification" in str(detail).lower() or detail == "verification_failed"):
            ex = _failure_verification_excerpt(session_dir, sid_f, max_log_chars=1_500)
            if ex:
                failures_md += ex + "\n"
    return failures_md


def _prior_section_and_refs(
    step: dict[str, Any],
    runs_map: dict[str, str],
    head: str | None,
    *,
    max_prior_dep_chars: int,
    per_dep_cap: int,
) -> tuple[str, list[dict[str, Any]]]:
    prior_refs: list[dict[str, Any]] = []
    prior_chunks: list[str] = []
    dep_budget = max_prior_dep_chars
    for dep in step.get("depends_on") or []:
        if not isinstance(dep, str) or dep_budget <= 0:
            continue
        od = runs_map.get(dep)
        if not od:
            continue
        outp = Path(od)
        if not outp.is_dir():
            continue
        cap = min(per_dep_cap, dep_budget)
        excerpt = _excerpt_prior_run(outp, max_chars=cap)
        if excerpt.strip():
            prior_chunks.append(f"### From dependency `{dep}` → `{outp}`\n{excerpt}\n")
            dep_budget -= len(excerpt)
            prior_refs.append(
                {
                    "kind": "run_output",
                    "step_id": dep,
                    "path": str(outp.resolve()),
                    "git_head_at_pack_build": head,
                }
            )
    if prior_chunks:
        prior_section = "## Prior dependency runs (excerpts)\n\n" + "\n".join(prior_chunks) + "\n"
    else:
        prior_section = "## Prior dependency runs (excerpts)\n\n- (none — no completed deps with outputs yet)\n\n"
    return prior_section, prior_refs


def _apply_char_cap(
    markdown_full: str,
    max_chars: int,
    step_id: str,
) -> tuple[str, bool, list[dict[str, Any]], list[dict[str, Any]]]:
    truncation_events: list[dict[str, Any]] = []
    reductions: list[dict[str, Any]] = []
    truncated = len(markdown_full) > max_chars
    if not truncated:
        return markdown_full, False, truncation_events, reductions
    provenance_id = f"ctxpack-{uuid.uuid4().hex[:16]}"
    removed = len(markdown_full) - max_chars
    truncation_events.append(
        {
            "provenance_id": provenance_id,
            "reason": "context_pack_char_cap",
            "chars_removed": removed,
            "max_chars": max_chars,
        }
    )
    reductions.append(
        {
            "provenance_id": provenance_id,
            "artifact": f"context_packs/{step_id}.json",
            "note": "markdown field is post-truncation; markdown_sha256_full is pre-truncation",
        }
    )
    body = markdown_full[:max_chars] + "\n…[context_pack truncated]\n"
    return body, True, truncation_events, reductions


def build_context_pack(
    *,
    repo_root: Path,
    session_dir: Path,
    step: dict[str, Any],
    prior_failures: list[dict[str, Any]],
    max_chars: int = 12_000,
    latest_runs_by_step: dict[str, str] | None = None,
    max_prior_dep_chars: int = 6_000,
    per_dep_cap: int = 2_500,
) -> dict[str, Any]:
    """Assemble capped markdown + metadata for planner/executor task prefix.

    Phase 2: dependency ``summary.json`` / ``report.md`` excerpts, verification log snippets,
    and HS03-style ``truncation_events`` + ``reductions`` when the markdown is capped.
    """
    scopes = step.get("path_scope") or []
    if not isinstance(scopes, list):
        scopes = []
    scopes_str = [str(s) for s in scopes if isinstance(s, str)]
    index = build_repo_index(repo_root, path_scopes=scopes_str, max_files=400)
    head = _git_head(repo_root)
    runs_map = latest_runs_by_step or {}

    failures_md = _failures_markdown(session_dir, prior_failures)
    paths_preview = "\n".join(f"- `{p}`" for p in index.get("paths", [])[:80])
    prior_section, prior_refs = _prior_section_and_refs(
        step,
        runs_map,
        head,
        max_prior_dep_chars=max_prior_dep_chars,
        per_dep_cap=per_dep_cap,
    )

    markdown_full = (
        "## Workspace\n"
        f"- repo_root: `{repo_root.resolve()}`\n"
        f"- git_head: `{head or 'unknown'}`\n"
        f"- path_scope: {scopes_str}\n\n"
        "## Repo index (capped)\n"
        f"{paths_preview}\n\n"
        f"{prior_section}"
        "## Recent failures / retries\n"
        f"{failures_md or '- (none)\\n'}\n"
        "## Step\n"
        f"- step_id: `{step.get('step_id')}`\n"
        f"- title: {step.get('title', '')}\n"
    )
    full_sha = _sha256_utf8(markdown_full)
    sid = str(step.get("step_id", "unknown"))
    body, truncated, truncation_events, reductions = _apply_char_cap(markdown_full, max_chars, sid)

    hs03_ok = _session_truncation_hs03_ok(truncation_events, reductions)
    pack: dict[str, Any] = {
        "schema_version": "1.1",
        "built_at": iso_now(),
        "truncated": truncated,
        "char_count": len(body),
        "markdown_char_count_full": len(markdown_full),
        "markdown_sha256_full": full_sha,
        "truncation_events": truncation_events,
        "reductions": reductions,
        "truncation_hs03_ok": hs03_ok,
        "git_head": head,
        "repo_index_summary": {"file_count": index.get("file_count"), "scopes": scopes_str},
        "references": prior_refs,
        "markdown": body,
    }
    out_dir = session_dir / "context_packs"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{sid}.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")

    _append_lineage(
        session_dir,
        {
            "step_id": sid,
            "built_at": pack["built_at"],
            "markdown_sha256_full": full_sha,
            "truncated": truncated,
            "truncation_hs03_ok": hs03_ok,
        },
    )
    return pack


def task_with_context(*, context_markdown: str, step_description: str) -> str:
    """Single string passed to ``execute_single_task``."""
    return context_markdown + "\n## Task for this step\n\n" + step_description.strip()
