# Core SDE features and upstream parity (post-pull checklist)

**In plain words:** after you **pull latest `main`**, use this page to see what the **local `sde` CLI** already does versus patterns in mature **coding-agent harnesses** (e.g. SWE-agent, OpenHands). It is **not** a line-by-line port list; it is the **contract** for what is implemented in *this* repo today and what remains **reasonable next work** under the **local-only** product decision.

**Related:** license notes when copying from upstream trees — [`upstream-harvest-licenses.md`](upstream-harvest-licenses.md). Trajectory / replay design notes — [`../superpowers/specs/2026-04-18-sde-trajectory-replay-cli-design.md`](../superpowers/specs/2026-04-18-sde-trajectory-replay-cli-design.md).

---

## Implemented core features (this repo)

| Area | What you get | Primary code / artifacts |
|------|----------------|---------------------------|
| **Staged pipeline** | `baseline` vs `guarded_pipeline` (planner → executor → verifier → optional fix → finalize) | `src/sde_modes/modes/`, `traces.jsonl` |
| **CTO-style gates** | `review.json`, `token_context.json`, `balanced_gates`, `validation_ready`, hard-stops **HS01–HS06** | `src/sde_gates/`, [`execution.md`](../coding-agent/execution.md) |
| **Static code + security gates** | `static_gates_report.json`: AST parse, high-signal dangerous patterns, optional **`ruff`**, **`bandit`**, **`basedpyright`/`pyright`** on `PATH`; failures in **verifier** and **HS04** | `src/sde_gates/static_analysis.py`, `verifier_report` |
| **Run manifests** | `run-manifest.json` for every `sde run` (task + mode + run_id) | `src/sde_pipeline/runner/single_task.py` |
| **Benchmark manifests + batch ergonomics** | `benchmark-manifest.json`, **`benchmark-checkpoint.json`** (per-task); `--max-tasks`, `--continue-on-error`, **`--resume-run-id`** | `src/sde_pipeline/benchmark/` |
| **Trajectory narrative + rerun** | `sde replay --run-id …` (`--format json|html`, `--write-html` → `trajectory.html`, `--rerun` for single-task from manifest) | `src/sde_pipeline/replay.py`, CLI |
| **Input safety (keyword refusal)** | Expanded refusal markers in task text | `src/sde_foundations/safeguards.py` |
| **Verifier checklist (docs)** | Heuristic checklist for prompts / review culture | [`prompts/verifier-heuristic-checklist.md`](prompts/verifier-heuristic-checklist.md) |

---

## Parity with SWE-agent / OpenHands (local CLI scope)

**Deliberately not targeted here:** Docker sandboxes, remote runtimes (E2B, Daytona, …), browser tools, full repo edit/test loops inside a container. Those are **infra-heavy**; this SDE stays a **local Ollama-first CLI** unless the product explicitly expands.

| Upstream theme | In this repo today | Gap / next step (still local) |
|----------------|-------------------|------------------------------|
| Trajectories + inspect | `traces.jsonl`, `orchestration.jsonl`, `sde replay`, `run.log`, **`trajectory.html`** via `--write-html` or `--format html` | Richer tables / filters (optional future) |
| Batch / suite | `sde benchmark` + manifests + caps + **checkpoint resume** | Suite **versioning** in summary (optional polish) |
| Lint / security | `static_gates_report.json` + optional `ruff` / `bandit` / `basedpyright`/`pyright` | Tune severities; add **`semgrep`** optional profile (future) |
| Reviewer agent | Heuristic verifier + `review.json` gate_snapshot | Optional **second-pass LLM reviewer** behind flag (tokens + contract) |
| Skills / playbooks | `docs/sde/prompts/*` | Keep prompts **versioned** next to gate changes |

---

## Suggested implementation order (core only)

1. ~~**Optional linters** — `bandit` / `basedpyright`~~ **Done** — same “binary on `PATH`” pattern as `ruff`; see `static_gates_report.json` keys `bandit` / `basedpyright`.
2. ~~**Trajectory viewer**~~ **Done (MVP)** — `sde replay --write-html` or `--format html` writes / prints `trajectory.html` under the run directory.
3. ~~**Benchmark resume**~~ **Done** — `benchmark-checkpoint.json` + `sde benchmark --resume-run-id <run_id>`; traces append per task so partial progress survives crashes.

When any remaining item ships, update **`what.md`**, this file, and **`implementation-contract.md`** in the same PR.
