"""Contracts for topology and repository layout artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TOPOLOGY_AND_REPOSITORY_LAYOUT_CONTRACT = "sde.topology_and_repository_layout.v1"
TOPOLOGY_AND_REPOSITORY_LAYOUT_SCHEMA_VERSION = "1.0"


def validate_topology_and_repository_layout_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["topology_and_repository_layout_not_object"]
    errs: list[str] = []
    if body.get("schema") != TOPOLOGY_AND_REPOSITORY_LAYOUT_CONTRACT:
        errs.append("topology_and_repository_layout_schema")
    if body.get("schema_version") != TOPOLOGY_AND_REPOSITORY_LAYOUT_SCHEMA_VERSION:
        errs.append("topology_and_repository_layout_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("topology_and_repository_layout_run_id")
    mode = body.get("mode")
    if mode not in {"baseline", "guarded_pipeline", "phased_pipeline"}:
        errs.append("topology_and_repository_layout_mode")
    status = body.get("status")
    if status not in {"ready", "not_ready"}:
        errs.append("topology_and_repository_layout_status")
    topology = body.get("topology")
    if not isinstance(topology, dict):
        errs.append("topology_and_repository_layout_topology")
        return errs
    for key in (
        "implementation_roadmap",
        "scalability_strategy",
        "core_components",
        "success_criteria",
        "workflow_pipelines",
    ):
        entry = topology.get(key)
        if not isinstance(entry, dict):
            errs.append(f"topology_and_repository_layout_topology_type:{key}")
            continue
        coverage = entry.get("coverage")
        if isinstance(coverage, bool) or not isinstance(coverage, (int, float)):
            errs.append(f"topology_and_repository_layout_coverage_type:{key}")
            continue
        if float(coverage) < 0.0 or float(coverage) > 1.0:
            errs.append(f"topology_and_repository_layout_coverage_range:{key}")
    return errs


def validate_topology_and_repository_layout_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["topology_and_repository_layout_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["topology_and_repository_layout_json"]
    return validate_topology_and_repository_layout_dict(body)

