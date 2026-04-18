# SDE project driver (meta-orchestrator)

**In plain words:** this is the **session-level** loop that sits **above** `sde run`: it owns a **real** `project_plan.json` (atomic `step_id`s, `depends_on`, per-step verification commands, `path_scope`), runs **`execute_single_task`** once per runnable step with a **bounded context pack**, runs **orchestrator verification** after each step, and only then advances `progress.json`. Per-run `outputs/runs/<id>/program/project_plan.json` from the V3 harness remains a **separate** CTO skeleton for that run; do not overwrite it with the session plan.

**Gap inventory sync:** this feature closes **Category 1** (context packs + optional repo index; **Phase 2** adds prior-run excerpts + session-level truncation provenance aligned with HS03 pairing), **Category 2** (repo-backed plan + orchestrator-only advancement; **Phase 3** adds session **DoD** + verification aggregate), **Category 4** (outer driver + verification-backed progress; **Phase 4** adds **``stop_report.json``** + terminal ``exit_code`` / ``stopped_reason`` on ``driver_state.json``; **Phase 5** adds ``continuous --project-plan`` and optional ``--progress-file``; `validation_ready` on each run is still **per-run**, not “product shipped”; session **``definition_of_done.json``** is the product-level bar when the driver finishes green; ``--stop-when`` applies to **task** ``continuous`` only), **Category 5** (workspace fields on the plan; **Phase 7** enforces optional ``workspace.branch`` via git and ``workspace.allowed_path_prefixes`` against each step’s ``path_scope`` when prefixes are set). **Category 3** (parallel lanes): **Phase 6** adds optional **isolated worktrees** when you pass **`--parallel-worktrees`** and the repo has **git** (``.git`` present); otherwise `max_concurrent_agents` > 1 still only **schedules** disjoint `path_scope` steps and runs them **sequentially** on the main checkout. **Phase 8** prunes **stale** ``leases.json`` rows by heartbeat age (default **86400s** unless ``workspace.lease_ttl_sec`` or CLI ``--lease-stale-sec``) and treats **persisted** non-stale leases as **conflicts** in ``try_acquire`` so a crashed tick cannot deadlock the next session forever. **Phase 9** adds **`sde project validate`** (read-only plan + cycle + optional workspace checks; optional ``progress.json`` conformance warnings) for CI preflight without executing steps. **Phase 10** adds **`sde project status`** (read-only JSON snapshot: plan health, progress body, ``driver_state`` / ``stop_report``, lease row count, and **next_tick_batch** hint from the scheduler). **Phase 11** adds append-only **`session_events.jsonl`** (``session_driver_start``, per-iteration ``tick``, terminal ``session_terminal``) for lightweight audit trails; ``project status`` reports ``line_count`` and the **last** parsed event. **Phase 12** extends **`sde project status`** / :func:`describe_project_session` with embedded bodies for **`verification_aggregate.json`** and **`definition_of_done.json`**, plus **`step_runs.jsonl`** line count and **last** row (same read-only contract). **Phase 13** caps embedded JSON reads and large JSONL scans: bodies omit with ``body_omitted`` + ``byte_len`` past a byte budget; ``session_events`` / ``step_runs`` past a scan budget omit exact ``line_count`` and derive ``last`` from a tail window only. **Phase 14** extends status with ``context_pack_lineage`` (same JSONL contract as session events), plus directory summaries for ``context_packs/`` and ``verification/`` (file counts + capped sorted ``step_ids``). **Phase 15** embeds ``leases.json`` under the Phase 13 JSON cap (with ``active_row_count_omitted`` when the body is skipped) and lists ``_worktrees/`` as ``parallel_worktrees`` (capped ``step_ids``). **Phase 16** adds ``plan_step_rollups`` (per-``step_id`` verification file presence, context-pack file presence, and ``aggregate_passed`` when the aggregate body is embedded; list length uses the same cap as ``--status-max-listed-step-ids``). **Phase 17** adds ``step_runs.by_step`` (latest ``run_id`` / ``output_dir`` per ``step_id``) when ``step_runs.jsonl`` is under the JSONL full-scan cap, plus matching ``latest_run_id`` / ``latest_output_dir`` on rollup rows; otherwise ``by_step_omitted``. **Phase 18** adds ``repo_snapshot`` (read-only ``git rev-parse`` for ``HEAD`` / short SHA / branch when ``repo_root`` is set and ``.git`` exists; ``reason`` when ``repo_root`` is omitted). **Phase 19** adds ``workspace_status`` (echo plan ``workspace`` plus ``branch_commit_match`` / detail from the same ``git_head_matches_branch`` check as Phase 7 when git is available). **Phase 20** adds ``path_prefix_errors`` / ``path_prefixes_configured`` / ``path_prefixes_ok`` on ``workspace_status`` (same rules as :func:`plan_workspace_path_errors` / Phase 7 plan validation). **Phase 21** adds ``status_at_a_glance`` on :func:`describe_project_session` / ``sde project status``: compact derived booleans and counts (plan health, runnable / next-tick sizes, driver and stop exit codes when embedded, DoD / aggregate hints, workspace prefix + branch echo, ``step_runs`` indexability) plus ``red_flags`` (``dependency_cycle`` vs generic plan failure, ``workspace_path_prefix_mismatch``, ``workspace_branch_mismatch``).

