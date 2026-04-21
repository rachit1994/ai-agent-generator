"""Write deterministic regression-testing-surface runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evaluation_framework.regression_testing_surface import (
    build_regression_testing_surface,
    validate_regression_testing_surface_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.regression_surface_contract import (
    validate_regression_anchors,
)


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[7]


def write_regression_testing_surface_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_regression_testing_surface(
        run_id=run_id,
        anchor_errors=validate_regression_anchors(_repo_root()),
        promotion_evaluation=_read_json_or_empty(output_dir / "learning" / "promotion_evaluation.json"),
        online_evaluation=_read_json_or_empty(output_dir / "learning" / "online_evaluation_shadow_canary.json"),
        summary=_read_json_or_empty(output_dir / "summary.json"),
    )
    errs = validate_regression_testing_surface_dict(payload)
    if errs:
        raise ValueError(f"regression_testing_surface_contract:{','.join(errs)}")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "learning" / "regression_testing_surface.json", payload)
    return payload
