# Coding-agent specs (removed)

**In plain words:** the old **V1–V7** Markdown specs that lived here (**execution**, **planning**, **completion**, **events**, **memory**, **evolution**, **organization**) were **deleted**. Behavior and contracts now live in **code** and a small set of SDE docs.

**Where to look instead:**

- **[`../ESSENTIAL.md`](../ESSENTIAL.md)** — minimum reading list.
- **[`../sde/implementation-contract.md`](../sde/implementation-contract.md)** — what a run should write.
- **[`../sde/project-driver.md`](../sde/project-driver.md)** — session **`sde project`** / **`continuous`** driver (including **Stage 1 plan lock** flags and **`SDE_REQUIRE_NON_STUB_REVIEWER`**).
- **[`../runbooks/stage1-intake-failures.md`](../runbooks/stage1-intake-failures.md)** — operator triage for Stage 1 intake + lock readiness.
- **`../../src/sde_gates/`** — CTO gates and hard-stops (**HS01+** in module names and tests).

This folder stays as a **stub** so old links fail loudly with this explanation.

---

## Changelog

- **2026-04-19:** Pointed stub readers at **project-driver** (Stage 1) + **stage1-intake-failures** runbook.
- **2026-04-18:** Removed **execution**, **planning**, **completion**, **events**, **memory**, **evolution**, **organization** Markdown specs; updated cross-links across the repo.
