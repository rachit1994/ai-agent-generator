from __future__ import annotations

from pathlib import Path

from agent_mvp.config import DEFAULT_CONFIG, config_snapshot
from agent_mvp.eval import aggregate_metrics
from agent_mvp.modes.baseline import run_baseline
from agent_mvp.modes.guarded import run_guarded
from agent_mvp.storage import append_jsonl, ensure_dir, write_json
from agent_mvp.utils import create_run_id


def execute_single_task(task: str, mode: str) -> dict:
    run_id = create_run_id()
    output_dir = Path("outputs") / "runs" / run_id
    ensure_dir(output_dir)
    if mode == "baseline":
        output, events = run_baseline(run_id, "manual-task", task, DEFAULT_CONFIG)
    else:
        output, events = run_guarded(run_id, "manual-task", task, DEFAULT_CONFIG)
    traces = output_dir / "traces.jsonl"
    for event in events:
        append_jsonl(traces, event)
    write_json(output_dir / "config-snapshot.json", config_snapshot())
    write_json(
        output_dir / "summary.json",
        {
            "runId": run_id,
            "mode": mode,
            "provider": DEFAULT_CONFIG.provider,
            "model": DEFAULT_CONFIG.implementation_model,
            "metrics": aggregate_metrics(events),
        },
    )
    return {"run_id": run_id, "output": output}
