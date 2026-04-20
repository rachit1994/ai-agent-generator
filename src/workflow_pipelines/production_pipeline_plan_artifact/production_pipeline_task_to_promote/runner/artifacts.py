"""Write guarded_pipeline-derived files from trace metadata."""

from __future__ import annotations

from pathlib import Path

from production_architecture.storage.storage.storage import write_json


def harvest_pipeline_artifacts(events: list[dict], output_dir: Path) -> dict[str, str]:
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
