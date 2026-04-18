"""Artifact path lists and manifest rows for review.json."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def manifest_paths_for_review(mode: str) -> list[str]:
    """Paths checked in ``review.json`` artifact_manifest (before review file itself exists)."""
    base = [
        "traces.jsonl",
        "orchestration.jsonl",
        "report.md",
        "run.log",
        "answer.txt",
        "static_gates_report.json",
        "outputs/README.txt",
        "outputs/manifest.json",
    ]
    if mode == "guarded_pipeline":
        base.extend(
            [
                "planner_doc.md",
                "executor_prompt.txt",
                "verifier_report.json",
            ]
        )
    return base


def all_required_v1_paths(mode: str) -> list[str]:
    return [
        "summary.json",
        "review.json",
        "token_context.json",
        *manifest_paths_for_review(mode),
    ]


def manifest_entries(output_dir: Path, relative_paths: list[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for rel in relative_paths:
        p = output_dir / rel
        entries.append({"path": rel, "present": p.is_file() or p.is_dir()})
    return entries
