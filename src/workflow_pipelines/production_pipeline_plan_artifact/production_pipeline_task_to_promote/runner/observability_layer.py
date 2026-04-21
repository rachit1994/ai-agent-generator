"""Write deterministic production observability artifact."""

from __future__ import annotations

from pathlib import Path

from production_architecture.observability import (
    build_production_observability,
    validate_production_observability_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _count_lines(path: Path) -> int:
    if not path.is_file():
        return 0
    return len([line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()])


def write_production_observability_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, object]:
    payload = build_production_observability(
        run_id=run_id,
        mode=mode,
        trace_rows=_count_lines(output_dir / "traces.jsonl"),
        orchestration_rows=_count_lines(output_dir / "orchestration.jsonl"),
        run_log_lines=_count_lines(output_dir / "run.log"),
    )
    errs = validate_production_observability_dict(payload)
    if errs:
        raise ValueError(f"production_observability_contract:{','.join(errs)}")
    ensure_dir(output_dir / "observability")
    write_json(output_dir / "observability" / "production_observability.json", payload)
    return payload