---

## Session directory layout

All paths are relative to a chosen **session directory** (e.g. `.agent/sde/projects/my-feature/`):

| File / directory | Purpose |
|------------------|---------|
| `project_plan.json` | Authoritative plan (`schema_version` **1.0**). |
| `progress.json` | `completed_step_ids`, `pending_step_ids`, `blocked_reason`, last run pointers. |
| `driver_state.json` | `status`: `running` \| `completed_review_pass` \| `blocked_human` \| `exhausted_budget` \| `dependency_cycle` \| `invalid_session`; budget counters; on terminal outcomes **`exit_code`** + **`stopped_reason`** (mirrors CLI exit). |
| `stop_report.json` | **Phase 4:** CI-oriented snapshot (`exit_code`, `stopped_reason`, `driver_status`, budget, `block_detail`, `ci.exit_code_meaning` + exit-code legend). Written on **every** terminal session outcome (including invalid plan). |
| `step_runs.jsonl` | Append-only map `step_id` → SDE `run_id` / `output_dir`. |
| `verification/<step_id>.json` | Orchestrator-run command results for that step. |
| `verification_aggregate.json` | **Phase 3:** roll-up of every plan step’s verification bundle (presence, ``passed``, timestamps); refreshed after each successful step. |
| `definition_of_done.json` | **Phase 3:** session **DoD** (not per-run ``review.json``): ``plan_graph_complete`` + ``aggregate_verification`` checks; ``all_required_passed`` only when driver status is ``completed_review_pass`` and both checks pass. |
| `context_packs/<step_id>.json` | Capped markdown + metadata injected into the task string (`schema_version` **1.1**): prior-dep excerpts, **HS03-style** ``truncation_events`` / ``reductions`` when capped, ``markdown_sha256_full``. |
| `context_pack_lineage.jsonl` | Append-only audit of each pack build (step_id, sha256, truncated, ``truncation_hs03_ok``). |
| `leases.json` | Path lease audit trail (MVP; overlap detection uses plan scopes). **Phase 8:** rows older than the lease TTL are pruned each driver tick; ``try_acquire`` also blocks on **fresh** persisted rows from other ``step_id``s. |
| `_worktrees/<step_id>/` | **Phase 6:** ephemeral detached git worktrees for a parallel tick (removed after the batch). |
| `session_events.jsonl` | **Phase 11:** append-only driver events (``session_driver_start``, ``tick``, ``session_terminal``); schema **1.0** per line. |

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

---

## CLI

