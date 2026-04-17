# SDE run config defaults

- provider: `ollama`
- implementation model: `qwen2.5:7b-instruct`
- support model: `gemma 4`
- provider base URL: `http://127.0.0.1:11434`

## Budgets

- planner timeout per call: `30000 ms`
- verifier timeout per call: `30000 ms`
- executor timeout per call: `90000 ms`
- retry cap per task: `1`
- token budget per task: `4096`

## Per-run artifacts (written under `outputs/runs/<run-id>/`)

Runs resolve the `outputs/` directory by walking up from the current working directory until a `pyproject.toml` is found (repo root), so artifacts land in **repository-root** `outputs/` even when the CLI is launched from `src/services/orchestrator/runtime/`. Override with env **`SDE_OUTPUTS_ROOT`** (absolute path to the `outputs` directory that will contain `runs/`).

- `orchestration.jsonl`: stage-by-stage log (agent name/type/role, attempts, retries, errors, excerpts)
- `answer.txt`: the raw `answer` string emitted by the mode
- `generated_script.py`: extracted Python code when present
- `planner_doc.md`: planner document (guarded_pipeline)
- `executor_prompt.txt`: executor prompt produced by planner (guarded_pipeline)
- `verifier_report.json`: verifier result and issues (guarded_pipeline)

## API Fallback Trigger Rules

1. Structured-output validity drops below 85% after stabilization.
2. Guarded pass rate remains below baseline after two iterations with model-quality evidence.
3. Local median latency is impractical for the local SDE runtime.
4. If fallback is used, rerun full A/B and document provider/model/reason in report output.
