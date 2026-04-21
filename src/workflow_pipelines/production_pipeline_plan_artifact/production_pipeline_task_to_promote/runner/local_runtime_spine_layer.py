"""Write deterministic local-runtime CLI spine artifact."""

from __future__ import annotations

from pathlib import Path

from production_architecture.local_runtime import (
    build_local_runtime_spine,
    validate_local_runtime_spine_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def write_local_runtime_spine_artifact(*, output_dir: Path, run_id: str, mode: str) -> dict[str, object]:
    payload = build_local_runtime_spine(
        run_id=run_id,
        mode=mode,
        has_run_manifest=(output_dir / "run-manifest.json").is_file(),
        has_orchestration=(output_dir / "orchestration.jsonl").is_file(),
        has_traces=(output_dir / "traces.jsonl").is_file(),
    )
    errs = validate_local_runtime_spine_dict(payload)
    if errs:
        raise ValueError(f"local_runtime_spine_contract:{','.join(errs)}")
    ensure_dir(output_dir / "orchestrator")
    write_json(output_dir / "orchestrator" / "local_runtime_spine.json", payload)
    return payload
