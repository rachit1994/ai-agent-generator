"""Write traces.jsonl and orchestration.jsonl stage stream."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.config import DEFAULT_CONFIG
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.run_logging import log_trace_narrative
from workflow_pipelines.orchestration_run_start.orchestration_run_start_contract import (
    validate_orchestration_run_start_dict,
)
from workflow_pipelines.orchestration_stage_event.orchestration_stage_event_contract import (
    validate_orchestration_stage_event_line_dict,
)
from workflow_pipelines.traces_jsonl.traces_jsonl_event_contract import (
    validate_traces_jsonl_event_dict,
)
from production_architecture.storage.storage.storage import append_jsonl


def persist_traces(output_dir: Path, events: list[dict], run_logger: Any) -> None:
    traces = output_dir / "traces.jsonl"
    for event in events:
        ev_errs = validate_traces_jsonl_event_dict(event)
        if ev_errs:
            raise ValueError(f"traces_jsonl_event_contract:{','.join(ev_errs)}")
        append_jsonl(traces, event)
        log_trace_narrative(run_logger, event)


def append_orchestration_run_start(orchestration: Path, run_id: str, mode: str) -> None:
    body = {
        "run_id": run_id,
        "type": "run_start",
        "mode": mode,
        "provider": DEFAULT_CONFIG.provider,
        "model": DEFAULT_CONFIG.implementation_model,
    }
    errs = validate_orchestration_run_start_dict(body)
    if errs:
        raise ValueError(f"orchestration_run_start_contract:{','.join(errs)}")
    append_jsonl(orchestration, body)


def append_orchestration_stage_events(orchestration: Path, run_id: str, events: list[dict]) -> None:
    for event in events:
        meta = event.get("metadata") or {}
        body = {
            "run_id": run_id,
            "type": "stage_event",
            "stage": event.get("stage"),
            "retry_count": event.get("retry_count"),
            "errors": event.get("errors"),
            "agent": meta.get("agent"),
            "model": meta.get("model"),
            "model_error": meta.get("model_error"),
            "attempt": meta.get("attempt"),
            "raw_response_excerpt": meta.get("raw_response_excerpt"),
            "started_at": event.get("started_at"),
            "ended_at": event.get("ended_at"),
            "latency_ms": event.get("latency_ms"),
        }
        line_errs = validate_orchestration_stage_event_line_dict(body)
        if line_errs:
            raise ValueError(f"orchestration_stage_event_contract:{','.join(line_errs)}")
        append_jsonl(orchestration, body)
