"""Write deterministic orchestration run-end runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.orchestration_run_end import (
    build_orchestration_run_end_runtime,
    validate_orchestration_run_end_runtime_dict,
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


def write_orchestration_run_end_runtime_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_orchestration_run_end_runtime(
        run_id=run_id,
        orchestration_rows=_read_jsonl_rows(output_dir / "orchestration.jsonl"),
    )
    errs = validate_orchestration_run_end_runtime_dict(payload)
    if errs:
        raise ValueError(f"orchestration_run_end_runtime_contract:{','.join(errs)}")
    ensure_dir(output_dir / "orchestration")
    write_json(output_dir / "orchestration" / "run_end_runtime.json", payload)
    return payload