- `sde project run (--session-dir <path> | --plan <path/to/project_plan.json>) [--repo-root <path>] [--max-steps N] [--mode ...] [--max-concurrent-agents K] [--progress-file <path>] [--parallel-worktrees] [--lease-stale-sec N]` — **`--plan`** is the file path to the authoritative plan; the **session directory** is the file’s parent. **`--progress-file`** (Phase 5) stores `progress.json` elsewhere. **`--parallel-worktrees`** (Phase 6) runs a multi-step tick in detached git worktrees when applicable. **`--lease-stale-sec`** (Phase 8) sets the lease stale TTL in seconds (**0** = disable pruning; overrides ``workspace.lease_ttl_sec``).
- `sde continuous (--project-session-dir <path> | --project-plan <path/to/project_plan.json>) [--progress-file <path>] [--parallel-worktrees] [--lease-stale-sec N] ...` — same driver as `sde project run`, reuses `--max-iterations` as the step budget. **`--stop-when`** still applies only to **task** mode (repeat `--task`); project mode stops per driver + `stop_report.json`.
- **`sde project validate (--session-dir <path> \| --plan <path>) [--repo-root <path>] [--skip-workspace] [--progress-file <path>]`** — **Phase 9:** validates ``project_plan.json`` (schema + workspace path rules), detects **dependency cycles**, optionally runs **Phase 7** git workspace checks (skip with ``--skip-workspace``), and emits **non-fatal** warnings if an optional ``progress.json`` does not match the progress schema. Exit codes: **0** ok, **1** workspace contract, **2** invalid plan / missing file / cycle. Does **not** write ``stop_report.json`` or run the driver loop.
- **`sde project status (--session-dir <path> \| --plan <path>) [--repo-root <path>] [--progress-file <path>] [--max-concurrent-agents K] [--status-max-json-bytes N] [--status-jsonl-full-scan-max-bytes N] [--status-jsonl-tail-bytes N] [--status-max-listed-step-ids N]`** — **Phase 10 + 12–21:** prints one JSON object: plan / progress / ``driver_state`` / ``stop_report`` / **leases** (capped body + row count) / ``session_events`` (Phases 10–11, 15) plus **``verification_aggregate``**, **``definition_of_done``**, and **``step_runs``** summaries when those files exist (Phase 12). **Phase 13** flags tune read caps for huge sessions; **Phase 14** adds **`context_pack_lineage`**, **`context_packs`**, and **`verification_bundles`** (and caps how many ``step_ids`` are listed per directory); **Phase 15** adds **`parallel_worktrees`** (``_worktrees/``); **Phase 16** adds **`plan_step_rollups`**; **Phase 17** enriches **``step_runs``** / rollups with latest run pointers when ``step_runs.jsonl`` is small enough to fully scan; **Phase 18** adds **`repo_snapshot`** (``--repo-root``; default cwd); **Phase 19–20** add **`workspace_status`** (branch + path prefix checks); **Phase 21** adds **`status_at_a_glance`** (compact derived fields + ``red_flags``). CLI always exits **0** (inspect fields for red flags).

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

- **API:** :func:`validate_project_session` in [`project_validate.py`](../../src/orchestrator/api/project_validate.py) returns ``ok``, ``exit_code``, and structured errors; no ``execute_single_task``, no lease mutation.
- **CLI:** ``sde project validate`` mirrors ``project run`` session/plan selection; ``--skip-workspace`` for sandboxes without git; optional ``--progress-file`` for resume-state warnings only.

## Phase 10 — Status snapshot (shipped)

- **API:** :func:`describe_project_session` in [`project_status.py`](../../src/orchestrator/api/project_status.py) aggregates on-disk session JSON without writes.
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

- **API:** ``plan_step_rollups`` appears when ``project_plan.json`` parses as an object: ``present``, ``step_count`` (full plan length), ``steps`` (first **N** rows in plan order, **N** = ``max_status_listed_step_ids`` default **256**), ``steps_omitted`` when truncated. Each row has ``step_id``, ``verification_json_present``, ``context_pack_present``, and ``aggregate_passed`` (bool or null when unknown or aggregate body omitted / missing cell).
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

- **API:** :func:`describe_project_session` adds ``status_at_a_glance``: derived ``plan_ok``, ``all_plan_steps_complete``, runnable / next-tick counts, ``driver_status`` / ``driver_exit_code`` / ``stop_exit_code`` when the corresponding embedded bodies are dicts, ``dod_all_required_passed`` / ``aggregate_all_steps_verification_passed`` when those bodies are present, ``path_prefixes_ok`` / ``branch_commit_match`` echoed from ``workspace_status``, ``step_runs_latest_indexed`` when ``by_step`` is populated (not ``by_step_omitted``), and ``red_flags`` (``dependency_cycle`` alone when the plan graph has a cycle; otherwise ``plan_invalid_or_unreadable_or_schema`` when ``plan_ok`` is false; plus ``workspace_path_prefix_mismatch`` / ``workspace_branch_mismatch`` when ``workspace_status.present`` and the respective checks are false).
- **CLI:** no new flags; same JSON envelope as Phase 10.

## Phase 11 — Session event log (shipped)

