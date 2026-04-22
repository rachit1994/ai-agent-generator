"""Write deterministic online-evaluation shadow/canary artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evaluation_framework.online_evaluation_shadow_canary_artifact import (
    ONLINE_EVALUATION_SHADOW_CANARY_ERROR_PREFIX,
    build_online_evaluation_shadow_canary,
    parse_online_eval_records_jsonl,
    validate_online_evaluation_shadow_canary_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return body if isinstance(body, dict) else {}


def write_online_evaluation_shadow_canary_artifact(
    *,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    records_path = output_dir / "learning" / "online_eval_records.jsonl"
    try:
        records = parse_online_eval_records_jsonl(records_path)
    except ValueError as exc:
        raise ValueError(f"{ONLINE_EVALUATION_SHADOW_CANARY_ERROR_PREFIX}{exc}") from exc
    payload = build_online_evaluation_shadow_canary(
        run_id=run_id,
        online_eval_records=records,
        canary_report=_read_json_or_empty(output_dir / "learning" / "canary_report.json"),
    )
    errs = validate_online_evaluation_shadow_canary_dict(payload)
    if errs:
        raise ValueError(f"{ONLINE_EVALUATION_SHADOW_CANARY_ERROR_PREFIX}{','.join(errs)}")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "learning" / "online_evaluation_shadow_canary.json", payload)
    return payload
