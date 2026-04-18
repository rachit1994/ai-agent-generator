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

---

## Prove a change

```bash
uv sync --group dev
uv run pytest src/orchestrator/tests/unit -q
```

---

## Changelog

- **2026-04-18:** Page trimmed; **canonical path** is [`../ESSENTIAL.md`](../ESSENTIAL.md).
