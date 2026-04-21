"""Write deterministic role-agents artifact."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core_components.role_agents import build_role_agents, validate_role_agents_dict
from production_architecture.storage.storage.storage import ensure_dir, write_json


def write_role_agents_artifact(
    *,
    output_dir: Path,
    run_id: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    skill_nodes: dict[str, Any],
) -> dict[str, Any]:
    payload = build_role_agents(
        run_id=run_id,
        parsed=parsed if isinstance(parsed, dict) else {},
        events=events if isinstance(events, list) else [],
        skill_nodes=skill_nodes if isinstance(skill_nodes, dict) else {},
    )
    errs = validate_role_agents_dict(payload)
    if errs:
        raise ValueError(f"role_agents_contract:{','.join(errs)}")
    ensure_dir(output_dir / "capability")
    write_json(output_dir / "capability" / "role_agents.json", payload)
    return payload
