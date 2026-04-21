"""Write deterministic scalability strategy artifact."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from production_architecture.storage.storage.storage import ensure_dir, write_json
from scalability_strategy import build_scalability_strategy, validate_scalability_strategy_dict


def write_scalability_strategy_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    cto: dict[str, Any],
) -> dict[str, Any]:
    payload = build_scalability_strategy(run_id=run_id, mode=mode, parsed=parsed, events=events, cto=cto)
    errs = validate_scalability_strategy_dict(payload)
    if errs:
        raise ValueError(f"scalability_strategy_contract:{','.join(errs)}")
    ensure_dir(output_dir / "strategy")
    write_json(output_dir / "strategy" / "scalability_strategy.json", payload)
    return payload

