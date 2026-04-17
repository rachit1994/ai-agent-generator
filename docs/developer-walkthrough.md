# Developer walkthrough

This guide is for engineers who are new to the repository. It tells you **what to read first**, **how the code is organized**, **what the system does at a high level**, and **how to run and change things safely**.

---

## 1. What this repository is

This project is an **architecture and local-runtime workspace** for an *AI Professional Evolution* style system: long-horizon, auditable agent execution with gates, benchmarks, and a path toward full platform capabilities described in the master document.

**What actually runs in code today** is the **SDE** (local CLI) package: a Python tool that can:

- **`sde run`** — execute a single task in `baseline` or `guarded_pipeline` mode and write a run directory under **`outputs/runs/<run-id>/`** at the **repository root**.
- **`sde benchmark`** — run a suite of tasks (JSONL) in baseline and/or guarded mode and aggregate metrics into a benchmark run directory.
- **`sde report`** — turn `summary.json` from a run into `report.md` / `report-meta.json`.

The **vision** (multi-service OS, event store, memory, org-wide IAM) lives in Markdown specs under **`docs/`**. The **implementation** that tracks those specs most closely today lives under **`src/services/orchestrator/orchestrator/runtime/`**.

---

## 2. Recommended reading order (follow-through)

Do these in order the first time through. Skipping ahead makes it easy to get lost.

| Step | Document | Why |
|------|----------|-----|
| 1 | [README.md](../README.md) (repo root) | Executive picture, links to all major docs. |
| 2 | [docs/sde/what.md](sde/what.md) | **SDE baseline**: goals, timebox, models, CLI commands — what “done” means for the local tool. |
| 3 | [docs/sde/implementation-contract.md](sde/implementation-contract.md) | Required artifacts, pipeline stages, guardrails — what the runtime promises to emit. |
| 4 | [docs/operating-system-folder-structure.md](operating-system-folder-structure.md) | **Target** folder layout; includes **“This repository (SDE orchestrator snapshot)”** mapping fantasy tree → real paths. |
| 5 | [docs/coding-agent/execution.md](coding-agent/execution.md) | First **coding-agent extension**: strict run layout, CTO-style gates, hard-stops HS01–HS06 — how runs are *supposed* to look when the extension is fully satisfied. |
| 6 | [docs/README.md](README.md) | Index of all extension specs and research links. |

After that, read other **`docs/coding-agent/*.md`** files as needed for the feature you touch. The master architecture is large; use [docs/architecture-goal-completion.md](architecture-goal-completion.md) to see how extension specs relate to “full” completion.

---

## 3. Repository map (where things live)

```text
coding-agent/
├── README.md                 # Product / architecture entry
├── pyproject.toml            # Distribution name `sde`; import package `orchestrator`; CLI `sde` / `agent`
├── data/
│   └── benchmark-tasks.jsonl # Default benchmark suite (tracked)
├── docs/                     # All specifications and this walkthrough
│   ├── developer-walkthrough.md   # ← you are here
│   ├── README.md             # Doc index + extension map
│   ├── coding-agent/         # Extension specs (execution, planning, …)
│   ├── sde/                    # SDE baseline (CLI, contract, prompts)
│   ├── templates/sde-demo/   # Tracked demo seed (copy to demo_apps/)
│   └── …
├── outputs/                  # Gitignored: created at repo root when you run SDE
│   └── runs/<run-id>/        # traces, summary, report, logs, …
└── src/
    └── services/
        └── orchestrator/     # Service shell
            ├── orchestrator/ # Import package root
            │   ├── api/      # Public re-exports (other services import here)
            │   └── runtime/  # CLI, modes, gates, storage, …
            └── tests/
                └── unit/     # Pytest
```

**Important:** Run artifacts always resolve to **`<repo>/outputs/`**, not under `src/`, via `orchestrator.runtime.utils.outputs_base()` (finds `pyproject.toml` walking up from your shell’s current directory). You should not commit anything under `outputs/`.

---

## 4. How execution flows in code (start here in the tree)

When you run `uv run sde run …` or `uv run sde benchmark …`:

