# Developer walkthrough

This guide is for engineers who are new to the repository. It tells you **what to read first**, **how the code is organized**, **what the system does at a high level**, and **how to run and change things safely**.

**Want a gentler on-ramp?** Start with **[start-here-reading-the-docs.md](start-here-reading-the-docs.md)** (ideas and doc order) and **[start-here-reading-the-code.md](start-here-reading-the-code.md)** (where the Python lives and what to open first).

**If you are an LLM:** follow **§2 reading order** before editing. Prefer **small, test-backed** changes under `src/orchestrator/tests/`. Do not invent new artifact filenames without updating **`docs/sde/implementation-contract.md`** and gate code.

---

## 1. What this repository is

**In plain words:** this repo holds **(a)** a large written vision of how a trustworthy AI engineering system should work, and **(b)** a **local Python CLI** that already runs tasks and records results. The CLI is the **first concrete slice**; many platform pieces exist today as **specs** so the team agrees on contracts before wiring every service.

This project is an **architecture and local-runtime workspace** for an *AI Professional Evolution* style system: long-horizon, auditable agent execution with gates, benchmarks, and a path toward full platform capabilities described in the master document.

**What actually runs in code today** is the **SDE** (local CLI) package: a Python tool that can:

- **`sde run`** — execute a single task in `baseline` or `guarded_pipeline` mode and write a run directory under **`outputs/runs/<run-id>/`** at the **repository root** (includes `run-manifest.json`, `static_gates_report.json` on success).
- **`sde benchmark`** — run a suite of tasks (JSONL) in baseline and/or guarded mode and aggregate metrics into a benchmark run directory (`benchmark-manifest.json`, optional `--max-tasks`, `--continue-on-error`).
- **`sde report`** — turn `summary.json` from a run into `report.md` / `report-meta.json`.
- **`sde replay`** — print a trajectory narrative or JSON for a run id; **`--rerun`** re-executes a single-task run from `run-manifest.json`.

The **vision** (multi-service OS, event store, memory, org-wide IAM) lives in Markdown specs under **`docs/`**. The **implementation** that tracks those specs most closely today lives under **`src/orchestrator/`** (CLI + API) and the sibling packages **`sde_pipeline`**, **`sde_modes`**, **`sde_gates`**, **`sde_foundations`**.

---

## 2. Recommended reading order (follow-through)

Do these in order the first time through. Skipping ahead makes it easy to get lost.

| Step | Document | Why |
|------|----------|-----|
| 0 | [start-here-reading-the-docs.md](start-here-reading-the-docs.md) / [start-here-reading-the-code.md](start-here-reading-the-code.md) | **Easy on-ramp** (docs side or code side). |
| 1 | [README.md](../README.md) (repo root) | Executive picture, links to all major docs. |
| 1b | [docs/onboarding/action-plan.md](action-plan.md) | **Product + delivery plan**: full-stack goal, V1–V7 rollup, safety-first precedence, parallel agents, phases. |
| 2 | [docs/sde/what.md](../sde/what.md) | **SDE baseline**: goals, timebox, models, CLI commands — what “done” means for the local tool. |
| 2b | [docs/sde/core-features-and-upstream-parity.md](../sde/core-features-and-upstream-parity.md) | **What is implemented** vs SWE-agent / OpenHands–class patterns; suggested next core work. |
| 3 | [docs/sde/implementation-contract.md](../sde/implementation-contract.md) | Required artifacts, pipeline stages, guardrails — what the runtime promises to emit. |
| 4 | [docs/architecture/operating-system-folder-structure.md](../architecture/operating-system-folder-structure.md) | **Target** folder layout; includes **“This repository (SDE orchestrator snapshot)”** mapping fantasy tree → real paths. |
| 5 | [docs/coding-agent/execution.md](../coding-agent/execution.md) | First **coding-agent extension**: strict run layout, CTO-style gates, hard-stops HS01–HS06 — how runs are *supposed* to look when the extension is fully satisfied. |
| 6 | [docs/README.md](../README.md) | Index of all extension specs and research links. |

After that, read other **`docs/coding-agent/*.md`** files as needed for the feature you touch. The master architecture is large; use [docs/architecture/architecture-goal-completion.md](../architecture/architecture-goal-completion.md) to see how extension specs relate to “full” completion.

