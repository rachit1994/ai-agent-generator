"""Write deterministic dual-control runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from guardrails_and_safety.dual_control import build_dual_control_runtime, validate_dual_control_dict
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_dual_control_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_dual_control_runtime(
        run_id=run_id,
        doc_review=_read_json_or_empty(output_dir / "program" / "doc_review.json"),
        dual_control_ack=_read_json_or_empty(output_dir / "program" / "dual_control_ack.json"),
    )
    errs = validate_dual_control_dict(payload)
    if errs:
        raise ValueError(f"dual_control_contract:{','.join(errs)}")
    ensure_dir(output_dir / "program")
    write_json(output_dir / "program" / "dual_control_runtime.json", payload)
    return payload
