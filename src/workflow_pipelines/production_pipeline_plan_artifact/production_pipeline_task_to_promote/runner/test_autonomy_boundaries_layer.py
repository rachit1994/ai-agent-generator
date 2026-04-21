from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.autonomy_boundaries_layer import (
    write_autonomy_boundaries_artifact,
)


def _token_context() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "run_id": "rid",
        "model_context_limit": 64,
        "stages": [],
        "context_policy": {"priority": ["a"], "version_hash": "hash"},
        "reductions": [],
        "truncation_events": [],
        "autonomy_anchor_at": "2030-01-01T00:00:00+00:00",
        "context_expires_at": "2030-01-01T00:01:00+00:00",
        "context_ttl_seconds": 60,
    }


def test_runner_layer_writes_autonomy_artifact(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    payload = write_autonomy_boundaries_artifact(
        output_dir=output_dir,
        run_id="rid",
        token_context=_token_context(),
        now_utc=datetime(2030, 1, 1, 0, 0, tzinfo=timezone.utc),
    )
    assert payload["schema"] == "sde.autonomy_boundaries_tokens_expiry.v1"
    written = json.loads((output_dir / "safety" / "autonomy_boundaries_tokens_expiry.json").read_text(encoding="utf-8"))
    assert written["evidence"]["token_context_ref"] == "token_context.json"


def test_runner_layer_fails_on_contract_invalid_payload(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="autonomy_boundaries_contract:"):
        write_autonomy_boundaries_artifact(
            output_dir=tmp_path / "run",
            run_id="rid",
            token_context={"run_id": "rid", "stages": []},
            now_utc=datetime(2030, 1, 1, 0, 0, tzinfo=timezone.utc),
        )


def test_runner_layer_fails_on_run_id_mismatch(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="autonomy_boundaries_run_id_mismatch"):
        write_autonomy_boundaries_artifact(
            output_dir=tmp_path / "run",
            run_id="rid-other",
            token_context=_token_context(),
            now_utc=datetime(2030, 1, 1, 0, 0, tzinfo=timezone.utc),
        )