---

## 3. Repository map (where things live)

```text
coding-agent/
├── README.md                 # Product / architecture entry
├── pyproject.toml            # Distribution name `sde`; import package `orchestrator`; CLI `sde` / `agent`
├── data/
│   └── benchmark-tasks.jsonl # Default benchmark suite (tracked)
├── docs/                     # All specifications and this walkthrough
│   ├── onboarding/           # Easy entry + this walkthrough + action plan
│   ├── architecture/         # Master blueprint, OS folder map, completion definition
│   ├── README.md             # Doc index + extension map
│   ├── coding-agent/         # Extension specs (execution, planning, …)
│   ├── sde/                    # SDE baseline (CLI, contract, prompts)
│   ├── templates/sde-demo/   # Tracked demo seed (copy to demo_apps/)
│   └── …
├── outputs/                  # Gitignored: created at repo root when you run SDE
│   └── runs/<run-id>/        # traces, summary, report, logs, …
└── src/
    ├── orchestrator/         # Import package `orchestrator` (api/, runtime/cli/, tests/unit/)
    ├── sde_pipeline/         # Runner, benchmark, report
    ├── sde_modes/            # Baseline + guarded execution modes
    ├── sde_gates/            # CTO-style gates on disk artifacts
    └── sde_foundations/      # Types, storage, utils, model adapter
```

**Important:** Run artifacts always resolve to **`<repo>/outputs/`**, not under `src/`, via `sde_foundations.utils.outputs_base()` (finds `pyproject.toml` walking up from your shell’s current directory). You should not commit anything under `outputs/`.

---

## 4. How execution flows in code (start here in the tree)

When you run `uv run sde run …` or `uv run sde benchmark …`:

1. **Entrypoint:** [`src/orchestrator/runtime/cli/main.py`](../src/orchestrator/runtime/cli/main.py) — parses arguments and dispatches.
2. **Single task:** [`sde_pipeline/runner/single_task.py`](../src/sde_pipeline/runner/single_task.py) (`execute_single_task`) — creates `run_id`, builds output dir, runs `baseline` or `guarded_pipeline`, writes JSONL traces and `summary.json`.
3. **Suite:** [`sde_pipeline/benchmark/run_benchmark.py`](../src/sde_pipeline/benchmark/run_benchmark.py) (`run_benchmark`) — loads JSONL tasks, runs baseline/guarded per task mode, aggregates metrics.
4. **Report:** [`sde_pipeline/report.py`](../src/sde_pipeline/report.py) — reads `summary.json`, writes `report.md` and `report-meta.json`.
5. **Modes:** [`sde_modes/modes/baseline/pipeline.py`](../src/sde_modes/modes/baseline/pipeline.py), [`sde_modes/modes/guarded.py`](../src/sde_modes/modes/guarded.py), [`sde_modes/modes/guarded_pipeline/pipeline.py`](../src/sde_modes/modes/guarded_pipeline/pipeline.py) — concrete execution strategies.
6. **Gates / validation:** [`sde_gates/run_directory.py`](../src/sde_gates/run_directory.py) (`validate_execution_run_directory`) — validates a run directory against strict contracts (tests and CI-style checks).

**Suggested first code read:** `orchestrator/api/__init__.py` (public surface) → `orchestrator/runtime/cli/main.py` → `sde_pipeline/runner/single_task.py` → `sde_modes/modes/guarded_pipeline/pipeline.py` (longest path) → `sde_foundations/storage.py` / `sde_pipeline/report.py`.

---

## 5. Following the folder structure (rules of thumb)

1. **Specs vs code:** If it is a *requirement* or *contract*, it belongs under **`docs/`**. If it is *executable*, it belongs under **`src/`**.
2. **Orchestrator + pipeline:** **`orchestrator/api/`**, **`orchestrator/runtime/cli/`**, **`orchestrator/tests/`** under `src/orchestrator/`; execution and gates live in **`sde_*`** siblings (see [`src/README.md`](../src/README.md)).
3. **Installable artifact:** The wheel is published as **`sde`** for CLI continuity; Python imports use **`orchestrator`** (e.g. `from orchestrator.api import execute_single_task`).
4. **Demos:** Local demos are **gitignored** under **`demo_apps/`**; copy from **`docs/templates/sde-demo/`** when you need a runnable tree (see template README there).
5. **Benchmarks:** Default suite path in docs is **`data/benchmark-tasks.jsonl`**. Paths in task prompts may reference **`demo_apps/sde-demo/`** after you copy the template.

