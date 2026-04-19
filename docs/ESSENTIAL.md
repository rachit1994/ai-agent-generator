# Essential reading (follow the code)

**In plain words:** the repo still has **long** architecture Markdown and research notes. **You do not read those** to work on the Python CLI day to day. Read **only** what is below, in order, then open the code files they point to.

---

## 1 — What the tool does

Read **[`sde/what.md`](sde/what.md)** once. It lists every **`sde`** command, models, and where **`outputs/`** lives. That is the product surface.

---

## 2 — Where the code lives (no extra doc)

Open these **in the repo** (they are the real map):

| Order | Path | Why |
|-------|------|-----|
| 1 | [`src/README.md`](../src/README.md) | Packages (`orchestrator`, `sde_*`) and pipeline **layer** files. |
| 2 | [`src/orchestrator/api/README.md`](../src/orchestrator/api/README.md) | Every **`from orchestrator.api import …`** symbol and what it does. |
| 3 | [`src/orchestrator/runtime/cli/main.py`](../src/orchestrator/runtime/cli/main.py) | CLI arguments → API calls. |

Then jump to the one module you need (e.g. `project_driver.py`, `single_task.py`). Use your editor’s search.

---

## 3 — Only when your change touches contracts

| You change… | Read this (still one doc each) |
|-------------|--------------------------------|
| Filenames under a run dir, pipeline stages, “what must exist” for CI | [`sde/implementation-contract.md`](sde/implementation-contract.md) |
| CTO gates, hard-stops **HS01–HS06**, balanced run layout | **`src/sde_gates/`** (especially `run_directory.py`, `hard_stops*.py`, `static_analysis.py`) and matching tests under **`src/orchestrator/tests/unit/`**. |

---

## 4 — Only for `sde project …` / session plans

Read **[`sde/project-driver.md`](sde/project-driver.md)** (including the **Stage 1 plan lock** section for `validate` / `project run` / `continuous` flags and `SDE_REQUIRE_NON_STUB_REVIEWER`). Ignore until you touch **`orchestrator/api/project_*.py`** or **`sde project`** / project **`continuous`** paths in **`main.py`**.

---

## 5 — Everything else

**Optional reference only** (do not read front-to-back): [`README.md`](README.md) lists folders and deep links. Architecture docs are for **big design** work, not for “where do I add a flag.”

---

## Check before you push

```bash
uv sync --group dev
uv run pytest src/orchestrator/tests/unit -q
```

**`.python-version`** at the repo root pins **3.11** for **`uv`**. If **`uv run python -V`** is not **3.11.x**, install that toolchain or run **`uv run --python 3.11 pytest src/orchestrator/tests/unit -q`** so you match **CI** (`.github/workflows/ci.yml`). If **`git config --get core.hooksPath`** is **`.githooks`**, a normal **`git push`** may auto-commit a **minor** `sde` version bump — use **`SKIP_VERSION_BUMP=1 git push`** when you do not want that (see **[`onboarding/developer-walkthrough.md`](onboarding/developer-walkthrough.md)**).
