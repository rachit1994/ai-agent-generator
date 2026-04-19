# Reading the documentation

**In plain words:** you **do not** need this page if you are here to **ship code**. Use **[`../ESSENTIAL.md`](../ESSENTIAL.md)** instead — it is the **only** required reading list (plus `src/` READMEs).

---

## When this page helps

Skim here if you want a **glossary** or a **story** about why the project exists before you read anything else. None of that is required to navigate **`src/`** or run **`sde`**.

| Word | In everyday terms |
|------|-------------------|
| **SDE** | The **local `sde` CLI** — run tasks, benchmarks, project sessions, etc. |
| **Orchestrator** | The **Python package** that wraps the pipeline and prints the CLI. |
| **CTO gates / hard-stops** | **Automatic checks** on run output; if they fail, the run is not “green.” |
| **V1–V7** | **Labels** for slices of one roadmap in the **action plan**; Markdown specs under **`docs/coding-agent/`** were **removed**—gates live in **`src/sde_gates/`**. |
| **Stage 1 / plan lock** | Session **`intake/`**, **`sde project plan-lock`**, **`validate --require-plan-lock`**, optional **`run` / `continuous` + `--enforce-plan-lock`** (and strict reviewer flags / **`SDE_REQUIRE_NON_STUB_REVIEWER`**). See **`docs/sde/project-driver.md`** and **`docs/runbooks/stage1-intake-failures.md`**. |

---

## If you want the full story later

- **Product flow:** [`action-plan.md`](action-plan.md)
- **Full doc index (lookup):** [`../README.md`](../README.md)

---

## Changelog

- **2026-04-19:** Glossary row for **Stage 1 / plan lock** (pointers to **project-driver** + intake runbook).
- **2026-04-18 (later):** Noted removal of **`docs/coding-agent/*`** versioned Markdown specs.
- **2026-04-18:** Page trimmed; **canonical path** is now [`../ESSENTIAL.md`](../ESSENTIAL.md).
