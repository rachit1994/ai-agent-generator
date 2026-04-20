"""Trace helpers for guarded pipeline stages."""

from __future__ import annotations

import time
from typing import Any

from sde_types.types import Score, TraceEvent
from common.utils import ms_to_iso


def _stage(
    run_id: str,
    task_id: str,
    stage: str,
    config: Any,
    *,
    retry_count: int,
    attempt: int | None = None,
    started_ms: int | None = None,
    ended_ms: int | None = None,
    passed: bool = True,
    errors: list[str] | None = None,
    metadata: dict | None = None,
) -> dict:
    """Build one ``TraceEvent`` dict for a pipeline stage."""
    started_epoch_ms = int(time.time() * 1000) if started_ms is None else started_ms
    ended_epoch_ms = started_epoch_ms if ended_ms is None else ended_ms
    return TraceEvent(
        run_id=run_id,
        task_id=task_id,
        mode="guarded_pipeline",
        model=config.implementation_model,
        provider=config.provider,
        stage=stage,
        started_at=ms_to_iso(started_epoch_ms),
        ended_at=ms_to_iso(ended_epoch_ms),
        latency_ms=ended_epoch_ms - started_epoch_ms,
        token_input=0,
        token_output=0,
        estimated_cost_usd=0,
        retry_count=retry_count,
        errors=errors or [],
        score=Score(passed=passed, reliability=1.0 if passed else 0.0, validity=1.0),
        metadata={**({"attempt": attempt} if attempt is not None else {}), **(metadata or {})},
    ).to_dict()


def _skipped_stage(run_id: str, task_id: str, stage: str, config: Any, *, agent_name: str) -> dict:
    """Emit a synthetic stage when upstream refusal skips work."""
    return _stage(
        run_id,
        task_id,
        stage,
        config,
        retry_count=0,
        attempt=0,
        passed=False,
        errors=["skipped_due_to_refusal"],
        metadata={"agent": {"name": agent_name, "type": "system", "role": stage}},
    )