---

## 5a. Package version and git hooks (optional)

The repo keeps the installable version in **`pyproject.toml`** under **`[project].version`** (semver `MAJOR.MINOR.PATCH`).

**Automatic bump on push (default: minor):**

1. One-time from the repo root: `sh scripts/init-git-hooks.sh`  
   (Equivalent: `git config core.hooksPath .githooks` — uses tracked hooks under **`.githooks/`**, not `.git/hooks/`.)
2. On **`git push`**, the **`.githooks/pre-push`** hook runs **`scripts/bump_version.py`**, which bumps **`minor`** by default (`0.3.0` → `0.4.0`), then creates a **`chore: bump version to …`** commit if `pyproject.toml` changed.
3. **Tag-only pushes** skip the bump (no new version commit).

**Overrides:**

| Goal | Command |
|------|---------|
| Skip bump for this push | `SKIP_VERSION_BUMP=1 git push` |
| Patch instead of minor | `VERSION_BUMP=patch git push` |
| Major | `VERSION_BUMP=major git push` |
| No file change (print current) | `VERSION_BUMP=none git push` |

Manual bump without pushing: `VERSION_BUMP=minor python3 scripts/bump_version.py` (writes `pyproject.toml` and prints the new version on stdout).

---

## 6. First day checklist (hands-on)

From the repository root:

1. **Python env:** `uv sync --group dev` (uses `pyproject.toml`).
2. **Sanity tests:** `uv run pytest src/orchestrator/tests/` — should be green before you rely on local changes.
3. **Optional smoke (needs local Ollama/models per docs):**  
   `uv run sde run --mode baseline --task "return the string hello"`  
   If models are missing, expect failures; that is an environment issue, not necessarily your code.
4. **Inspect a run:** After a successful run, open **`outputs/runs/<run-id>/summary.json`** and **`traces.jsonl`** and map fields to [implementation-contract.md](../sde/implementation-contract.md).

---

## 7. How to contribute safely

- **Small changes:** Match existing style; keep imports at top of files; extend tests beside **`src/orchestrator/tests/unit/`**.
- **Contracts:** If you change artifact names or schemas, update **`docs/sde/implementation-contract.md`** and any **`docs/coding-agent/*.md`** that references those paths, then adjust **`sde_gates/`** and tests.
- **CI:** [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs `compileall` on `src/` and pytest — keep both green.

---

## 8. Where to ask “what does X mean?”

| Topic | Document |
|-------|----------|
| CLI commands, models, timebox | [docs/sde/what.md](../sde/what.md) |
| Artifact list, pipeline order | [docs/sde/implementation-contract.md](../sde/implementation-contract.md) |
| Run directory layout, gates, HS01+ | [docs/coding-agent/execution.md](../coding-agent/execution.md) |
| Repo vs master OS tree | [docs/architecture/operating-system-folder-structure.md](../architecture/operating-system-folder-structure.md) |
| Extension ladder, hard-stop index | [Documentation index](../README.md) |
| Full platform vision | [docs/architecture/AI-Professional-Evolution-Master-Architecture.md](../architecture/AI-Professional-Evolution-Master-Architecture.md) |

---

## 9. Glossary (quick)

| Term | Meaning |
|------|---------|
| **SDE** | Local CLI/runtime package (`sde`) for run / benchmark / report / replay + static gates on disk. |
| **Baseline** | Simpler execution mode used for A/B comparison. |
| **Guarded pipeline** | Multi-stage pipeline (planner → executor → verifier, …). |
| **Extension spec** | A document under **`docs/coding-agent/`** describing a capability slice beyond the SDE baseline. |
| **`outputs_base()`** | Resolves the directory containing **`runs/`** — normally repo root **`outputs/`**. |

You now have a path from **README → SDE docs → folder map → CLI entry → run artifacts**. Use the doc index [docs/README.md](../README.md) whenever you need the full list of specs.
