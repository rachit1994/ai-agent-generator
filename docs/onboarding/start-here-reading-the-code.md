# Reading the code — where to start

This page explains **what the code is for**, **where it lives**, and **which files to open first** so the tree feels less overwhelming. It pairs with **[start-here-reading-the-docs.md](start-here-reading-the-docs.md)**, which walks the documentation side the same way.

---

## Words you will keep seeing

| Word | In everyday terms |
|------|-------------------|
| **Repository** | The **project folder**: code, docs, and config kept together. |
| **Python** | The language most of the runnable pieces here are written in. |
| **CLI** | You type a **command in a terminal** instead of clicking through a separate app window. |
| **`sde` / `agent`** | The **command names** after you install this project. Both run the same entrypoint (see `pyproject.toml` at the repo root). |
| **`src/orchestrator/`** | The **front door**: CLI wiring and the small public API that pulls the rest in. |
| **`outputs/`** | A folder the tool **creates when it runs** (often not checked into git). Each run gets its own subfolder with logs and results. |
| **Test** | A **small automatic check** that locks in expected behavior. |

---

## How the code side fits the plan

The **detailed behavior** lives in `docs/` first so everyone shares the same picture of “good.” The **Python under `src/`** implements the **early slices** of that picture: run a task, write a run folder, compare baseline vs guarded modes, and run CTO-style checks on disk.

**Versions V4–V7** (events, memory, evolution, parallel org) are **mostly spelled out in Markdown for now**; the code will grow to match. If you only read code, the project can look “small”; if you read docs too, you see the **full roadmap**.

---

## Where the pieces live (simple map)

```text
coding-agent/                         ← project root
├── pyproject.toml                    ← how `sde` / `agent` start; which packages ship in the wheel
├── docs/                             ← behavior spelled out in words (not executable)
└── src/
    ├── README.md                     ← short pointers into the tree
    ├── orchestrator/                 ← CLI + public API
    │   ├── api/__init__.py           ← wires in single-task, benchmark, report from sde_pipeline
    │   ├── runtime/cli/main.py       ← **good first file** — where `sde run` / `sde benchmark` start
    │   └── tests/unit/               ← pytest checks
    ├── sde_pipeline/                 ← one task, benchmarks, reports, writing run artifacts
    │   └── runner/single_task.py     ← creates a run id and the output folder
    ├── sde_modes/                    ← baseline vs guarded_pipeline (how a task is executed)
    │   └── modes/baseline|guarded_pipeline/pipeline.py
    ├── sde_gates/                    ← checks a run folder against the rules (e.g. run_directory.py)
    └── sde_foundations/              ← types, safeguards, eval helpers, paths
```

**Master OS scaffold** (extra `contracts/`, `services/`, `tools/`, …) is described in [`operating-system-folder-structure.md`](operating-system-folder-structure.md) as a **target** layout; this repo keeps **`src/`** flat with only the runnable packages above.

---

## A simple path through the files

Go **in order** below. Roughly **15–30 minutes** each the first time is plenty.

### Step 1 — Where the command starts

Open **`src/orchestrator/runtime/cli/main.py`**.

Look for **`main`** or argument parsing — that is where a typed command like `sde run …` **enters** the program.

### Step 2 — How one task becomes one folder of output

Open **`src/sde_pipeline/runner/single_task.py`**.

Look for where a **run id** is created and a folder under **`outputs/runs/<run-id>/`** appears. That folder is the **job packet** for one run.

### Step 3 — The two ways to execute a task

Open:

- **`src/sde_modes/modes/baseline/pipeline.py`** — short path: task → model → output.
- **`src/sde_modes/modes/guarded_pipeline/pipeline.py`** — longer path: plan → execute → verify → optional fix.

**Everyday read:** baseline is closer to **one pass**; guarded pipeline is closer to **outline → draft → edit**.

### Step 4 — Where “CTO gates” hit the disk

Open **`src/sde_gates/run_directory.py`** and find **`validate_execution_run_directory`**.

That function **reads what the run wrote** and checks it against the **rules in the docs** (for example: review file present, token file present).

### Step 5 — How behavior stays pinned down

Open anything under **`src/orchestrator/tests/unit/`**.

Tests are **living examples** of what “correct” means. If you change code and a test fails, you touched something the team cares about.

---

## How versions (V1–V7) line up with code **today**

| Version | Where it mostly lives in code (today) | What you will actually find |
|---------|----------------------------------------|------------------------------|
| **V1** Execution | `sde_modes/`, `sde_gates/`, `sde_pipeline/` (under `src/`) | Run folders, traces, reviews, gate checks — **closest to built**. |
| **V2** Planning | Target repo `.agent/sde/` + future orchestrator wiring | **Largely spec** for now. |
| **V3** Completion | Step loop + verification (overlaps guarded pipeline) | **Spec ahead** of a full dedicated loop in places. |
| **V4–V7** | Planned modules | **Mostly docs** today. |

So: **start reading where V1 lives.** Use the specs to see **what comes next**.

---

## Optional: run it once

From the project root (adjust if your team uses a different setup):

1. `uv sync --group dev`
2. `uv run pytest src/orchestrator/tests/unit -q`
3. `uv run sde run --mode baseline --task "return the string hello"`

If step 3 fails because no model is installed, that is usually **setup on the machine**, not a sign you read the wrong file.

---

## If something feels confusing

| Situation | Try this |
|-----------|----------|
| Heavy jargon | Skim the word list at the top of [start-here-reading-the-docs.md](start-here-reading-the-docs.md), then come back. |
| Huge file | Read only the **top** (imports + first function). Drill down later. |
| Doc says X, code does not | Check **which version** the doc is for — early versions land in code first. |
| Want a path with more file names | [developer-walkthrough.md](developer-walkthrough.md) §3–4 |

---

## Changelog

- **2026-04-18:** Flattened `src/` paths (`sde_*` at top level; removed unused OS placeholder trees).
- **2026-04-18:** First version of this guide.
