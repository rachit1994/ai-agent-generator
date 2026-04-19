# SDE baseline overview (single source of truth)

**Reading path:** this file is **required** — see **[`../ESSENTIAL.md`](../ESSENTIAL.md)** (it lists this doc first).

**In plain words:** this file is the **ground truth for the current local tool** (`sde`): what machines and models we assumed, which **commands** exist, and what “baseline vs guarded pipeline” means. It is **shorter and more concrete** than the long architecture docs — read it first if you just need to **run** the CLI. For **where each command lives in Python**, see **[`../../src/orchestrator/api/README.md`](../../src/orchestrator/api/README.md)** and **`../../src/orchestrator/runtime/cli/main.py`** (from repo root: `src/orchestrator/...`).

## Goal

Build a local CLI SDE baseline that tests whether guardrails + a staged execution
pipeline improve outcomes versus a plain one-shot baseline.

**Product trajectory (north star):** SDE grows into the **single orchestrator** that drives **full-stack product delivery** the way a small company would: **parallel junior-class agents**, mandatory **reviews and verification**, **governed self-learning**, and **gates that support reliable production pushes**. Older **V1–V7** Markdown specs were **removed**; the roadmap story lives in [../onboarding/action-plan.md](../onboarding/action-plan.md), and **what actually runs** is this repo’s **Python + SDE docs**. See [../architecture/architecture-goal-completion.md](../architecture/architecture-goal-completion.md) for “how much of the master doc this repo claims.”

Implementation language/runtime:
- Python 3 CLI (installable import package **`orchestrator`** under `src/orchestrator/`; wheel / CLI names remain **`sde`** / **`agent`** per `pyproject.toml`). **Supported floor:** **Python 3.11** (what **GitHub Actions** runs in `.github/workflows/ci.yml` after `uv sync`); keep `src/` syntax and types compatible with 3.11 unless you intentionally raise the CI pin.

## Timebox And Environment

- Timebox: 2 days.
- Machine constraints:
  - OS: macOS 26.3.1 (Darwin 25.3.0)
  - CPU: Apple M1 (8 cores)
  - RAM: 16 GB
  - Disk available: ~29 GiB

## Model Strategy

