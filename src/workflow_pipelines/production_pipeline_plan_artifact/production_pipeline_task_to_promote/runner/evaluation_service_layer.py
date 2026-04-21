"""Write deterministic core evaluation-service artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.evaluation_service import build_evaluation_service, validate_evaluation_service_dict
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_evaluation_service_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_evaluation_service(
        run_id=run_id,
        summary=_read_json_or_empty(output_dir / "summary.json"),
        online_eval=_read_json_or_empty(output_dir / "learning" / "online_evaluation_shadow_canary.json"),
        promotion_eval=_read_json_or_empty(output_dir / "learning" / "promotion_evaluation.json"),
    )
    errs = validate_evaluation_service_dict(payload)
    if errs:
        raise ValueError(f"evaluation_service_contract:{','.join(errs)}")
    ensure_dir(output_dir / "evaluation")
    write_json(output_dir / "evaluation" / "service_runtime.json", payload)
    return payload
