# Understanding the code (CLI, layout, contracts)

This repository keeps **exactly four** Markdown files under `docs/`:

| File | Purpose |
|------|---------|
| [`AI-Professional-Evolution-Master-Architecture.md`](AI-Professional-Evolution-Master-Architecture.md) | **Source of truth** — full platform blueprint. |
| **This file** | How to run and change the **Python `sde` tool** (`src/`, CLI, artifacts, project sessions). |
| [`RESEARCH.md`](RESEARCH.md) | External papers and library notes (never overrides gates). |
| [`architecture/master-architecture-feature-completion.md`](architecture/master-architecture-feature-completion.md) | Master doc → `% complete` map for this repo. |

**Fast path:** read §1–2 below, then open [`docs/architecture/repository-layout-from-completion-inventory.md`](architecture/repository-layout-from-completion-inventory.md), [`libs/README.md`](../libs/README.md), [`src/workflow_pipelines/README.md`](../src/workflow_pipelines/README.md), [`src/guardrails_and_safety/README.md`](../src/guardrails_and_safety/README.md), `src/production_architecture_what_runs_on_the_laptop/orchestrator/api/README.md`, and `src/production_architecture_what_runs_on_the_laptop/orchestrator/runtime/cli/main.py`.

---

## 1 — Where the code lives

| Order | Path | Why |
|-------|------|-----|
| 1 | [`repository-layout-from-completion-inventory.md`](architecture/repository-layout-from-completion-inventory.md) | Target `src/<section>/<row>/` map (orchestrator, workflow_pipelines, guardrails, libs). |
| 2 | [`libs/README.md`](../libs/README.md) | Repo-root **`libs/`** packages and import boundaries. |
| 3 | [`src/workflow_pipelines/README.md`](../src/workflow_pipelines/README.md) | Runner vs **`execution_modes`** split at a glance. |
| 4 | [`src/guardrails_and_safety/README.md`](../src/guardrails_and_safety/README.md) | Gates folders + **`libs/`** shared pieces. |
| 5 | [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/README.md`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/README.md) | Public `orchestrator.api` surface. |
| 6 | [`src/production_architecture_what_runs_on_the_laptop/orchestrator/runtime/cli/main.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/runtime/cli/main.py) | CLI arguments → API calls. |

```text
src/
├── production_architecture_what_runs_on_the_laptop/orchestrator/   # CLI + orchestrator.api
├── workflow_pipelines/production_pipeline_task_to_promote/        # runner, benchmark, replay
├── workflow_pipelines/execution_modes/                            # baseline / guarded / phased modes
├── guardrails_and_safety/                                         # gates (risk_budgets, review_gating, …)
└── (repo root) libs/                                              # storage, types, gates_constants, …
```

Runs write under repo-root **`outputs/`** (often gitignored).

---

## 2 — When you change contracts or gates

| You change… | Open |
|-------------|------|
| Filenames under a run dir, pipeline stages, required artifacts | **§ Implementation contract** below |
| CTO gates, hard-stops **HS01+**, `validate_execution_run_directory` | `src/guardrails_and_safety/review_gating/run_directory.py`, `src/guardrails_and_safety/risk_budgets/hard_stops*.py` + `static_analysis.py`, plus tests under `src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/` |

---

## 3 — Check before you push

```bash
uv sync --group dev
uv run pytest src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit -q
```

From repo root, **`uv run pytest`** (per `pyproject.toml` **`testpaths`**) also runs **`tests/`** (e.g. **`test_version_bump.py`**). The **architecture** doc’s **`test_*.py`** file-count snapshot (**68** under **`orchestrator/tests/`** + **1** under **`tests/`**) and the layout inventory **Part A** **`src/`**+**`libs/`** **`.py`/`.md`** path count (**215**) are enforced in CI by **`test_architecture_test_file_inventory.py`**; the human-readable tables live in **[`architecture/master-architecture-feature-completion.md`](architecture/master-architecture-feature-completion.md)** and **[`architecture/repository-layout-from-completion-inventory.md`](architecture/repository-layout-from-completion-inventory.md)**.

Repo-root **`.python-version`** pins **3.11** (same as CI).

---

## SDE baseline (`what.md`)

# SDE baseline overview (single source of truth)

**In plain words:** this file is the **ground truth for the current local tool** (`sde`): what machines and models we assumed, which **commands** exist, and what “baseline vs guarded pipeline” means. It is **shorter and more concrete** than the long architecture docs — read it first if you just need to **run** the CLI. For **where each command lives in Python**, see **[`../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/README.md`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/README.md)** and **`../src/production_architecture_what_runs_on_the_laptop/orchestrator/runtime/cli/main.py`** (from repo root: `src/production_architecture_what_runs_on_the_laptop/orchestrator/...`).

## Goal

Build a local CLI SDE baseline that tests whether guardrails + a staged execution
pipeline improve outcomes versus a plain one-shot baseline.

**Product trajectory (north star):** SDE grows into the **single orchestrator** that drives **full-stack product delivery** the way a small company would: **parallel junior-class agents**, mandatory **reviews and verification**, **governed self-learning**, and **gates that support reliable production pushes**. Older **V1–V7** Markdown specs were **removed**; the roadmap story lives in [`AI-Professional-Evolution-Master-Architecture.md`](AI-Professional-Evolution-Master-Architecture.md) (product story lives in master §2 / §17), and **what actually runs** is this repo’s **Python + SDE docs**. See [`architecture/master-architecture-feature-completion.md`](architecture/master-architecture-feature-completion.md) for “how much of the master doc this repo claims.”

Implementation language/runtime:
- Python 3 CLI (installable import package **`orchestrator`** under `src/production_architecture_what_runs_on_the_laptop/orchestrator/`; wheel / CLI names remain **`sde`** / **`agent`** per `pyproject.toml`). **Supported floor:** **Python 3.11** (what **GitHub Actions** runs in `.github/workflows/ci.yml` after `uv sync`). Repo-root **`.python-version`** is **`3.11`** so **`uv`** picks the same interpreter locally; keep `src/` syntax and types compatible with 3.11 unless you intentionally raise the CI pin and this file.

## Timebox And Environment

- Timebox: 2 days.
- Machine constraints:
  - OS: macOS 26.3.1 (Darwin 25.3.0)
  - CPU: Apple M1 (8 cores)
  - RAM: 16 GB
  - Disk available: ~29 GiB

## Model Strategy

