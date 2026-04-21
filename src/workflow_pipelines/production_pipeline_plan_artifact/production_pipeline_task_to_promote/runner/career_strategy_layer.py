"""Write deterministic career strategy layer artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.career_strategy_layer import (
    build_career_strategy_layer,
    validate_career_strategy_layer_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_career_strategy_layer_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    payload = build_career_strategy_layer(
        run_id=run_id,
        mode=mode,
        summary=_read_json_or_empty(output_dir / "summary.json"),
        review=_read_json_or_empty(output_dir / "review.json"),
        promotion_package=_read_json_or_empty(output_dir / "lifecycle" / "promotion_package.json"),
        capability_growth=_read_json_or_empty(output_dir / "learning" / "capability_growth_metrics.json"),
        transfer_learning=_read_json_or_empty(output_dir / "learning" / "transfer_learning_metrics.json"),
        error_reduction=_read_json_or_empty(output_dir / "learning" / "error_reduction_metrics.json"),
        scalability_strategy=_read_json_or_empty(output_dir / "strategy" / "scalability_strategy.json"),
    )
    errs = validate_career_strategy_layer_dict(payload)
    if errs:
        raise ValueError(f"career_strategy_layer_contract:{','.join(errs)}")
    ensure_dir(output_dir / "strategy")
    write_json(output_dir / "strategy" / "career_strategy_layer.json", payload)
    return payload

