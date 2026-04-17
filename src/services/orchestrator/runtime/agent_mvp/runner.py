from __future__ import annotations

import json
from pathlib import Path

from agent_mvp.config import DEFAULT_CONFIG, config_snapshot
from agent_mvp.eval import aggregate_metrics
from agent_mvp.artifacts import extract_python_code
from agent_mvp.modes.baseline import run_baseline
from agent_mvp.modes.guarded import run_guarded
from agent_mvp.storage import append_jsonl, ensure_dir, write_json
from agent_mvp.utils import create_run_id


def _harvest_pipeline_artifacts(events: list[dict], output_dir: Path) -> dict[str, str]:
    artifacts: dict[str, str] = {}
    planner_doc = ""
    executor_prompt = ""
    verifier_report: dict | None = None
    for event in events:
        meta = event.get("metadata") or {}
        if isinstance(meta.get("planner_doc"), str) and meta.get("planner_doc"):
            planner_doc = meta["planner_doc"]
        if isinstance(meta.get("executor_prompt"), str) and meta.get("executor_prompt"):
            executor_prompt = meta["executor_prompt"]
        if isinstance(meta.get("verifier_report"), dict):
            verifier_report = meta["verifier_report"]
    if planner_doc:
        doc_path = output_dir / "planner_doc.md"
        doc_path.write_text(planner_doc + "\n", encoding="utf-8")
        artifacts["planner_doc_md"] = str(doc_path)
    if executor_prompt:
        prompt_path = output_dir / "executor_prompt.txt"
        prompt_path.write_text(executor_prompt + "\n", encoding="utf-8")
        artifacts["executor_prompt_txt"] = str(prompt_path)
    if verifier_report is not None:
        report_path = output_dir / "verifier_report.json"
        write_json(report_path, verifier_report)
        artifacts["verifier_report_json"] = str(report_path)
    return artifacts


def execute_single_task(task: str, mode: str) -> dict:
    run_id = create_run_id()
    output_dir = Path("outputs") / "runs" / run_id
    ensure_dir(output_dir)
    orchestration = output_dir / "orchestration.jsonl"
    if mode == "baseline":
        output, events = run_baseline(run_id, "manual-task", task, DEFAULT_CONFIG)
    else:
        output, events = run_guarded(run_id, "manual-task", task, DEFAULT_CONFIG)
    traces = output_dir / "traces.jsonl"
    for event in events:
        append_jsonl(traces, event)
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
    parsed = json.loads(output)
    answer_text = str(parsed.get("answer", ""))
    (output_dir / "answer.txt").write_text(answer_text, encoding="utf-8")
    code = extract_python_code(answer_text)
    artifacts: dict[str, str] = {"answer_txt": str(output_dir / "answer.txt")}
    if code:
        script_path = output_dir / "generated_script.py"
        script_path.write_text(code + "\n", encoding="utf-8")
        artifacts["generated_script_py"] = str(script_path)
    artifacts.update(_harvest_pipeline_artifacts(events, output_dir))
    append_jsonl(
        orchestration,
        {
            "run_id": run_id,
            "type": "run_end",
            "artifacts": artifacts,
            "output_refusal": parsed.get("refusal"),
            "checks": parsed.get("checks"),
        },
    )
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
    return {"run_id": run_id, "output": output, "output_dir": str(output_dir)}