- Primary runtime: local `ollama` (no API token required).
- **Qwen line:** defaults use **Qwen3** on Ollama ([library `qwen3`](https://ollama.com/library/qwen3)). SDE pins **`qwen3:14b`** in `RunConfig`; use smaller tags (`qwen3:8b`, `qwen3:4b`, …) or **`qwen2.5:*-instruct`** only if you explicitly choose them in config. **Without editing code**, you can override tags and base URL via environment variables read at process start: **`SDE_IMPLEMENTATION_MODEL`**, **`SDE_SUPPORT_MODEL`**, **`SDE_OLLAMA_URL`** (see `src/workflow_pipelines/production_pipeline_task_to_promote/config.py`).
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
- `sde run --task "..." --mode baseline|guarded_pipeline|phased_pipeline` (optional **`--repeat N`**: same task and mode **N** times, each under a fresh `outputs/runs/<run-id>/` — V1 **RepeatProfile**); successful parses also emit **V4** lineage, **V5** memory, **V6** evolution, and **V7** org stubs under the run directory (replay manifest, event envelope, memory retrieval, reflection + canary, leases + IAM audit, shard map, strategy proposal) unless you mark the run **`coding_only`** in `summary.json`, which skips extended hard-stops **HS17+** (see **`src/guardrails_and_safety/risk_budgets/hard_stops_*.py`** and pipeline **`src/workflow_pipelines/production_pipeline_task_to_promote/runner/*_layer.py`**).
- `sde benchmark --suite ./data/medium-hard-sde-suite.jsonl` (optional `--max-tasks N`, `--continue-on-error`, **`--resume-run-id <run_id>`** to continue under `outputs/runs/<run_id>`; `--suite` optional on resume but must match the manifest if provided). The repo’s curated rows are **`mh-01`–`mh-05`** (see `src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_medium_hard_sde_suite.py`); use any other JSONL path with the same schema for local suites.
- `sde report --run-id <id>`
- `sde replay --run-id <id>` (optional `--format json|html`, `--write-html` to save `trajectory.html` in the run dir, `--rerun` for single-task re-execution from `run-manifest.json`)
- `sde validate --run-id <id>` (optional `--mode` to override manifest): prints JSON and exits **0** when validation passes (CI-friendly). **Single-task** runs (`run-manifest.json`): exit **0** iff `ok` and `validation_ready`. **Benchmark aggregate** runs (`benchmark-manifest.json` only, no run manifest): light integrity check (`manifest` + finished `benchmark-checkpoint.json` + `summary.json` verdict + `traces.jsonl`); response includes `run_kind: benchmark_aggregate` and `execution_gates_applied: false`, and the CLI exits **0** iff `ok` (CTO ladder not applicable). If only `benchmark-manifest.json` exists and its mode is `both`, pass `--mode baseline` or `--mode guarded_pipeline`.
- `sde roadmap-review` (optional `--repo-root`, repeatable `--context-file`, `--append-learning [path]`): sends excerpted SDE docs to **support_model** (default **Gemma** in `RunConfig`) and prints JSON with `per_version_pct` (V1–V7), `overall_pct`, `code_quality_0_100`, `done`, `remaining`, `learning_note`. Exit **0** on parse success, **2** on model/parse failure. Does **not** auto-complete the product; it externalizes the “Gemma reviews % complete” step you asked for.
- `sde evolve` (optional `--max-rounds`, `--target-pct`, `--task`, `--mode`, `--learning-path`, `--verbose`, `--print-task-result`): bounded loop — each round runs `roadmap_review`, appends a line to a JSONL learning file (default `.agent/sde/learning_events.jsonl`), optionally runs `execute_single_task` for a fixed task string, then stops when `overall_pct >= target-pct` or rounds exhaust (exit **1** if target never met). **Cannot** honestly guarantee “all seven versions fullest”; use it as a cadence tool with Ollama running.
- `sde continuous --task "..."` (optional `--mode`, **`--max-iterations`**, **`--stop-when`** `validation_ready` \| `definition_of_done` \| `never`, **`--continue-on-pipeline-error`**): repeats `execute_single_task` with the **same** task string until the stop condition hits or the iteration cap is reached (each attempt is still a fresh `outputs/runs/<id>/`). Default stop is **`validation_ready`** (strict re-validate after every run). Use **`never`** with a large `--max-iterations` when you want a fixed number of back-to-back runs without an automatic “repo complete” detector (there is no machine oracle for “entire repo built”; encode completion in tests/gates or in the task prompt).
- `sde continuous (--project-session-dir <dir> | --project-plan <path/to/project_plan.json>)` (optional **`--progress-file`**, **`--parallel-worktrees`**, **`--lease-stale-sec`**, **`--repo-root`**, **`--enforce-plan-lock`**, **`--require-non-stub-reviewer`**, …; **`--task`** optional when a project flag is set): drives the **project session** — **`--max-iterations`** caps **plan steps**. **`--enforce-plan-lock`** runs Stage 1 lock-readiness before steps; **`--require-non-stub-reviewer`** only applies with **`--enforce-plan-lock`**. See **[§ Project driver](#project-driver-meta-orchestrator)** (Stage 1 section) and **[§ Stage 1 runbook](#stage-1-intake-operator-runbook)**.
- `sde project run (--session-dir <dir> | --plan <path/to/project_plan.json>)` (optional **`--repo-root`**, **`--max-steps`**, **`--mode`**, **`--max-concurrent-agents`**, **`--progress-file`**, **`--parallel-worktrees`**, **`--lease-stale-sec`**, **`--enforce-plan-lock`**, **`--require-non-stub-reviewer`**): meta-orchestrator — bounded context per step (when **`intake/`** exists, each step’s context pack includes discovery, **`doc_review.json`**, **`research_digest.md`**, and a capped tail of **`question_workbook.jsonl`**), per-step shell verification, honest **`driver_state.json`** / **`stop_report.json`** terminal status. Same plan-lock / strict-reviewer pairing as **`continuous`** above.
- Other **`sde project`** subcommands: **`validate`** (read-only plan + workspace preflight; optional **`--require-plan-lock`**, **`--require-non-stub-reviewer`**, **`--skip-workspace`**); **`status`** (read-only JSON snapshot; **`session_events`** block includes **`intake_lineage_manifest_*`** when **`intake/lineage_manifest.json`** exists); **`plan-lock`** (write **`project_plan_lock.json`** or **`--check-only`** readiness); **`intake-revise`** (bounded revise loop); **`export-stage1-observability`** (writes **`intake/stage1_observability_export.json`**: **`revise_metrics`** + **`status_at_a_glance`** for CI/operators). Optional env **`SDE_REQUIRE_NON_STUB_REVIEWER`** applies strict reviewer rules on supported commands when plan-lock enforcement is active (CLI-only; details in **[§ Project driver](#project-driver-meta-orchestrator)**). **End-to-end Stage 1 CLI demo (scaffold → plan file → revise → lock → validate → export):** **`./scripts/stage1-cold-start-demo.sh`** from repo root (see **[§ Stage 1 runbook](#stage-1-intake-operator-runbook)** §Golden cold start). **S1a policy (attestation + model revise scope):** **ADR policy (historical: S1a reviewer attestation + model revise scope; implementation in `src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_plan_lock.py`)** ADRs **0001** and **0002**.
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
7. **Static code gates** (local, no sandbox): `static_gates_report.json` on successful runs — Python `ast` parse, high-signal dangerous patterns (e.g. `eval`, `subprocess`…`shell=True`), optional `ruff check` when `ruff` is on `PATH`. Failures surface in the verifier and in **HS04** (see **`src/guardrails_and_safety/risk_budgets/static_analysis.py`** and **`src/guardrails_and_safety/risk_budgets/hard_stops.py`**).

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
  production_architecture_what_runs_on_the_laptop/orchestrator/
    api/
    runtime/
      cli/
    tests/
      unit/
  workflow_pipelines/production_pipeline_task_to_promote/
    runner/
    benchmark/
    replay.py
    config.py
    report.py
    run_logging.py
  workflow_pipelines/execution_modes/
    modes/
  guardrails_and_safety/
    risk_budgets/
    review_gating/
    autonomy_boundaries_tokens_expiry/
  libs/
data/
  medium-hard-sde-suite.jsonl
  company-os-progress-rules.json
  company-os-progress-checklist.md
  sde-project-plan.example.json
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
- Session meta-orchestrator (**`sde project`** and project-mode **`sde continuous`**) over a disk-backed **`project_plan.json`**; Stage 1 intake + plan-lock flags and env semantics are documented in **[§ Project driver](#project-driver-meta-orchestrator)** (Stage 1 section) and **[§ Stage 1 runbook](#stage-1-intake-operator-runbook)**.

## Out Of Scope

This section lists what the **baseline SDE release described in this document** does not yet implement. Those capabilities are **in scope for the program** under [`AI-Professional-Evolution-Master-Architecture.md`](AI-Professional-Evolution-Master-Architecture.md) (product story lives in master §2 / §17)—not abandoned.

- Multi-agent lifecycle systems (organization harness stubs under `outputs/`; gates in **`src/guardrails_and_safety/risk_budgets/hard_stops_organization.py`**).
- Distributed/event-sourced production architecture (event lineage under **`src/workflow_pipelines/production_pipeline_task_to_promote/runner/event_lineage_layer.py`**; gates **`src/guardrails_and_safety/risk_budgets/hard_stops_events.py`**).
- Cloud deployment and scaling (optional; `local-prod` remains the production profile per master doc).
- UI/dashboard work.
- Production-grade org authz/policy systems (see V7).

## Definition Of Done

1. `sde run` succeeds and returns run id.
2. `sde benchmark` runs both modes on same suite.
3. Required artifacts are written per run.
4. `sde report` emits clear verdict and recommendation.
5. Entire flow runs locally within machine constraints.
6. When you rely on **Stage 1** intake + plan lock for a session directory, **`sde project validate --require-plan-lock`** (and optional **`sde project run` / `sde continuous` + `--enforce-plan-lock`**) match the policy you document for operators — see **[§ Project driver](#project-driver-meta-orchestrator)** and **[§ Stage 1 runbook](#stage-1-intake-operator-runbook)**.


---

## Implementation contract (`implementation-contract.md`)

# SDE implementation contract

**In plain words:** this is the **checklist of files and stages** a baseline run is expected to produce. Think “**if these files are missing or empty, the run is incomplete**,” not product marketing. For stricter rules (extra artifacts, hard-stops), see **`src/guardrails_and_safety/`** and tests that call **`validate_execution_run_directory`**.

---

## Contract

- Stage 1 on a **session directory** (often with **`intake/`**): optional **`sde project plan-lock`**, **`sde project validate --require-plan-lock`**, **`sde project run`** / **`sde continuous`** with **`--enforce-plan-lock`**, and optional strict reviewer via **`--require-non-stub-reviewer`** or env **`SDE_REQUIRE_NON_STUB_REVIEWER`** (pairing rules in **[§ Project driver](#project-driver-meta-orchestrator)** and **[§ Stage 1 runbook](#stage-1-intake-operator-runbook)**); may write **`project_plan_lock.json`**.
- In scope: local CLI MVP with `run`, `benchmark`, `report`, **`replay`**, **`validate`**, **`project`** (meta-orchestrator: session `project_plan.json` → optional **`workspace`** contract (branch + allowed path prefixes + optional **lease TTL**), **`project validate`** read-only preflight, **`project status`** read-only snapshot (including aggregate / session DoD / ``step_runs`` when present; **Phase 13** byte caps / JSONL tail scan for very large files; **Phase 14** ``context_pack_lineage`` + ``context_packs`` / ``verification`` directory summaries with capped ``step_ids``; **Phase 15** capped ``leases.json`` body + ``_worktrees`` as ``parallel_worktrees``; **Phase 16** ``plan_step_rollups``; **Phase 17** ``step_runs.by_step`` + rollup run pointers when JSONL is small enough to fully scan; **Phase 18** ``repo_snapshot`` when ``repo_root`` is set; **Phase 19–20** ``workspace_status``: plan ``workspace`` echo, branch commit match, and ``allowed_path_prefixes`` vs ``path_scope`` errors; **Phase 21** ``status_at_a_glance`` (compact derived fields + ``red_flags``), **`session_events.jsonl`** on driver runs, per-step `execute_single_task` + orchestrator verification + `progress.json` (optional **`--progress-file`** override) + **`verification_aggregate.json`** + session **`definition_of_done.json`** + terminal **`stop_report.json`** / **`driver_state.json`** exit metadata; optional **`--parallel-worktrees`** when the repo is git and the scheduler picks disjoint-scoped steps; see **[§ Project driver](#project-driver-meta-orchestrator)**), and **`continuous`** (repeat `--task` **or** drive **`--project-session-dir`** / **`--project-plan`** with optional **`--progress-file`** and optional **`--parallel-worktrees`**). **`validate`** re-checks `outputs/runs/<id>/` (**single-task** → manifest + hard-stops, exit **0** when `ok` and `validation_ready`; **benchmark aggregate** → light integrity, exit **0** when `ok`, fields `run_kind` / `execution_gates_applied` in JSON).
- Out of scope: UI, cloud deployment, and production architecture refactors (see also **`what.md`** “Out of scope”).
- Guardrails: input validation, output schema validation, refusal policy, retry cap, timeout cap, token cap, **static code gates** (AST + security patterns + optional `ruff` / `bandit` / `basedpyright` or `pyright` on `PATH`).
- Pipeline stages (sequential, never skipped): `planner_doc -> planner_prompt -> executor -> verifier -> executor_fix(optional, max 1) -> verifier_fix(optional) -> finalize`.
- Required artifacts:
  - per-run traces: `traces.jsonl`, `summary.json`, `report.md`
  - per-run run log: `orchestration.jsonl`, `run.log`
  - per-run **manifest**: `run-manifest.json` (always for `sde run`; task + mode for replay / audit; optional **`project_step_id`** / **`project_session_dir`** when the attempt was started from the **project driver** — Phase 1 traceability to the session plan)
  - **`sde run --repeat N`**: **N** independent runs (each its own `run-manifest.json` and `outputs/runs/<run-id>/`); JSON envelope when **N > 1** (see **§ SDE baseline (`what.md` content below)** RepeatProfile / multi-run envelope)
  - CTO / V1 gate files: `review.json` (**schema 1.1**, includes severity-tagged **`review_findings`** for §11 stop-ship rollup + **HS15** honesty with `definition_of_done`), `token_context.json`, **`static_gates_report.json`** (successful parse path)
  - per-run generated outputs (when applicable): `answer.txt`, `generated_script.py`
  - per-run pipeline artifacts (guarded_pipeline): `planner_doc.md`, `executor_prompt.txt`, `verifier_report.json`
- Benchmark runs additionally persist **`benchmark-manifest.json`** and incremental **`benchmark-checkpoint.json`** (per-task progress); CLI supports **`--max-tasks`**, **`--continue-on-error`**, and **`--resume-run-id`** (same `outputs/runs/<id>` directory; suite path and mode must match the manifest).
- Required metrics: pass rate, reliability, p50/p95 latency, estimated cost, validity rate, retry frequency.

**Feature status vs upstream harnesses:** `src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit` + gate modules under `src/guardrails_and_safety/`.

## Assumptions

- Local runtime uses Ollama by default.
- Implementation model is `qwen3:14b`; support model is `gemma 4`.
- API provider exists only as fallback and must be explicitly justified in report.

## Risks

- Missing local model pulls can block benchmark execution.
- Non-JSON model outputs can fail closed and reduce pass rate.
- Latency may regress under guarded mode due to extra stages.


---

## Project driver (meta-orchestrator)

# SDE project driver (meta-orchestrator)

**In plain words:** this is the **session-level** loop that sits **above** `sde run`: it owns a **real** `project_plan.json` (atomic `step_id`s, `depends_on`, per-step verification commands, `path_scope`), runs **`execute_single_task`** once per runnable step with a **bounded context pack**, runs **orchestrator verification** after each step, and only then advances `progress.json`. Per-run `outputs/runs/<id>/program/project_plan.json` from the V3 harness remains a **separate** CTO skeleton for that run; do not overwrite it with the session plan.

**Gap inventory sync:** this feature closes **Category 1** (context packs + optional repo index; **Phase 2** adds prior-run excerpts + session-level truncation provenance aligned with HS03 pairing), **Category 2** (repo-backed plan + orchestrator-only advancement; **Phase 3** adds session **DoD** + verification aggregate), **Category 4** (outer driver + verification-backed progress; **Phase 4** adds **``stop_report.json``** + terminal ``exit_code`` / ``stopped_reason`` on ``driver_state.json``; **Phase 5** adds ``continuous --project-plan`` and optional ``--progress-file``; `validation_ready` on each run is still **per-run**, not “product shipped”; session **``definition_of_done.json``** is the product-level bar when the driver finishes green; ``--stop-when`` applies to **task** ``continuous`` only), **Category 5** (workspace fields on the plan; **Phase 7** enforces optional ``workspace.branch`` via git and ``workspace.allowed_path_prefixes`` against each step’s ``path_scope`` when prefixes are set). **Category 3** (parallel lanes): **Phase 6** adds optional **isolated worktrees** when you pass **`--parallel-worktrees`** and the repo has **git** (``.git`` present); otherwise `max_concurrent_agents` > 1 still only **schedules** disjoint `path_scope` steps and runs them **sequentially** on the main checkout. **Phase 8** prunes **stale** ``leases.json`` rows by heartbeat age (default **86400s** unless ``workspace.lease_ttl_sec`` or CLI ``--lease-stale-sec``) and treats **persisted** non-stale leases as **conflicts** in ``try_acquire`` so a crashed tick cannot deadlock the next session forever. **Phase 9** adds **`sde project validate`** (read-only plan + cycle + optional workspace checks; optional ``progress.json`` conformance warnings) for CI preflight without executing steps. **Phase 10** adds **`sde project status`** (read-only JSON snapshot: plan health, progress body, ``driver_state`` / ``stop_report``, lease row count, and **next_tick_batch** hint from the scheduler). **Phase 11** adds append-only **`session_events.jsonl`** (``session_driver_start``, per-iteration ``tick``, terminal ``session_terminal``) for lightweight audit trails; ``project status`` reports ``line_count`` and the **last** parsed event. **Phase 12** extends **`sde project status`** / :func:`describe_project_session` with embedded bodies for **`verification_aggregate.json`** and **`definition_of_done.json`**, plus **`step_runs.jsonl`** line count and **last** row (same read-only contract). **Phase 13** caps embedded JSON reads and large JSONL scans: bodies omit with ``body_omitted`` + ``byte_len`` past a byte budget; ``session_events`` / ``step_runs`` past a scan budget omit exact ``line_count`` and derive ``last`` from a tail window only. **Phase 14** extends status with ``context_pack_lineage`` (same JSONL contract as session events), plus directory summaries for ``context_packs/`` and ``verification/`` (file counts + capped sorted ``step_ids``). **Phase 15** embeds ``leases.json`` under the Phase 13 JSON cap (with ``active_row_count_omitted`` when the body is skipped) and lists ``_worktrees/`` as ``parallel_worktrees`` (capped ``step_ids``). **Phase 16** adds ``plan_step_rollups`` (per-``step_id`` verification file presence, context-pack file presence, and ``aggregate_passed`` when the aggregate body is embedded; list length uses the same cap as ``--status-max-listed-step-ids``). **Phase 17** adds ``step_runs.by_step`` (latest ``run_id`` / ``output_dir`` per ``step_id``) when ``step_runs.jsonl`` is under the JSONL full-scan cap, plus matching ``latest_run_id`` / ``latest_output_dir`` on rollup rows; otherwise ``by_step_omitted``. **Phase 18** adds ``repo_snapshot`` (read-only ``git rev-parse`` for ``HEAD`` / short SHA / branch when ``repo_root`` is set and ``.git`` exists; ``reason`` when ``repo_root`` is omitted). **Phase 19** adds ``workspace_status`` (echo plan ``workspace`` plus ``branch_commit_match`` / detail from the same ``git_head_matches_branch`` check as Phase 7 when git is available). **Phase 20** adds ``path_prefix_errors`` / ``path_prefixes_configured`` / ``path_prefixes_ok`` on ``workspace_status`` (same rules as :func:`plan_workspace_path_errors` / Phase 7 plan validation). **Phase 21** adds ``status_at_a_glance`` on :func:`describe_project_session` / ``sde project status``: compact derived booleans and counts (plan health, runnable / next-tick sizes, driver and stop exit codes when embedded, DoD / aggregate hints, workspace prefix + branch echo, ``step_runs`` indexability) plus ``red_flags`` (``dependency_cycle`` vs generic plan failure, ``workspace_path_prefix_mismatch``, ``workspace_branch_mismatch``).

---

## Session directory layout

All paths are relative to a chosen **session directory** (e.g. `.agent/sde/projects/my-feature/`):

| File / directory | Purpose |
|------------------|---------|
| `project_plan.json` | Authoritative plan (`schema_version` **1.0**). |
| `progress.json` | `completed_step_ids`, `pending_step_ids`, `blocked_reason`, last run pointers, `intake_loaded_last` (whether the last step’s context pack merged `intake/`). |
| `driver_state.json` | `status`: `running` \| `completed_review_pass` \| `blocked_human` \| `exhausted_budget` \| `dependency_cycle` \| `invalid_session`; budget counters; while **`running`**, optional **`intake_loaded_last`** (same meaning as `progress.json`); on terminal outcomes **`exit_code`** + **`stopped_reason`** (mirrors CLI exit); terminal **`intake_loaded_last`** is copied from `progress.json` when present. |
| `stop_report.json` | **Phase 4:** CI-oriented snapshot (`exit_code`, `stopped_reason`, `driver_status`, budget, `block_detail`, `ci.exit_code_meaning` + exit-code legend). Written on **every** terminal session outcome (including invalid plan). |
| `step_runs.jsonl` | Append-only map `step_id` → SDE `run_id` / `output_dir`. |
| `verification/<step_id>.json` | Orchestrator-run command results for that step. |
| `verification_aggregate.json` | **Phase 3:** roll-up of every plan step’s verification bundle (presence, ``passed``, timestamps); refreshed after each successful step. |
| `definition_of_done.json` | **Phase 3:** session **DoD** (not per-run ``review.json``): ``plan_graph_complete`` + ``aggregate_verification`` checks; ``all_required_passed`` only when driver status is ``completed_review_pass`` and both checks pass. |
| `context_packs/<step_id>.json` | Capped markdown + metadata injected into the task string (`schema_version` **1.1**): prior-dep excerpts, **HS03-style** ``truncation_events`` / ``reductions`` when capped, ``markdown_sha256_full``. |
| `context_pack_lineage.jsonl` | Append-only audit of each pack build (step_id, sha256, truncated, ``truncation_hs03_ok``, ``intake_loaded``). |
| `leases.json` | Path lease audit trail (MVP; overlap detection uses plan scopes). **Phase 8:** rows older than the lease TTL are pruned each driver tick; ``try_acquire`` also blocks on **fresh** persisted rows from other ``step_id``s. |
| `_worktrees/<step_id>/` | **Phase 6:** ephemeral detached git worktrees for a parallel tick (removed after the batch). |
| `session_events.jsonl` | **Phase 11:** append-only driver events (``session_driver_start``, ``tick``, ``session_terminal``); schema **1.0** per line. |
| `intake/` | Stage 1 artifacts (discovery, digest, workbook, `doc_review.json`, revise state, reviewer identity, lineage manifest, etc.); consumed by lock-readiness and context packs when present. |
| `project_plan_lock.json` | Optional Stage 1 lock artifact written by `sde project plan-lock`; read by status and lock-readiness checks. |

---

## `project_plan.json` (schema 1.0)

Top-level keys:

- `schema_version`: `"1.0"`.
- `repo_root` (optional): informational default `"."`; driver uses CLI `--repo-root`.
- `workspace` (optional object): `branch` (string: ``HEAD`` must equal ``refs/heads/<branch>``), `allowed_path_prefixes` (non-empty string array when present: every step’s ``path_scope`` pattern must overlap one prefix on the repo tree), `lease_ttl_sec` (optional int **≥ 60**: seconds before a lease row is considered stale and pruned each tick; omit for default **86400**). **Phase 7** validates prefixes + branch; **Phase 8** uses ``lease_ttl_sec`` for pruning.
- `steps`: non-empty array of objects, each with:
  - `step_id` (string, unique)
  - `phase` (string)
  - `title` (string)
  - `description` (string) — becomes the **task body** after the context pack prefix.
  - `depends_on` (string array of `step_id`s)
  - `path_scope` (string array, glob-like patterns relative to repo root for repo index)
  - `verification` (optional object): `commands` — array of `{ "cmd": "pytest", "args": ["-q"], "cwd": null, "timeout_sec": 600 }`.

---

## `progress.json` (schema 1.0)

- `schema_version`: `"1.0"`
- `session_id`: directory name or explicit id
- `completed_step_ids`, `pending_step_ids`: string arrays
- `failed_step_id`, `blocked_reason`, `last_run_id`, `last_output_dir`
- `intake_loaded_last` (boolean): set after each step’s context pack is built; mirrors `context_packs/<step_id>.json` → `intake_loaded`

---

## CLI

- `sde project run (--session-dir <path> | --plan <path/to/project_plan.json>) [--repo-root <path>] [--max-steps N] [--mode ...] [--max-concurrent-agents K] [--progress-file <path>] [--parallel-worktrees] [--lease-stale-sec N] [--enforce-plan-lock] [--require-non-stub-reviewer]` — **`--plan`** is the file path to the authoritative plan; the **session directory** is the file’s parent. **`--progress-file`** (Phase 5) stores `progress.json` elsewhere. **`--parallel-worktrees`** (Phase 6) runs a multi-step tick in detached git worktrees when applicable. **`--lease-stale-sec`** (Phase 8) sets the lease stale TTL in seconds (**0** = disable pruning; overrides ``workspace.lease_ttl_sec``). **`--enforce-plan-lock`** runs Stage 1 lock-readiness before the first step; **`--require-non-stub-reviewer`** only applies together with **`--enforce-plan-lock`** (strict reviewer policy; see Stage 1 section below).
- `sde continuous (--project-session-dir <path> | --project-plan <path/to/project_plan.json>) [--progress-file <path>] [--parallel-worktrees] [--lease-stale-sec N] [--enforce-plan-lock] [--require-non-stub-reviewer] ...` — same driver as `sde project run`, reuses `--max-iterations` as the step budget. **`--stop-when`** still applies only to **task** mode (repeat `--task`); project mode stops per driver + `stop_report.json`. Project mode accepts the same **`--enforce-plan-lock`** / **`--require-non-stub-reviewer`** pairing as **`project run`**.
- **`sde project validate (--session-dir <path> \| --plan <path>) [--repo-root <path>] [--skip-workspace] [--progress-file <path>] [--require-plan-lock] [--require-non-stub-reviewer]`** — **Phase 9:** validates ``project_plan.json`` (schema + workspace path rules), detects **dependency cycles**, optionally runs **Phase 7** git workspace checks (skip with ``--skip-workspace``), and emits **non-fatal** warnings if an optional ``progress.json`` does not match the progress schema. With **`--require-plan-lock`**, fails closed when Stage 1 lock-readiness is not satisfied; optional **`--require-non-stub-reviewer`** rejects ``local_stub`` reviewer attestation during that check. Exit codes: **0** ok, **1** workspace contract, **2** invalid plan / missing file / cycle. Does **not** write ``stop_report.json`` or run the driver loop.
- **`sde project status (--session-dir <path> \| --plan <path>) [--repo-root <path>] [--progress-file <path>] [--max-concurrent-agents K] [--status-max-json-bytes N] [--status-jsonl-full-scan-max-bytes N] [--status-jsonl-tail-bytes N] [--status-max-listed-step-ids N]`** — **Phase 10 + 12–21:** prints one JSON object: plan / progress / ``driver_state`` / ``stop_report`` / **leases** (capped body + row count) / ``session_events`` (Phases 10–11, 15) plus **``verification_aggregate``**, **``definition_of_done``**, and **``step_runs``** summaries when those files exist (Phase 12). **Phase 13** flags tune read caps for huge sessions; **Phase 14** adds **`context_pack_lineage`**, **`context_packs`**, and **`verification_bundles`** (and caps how many ``step_ids`` are listed per directory); **Phase 15** adds **`parallel_worktrees`** (``_worktrees/``); **Phase 16** adds **`plan_step_rollups`**; **Phase 17** enriches **``step_runs``** / rollups with latest run pointers when ``step_runs.jsonl`` is small enough to fully scan; **Phase 18** adds **`repo_snapshot`** (``--repo-root``; default cwd); **Phase 19–20** add **`workspace_status`** (branch + path prefix checks); **Phase 21** adds **`status_at_a_glance`** (compact derived fields + ``red_flags``). CLI always exits **0** (inspect fields for red flags).
- **`sde project export-stage1-observability`** — same session selection as ``project status`` (``--session-dir`` or ``--plan``) plus optional ``--output`` (default ``intake/stage1_observability_export.json`` under the session). Writes a small versioned JSON snapshot of ``revise_metrics`` and ``status_at_a_glance`` for operators / CI artifacts (OSV-STORY-01 B4); see **§ Stage 1 intake** below.
- **Cold-start demo** — end-to-end Stage 1 CLI walk: ``./scripts/stage1-cold-start-demo.sh`` (runbook §Golden cold start; OSV-STORY-01 §5 / B5).

## Phase 1 — run ↔ plan linkage

Each per-step `execute_single_task` run writes `outputs/runs/<run-id>/run-manifest.json` with optional:

- `project_step_id` — `step_id` from the session plan for that tick.
- `project_session_dir` — absolute path to the session directory (parent of `project_plan.json` when using `--plan`).

Plain `sde run` omits these keys. **`sde replay --rerun`** copies them when present so reruns stay tied to the same session metadata.

---

## Phase 3 — Verification as session truth (shipped)

- **Per-step** commands still live under ``verification/<step_id>.json`` (orchestrator-owned).
- **Aggregate:** ``verification_aggregate.json`` lists every ``step_id`` in plan order; missing or failed bundles surface in ``missing_step_bundles`` / per-step ``passed``.
- **Session DoD:** ``definition_of_done.json`` mirrors the guarded-run shape (``checks[]``, ``all_required_passed``) but keys off **plan completion + aggregate verification**, not LLM self-report. Per-run ``validation_ready`` in ``outputs/runs/...`` remains the **single-task** quality bar.
- Successful ``run_project_session`` returns ``definition_of_done``, ``verification_aggregate_path``, ``definition_of_done_path``, and ``stop_report_path`` in the JSON summary.

## Phase 5 — Continuous + plan store (shipped)

- **`sde continuous --project-plan`** — same as pointing `--project-session-dir` at the plan’s parent directory; use when you prefer a file path to the authoritative `project_plan.json`.
- **`--progress-file`** on **`continuous`** (with a project flag) and **`project run`** — optional override for `progress.json` so resume state can live next to CI artifacts or a writable volume while the plan stays read-only.

## Phase 6 — Parallel worktrees (shipped, opt-in)

- **Flag:** `sde project run … --parallel-worktrees` or `sde continuous … --parallel-worktrees` (with a project session/plan). Default remains **single checkout** sequential execution.
- **Requirements:** git repo at **`--repo-root`** (or cwd when not passed); scheduler must have placed **2+** runnable steps with **pairwise disjoint** `path_scope`; `max_concurrent_agents` > 1. Otherwise the driver keeps the Phase 5 sequential path.
- **Behavior:** one detached worktree per step under `session_dir/_worktrees/<step_id>/`; `execute_single_task` and per-step verification use that worktree as `repo_root`; `step_runs.jsonl` writes are serialized with a session lock.

## Phase 7 — Workspace contract (shipped)

- **Plan validation:** non-empty ``allowed_path_prefixes`` requires every step to declare non-empty ``path_scope``, and each pattern must overlap a prefix (no ``..`` segments; ``./`` leaders stripped safely). Empty ``allowed_path_prefixes`` array is invalid.
- **Runtime:** when ``workspace.branch`` is set, the driver compares ``git rev-parse HEAD`` to ``git rev-parse refs/heads/<branch>`` (works at a detached tip). Wrong ref / missing git / missing local branch → terminal stop with ``stopped_reason`` ``workspace_contract`` (exit **1**, ``blocked_human``).

## Phase 8 — Lease TTL + persisted conflicts (shipped)

- **Pruning:** at the start of each driver tick, ``leases.json`` rows older than the effective TTL (CLI ``--lease-stale-sec``, else ``workspace.lease_ttl_sec`` if set, else **86400** seconds) are removed using ``heartbeat_at`` (fallback ``acquired_at``).
- **Acquire:** ``try_acquire`` rejects overlaps with **persisted** lease rows for ``step_id``\ s **outside** the current batch, using the row’s stored ``path_scope`` (so a crash mid-session cannot leave a ghost lease that blocks unrelated steps once TTL passes; while fresh, overlaps fail closed with ``lease_conflict``).

## Phase 9 — Plan validate subcommand (shipped)

- **API:** :func:`validate_project_session` in [`project_validate.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_validate.py) returns ``ok``, ``exit_code``, and structured errors; on success it also returns an ``intake`` object (``intake_dir_present``, ``merge_anchor_present``, ``progress_intake_loaded_last`` when ``progress.json`` was read). No ``execute_single_task``, no lease mutation.
- **CLI:** ``sde project validate`` mirrors ``project run`` session/plan selection; ``--skip-workspace`` for sandboxes without git; optional ``--progress-file`` for resume-state warnings only; optional ``--require-plan-lock`` / ``--require-non-stub-reviewer`` for Stage 1 preflight (see below).

## Stage 1 plan lock — validate, run, and continuous (shipped)

- **Preflight:** ``sde project validate ... --require-plan-lock`` evaluates the same Stage 1 lock-readiness rules as ``sde project plan-lock --check-only`` (intake artifacts, reviewer separation, lineage, plan metadata, etc.). Optional ``--require-non-stub-reviewer`` applies strict non-stub reviewer policy **only together with** ``--require-plan-lock``; environment ``SDE_REQUIRE_NON_STUB_REVIEWER`` (``1`` / ``true`` / ``yes`` / ``on``) does the same when plan-lock is required. These CLI-only env semantics do **not** change Python API defaults used by unit tests and golden flows.
- **Runtime:** ``sde project run ... --enforce-plan-lock`` and ``sde continuous`` in project mode with ``--enforce-plan-lock`` call :func:`evaluate_project_plan_lock_readiness` in [`project_plan_lock.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_plan_lock.py) **before** any plan step runs (after workspace/repo gates). When readiness is not satisfied, the driver exits **1** with ``stopped_reason`` / ``blocked_human`` consistent with other human-facing gates; see ``stop_report.json``.
- **Strict reviewer at runtime:** ``--require-non-stub-reviewer`` is honored only when ``--enforce-plan-lock`` is set; it forwards ``allow_local_stub_attestation=False`` into readiness (same effect as strict ``plan-lock`` / ``validate --require-plan-lock``). ``SDE_REQUIRE_NON_STUB_REVIEWER`` turns on that strict path whenever ``--enforce-plan-lock`` is present on ``project run`` / ``continuous`` (still CLI-only).
- **API:** :func:`run_project_session` and :func:`run_continuous_project_session` accept ``enforce_plan_lock`` and ``require_non_stub_reviewer`` for programmatic parity.
- **Runbook:** failure modes and triage commands live in **[§ Stage 1 runbook](#stage-1-intake-operator-runbook)**.

## Phase 10 — Status snapshot (shipped)

- **API:** :func:`describe_project_session` in [`project_status.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_status.py) aggregates on-disk session JSON without writes.
- **CLI:** ``sde project status`` for operators / dashboards; ``--max-concurrent-agents`` only affects the ``next_tick_batch`` hint.

## Phase 12 — Status: aggregate, DoD, step_runs (shipped)

- **API:** same :func:`describe_project_session`; adds ``verification_aggregate`` / ``definition_of_done`` (each ``path``, ``present``, full ``body`` when readable) and ``step_runs`` (``line_count`` + ``last`` parsed object from ``step_runs.jsonl``).

## Phase 13 — Status: bounded reads (shipped)

- **API:** :func:`describe_project_session` accepts optional ``max_status_json_bytes`` (default **524288**), ``max_status_jsonl_full_scan_bytes`` (default **1048576**), ``max_status_jsonl_tail_bytes`` (default **262144**). Embedded JSON for **progress**, **driver_state**, **stop_report**, **verification_aggregate**, and **definition_of_done** is skipped when the file exceeds the JSON cap (``body`` null, ``body_omitted`` true, ``byte_len`` set). ``session_events.jsonl`` and ``step_runs.jsonl`` use a full line scan only while the file is under the JSONL cap; otherwise ``line_count`` is null with ``line_count_omitted`` true and ``last`` is parsed from the tail window only.
- **CLI:** ``sde project status`` exposes the same knobs as ``--status-max-json-bytes``, ``--status-jsonl-full-scan-max-bytes``, and ``--status-jsonl-tail-bytes``.

## Phase 14 — Status: context + verification inventory (shipped)

- **API:** :func:`describe_project_session` adds ``context_pack_lineage`` (``context_pack_lineage.jsonl``: ``line_count`` / ``last`` / JSONL omission flags, same caps as Phase 13), ``context_packs`` (non-recursive ``*.json`` under ``context_packs/``: ``file_count``, sorted ``step_ids``, optional ``step_ids_omitted``), and ``verification_bundles`` (same shape for ``verification/*.json``). Optional ``max_status_listed_step_ids`` (default **256**) bounds the listed stems.
- **CLI:** ``--status-max-listed-step-ids`` overrides the default cap (also bounds **Phase 16** ``plan_step_rollups`` and **Phase 15** ``parallel_worktrees``).

## Phase 15 — Status: leases body + worktrees inventory (shipped)

- **API:** ``leases`` is now the same **capped JSON embed** shape as ``driver_state`` / ``stop_report`` (``path``, ``present``, ``body``, optional ``body_omitted`` / ``byte_len``). ``active_row_count`` counts dict rows in ``body.leases`` when the body is present; when ``body_omitted`` is true, ``active_row_count`` is null and ``active_row_count_omitted`` is true. ``parallel_worktrees`` summarizes ``_worktrees/`` (child directory names as ``step_ids``, ``dir_count``, same ``step_ids`` cap as Phase 14).
- **CLI:** no new flags; ``--status-max-json-bytes`` controls lease embed size; ``--status-max-listed-step-ids`` caps worktree dir names listed.

## Phase 16 — Status: plan step rollups (shipped)

- **API:** ``plan_step_rollups`` appears when ``project_plan.json`` parses as an object: ``present``, ``step_count`` (full plan length), ``steps`` (first **N** rows in plan order, **N** = ``max_status_listed_step_ids`` default **256**), ``steps_omitted`` when truncated. Each row has ``step_id``, ``verification_json_present``, ``context_pack_present``, ``context_pack_intake_loaded`` (bool from ``context_packs/<step_id>.json`` → ``intake_loaded`` when the file is **≤** ``--status-max-json-bytes``; otherwise ``null``), and ``aggregate_passed`` (bool or null when unknown or aggregate body omitted / missing cell).
- **CLI:** ``--status-max-listed-step-ids`` bounds rollup rows; ``--status-max-json-bytes`` bounds aggregate embed used for ``aggregate_passed``.

## Phase 17 — Status: step_runs latest-by-step (shipped)

- **API:** When ``step_runs.jsonl`` is **≤** ``max_status_jsonl_full_scan_bytes``, a single full read fills ``line_count`` / ``last`` / ``by_step`` (map ``step_id`` → ``{ run_id?, output_dir? }``, last line wins per step). When the file is larger, tail stats behave as in Phase 13 and ``by_step`` is null with ``by_step_omitted`` true. ``plan_step_rollups`` rows gain ``latest_run_id`` / ``latest_output_dir`` when present in ``by_step``.
- **CLI:** ``--status-jsonl-full-scan-max-bytes`` controls this threshold (same as session_events / step_runs line-count behavior).

## Phase 18 — Status: repo git snapshot (shipped)

- **API:** ``repo_snapshot`` summarizes ``--repo-root`` (resolved path, ``git_dir_present``, ``inside_work_tree`` when applicable, ``git_available``, ``head``, ``head_short``, ``branch`` from ``git rev-parse``; **10s** subprocess timeout per call). If ``repo_root`` is not passed to :func:`describe_project_session`, the block records ``reason: repo_root_not_provided`` and skips git.
- **CLI:** ``--repo-root`` on ``sde project status`` (default **cwd** in the CLI) selects the tree inspected for ``repo_snapshot``.

## Phase 19 — Status: plan workspace + branch match (shipped)

- **API:** ``workspace_status`` is ``{ "present": false }`` when the plan is missing or has no non-empty ``workspace`` object. Otherwise ``from_plan`` copies the plan’s ``workspace`` dict, and when ``workspace.branch`` is a non-empty string and ``repo_snapshot.git_available`` is true, ``branch_commit_match`` / ``branch_commit_detail`` mirror :func:`git_head_matches_branch` (Phase 7 semantics). Skip reasons: ``repo_root_not_provided``, ``plan_branch_not_set``, ``git_not_available``.
- **CLI:** same ``--repo-root`` as Phase 18; required for a branch commit check.

## Phase 20 — Status: workspace path prefixes (shipped)

- **API:** On ``workspace_status``, ``path_prefix_errors`` lists the same machine strings as :func:`plan_workspace_path_errors` (``workspace.allowed_path_prefixes`` vs each step’s ``path_scope``). ``path_prefixes_configured`` is true when that prefix list is non-empty after filtering; ``path_prefixes_ok`` is true iff configured and the error list is empty, or ``null`` when prefixes are not configured (N/A).

## Phase 21 — Status: at-a-glance + red_flags (shipped)

- **API:** :func:`describe_project_session` adds ``status_at_a_glance``: derived ``plan_ok``, ``all_plan_steps_complete``, runnable / next-tick counts, ``driver_status`` / ``driver_exit_code`` / ``stop_exit_code`` when the corresponding embedded bodies are dicts, ``dod_all_required_passed`` / ``aggregate_all_steps_verification_passed`` when those bodies are present, ``path_prefixes_ok`` / ``branch_commit_match`` echoed from ``workspace_status``, ``step_runs_latest_indexed`` when ``by_step`` is populated (not ``by_step_omitted``), **intake** fields ``intake_merge_anchor_present`` (``intake/discovery.json`` or ``intake/doc_review.json`` exists), ``intake_loaded_last_progress`` / ``intake_loaded_last_driver_state`` (booleans from embedded ``progress`` / ``driver_state`` bodies when present), **rollup intake tallies** ``rollup_context_pack_intake_loaded_true_count`` / ``false_count`` / ``null_count`` (from ``plan_step_rollups`` per-step ``context_pack_intake_loaded``; rollups also expose ``context_pack_intake_loaded_skipped_oversized`` per step), and ``red_flags`` (``dependency_cycle`` alone when the plan graph has a cycle; otherwise ``plan_invalid_or_unreadable_or_schema`` when ``plan_ok`` is false; plus ``workspace_path_prefix_mismatch`` / ``workspace_branch_mismatch`` when ``workspace_status.present`` and the respective checks are false; plus ``intake_loaded_last_progress_vs_driver_state_mismatch`` when both intake booleans are present and disagree; plus ``intake_merge_anchor_present_but_context_pack_intake_loaded_unknown`` when an intake merge anchor exists but an on-disk context pack under the status JSON byte cap lacks a boolean ``intake_loaded``).
- **CLI:** no new flags; same JSON envelope as Phase 10.

## Phase 11 — Session event log (shipped)

- **Writer:** :func:`append_session_event` in [`project_events.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_events.py); best-effort (swallows ``OSError`` so logging never crashes the driver).
- **Events:** ``session_driver_start`` once per ``run_project_session`` after the session enters ``running`` (payload includes ``intake_merge_anchor_present`` and ``intake_loaded_last`` from in-memory ``progress``); ``tick`` before each non-empty lease batch (same intake snapshot fields plus ``steps_used``, ``batch``, ``completed_step_ids``); ``session_terminal`` on **every** terminal outcome via ``_emit_stop_and_session_dod`` (payload includes ``exit_code``, ``stopped_reason``, ``completed_step_ids``, plus ``intake_merge_anchor_present`` and ``intake_loaded_last`` read from disk via ``progress.json`` when available, …). When ``intake/lineage_manifest.json`` exists, all three event kinds also carry ``intake_lineage_manifest_present``, optional ``intake_lineage_manifest_schema_version`` / ``created_at`` / ``artifact_count``, and ``intake_lineage_manifest_file_sha256`` (hash of the manifest file) for OSV-STORY-01 traceability (:func:`lineage_manifest_session_event_snapshot` in [`project_plan_lock.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_plan_lock.py)).

## Phase 4 — Stop policy (shipped)

- **Exit codes:** **0** = ``completed_review_pass`` (plan graph complete + aggregate verification passed). **1** = expected stop — ``blocked_human``, ``exhausted_budget``, ``dependency_cycle``, or ``workspace_contract`` (inspect ``stop_report.json`` / ``progress.json``). **2** = invalid session input or unexpected driver end (missing/invalid ``project_plan.json``, or internal ``unexpected_end``).
- **Artifacts:** every terminal path writes **``stop_report.json``** and refreshes **``driver_state.json``** with matching ``exit_code`` / ``stopped_reason``. When the plan is schema-valid, the driver also refreshes **``verification_aggregate.json``** and **``definition_of_done.json``** so the last session state is always on disk (failed runs get ``all_required_passed: false`` unless status is ``completed_review_pass``).
- **Per-run quality:** each ``execute_single_task`` remains **``validation_ready``-capable** under the chosen mode; session exit **0** does not imply every intermediate run was ``validation_ready`` unless your plan’s verification commands enforce it.

## Phase 2 — Context service (shipped)

- **ContextPack** pulls **dependency outputs** before each step: for every `depends_on` step that already has a row in `step_runs.jsonl`, it reads that run’s `summary.json` and `report.md` (capped excerpts) and lists **references** (paths + git head at build time when known).
- **Failures:** recent `prior_failures` plus, for verification failures, the tail of command logs from `verification/<step_id>.json`.
- **HS03 at session scope:** when the markdown exceeds ``max_chars``, the pack records paired ``truncation_events`` and ``reductions`` (shared ``provenance_id``), ``markdown_sha256_full`` of the pre-truncation body, and ``truncation_hs03_ok`` (same pairing rule as per-run ``token_context.json``). Per-run **HS03** from the pipeline is unchanged; this is additional honesty for the **driver-injected** prefix.

## Code map

- Validation: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_schema.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_schema.py)
- Graph: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_plan.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_plan.py)
- Driver loop: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_driver.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_driver.py)
- Task / project continuous: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/continuous_run.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/continuous_run.py)
- Context: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/context_pack.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/context_pack.py)
- Repo index MVP: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/repo_index.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/repo_index.py)
- Verification: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_verify.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_verify.py)
- Aggregate / session DoD: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_aggregate.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_aggregate.py)
- Stop policy: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_stop.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_stop.py)
- Scheduler / leases: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_scheduler.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_scheduler.py), [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_lease.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_lease.py)
- Parallel worktrees: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_worktree.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_worktree.py), [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_parallel.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_parallel.py)
- Workspace gates: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_workspace.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_workspace.py)
- Plan preflight: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_validate.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_validate.py)
- Stage 1 plan lock readiness + lock artifact: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_plan_lock.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_plan_lock.py)
- Session snapshot: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_status.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_status.py)
- Session events: [`src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_events.py`](../src/production_architecture_what_runs_on_the_laptop/orchestrator/api/project_events.py)

Example plan: [`data/sde-project-plan.example.json`](../data/sde-project-plan.example.json).


---

## Stage 1 intake (operator runbook)

# Stage 1 intake failure runbook

This runbook covers Stage 1 intake failure modes for `OSV-STORY-01` in the local orchestrator spine.

## OSV-STORY-01 status (done vs remaining)

Mapped historically to OSV-STORY-01 Stage 1 intake milestones (version plans removed; behavior is in `src/production_architecture_what_runs_on_the_laptop/orchestrator/api/` + tests).

Implemented now:

- [x] `discovery.json` schema checks (`goal_excerpt` non-empty for anchor semantics)
- [x] `research_digest.md` + `question_workbook.jsonl` presence in lock-readiness checks
- [x] `doc_review.json` schema validation (`passed` bool + `findings` list/dict), fail-closed in validate
- [x] bounded revise loop with deterministic `blocked_human` after retry cap
- [x] lock-readiness evaluation + lock artifact (`project_plan_lock.json`)
- [x] run-time lock enforcement (`sde project run --enforce-plan-lock`)
- [x] preflight lock enforcement (`sde project validate --require-plan-lock`)
- [x] golden Stage 1 success + failure tests in `src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_stage1_golden_flow.py`
- [x] runbook + runbook consistency test
- [x] CI wall-clock SLO for Stage 1 preflight (`STAGE1_SUITE_MAX_SECONDS` in `scripts/run-stage1-suite.sh`, set in CI)
- [x] intake `lineage_manifest.json` + hash checks at plan-lock readiness
- [x] session-local revise metrics (`intake/revise_metrics.jsonl`) surfaced via `project status`
- [x] structured Stage 1 observability export (`intake/stage1_observability_export.json`) via `sde project export-stage1-observability` (schema validated in tests; `revise_metrics` + `status_at_a_glance`)
- [x] golden cold-start command narrative: `./scripts/stage1-cold-start-demo.sh` (mirrors `test_stage1_golden_flow.py` success path; exercised by `test_stage1_cold_start_demo.py` in the Stage 1 suite)

Remaining for full Stage 1 closure:

- [ ] independent reviewer identity/credentials boundary with audit proof (not local stub reviewer)
- [ ] full autonomous model-driven revise/doc regeneration loop (current loop applies deterministic local regeneration only)
- [ ] durable platform lineage/event binding beyond session-local manifests
- [ ] production/local-prod observability service for `doc_review` latency + retry trends

## Structured observability export (doc_review / revise)

For automation, CI artifacts, or log scrapers, write a **small versioned JSON** file (default **`intake/stage1_observability_export.json`**) that embeds `revise_metrics` and `status_at_a_glance` from the same read-only snapshot as `project status`:

```bash
sde project export-stage1-observability --session-dir /path/to/session
```

Custom path:

```bash
sde project export-stage1-observability --session-dir /path/to/session --output /tmp/stage1_metrics.json
```

Contract: top-level `schema_version` **`1.0`**, `kind` **`project_stage1_observability`**, plus `captured_at`, `session_dir`, `revise_metrics`, `status_at_a_glance`. Validate with `stage1_observability_export_schema_errors` in `orchestrator.api` (used by unit tests).

## Golden cold start (operator demo, OSV-STORY-01 §5 / B5)

End-to-end **CLI** sequence from an empty session directory through scaffold → minimal `project_plan.json` → `intake-revise` → `plan-lock` → `validate --require-plan-lock` → `export-stage1-observability`. Expected end state: **`project_plan_lock.json`** with `locked: true`, validate **`exit_code` 0**, and **`intake/stage1_observability_export.json`** present.

From **repository root**:

```bash
./scripts/stage1-cold-start-demo.sh
```

Each `uv run sde …` step prints JSON to **stdout**; the script echoes the session path to **stderr**. Exits **`0`** only if every step succeeds. Uses a fresh temp session unless you pin a directory:

```bash
STAGE1_COLD_START_SESSION_DIR=/path/to/empty-session ./scripts/stage1-cold-start-demo.sh
```

**Per-step exit semantics (when invoked via `sde`):**

| Step | Command | Success exit |
|------|---------|---------------|
| 1 | `project scaffold-intake` | **0** (`ok` in JSON) |
| 2 | *(write `project_plan.json`; script uses fixed golden shape)* | — |
| 3 | `project intake-revise` | **0** if `review_passed`; **1** if `retry_allowed` / `blocked_human`; **2** on error |
| 4 | `project plan-lock` | **0** if ready and lock written; **1** if evaluated but not ready; **2** on hard failure |
| 5 | `project validate --require-plan-lock` | **0** ok; **1** workspace; **2** plan / lock failure |
| 6 | `project export-stage1-observability` | **0** if export written |

Automated parity: `src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_stage1_cold_start_demo.py` runs this script (included in `./scripts/run-stage1-suite.sh`). The Python golden path remains in `test_stage1_golden_flow.py`.

## One-shot verification command

From repo root, run the Stage 1 verification subset:

```bash
./scripts/run-stage1-suite.sh
```

Optional local SLO (whole seconds, must be `>= 1` when set); fails with exit code 1 if the suite wall time exceeds the budget:

```bash
STAGE1_SUITE_MAX_SECONDS=300 ./scripts/run-stage1-suite.sh
```

Optional strict reviewer policy for **CLI** invocations only (does not change Python API defaults used by tests): when `SDE_REQUIRE_NON_STUB_REVIEWER` is `1`, `true`, `yes`, or `on`, these commands apply the same rules as `--require-non-stub-reviewer` without repeating the flag (useful in CI wrappers or shell profiles): `sde project plan-lock`, `sde project validate --require-plan-lock`, `sde project run --enforce-plan-lock`, and `sde continuous` when driving a project session with `--enforce-plan-lock`.

Equivalent inline command:

```bash
uv run pytest \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_intake_scaffold.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_intake_util.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_intake_revise.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_plan_lock.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_validate.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_status.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_stage1_observability_export.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_stop.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_stage1_golden_flow.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_stage1_cold_start_demo.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_stage1_runbook_consistency.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_stage1_suite_script.py -q
```

## Scope

- Intake scaffold artifacts under `<session>/intake/`
- `doc_review.json` validation + revise loop
- Plan-lock readiness and enforcement
- Validate preflight with required plan lock

## Fast triage commands

From repo root:

```bash
uv run sde project status --session-dir "<session_dir>"
uv run sde project validate --session-dir "<session_dir>" --skip-workspace --require-plan-lock
uv run sde project validate --session-dir "<session_dir>" --skip-workspace --require-plan-lock --require-non-stub-reviewer
uv run sde project plan-lock --session-dir "<session_dir>" --check-only
uv run sde project plan-lock --session-dir "<session_dir>" --check-only --require-non-stub-reviewer
uv run sde project run --session-dir "<session_dir>" --enforce-plan-lock --require-non-stub-reviewer --mode guarded_pipeline
uv run sde continuous --project-session-dir "<session_dir>" --repo-root "<repo_root>" --enforce-plan-lock --require-non-stub-reviewer
```

Interpret quickly:

- `project validate` exit `0`: lock-ready preflight passed
- `project validate` exit `2`: invalid plan/intake/lock readiness failed
- `project run --enforce-plan-lock` (and `continuous` project mode with `--enforce-plan-lock`) exit `1` with `blocked_human`: lock gate blocked execution; with `--require-non-stub-reviewer` or `SDE_REQUIRE_NON_STUB_REVIEWER`, stub reviewer attestation fails lock readiness the same way as on `plan-lock` / `validate`
- `project plan-lock --require-non-stub-reviewer` exit `1` with reason `reviewer_identity_attestation_stub_disallowed`: local stub reviewer proof is rejected

## Failure mode matrix

- `invalid_doc_review_json`
  - Trigger: `intake/doc_review.json` has bad schema (`passed` not bool or bad `findings` type)
  - Detect: `sde project validate ... --require-plan-lock`
  - Fix: rewrite `doc_review.json` to valid shape, then re-run validate

- `plan_lock_not_ready`
  - Trigger: one or more Stage 1 prerequisites missing (digest/workbook/revise_state/contract step/rollback hints/etc.)
  - Detect: `sde project plan-lock --check-only`
  - Fix: satisfy reasons list, then write lock again

- `blocked_human` from revise loop
  - Trigger: repeated failed `doc_review` reached retry cap in `intake/revise_state.json`
  - Detect: `intake/revise_state.json` has `status: blocked_human`
  - Fix: provide corrected reviewer output (`passed: true` + findings shape), then apply revise again

- deterministic auto-regeneration applied
  - Trigger: `doc_review.passed == false` and `intake-revise` runs
  - Detect: `intake/revise_autogen.json` exists and `research_digest.md` / `question_workbook.jsonl` include `auto-revise-*` entries
  - Fix: if not present, rerun `intake-revise`; if still absent, treat as intake tooling failure and escalate

- `plan_lock_gate_failed` during project run
  - Trigger: `--enforce-plan-lock` enabled and readiness false
  - Detect: `stop_report.json` and run output detail `plan_lock_not_ready`
  - Fix: run `plan-lock --check-only`, resolve reasons, then retry run

## Required files and expected fields

- `intake/discovery.json`
  - must include non-empty `goal_excerpt`
- `intake/research_digest.md`
  - non-empty markdown content
- `intake/question_workbook.jsonl`
  - at least one JSON object row
- `intake/doc_review.json`
  - `passed: <bool>`
  - `findings: <list|dict>`
  - `reviewer: <non-empty string>`
  - `reviewed_at: <valid ISO timestamp>`
- `intake/planner_identity.json`
  - `actor_id: <non-empty string>`
- `intake/reviewer_identity.json`
  - `actor_id: <non-empty string>`
  - `role: reviewer`
  - `attestation_type: one of [local_stub, agent_signature, service_token]`
  - `attestation: <non-empty string>`
  - `reviewed_at: <non-empty string>`
  - `reviewed_at` must be a valid ISO timestamp and be within 300s of `doc_review.reviewed_at`
  - `doc_review.reviewer` must equal reviewer `actor_id`
  - reviewer `actor_id` must not equal planner `actor_id`
- `intake/revise_state.json` (when required)
  - `status: review_passed`
- `project_plan.json`
  - valid schema
  - each step has non-empty `rollback_hint`
  - at least one step with `contract_step: true`

## Recovery playbook (ordered)

1. Run `status` and `validate --require-plan-lock` to capture current state.
2. If `doc_review` invalid, fix schema first.
3. Apply revise loop:
   - `uv run sde project intake-revise --session-dir "<session_dir>" --max-retries 2`
4. Check lock readiness:
   - `uv run sde project plan-lock --session-dir "<session_dir>" --check-only`
5. Write lock artifact:
   - `uv run sde project plan-lock --session-dir "<session_dir>"`
6. Re-run preflight:
   - `uv run sde project validate --session-dir "<session_dir>" --skip-workspace --require-plan-lock`
7. Resume execution:
   - `uv run sde project run --session-dir "<session_dir>" --enforce-plan-lock --mode guarded_pipeline`
   - For CI parity with strict reviewer policy: add `--require-non-stub-reviewer` or set `SDE_REQUIRE_NON_STUB_REVIEWER` (same semantics as validate/plan-lock)

## Stage 1 progress signals (quick JSON checklist)

Use these commands:

```bash
uv run sde project status --session-dir "<session_dir>"
uv run sde project plan-lock --session-dir "<session_dir>" --check-only
uv run sde project validate --session-dir "<session_dir>" --skip-workspace --require-plan-lock
```

Reviewer proof locations:

- `sde project plan-lock --check-only ...` JSON includes `reviewer_proof_summary`
- `<session_dir>/project_plan_lock.json` includes `reviewer_proof_summary` when lock is written
- `sde project status --session-dir ...` `status_at_a_glance.reviewer_*` fields prefer `plan_lock.reviewer_proof_summary` when present (fallback: live `reviewer_proof` from intake files)
- `status_at_a_glance.reviewer_signal_source` reports `plan_lock` vs `intake`

Healthy indicators:

- `status_at_a_glance.plan_lock_ready == true`
- `status_at_a_glance.plan_lock_locked == true`
- `status_at_a_glance.intake_merge_anchor_present == true`
- `status_at_a_glance.reviewer_attestation_type_allowed == true`
- `status_at_a_glance.reviewer_attestation_policy_ok == true` (when strict reviewer policy is active)
- `status_at_a_glance.reviewer_matches_doc_review == true`
- `status_at_a_glance.reviewer_differs_from_planner == true`
- `status_at_a_glance.reviewed_at_skew_ok == true`
- `status_at_a_glance.red_flags` does not include:
  - `intake_doc_review_invalid`
  - `plan_lock_not_ready`
  - `plan_lock_not_locked`
- `project validate` returns `exit_code: 0`

Blocked indicators:

- `status_at_a_glance.plan_lock_ready == false`
- `status_at_a_glance.plan_lock_locked == false`
- `status_at_a_glance.red_flags` includes one or more of:
  - `plan_lock_not_ready`
  - `plan_lock_not_locked`
  - `reviewer_attestation_type_invalid`
  - `reviewer_attestation_policy_failed`
  - `reviewer_identity_doc_review_mismatch`
  - `reviewer_identity_matches_planner`
  - `reviewed_at_skew_exceeded`
- `project validate` returns `error: "plan_lock_not_ready"` with `details` reasons
- `project run --enforce-plan-lock` stops with `stopped_reason: "blocked_human"` and detail `plan_lock_not_ready`

Useful files to inspect directly:

- `<session_dir>/project_plan_lock.json`
- `<session_dir>/intake/doc_review.json`
- `<session_dir>/intake/revise_state.json`
- `<session_dir>/stop_report.json` (after blocked runs)

## Escalation

Escalate when any condition persists after one correction loop:

- lock reasons remain unchanged after fixes
- revise state stays `blocked_human` with corrected `doc_review.json`
- validate fails with unreadable/malformed plan artifacts

Attach in escalation:

- `project_plan.json`
- `intake/doc_review.json`
- `intake/revise_state.json` (if present)
- `project_plan_lock.json` (if present)
- `stop_report.json` (if present)