- Primary runtime: local `ollama` (no API token required).
- **Qwen line:** defaults use **Qwen3** on Ollama ([library `qwen3`](https://ollama.com/library/qwen3)). SDE pins **`qwen3:14b`** in `RunConfig`; use smaller tags (`qwen3:8b`, `qwen3:4b`, …) or **`qwen2.5:*-instruct`** only if you explicitly choose them in config. **Without editing code**, you can override tags and base URL via environment variables read at process start: **`SDE_IMPLEMENTATION_MODEL`**, **`SDE_SUPPORT_MODEL`**, **`SDE_OLLAMA_URL`** (see `src/sde_pipeline/config.py`).
- Implementation model: `qwen3:14b` (all coding/execution agents).
- Non-implementation model: `gemma 4` (planning/review/research/support agents).
- Optional local alternate for implementation: `llama3.1:8b-instruct`.
- API fallback: allowed only when documented triggers fire.

## Agent Role Model Assignment

- Use `qwen3:14b` for implementation-critical tasks:
  - writing/refactoring code
  - test authoring and fixes
  - benchmark execution and artifact generation
- Use `gemma 4` for non-implementation tasks:
  - planning and breakdown
  - checklist tracking
  - review summaries and documentation polish
  - analysis and risk enumeration

Fallback triggers:
1. Guarded structured-output validity < 85% after stabilization.
2. Guarded pass rate remains below baseline after two iterations with clear
   model-quality failures.
3. Local median latency is impractical for local SDE execution.

If fallback is used, rerun full A/B and document provider/model/reason in
`report.md`.

## Product Surface

CLI commands:
- `sde run --task "..." --mode baseline|guarded_pipeline|phased_pipeline` (optional **`--repeat N`**: same task and mode **N** times, each under a fresh `outputs/runs/<run-id>/` — V1 **RepeatProfile**); successful parses also emit **V4** lineage, **V5** memory, **V6** evolution, and **V7** org stubs under the run directory (replay manifest, event envelope, memory retrieval, reflection + canary, leases + IAM audit, shard map, strategy proposal) unless you mark the run **`coding_only`** in `summary.json`, which skips extended hard-stops **HS17+** (see **`src/sde_gates/hard_stops_*.py`** and pipeline **`src/sde_pipeline/runner/*_layer.py`**).
- `sde benchmark --suite ./data/benchmark-tasks.jsonl` (optional `--max-tasks N`, `--continue-on-error`, **`--resume-run-id <run_id>`** to continue under `outputs/runs/<run_id>`; `--suite` optional on resume but must match the manifest if provided)
- `sde report --run-id <id>`
- `sde replay --run-id <id>` (optional `--format json|html`, `--write-html` to save `trajectory.html` in the run dir, `--rerun` for single-task re-execution from `run-manifest.json`)
- `sde validate --run-id <id>` (optional `--mode` to override manifest): prints JSON and exits **0** when validation passes (CI-friendly). **Single-task** runs (`run-manifest.json`): exit **0** iff `ok` and `validation_ready`. **Benchmark aggregate** runs (`benchmark-manifest.json` only, no run manifest): light integrity check (`manifest` + finished `benchmark-checkpoint.json` + `summary.json` verdict + `traces.jsonl`); response includes `run_kind: benchmark_aggregate` and `execution_gates_applied: false`, and the CLI exits **0** iff `ok` (CTO ladder not applicable). If only `benchmark-manifest.json` exists and its mode is `both`, pass `--mode baseline` or `--mode guarded_pipeline`.
- `sde roadmap-review` (optional `--repo-root`, repeatable `--context-file`, `--append-learning [path]`): sends excerpted SDE docs to **support_model** (default **Gemma** in `RunConfig`) and prints JSON with `per_version_pct` (V1–V7), `overall_pct`, `code_quality_0_100`, `done`, `remaining`, `learning_note`. Exit **0** on parse success, **2** on model/parse failure. Does **not** auto-complete the product; it externalizes the “Gemma reviews % complete” step you asked for.
- `sde evolve` (optional `--max-rounds`, `--target-pct`, `--task`, `--mode`, `--learning-path`, `--verbose`, `--print-task-result`): bounded loop — each round runs `roadmap_review`, appends a line to a JSONL learning file (default `.agent/sde/learning_events.jsonl`), optionally runs `execute_single_task` for a fixed task string, then stops when `overall_pct >= target-pct` or rounds exhaust (exit **1** if target never met). **Cannot** honestly guarantee “all seven versions fullest”; use it as a cadence tool with Ollama running.
- `sde continuous --task "..."` (optional `--mode`, **`--max-iterations`**, **`--stop-when`** `validation_ready` \| `definition_of_done` \| `never`, **`--continue-on-pipeline-error`**): repeats `execute_single_task` with the **same** task string until the stop condition hits or the iteration cap is reached (each attempt is still a fresh `outputs/runs/<id>/`). Default stop is **`validation_ready`** (strict re-validate after every run). Use **`never`** with a large `--max-iterations` when you want a fixed number of back-to-back runs without an automatic “repo complete” detector (there is no machine oracle for “entire repo built”; encode completion in tests/gates or in the task prompt).
- `sde continuous (--project-session-dir <dir> | --project-plan <path/to/project_plan.json>)` (optional **`--progress-file`**, **`--parallel-worktrees`**, **`--lease-stale-sec`**, **`--repo-root`**, **`--enforce-plan-lock`**, **`--require-non-stub-reviewer`**, …; **`--task`** optional when a project flag is set): drives the **project session** — **`--max-iterations`** caps **plan steps**. **`--enforce-plan-lock`** runs Stage 1 lock-readiness before steps; **`--require-non-stub-reviewer`** only applies with **`--enforce-plan-lock`**. See **[`project-driver.md`](project-driver.md)** (Stage 1 section) and **[`../runbooks/stage1-intake-failures.md`](../runbooks/stage1-intake-failures.md)**.
- `sde project run (--session-dir <dir> | --plan <path/to/project_plan.json>)` (optional **`--repo-root`**, **`--max-steps`**, **`--mode`**, **`--max-concurrent-agents`**, **`--progress-file`**, **`--parallel-worktrees`**, **`--lease-stale-sec`**, **`--enforce-plan-lock`**, **`--require-non-stub-reviewer`**): meta-orchestrator — bounded context per step (when **`intake/`** exists, each step’s context pack includes discovery, **`doc_review.json`**, **`research_digest.md`**, and a capped tail of **`question_workbook.jsonl`**), per-step shell verification, honest **`driver_state.json`** / **`stop_report.json`** terminal status. Same plan-lock / strict-reviewer pairing as **`continuous`** above.
- Other **`sde project`** subcommands: **`validate`** (read-only plan + workspace preflight; optional **`--require-plan-lock`**, **`--require-non-stub-reviewer`**, **`--skip-workspace`**); **`status`** (read-only JSON snapshot; **`session_events`** block includes **`intake_lineage_manifest_*`** when **`intake/lineage_manifest.json`** exists); **`plan-lock`** (write **`project_plan_lock.json`** or **`--check-only`** readiness); **`intake-revise`** (bounded revise loop); **`export-stage1-observability`** (writes **`intake/stage1_observability_export.json`**: **`revise_metrics`** + **`status_at_a_glance`** for CI/operators). Optional env **`SDE_REQUIRE_NON_STUB_REVIEWER`** applies strict reviewer rules on supported commands when plan-lock enforcement is active (CLI-only; details in **[`project-driver.md`](project-driver.md)**). **End-to-end Stage 1 CLI demo (scaffold → plan file → revise → lock → validate → export):** **`./scripts/stage1-cold-start-demo.sh`** from repo root (see **[`../runbooks/stage1-intake-failures.md`](../runbooks/stage1-intake-failures.md)** §Golden cold start). **S1a policy (attestation + model revise scope):** **[`../adrs/`](../adrs/)** ADRs **0001** and **0002**.
- `sde project scaffold-intake --session-dir <dir> --goal "..."` (optional **`--repo-label`**): writes **`intake/`** stubs (`discovery.json`, `research_digest.md`, `doc_review.json`, `question_workbook.jsonl`, `README.txt`) for Stage 1 doc alignment; **does not** create or edit `project_plan.json`. Exit **0** on success, **2** if the directory is missing, not a directory, or the goal is empty.

Modes:
- `baseline`: `task -> model -> output`
- `guarded_pipeline`: `planner_doc -> planner_prompt -> executor -> verifier -> executor_fix(optional, max 1) -> verifier_fix(optional) -> finalize` — on a **non–safety-refusal** success path the run directory also gets a **V3 harness** slice: `program/` (plan, progress, V2-style stubs), `step_reviews/*.json`, `verification_bundle.json`, and `review.json` → `definition_of_done`; balanced gates include **HS07–HS16** for this mode.
- `phased_pipeline`: **decompose → repeat guarded_pipeline per atomic todo**. The support model emits a JSON phased plan (`phased_decompose` stage); each todo then runs the full **guarded** planner → executor → verifier cycle with a scoped prompt (overall goal + todo title + acceptance). Traces merge into one run (sub-finalize events are dropped; one aggregate `finalize`). Writes `program/phased_plan.json` and the same V3 completion harness / CTO gates as `guarded_pipeline`.

## Required Guardrails

1. Input validation (non-empty + schema-valid task payload).
2. Output schema validation (fail closed on malformed outputs).
3. Retry cap (maximum one repair retry).
4. Timeout cap (per-task execution limit).
5. Token cap (per-task token budget).
6. Refusal policy for unsafe/invalid actions with machine-readable reason.
7. **Static code gates** (local, no sandbox): `static_gates_report.json` on successful runs — Python `ast` parse, high-signal dangerous patterns (e.g. `eval`, `subprocess`…`shell=True`), optional `ruff check` when `ruff` is on `PATH`. Failures surface in the verifier and in **HS04** (see **`src/sde_gates/static_analysis.py`** and **`src/sde_gates/hard_stops.py`**).

## Minimal Architecture

Components:
1. CLI entrypoint + command parser
2. Runner
3. Mode implementations (`baseline`, `guarded_pipeline`)
4. Guardrails
5. Model adapter (`ollama` default, `api` optional fallback)
6. Evaluator
7. Storage (`traces.jsonl`, `summary.json`)
8. Reporter (`report.md`)

Suggested code layout:

```text
src/
  orchestrator/
    api/
    runtime/
      cli/
    tests/
      unit/
  sde_pipeline/
    runner/
    benchmark/
    replay.py
    config.py
    report.py
    run_logging.py
  sde_modes/
    modes/
  sde_gates/
    static_analysis.py
  sde_foundations/
data/
  benchmark-tasks.jsonl
outputs/
  runs/<run-id>/
    traces.jsonl
    summary.json
    report.md
    run.log
    orchestration.jsonl
    run-manifest.json              # sde run
    benchmark-manifest.json        # sde benchmark (that run id)
    benchmark-checkpoint.json      # sde benchmark progress / resume
    trajectory.html                # optional: sde replay --write-html
    review.json
    token_context.json
    static_gates_report.json
    answer.txt
    generated_script.py
    planner_doc.md
    executor_prompt.txt
    verifier_report.json
```

## Core features status (after pull)

For a **maintainer-facing** table of what is implemented vs SWE-agent / OpenHands–class patterns (and what is intentionally out of scope for local CLI), see **[`core-features-and-upstream-parity.md`](core-features-and-upstream-parity.md)**.

## Experiment And Verdict Rules

Task suite:
- 10-30 tasks
- includes simple, medium, and failure-prone tasks
- each row has `task_id`, `prompt`, `expected_checks`, `difficulty`

Primary metrics:
- pass rate
- reliability score

Secondary metrics:
- p50/p95 latency
- estimated cost per task
- retry frequency
- structured-output validity rate

Verdict:
- `supported` if pass-rate delta >= 10 points AND reliability improves AND
  median latency degradation <= 30%
- `partially supported` if pass improves but latency/cost degrade materially
- otherwise `rejected` or `inconclusive`

## Required Test Coverage

1. Guardrail unit tests (pass/fail cases for all guardrails).
2. Pipeline integration tests (stage order and trace emission).
3. Benchmark parity tests (same suite/settings/provider per pass).
4. Artifact integrity tests (`traces.jsonl`, `summary.json`, `report.md`).
5. Verdict logic tests (threshold branches).

## In Scope

- Local CLI SDE baseline only.
- A/B benchmark and report generation.
- Traceability and measurable verdict.
- Session meta-orchestrator (**`sde project`** and project-mode **`sde continuous`**) over a disk-backed **`project_plan.json`**; Stage 1 intake + plan-lock flags and env semantics are documented in **[`project-driver.md`](project-driver.md)** (Stage 1 section) and **[`../runbooks/stage1-intake-failures.md`](../runbooks/stage1-intake-failures.md)**.

## Out Of Scope

This section lists what the **baseline SDE release described in this document** does not yet implement. Those capabilities are **in scope for the program** under [../onboarding/action-plan.md](../onboarding/action-plan.md)—not abandoned.

- Multi-agent lifecycle systems (organization harness stubs under `outputs/`; gates in **`src/sde_gates/hard_stops_organization.py`**).
- Distributed/event-sourced production architecture (event lineage under **`src/sde_pipeline/runner/event_lineage_layer.py`**; gates **`src/sde_gates/hard_stops_events.py`**).
- Cloud deployment and scaling (optional; `local-prod` remains the production profile per master doc).
- UI/dashboard work.
- Production-grade org authz/policy systems (see V7).

## Definition Of Done

1. `sde run` succeeds and returns run id.
2. `sde benchmark` runs both modes on same suite.
3. Required artifacts are written per run.
4. `sde report` emits clear verdict and recommendation.
5. Entire flow runs locally within machine constraints.
6. When you rely on **Stage 1** intake + plan lock for a session directory, **`sde project validate --require-plan-lock`** (and optional **`sde project run` / `sde continuous` + `--enforce-plan-lock`**) match the policy you document for operators — see **[`project-driver.md`](project-driver.md)** and **[`../runbooks/stage1-intake-failures.md`](../runbooks/stage1-intake-failures.md)**.
