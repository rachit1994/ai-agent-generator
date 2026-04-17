"""On successful JSON parse: answer files, outputs dir, first summary, first report."""

from __future__ import annotations

from pathlib import Path

from sde_pipeline.config import DEFAULT_CONFIG, config_snapshot
from sde_foundations.artifacts import extract_python_code
from sde_foundations.eval import aggregate_metrics
from sde_pipeline.report import generate_report
from sde_foundations.storage import append_jsonl, ensure_dir, write_json

from .artifacts import harvest_pipeline_artifacts


def write_success_artifact_layer(
    *,
    parsed: dict,
    events: list[dict],
    output_dir: Path,
    run_id: str,
    mode: str,
    orchestration: Path,
) -> dict[str, str]:
    """Persist answer, optional script, pipeline harvest, outputs manifest, run_end, config, summary v1."""
    answer_text = str(parsed.get("answer", ""))
    (output_dir / "answer.txt").write_text(answer_text, encoding="utf-8")
    code = extract_python_code(answer_text)
    artifacts: dict[str, str] = {"answer_txt": str(output_dir / "answer.txt")}
    if code:
        script_path = output_dir / "generated_script.py"
        script_path.write_text(code + "\n", encoding="utf-8")
        artifacts["generated_script_py"] = str(script_path)
    artifacts.update(harvest_pipeline_artifacts(events, output_dir))
    outputs_sub = output_dir / "outputs"
    ensure_dir(outputs_sub)
    (outputs_sub / "README.txt").write_text(
        "SDE run outputs: generated artifacts and extracted files land here.\n",
        encoding="utf-8",
    )
    write_json(
        outputs_sub / "manifest.json",
        {"run_id": run_id, "mode": mode, "artifacts": list(artifacts.keys())},
    )
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
    metrics = aggregate_metrics(events)
    write_json(
        output_dir / "summary.json",
        {
            "runId": run_id,
            "mode": mode,
            "runStatus": "ok",
            "provider": DEFAULT_CONFIG.provider,
            "model": DEFAULT_CONFIG.implementation_model,
            "metrics": metrics,
        },
    )
    generate_report(run_id)
    return artifacts
