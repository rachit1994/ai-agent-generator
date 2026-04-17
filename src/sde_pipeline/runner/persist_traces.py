"""Write traces.jsonl and orchestration.jsonl stage stream."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sde_pipeline.config import DEFAULT_CONFIG
from sde_pipeline.run_logging import log_trace_narrative
from sde_foundations.storage import append_jsonl


def persist_traces(output_dir: Path, events: list[dict], run_logger: Any) -> None:
    traces = output_dir / "traces.jsonl"
    for event in events:
        append_jsonl(traces, event)
        log_trace_narrative(run_logger, event)


def append_orchestration_run_start(orchestration: Path, run_id: str, mode: str) -> None:
    append_jsonl(
        orchestration,
        {
            "run_id": run_id,
            "type": "run_start",
            "mode": mode,
            "provider": DEFAULT_CONFIG.provider,
            "model": DEFAULT_CONFIG.implementation_model,
        },
    )


def append_orchestration_stage_events(orchestration: Path, run_id: str, events: list[dict]) -> None:
    for event in events:
        append_jsonl(
            orchestration,
            {
                "run_id": run_id,
                "type": "stage_event",
                "stage": event.get("stage"),
                "retry_count": event.get("retry_count"),
                "errors": event.get("errors"),
                "agent": (event.get("metadata") or {}).get("agent"),
                "model": (event.get("metadata") or {}).get("model"),
                "model_error": (event.get("metadata") or {}).get("model_error"),
                "attempt": (event.get("metadata") or {}).get("attempt"),
                "raw_response_excerpt": (event.get("metadata") or {}).get("raw_response_excerpt"),
                "started_at": event.get("started_at"),
                "ended_at": event.get("ended_at"),
                "latency_ms": event.get("latency_ms"),
            },
        )