1. **Entrypoint:** [`src/services/orchestrator/orchestrator/runtime/cli/main.py`](../src/services/orchestrator/orchestrator/runtime/cli/main.py) — parses arguments and dispatches.
2. **Single task:** [`runner.py`](../src/services/orchestrator/orchestrator/runtime/runner.py) — `execute_single_task`: creates `run_id`, builds output dir, runs `baseline` or `guarded_pipeline`, writes JSONL traces and `summary.json`.
3. **Suite:** [`benchmark.py`](../src/services/orchestrator/orchestrator/runtime/benchmark.py) — loads JSONL tasks, runs baseline/guarded per task mode, aggregates metrics.
4. **Report:** [`report.py`](../src/services/orchestrator/orchestrator/runtime/report.py) — reads `summary.json`, writes `report.md` and `report-meta.json`.
5. **Modes:** [`modes/baseline.py`](../src/services/orchestrator/orchestrator/runtime/modes/baseline.py), [`modes/guarded.py`](../src/services/orchestrator/orchestrator/runtime/modes/guarded.py), [`modes/guarded_pipeline.py`](../src/services/orchestrator/orchestrator/runtime/modes/guarded_pipeline.py) — concrete execution strategies.
6. **Gates / validation:** [`cto_gates.py`](../src/services/orchestrator/orchestrator/runtime/cto_gates.py) — helpers to validate a run directory against strict contracts (used in tests and for CI-style checks).

**Suggested first code read:** `orchestrator/api/__init__.py` (public surface) → `cli/main.py` → `runner.py` → `modes/guarded_pipeline.py` (longest path) → `storage.py` / `report.py`.

---

## 5. Following the folder structure (rules of thumb)

1. **Specs vs code:** If it is a *requirement* or *contract*, it belongs under **`docs/`**. If it is *executable*, it belongs under **`src/`**.
2. **Orchestrator service:** Layout matches the OS doc: **`orchestrator/api/`**, **`orchestrator/runtime/`**, **`tests/`** under `src/services/orchestrator/` — see [orchestrator README](../src/services/orchestrator/README.md).
3. **Installable artifact:** The wheel is published as **`sde`** for CLI continuity; Python imports use **`orchestrator`** (e.g. `from orchestrator.api import execute_single_task`).
4. **Demos:** Local demos are **gitignored** under **`demo_apps/`**; copy from **`docs/templates/sde-demo/`** when you need a runnable tree (see template README there).
5. **Benchmarks:** Default suite path in docs is **`data/benchmark-tasks.jsonl`**. Paths in task prompts may reference **`demo_apps/sde-demo/`** after you copy the template.

---

## 6. First day checklist (hands-on)

From the repository root:

1. **Python env:** `uv sync --group dev` (uses `pyproject.toml`).
2. **Sanity tests:** `uv run pytest src/services/orchestrator/tests/` — should be green before you rely on local changes.
3. **Optional smoke (needs local Ollama/models per docs):**  
   `uv run sde run --mode baseline --task "return the string hello"`  
   If models are missing, expect failures; that is an environment issue, not necessarily your code.
4. **Inspect a run:** After a successful run, open **`outputs/runs/<run-id>/summary.json`** and **`traces.jsonl`** and map fields to [implementation-contract.md](sde/implementation-contract.md).

---

## 7. How to contribute safely

- **Small changes:** Match existing style; keep imports at top of files; extend tests beside **`src/services/orchestrator/tests/unit/`**.
- **Contracts:** If you change artifact names or schemas, update **`docs/sde/implementation-contract.md`** and any **`docs/coding-agent/*.md`** that references those paths, then adjust **`cto_gates.py`** and tests.
- **CI:** [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs `compileall` on `src/services/orchestrator/orchestrator` and pytest — keep both green.

---

## 8. Where to ask “what does X mean?”

| Topic | Document |
|-------|----------|
| CLI commands, models, timebox | [docs/sde/what.md](sde/what.md) |
| Artifact list, pipeline order | [docs/sde/implementation-contract.md](sde/implementation-contract.md) |
| Run directory layout, gates, HS01+ | [docs/coding-agent/execution.md](coding-agent/execution.md) |
| Repo vs master OS tree | [docs/operating-system-folder-structure.md](operating-system-folder-structure.md) |
| Extension ladder, hard-stop index | [Documentation index](README.md) |
| Full platform vision | [docs/AI-Professional-Evolution-Master-Architecture.md](AI-Professional-Evolution-Master-Architecture.md) |

---

## 9. Glossary (quick)

| Term | Meaning |
|------|---------|
| **SDE** | Local CLI/runtime package (`sde`) for run / benchmark / report. |
| **Baseline** | Simpler execution mode used for A/B comparison. |
| **Guarded pipeline** | Multi-stage pipeline (planner → executor → verifier, …). |
| **Extension spec** | A document under **`docs/coding-agent/`** describing a capability slice beyond the SDE baseline. |
| **`outputs_base()`** | Resolves the directory containing **`runs/`** — normally repo root **`outputs/`**. |

You now have a path from **README → SDE docs → folder map → CLI entry → run artifacts**. Use the doc index [docs/README.md](README.md) whenever you need the full list of specs.
