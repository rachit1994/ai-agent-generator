# SDE run config defaults

**In plain words:** quick **defaults** for models, URLs, timeouts, and token caps — the numbers people copy when reproducing runs. The list under **Per-run artifacts** tells you **which files** should appear under **`outputs/runs/<run-id>/`** for a normal run.

- provider: `ollama`
- implementation model: `qwen3:14b`
- support model: `gemma 4`
- provider base URL: `http://127.0.0.1:11434`

## Budgets

- planner timeout per call: `30000 ms`
- verifier timeout per call: `30000 ms`
- executor timeout per call: `90000 ms`
- retry cap per task: `1`
- token budget per task: `4096`

## Per-run artifacts (written under `outputs/runs/<run-id>/`)

Runs resolve the `outputs/` directory by walking up from the current working directory until a `pyproject.toml` is found (repo root), so artifacts land in **repository-root** `outputs/` even when the CLI is launched from `src/orchestrator/runtime/` (or any subdirectory). Override with env **`SDE_OUTPUTS_ROOT`** (absolute path to the `outputs` directory that will contain `runs/`).

- `run-manifest.json`: written at the start of **`sde run`** (task text, mode, schema) for audit and `sde replay --rerun`
- `benchmark-manifest.json`: written at the start of **`sde benchmark`** (suite path, task list slice, flags)
- `benchmark-checkpoint.json`: updated after each task during a benchmark (and marked `finished` when the suite completes); used by **`sde benchmark --resume-run-id …`**
- `traces.jsonl`, `run.log`, `orchestration.jsonl`: trace and narrative streams
- `summary.json`, `report.md`, `review.json`, `token_context.json`: metrics, human report, CTO review, token accounting
- `static_gates_report.json`: local **AST + security patterns + optional `ruff` / `bandit` / `basedpyright` or `pyright`** (when those binaries are on `PATH`); feeds verifier and **HS04**
- `trajectory.html` (optional): written by `sde replay --run-id … --write-html` (or print HTML with `--format html`)
- `answer.txt`: the raw `answer` string emitted by the mode
- `generated_script.py`: extracted Python code when present
- `planner_doc.md`: planner document (guarded_pipeline)
- `executor_prompt.txt`: executor prompt produced by planner (guarded_pipeline)
- `verifier_report.json`: verifier result, issues, and embedded **`static_gates`** snapshot (guarded_pipeline)

See also **[`core-features-and-upstream-parity.md`](core-features-and-upstream-parity.md)** for feature status vs upstream harnesses.

## API Fallback Trigger Rules

1. Structured-output validity drops below 85% after stabilization.
2. Guarded pass rate remains below baseline after two iterations with model-quality evidence.
3. Local median latency is impractical for the local SDE runtime.
4. If fallback is used, rerun full A/B and document provider/model/reason in report output.
