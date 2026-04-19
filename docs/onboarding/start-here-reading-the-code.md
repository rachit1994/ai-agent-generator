# Reading the code

**In plain words:** start with **[`../ESSENTIAL.md`](../ESSENTIAL.md)**. It tells you which **four** Markdown files matter (at most), then sends you straight to **`src/README.md`**, **`src/orchestrator/api/README.md`**, and **`main.py`**.

---

## Tiny map (after you read `ESSENTIAL.md`)

```text
src/
├── README.md                 ← packages + *layer.py list
├── orchestrator/
│   ├── api/README.md         ← public Python API
│   └── runtime/cli/main.py   ← CLI entry
├── sde_pipeline/runner/      ← single_task.py + post-run layers
├── sde_modes/                ← baseline / guarded_pipeline
├── sde_gates/                ← validate_execution_run_directory, hard_stops_*
└── sde_foundations/          ← paths, storage, model adapter
```

**Outputs:** runs write under repo-root **`outputs/`** (usually gitignored).

**Project sessions** (`sde project …`, `sde continuous` with `--project-plan` / `--project-session-dir`): implementation under **`src/orchestrator/api/`** — start with **`project_driver.py`**, **`project_plan_lock.py`**, **`project_validate.py`**, **`continuous_run.py`**, **`project_status.py`**; CLI switches in **`orchestrator/runtime/cli/main.py`**. Operator flow + Stage 1 lock flags / **`SDE_REQUIRE_NON_STUB_REVIEWER`**: **`docs/sde/project-driver.md`** and **`docs/runbooks/stage1-intake-failures.md`**.

---

## Prove a change

```bash
uv sync --group dev
uv run pytest src/orchestrator/tests/unit -q
# If your default Python is 3.12+, match CI (3.11):
# uv run --python 3.11 pytest src/orchestrator/tests/unit -q
```

---

## Changelog

- **2026-04-19:** Added **project session** file pointers + Stage 1 / runbook links (same surface as glossary in [`start-here-reading-the-docs.md`](start-here-reading-the-docs.md)).
- **2026-04-18:** Page trimmed; **canonical path** is [`../ESSENTIAL.md`](../ESSENTIAL.md).