- **Writer:** :func:`append_session_event` in [`project_events.py`](../../src/orchestrator/api/project_events.py); best-effort (swallows ``OSError`` so logging never crashes the driver).
- **Events:** ``session_driver_start`` once per ``run_project_session`` after the session enters ``running``; ``tick`` before each non-empty lease batch; ``session_terminal`` on **every** terminal outcome via ``_emit_stop_and_session_dod`` (payload includes ``exit_code``, ``stopped_reason``, ``completed_step_ids``, …).

## Phase 4 — Stop policy (shipped)

- **Exit codes:** **0** = ``completed_review_pass`` (plan graph complete + aggregate verification passed). **1** = expected stop — ``blocked_human``, ``exhausted_budget``, ``dependency_cycle``, or ``workspace_contract`` (inspect ``stop_report.json`` / ``progress.json``). **2** = invalid session input or unexpected driver end (missing/invalid ``project_plan.json``, or internal ``unexpected_end``).
- **Artifacts:** every terminal path writes **``stop_report.json``** and refreshes **``driver_state.json``** with matching ``exit_code`` / ``stopped_reason``. When the plan is schema-valid, the driver also refreshes **``verification_aggregate.json``** and **``definition_of_done.json``** so the last session state is always on disk (failed runs get ``all_required_passed: false`` unless status is ``completed_review_pass``).
- **Per-run quality:** each ``execute_single_task`` remains **``validation_ready``-capable** under the chosen mode; session exit **0** does not imply every intermediate run was ``validation_ready`` unless your plan’s verification commands enforce it.

## Phase 2 — Context service (shipped)

- **ContextPack** pulls **dependency outputs** before each step: for every `depends_on` step that already has a row in `step_runs.jsonl`, it reads that run’s `summary.json` and `report.md` (capped excerpts) and lists **references** (paths + git head at build time when known).
- **Failures:** recent `prior_failures` plus, for verification failures, the tail of command logs from `verification/<step_id>.json`.
- **HS03 at session scope:** when the markdown exceeds ``max_chars``, the pack records paired ``truncation_events`` and ``reductions`` (shared ``provenance_id``), ``markdown_sha256_full`` of the pre-truncation body, and ``truncation_hs03_ok`` (same pairing rule as per-run ``token_context.json``). Per-run **HS03** from the pipeline is unchanged; this is additional honesty for the **driver-injected** prefix.

## Code map

- Validation: [`src/orchestrator/api/project_schema.py`](../../src/orchestrator/api/project_schema.py)
- Graph: [`src/orchestrator/api/project_plan.py`](../../src/orchestrator/api/project_plan.py)
- Driver loop: [`src/orchestrator/api/project_driver.py`](../../src/orchestrator/api/project_driver.py)
- Task / project continuous: [`src/orchestrator/api/continuous_run.py`](../../src/orchestrator/api/continuous_run.py)
- Context: [`src/orchestrator/api/context_pack.py`](../../src/orchestrator/api/context_pack.py)
- Repo index MVP: [`src/orchestrator/api/repo_index.py`](../../src/orchestrator/api/repo_index.py)
- Verification: [`src/orchestrator/api/project_verify.py`](../../src/orchestrator/api/project_verify.py)
- Aggregate / session DoD: [`src/orchestrator/api/project_aggregate.py`](../../src/orchestrator/api/project_aggregate.py)
- Stop policy: [`src/orchestrator/api/project_stop.py`](../../src/orchestrator/api/project_stop.py)
- Scheduler / leases: [`src/orchestrator/api/project_scheduler.py`](../../src/orchestrator/api/project_scheduler.py), [`src/orchestrator/api/project_lease.py`](../../src/orchestrator/api/project_lease.py)
- Parallel worktrees: [`src/orchestrator/api/project_worktree.py`](../../src/orchestrator/api/project_worktree.py), [`src/orchestrator/api/project_parallel.py`](../../src/orchestrator/api/project_parallel.py)
- Workspace gates: [`src/orchestrator/api/project_workspace.py`](../../src/orchestrator/api/project_workspace.py)
- Plan preflight: [`src/orchestrator/api/project_validate.py`](../../src/orchestrator/api/project_validate.py)
- Session snapshot: [`src/orchestrator/api/project_status.py`](../../src/orchestrator/api/project_status.py)
- Session events: [`src/orchestrator/api/project_events.py`](../../src/orchestrator/api/project_events.py)

Example plan: [`data/sde-project-plan.example.json`](../../data/sde-project-plan.example.json).
