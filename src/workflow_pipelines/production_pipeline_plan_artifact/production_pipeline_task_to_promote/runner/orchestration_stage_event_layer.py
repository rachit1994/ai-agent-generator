"""Write deterministic orchestration stage-event runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.orchestration_stage_event import (
    build_orchestration_stage_event_runtime,
    validate_orchestration_stage_event_runtime_dict,
)


def _read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        body = json.loads(line)
        if isinstance(body, dict):
            rows.append(body)
    return rows


def write_orchestration_stage_event_runtime_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_orchestration_stage_event_runtime(
        run_id=run_id,
        orchestration_rows=_read_jsonl_rows(output_dir / "orchestration.jsonl"),
    )
    errs = validate_orchestration_stage_event_runtime_dict(payload)
    if errs:
        raise ValueError(f"orchestration_stage_event_runtime_contract:{','.join(errs)}")
    ensure_dir(output_dir / "orchestration")
    write_json(output_dir / "orchestration" / "stage_event_runtime.json", payload)
    return payload
