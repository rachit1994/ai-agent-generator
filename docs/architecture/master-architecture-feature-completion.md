# Master architecture — feature inventory vs implementation (%)

**Sole product architecture source of truth:** [`../AI-Professional-Evolution-Master-Architecture.md`](../AI-Professional-Evolution-Master-Architecture.md) (this document defers to that file for intent and scope).

**What this file is:** a **maintainer-facing** map from the master blueprint to **how much of each named capability exists today in this repository** (`src/`, repo-root **`libs/`**, CLI, docs). It is **not** a replacement for the master doc.

**Target repository layout (headings + rows → folders):** the canonical **inventory + per-file mapping** spec lives in [`repository-layout-from-completion-inventory.md`](repository-layout-from-completion-inventory.md). **Physical migration is landed** (`src/<section_snake>/<row_snake>/` + repo-root **`libs/`**). Use that doc for **Part A** (regenerated `find` snapshot), **Part C** (first column = stable **legacy flat-tree path keys**), **`+` row splits**, and **`contracts/`** vs **`libs/`** posture.

**How percentages are scored (read this once):**

| % | Meaning |
|---|--------|
| **0** | No material implementation as described in the master (may exist only as prose, plans, or empty layout). |
| **10–25** | Harness stubs, run-local artifacts, partial scripts, or prose-only runbooks without the named service/runtime. |
| **30–45** | Meaningful **local / session** behavior that aligns with the idea but **not** durable platform, multi-service, or `local-prod` as fully specified. |
| **50–65** | Strong local slice: gates, driver flows, or artifacts that **approximate** the feature for CLI runs; major platform gaps remain. |
| **70–85** | Close for a **narrow** interpretation (e.g. subset of run classes); still missing master-class durability, isolation, or org-wide enforcement. |
| **90–100** | Matches the master’s described behavior for that item **in this repo’s honest scope** (rare for production-only rows). |

Cross-checks used while scoring: prior gap-analysis notes (removed with doc consolidation), plus **[`../UNDERSTANDING-THE-CODE.md`](../UNDERSTANDING-THE-CODE.md)** , **[`repository-layout-from-completion-inventory.md`](repository-layout-from-completion-inventory.md)** Part A, and the live **`src/`** + **`libs/`** trees (gates, orchestrator, pipeline, shared packages).

### Evidence snapshot (tree-verified, 2026-04-20)

These are **facts** from the repo at scoring time (use them to re-score after large `src/` changes):

| Check | Result |
|-------|--------|
| Part A inventory (`src/` + `libs/` `*.py` / `*.md`, no `__pycache__`) | **215** paths — CI-enforced in **`test_architecture_test_file_inventory.py`** (`test_layout_inventory_part_a_path_count_matches_disk`). |
| CTO hard-stops | **HS01–HS32** implemented as on-disk evidence checks under **`src/guardrails_and_safety/risk_budgets/`** (`hard_stops.py` HS01–06 incl. **`token_context.json`** window expiry when set, `hard_stops_guarded.py` HS07–16 incl. **HS08** doc review + **`program/dual_control_ack.json`**, `hard_stops_events.py` HS17–20, `hard_stops_memory.py` HS21–24, `hard_stops_evolution.py` HS25–28, `hard_stops_organization.py` HS29–32 incl. **HS30** approval-token expiry). **`hard_stop_schedule.expected_hard_stop_ids`** mirrors which IDs run for a given **`mode`** + artifact layout (see §11.B). |
| Run persistence | Per-run **`traces.jsonl`**, **`orchestration.jsonl`**, **`replay_manifest.json`**, **`event_store/run_events.jsonl`** (see `workflow_pipelines/production_pipeline_task_to_promote/runner/event_lineage_layer.py`, `workflow_pipelines/production_pipeline_task_to_promote/replay.py`, `workflow_pipelines/production_pipeline_task_to_promote/runner/persist_traces.py`). |
| Run-directory contract | **`validate_execution_run_directory`** (`review_gating/run_directory.py`) checks required paths for **`mode`**, merges **HS01–HS32**, and (§11.E) validates optional **`program/policy_bundle_rollback.json`**. |
| Storage API in master (Postgres + projections + vector) | **Not present** in `src/`; JSON/JSONL via **`libs/storage/storage.py`** only. |
| Versioned **`contracts/`** tree (master §21) | **Absent** at repo root (no `contracts/**` checked in). |
| **OpenTelemetry** in `src/` | **No** instrumentation; master §15 OTel remains documentation-only here. |
| **Chaos / fault-injection** harness | **No** matches in `src/` or shell/CI scripts for chaos-style suites. |
| Python unit tests | **69** `test_*.py` files (**68** under `src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/`, **1** under repo-root `tests/`; count of files, not assertions). |

**Overall (hand-wavy but honest):** the master describes an **organization-scale OS**; this repo ships a **local SDE orchestrator spine** with gates, JSON/JSONL contracts on hot paths, and session drivers. A **weighted** completion against **every** row below lands roughly **20–35%** depending on how heavily you weight Tier-2 services vs the CLI spine (contracts and tests grew; Postgres / `contracts/` / OTel / chaos remain absent).

**Spine vs whole blueprint:** the **repository implementation spine** row (**P10**) can sit **~68–78%** for “does this repo deliver its own documented CLI + gates + artifact contracts?” while the **weighted** overall stays low — the spine is necessary, not sufficient, for the full master (see master §17 “completion” paragraph).

---

## CTO priority order (end users first)

**“End user”** here means someone (or a team) **running SDE on real work**: they need **safe output**, **honest pass/fail**, **predictable runs**, **recoverability**, and **visibility** before they need org-scale services or long-horizon governance.

Sections **below are reordered** for **implementation priority**: ship from the top down when choosing roadmap work. **Master §** labels on each row still point to the canonical spec location in the architecture doc.

| Tier | Focus | Why this order |
|------|--------|----------------|
| **P1** | Safety + review gates | Stops bad merges and unsafe tool behavior — highest direct harm reduction. |
| **P2** | Evaluation + verification | Users trust outcomes; benchmarks and regression are the product’s “truth layer.” |
| **P3** | Execution pipelines + recovery | Tasks finish, retries behave, failures are contained — daily workflow quality. |
| **P4** | Runtime users touch | CLI stability, leases, local runtime — what people actually run. |
| **P5** | Evidence + replay | Debuggability and disputes after the fact. |
| **P6** | Success metrics + transparency | Reporting and KPIs once the core is credible. |
| **P7** | Core platform slices | Memory, events, learning — compound value after trust exists. |
| **P8** | Roles, lifecycle, capability | Org model — matters more as teams and autonomy grow. |
| **P9** | Scale + service mesh | Throughput and separation when single-machine limits hurt. |
| **P10** | Program / meta / readiness | CTO operating system for the OS — valuable once users are protected and served. |

---

## P1 — §11 Guardrails and safety

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Review gating + evaluator authority | §11 | **100** | **Repo-local scope (§11.A):** `review.json` **1.1** carries severity-tagged **`review_findings`** (static gates, manifest gaps, verifier outcome); **HS15** rejects `completed_review_pass` if any **blocker** finding remains; guarded **`definition_of_done`** + step reviews + **`verification_bundle.json`** encode evaluator pass/fail; **HS01** schema includes **`review_findings`**. **Out of master scope here:** centralized **`SafetyController`** veto **service**, org-wide promotion committee, IAM plane (see master §11 Dual Control / §15). |
| Risk budgets + permission matrix | §11 | **60** | **§11.B:** executable **HS01–HS32 schedule** (`hard_stop_schedule.expected_hard_stop_ids`, contract-tested vs `evaluate_hard_stops`) for **mode × on-disk harness** bands; token budgets (**HS04–HS06**), static gates, **HS30** high-risk approval on **`iam/action_audit.jsonl`** when the org plane is active. **Not shipped:** full IAM × stage permission matrix or org-wide policy engine. |
| Autonomy boundaries (tokens, expiry) | §11 | **70** | **§11.C:** **`token_context.json`** carries **`autonomy_anchor_at`**, **`context_expires_at`**, **`context_ttl_seconds`** (CTO **`build_token_context`**); **HS06** fails when **`context_expires_at`** is present and in the past or malformed; **HS30** rejects **`approval_token_expires_at`** in the past when set on **`risk: high`** rows (**`iam/action_audit.jsonl`**). **Not shipped:** IAM/session token service or org-wide TTL policy plane. |
| Dual control | §11 | **54** | **§11.D:** **`program/dual_control_ack.json`** (schema **1.0**, two distinct actor ids) + **HS08** when **`doc_review.json`** sets **`dual_control.required`** or when an ack file is present; guarded completion harness writes a stub ack; session **plan lock** + **HS30** remain separate controls. **Not shipped:** enterprise maker-checker workflow UI / policy service. |
| Rollback rules (atomic policy bundle rollback) | §11 | **50** | **§11.E:** **`program/policy_bundle_rollback.json`** (schema **1.0**, **`status`** `none` \| `rolled_back_atomic`) validated by **`validate_execution_run_directory`**; guarded completion harness writes **`none`** stub; **`rolled_back_atomic`** requires paired **SHA-256** policy hashes + non-empty **`paths_touched`**. **Not shipped:** signed bundle service / atomic multi-tenant rollback controller. |

### §11.A — Review gating + evaluator authority (**100%** for this repository)

**Master §11 intent:** severity-tagged review findings drive stop-ship; evaluator pass/fail controls rollout eligibility.

**Completed here (disk-backed SDE / CLI honest scope):**

- **`review.json`** schema **1.1** (`REVIEW_SCHEMA`) with required **`review_findings`**: each item has **`severity`** (`blocker` \| `warn` \| `info`), **`code`**, **`message`**, **`evidence_ref`**. Sources: **`static_gates_report.json`** blockers/warnings, missing **`artifact_manifest`** rows, terminal verifier failure, incomplete runs, safety-refusal terminal info.
- **`build_review`** (`guardrails_and_safety.review_gating.review`) supplies those fields for **`review.json`** written by the CTO publish path (`workflow_pipelines/.../cto_publish.py`); tests and fixtures may stub minimal **`review.json`** files without calling **`build_review`**.
- **HS15** (`hard_stops_guarded._hs15_terminal_honesty`) enforces stop-ship honesty: **`completed_review_pass`** is invalid if **`review_findings`** contains a **blocker** (defense in depth with **HS04** static safety).
- **Evaluator authority (guarded / phased):** verifier outcome → **`review.status`**; **`definition_of_done`** + **`step_reviews/*.json`** + **`verification_bundle.json`** gate **`all_required_passed`** (existing **`_guarded_definition_of_done`** path).
- **Project / intake authority:** Stage 1 **`doc_review.json`**, **`evaluate_project_plan_lock_readiness`**, and driver stop semantics remain the human-governed review boundary (unchanged; documented in **`docs/UNDERSTANDING-THE-CODE.md`**).

Regression: **`test_review_gating_findings.py`**.

**Not claimed in this row (other P1 rows or master services):** risk×stage permission matrix, dual-control workflow UI, policy-bundle rollback plane, **`SafetyController`** as a running service.

### §11.B — Risk budgets + permission matrix (**60%** for this repository)

**Master §11 intent:** resource and safety budgets bind execution; high-risk actions require explicit approval and traceable permissions.

**Completed here (local / disk-honest scope):**

- **Token + truncation budgets:** **HS02–HS03**, **HS06** over **`token_context.json`** (per-stage caps plus optional **`context_expires_at`** window honesty; **`build_token_context`** in CTO publish).
- **Safety + lineage:** **HS04–HS05** (static gates report + traces/orchestration expectations).
- **Executable schedule:** **`expected_hard_stop_ids(mode, output_dir)`** in **`guardrails_and_safety.risk_budgets.hard_stop_schedule`** lists exactly which **HS01–HS32** entries **`evaluate_hard_stops`** evaluates for **`baseline` / `guarded_pipeline` / `phased_pipeline`** and the artifact triggers (guarded program plane, replay manifest, memory / evolution bundles, org **`lease_table.json`**, **`summary.json` `run_class`** coding-only short-circuit). Regression: **`test_hard_stop_schedule.py`**.
- **High-risk approval hook:** **HS30** when **`coordination/lease_table.json`** exists — requires **`approval_token_id`** on **`iam/action_audit.jsonl`** rows marked **`risk: high`** (see **`hard_stops_organization.py`**).

**Not claimed in this row:** enterprise IAM × stage matrix, live permission service, or org-wide risk registry beyond these on-disk checks.

### §11.C — Autonomy boundaries (tokens, expiry) (**70%** for this repository)

**Master §11 intent:** execution stays within bounded autonomy — resource caps and time-bounded trust for elevated-risk actions.

**Completed here (artifact + gate honest scope):**

- **Token context window:** **`build_token_context`** emits **`autonomy_anchor_at`**, **`context_expires_at`**, and **`context_ttl_seconds`** (default **604800** seconds / 7 days; override via **`context_ttl_seconds`** for tests or policy experiments). CTO publish continues to write **`token_context.json`** via the existing path.
- **HS06 (budgets + expiry):** per-stage caps unchanged; if **`context_expires_at`** is set and parses as ISO-8601 UTC, it must be **not before “now”** when hard-stops run; malformed timestamps fail closed.
- **HS30 (high-risk approvals):** when **`risk: high`**, **`approval_token_id`** remains required; if **`approval_token_expires_at`** is present, it must parse and be **not expired** relative to gate evaluation time.
- **Shared parsing:** **`time_and_budget.time_util.parse_iso_utc`** centralizes ISO parsing for these checks.

Regression: **`test_autonomy_boundaries_expiry.py`**.

**Not claimed in this row:** centralized session/IAM services, automatic token refresh, or org-wide TTL configuration UI.

### §11.D — Dual control (**54%** for this repository)

**Master §11 intent:** material changes and elevated-risk execution require separation of duties — not a single unreviewed actor string.

**Completed here (artifact + HS08 honest scope):**

- **`program/dual_control_ack.json`:** optional unless **`doc_review.json`** includes **`dual_control: {"required": true}`**; when evaluated, schema **`1.0`** with distinct non-empty **`implementor_actor_id`** and **`independent_reviewer_actor_id`** (self-ack is rejected). When **`dual_control.required`** is true, the ack file **must** exist and validate.
- **HS08** ties doc review pass/fail to the dual-ack contract above (evidence refs include both JSON paths).
- **Harness:** guarded **`completion_layer`** writes a stub ack pairing **`harness_implementor`** / **`harness_independent_reviewer`** alongside stub **`doc_review.json`** so **`artifact_manifest`** and CTO paths stay green for default runs.
- **Related (unchanged rows):** session **`project_plan_lock.json`** + **`evaluate_project_plan_lock_readiness`** (orchestrator) and **HS30** high-risk approvals (**§11.B**) remain the other local “two-party” surfaces.

Regression: **`test_dual_control_hs08.py`**.

**Not claimed in this row:** live maker-checker queues, org-wide SoD policy engines, or UI workflows beyond these JSON contracts.

### §11.E — Rollback rules (policy bundle evidence) (**50%** for this repository)

**Master §11 intent:** policy and gate bundles can be rolled back with explicit, replayable evidence — not silent disk drift.

**Completed here (validate + artifact honest scope):**

- **`program/policy_bundle_rollback.json`:** schema **`1.0`** with **`status`** **`none`** (no rollback) or **`rolled_back_atomic`**. Atomic rollback requires **`previous_policy_sha256`** and **`current_policy_sha256`** (64-hex **SHA-256**) plus a non-empty **`paths_touched`** list of relative paths (strings).
- **`validate_policy_bundle_rollback`** (`guardrails_and_safety.review_gating.policy_bundle_rollback`) returns stable error codes; **`validate_execution_run_directory`** merges those into **`errors`** so **`validate_run`** / **`continuous_run`** / harness smoke treat malformed rollback records like other contract breaks.
- **Guarded completion harness** writes a **`status: none`** stub next to other **`program/`** Stage-1 artifacts so default guarded/phased runs satisfy **`artifact_manifest`** and the validator.

Regression: **`test_policy_bundle_rollback.py`**.

**Not claimed in this row:** cryptographically signed policy bundles, coordinated multi-node rollback controllers, or cloud policy planes.

---

## P2 — §13 Evaluation framework

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Offline evaluation | §13 | **60** | **§13.A:** JSONL suite **structural contract** (`benchmark/offline_eval_contract`, **`OFFLINE_EVAL_SUITE_CONTRACT`**) enforced in **`read_suite`** before **`validate_task_payload`**; **`validate_suite_document`** / **`validate_suite_jsonl`** for CI reuse; benchmark driver + **`data/medium-hard-sde-suite.jsonl`** unchanged. **Not shipped:** hosted eval service or fleet-scale offline runner. |
| Regression testing (capability/safety/memory/coordination) | §13 | **55** | **§13.B:** **`benchmark/regression_surface_contract`** (**`REGRESSION_SURFACE_CONTRACT`**, **`REGRESSION_DIMENSION_ANCHORS`**, **`validate_regression_anchors`**) pins eight orchestrator **`test_*.py`** anchors across capability/safety/memory/coordination; **`test_regression_surface_contract.py`**. **69** total `test_*.py` files + gate suites; not full master coordination matrix. |
| Promotion evaluation | §13 | **42** | **§13.C:** **`benchmark/promotion_eval_contract`** (**`PROMOTION_EVAL_PACKAGE_CONTRACT`**, **`validate_promotion_package_dict`**, **`validate_promotion_package_path`**) structural gate for **`lifecycle/promotion_package.json`** before write in **`write_evolution_artifacts`** (**HS26**-compatible evaluator signals + evidence window); **`test_promotion_eval_package_contract.py`**. **Not shipped:** committee / governance **service**. |
| Online evaluation (shadow/canary, trajectory safety) | §13 | **30** | **§13.D:** **`benchmark/online_eval_shadow_contract`** (**`ONLINE_EVAL_SHADOW_CONTRACT`**, **`validate_canary_report_dict`**, **`validate_canary_report_path`**) structural gate for **`learning/canary_report.json`** before write in **`write_evolution_artifacts`** (**HS28**: **`shadow_metrics`** object + boolean **`promote`**); **`test_online_eval_shadow_contract.py`**. **Not shipped:** live shadow traffic plane, trajectory safety **service**, or fleet canary controller. |

### §13.A — Offline evaluation (**60%** for this repository)

**Master §13 intent:** tasks and suites can be evaluated reproducibly from disk without a live control plane.

**Completed here (suite-load honest scope):**

- **`OFFLINE_EVAL_SUITE_CONTRACT`** (`sde.offline_eval_suite.v1`) documents the JSONL row shape checked before semantic **`validate_task_payload`** rules.
- **`validate_suite_document`** / **`validate_suite_jsonl`** reject empty suites, bad JSON lines, missing **`taskId`/`task_id`**, non-string/blank **`prompt`**, missing **`difficulty`**, and non-list **`expectedChecks`** when present.
- **`read_suite`** applies the structural gate (single file read) then existing payload normalization + **`safeguards.validate_task_payload`** (difficulty enum, required keys).

Regression: **`test_offline_eval_suite_contract.py`**, **`test_medium_hard_sde_suite.py`**.

**Not claimed in this row:** managed offline-eval fleet, distributed result aggregation, or model-grading services.

### §13.B — Regression testing surface (**55%** for this repository)

**Master §13 intent:** capability, safety, memory, and coordination regressions stay tied to concrete tests—not only a file count.

**Completed here (anchor-path honest scope):**

- **`REGRESSION_SURFACE_CONTRACT`** (`sde.regression_surface.v1`) documents the curated anchor list checked against disk from repo root.
- **`REGRESSION_DIMENSION_ANCHORS`** lists **`(dimension, relative_path)`** pairs (two anchors each for **capability**, **safety**, **memory**, **coordination**) under **`orchestrator/tests/unit/`**.
- **`validate_regression_anchors(root)`** returns stable **`regression_surface_missing_<dimension>_<stem>`** tokens when an anchor file is absent.

Regression: **`test_regression_surface_contract.py`**, **`test_architecture_test_file_inventory.py`** (total **`test_*.py`** count), **`test_public_export_surface.py`** (exports **`regression_surface_contract`**).

**Not claimed in this row:** full coordination matrix from the master architecture doc or cross-repo test aggregation.

### §13.C — Promotion evaluation (**42%** for this repository)

**Master §13 intent:** promotion decisions have inspectable, machine-checkable evidence on disk (independent evaluator signals), not only narrative sign-off.

**Completed here (artifact-shape honest scope):**

- **`PROMOTION_EVAL_PACKAGE_CONTRACT`** (`sde.promotion_eval_package.v1`) documents required fields for **`lifecycle/promotion_package.json`** (including **`independent_evaluator_signal_ids`** non-empty list, matching **HS26**’s pass condition).
- **`validate_promotion_package_dict`** / **`validate_promotion_package_path`** return stable **`promotion_package_*`** error tokens (missing file, JSON errors, schema/stage/signal/window violations).
- **`write_evolution_artifacts`** raises **`ValueError`** with prefix **`promotion_eval_package_contract:`** if the harness payload fails validation before **`write_json`**.

Regression: **`test_promotion_eval_package_contract.py`**, **`test_public_export_surface.py`** (exports **`promotion_eval_contract`**).

**Not claimed in this row:** governance committee workflows, multi-party promotion votes, or hosted promotion services.

### §13.D — Online evaluation (shadow/canary artifact) (**30%** for this repository)

**Master §13 intent:** shadow and canary decisions leave comparable, machine-checkable evidence—not only runtime metrics in a hosted control plane.

**Completed here (artifact-only honest scope):**

- **`ONLINE_EVAL_SHADOW_CONTRACT`** (`sde.online_eval_shadow.v1`) documents the **`learning/canary_report.json`** shape aligned with **HS28** (**`shadow_metrics`** must be an object; **`promote`** must be a JSON boolean).
- **`validate_canary_report_dict`** / **`validate_canary_report_path`** return stable **`online_eval_shadow_*`** error tokens (missing file, JSON errors, schema / metrics / promote / **`recorded_at`** violations).
- **`write_evolution_artifacts`** raises **`ValueError`** with prefix **`online_eval_shadow_contract:`** if the canary payload fails validation before **`write_json`**.

Regression: **`test_online_eval_shadow_contract.py`**, **`test_public_export_surface.py`** (exports **`online_eval_shadow_contract`**).

**Not claimed in this row:** always-on shadow traffic, online trajectory safety monitors, or automated canary rollout controllers.

---

## P3 — §10 Workflow pipelines

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Strategy overlay (`CareerStrategy → TaskPortfolio → Production`) | §10 | **24** | **§10.A:** **`benchmark/strategy_overlay_contract`** (**`STRATEGY_OVERLAY_CONTRACT`**, **`validate_strategy_proposal_dict`**, **`validate_strategy_proposal_path`**) structural gate for **`strategy/proposal.json`** before write in **`write_organization_artifacts`** (**HS32** autonomy + **`proposal_ref`** rules); **`test_strategy_overlay_contract.py`**. **Not shipped:** `CareerStrategyAgent` / portfolio **service** — project driver + scheduler still only **partially** echo master planning. |
| Production pipeline (`Task → … → Promote`) | §10 | **50** | **§10.B:** **`benchmark/production_pipeline_plan_contract`** (**`PRODUCTION_PIPELINE_PLAN_CONTRACT`**, **`validate_harness_project_plan_dict`**, **`validate_harness_project_plan_path`**) structural gate for harness **`program/project_plan.json`** (`plan_version` + **`steps`** with **`step_id`** / **`depends_on`** / **`phase`**) before write in **`write_completion_artifacts`**; **`test_production_pipeline_plan_contract.py`**. Distinct from meta-orchestrator **`project_schema.validate_project_plan`** (session **`schema_version`** plans). **Not shipped:** full Task→…→Promote **service** chain. |
| Retry pipeline (reason-coded, escalation) | §10 | **58** | **§10.C:** **`benchmark/retry_pipeline_contract`** (**`RETRY_PIPELINE_REPEAT_CONTRACT`**, **`validate_repeat_profile_result`**) validates **`execute_single_task`** V1 **repeat** envelope (**`runs`** length, **`run_id`**/**`output_dir`**, exclusive **`output`** vs **`error`**, boolean rollups) when **`repeat`** is **>= 2**; **`test_retry_pipeline_repeat_contract.py`**. Mode-level **`max_retries`** / verifier fix paths unchanged. **Not shipped:** reason-coded escalation matrix or hosted retry **service**. |
| Deterministic state machines (task / learning / recovery) | §10 | **64** | **§10.E:** **`benchmark/run_manifest_contract`** (**`RUN_MANIFEST_CONTRACT`**, **`validate_run_manifest_dict`**, **`validate_run_manifest_path`**) gate for **`run-manifest.json`** before write in **`execute_single_task`** (**`run_manifest_contract:`** prefix); **`replay.py`** shares **`RUN_MANIFEST_CONTRACT`**; **`test_run_manifest_contract.py`**. **§10.I:** **`runner/orchestration_run_start_contract`** (**`ORCHESTRATION_RUN_START_CONTRACT`**, **`validate_orchestration_run_start_dict`**) gate on **`append_orchestration_run_start`** before the first **`run_start`** line appends to **`orchestration.jsonl`** (**`orchestration_run_start_contract:`** prefix); **`test_orchestration_run_start_contract.py`**. **§10.L:** **`runner/orchestration_run_error_contract`** (**`ORCHESTRATION_RUN_ERROR_CONTRACT`**, **`validate_orchestration_run_error_dict`**) gate on **`run_error`** lines before **`single_task`** appends on pipeline / JSON-parse failures (**`orchestration_run_error_contract:`** prefix); **`test_orchestration_run_error_contract.py`**. **§10.K:** **`runner/orchestration_stage_event_contract`** (**`ORCHESTRATION_STAGE_EVENT_CONTRACT`**, **`validate_orchestration_stage_event_line_dict`**) gate on each flattened **`stage_event`** line before **`append_orchestration_stage_events`** appends (**`orchestration_stage_event_contract:`** prefix); **`test_orchestration_stage_event_contract.py`**. **§10.M:** **`runner/orchestration_run_end_contract`** (**`ORCHESTRATION_RUN_END_CONTRACT`**, **`validate_orchestration_run_end_dict`**) gate on **`run_end`** before **`write_success_artifact_layer`** appends (**`orchestration_run_end_contract:`** prefix); **`test_orchestration_run_end_contract.py`**. **§10.N:** **`runner/traces_jsonl_event_contract`** (**`TRACES_JSONL_EVENT_CONTRACT`**, **`validate_traces_jsonl_event_dict`**) gate on each **`TraceEvent`**-shaped dict before **`persist_traces`** / **`run_benchmark`** trace **`append_jsonl`** to **`traces.jsonl`** (**`traces_jsonl_event_contract:`** prefix); **`test_traces_jsonl_event_contract.py`**. Runner FSM + **HS17–HS20** event/replay checks unchanged; recovery **service** still absent. |
| Failure pipeline (contain → replay → rollback) | §10 | **50** | **§10.D:** **`benchmark/failure_pipeline_contract`** (**`REPLAY_MANIFEST_CONTRACT`**, **`validate_replay_manifest_dict`** / **`validate_replay_manifest_path`**, **`FAILURE_PIPELINE_SUMMARY_CONTRACT`**, **`validate_failure_summary_dict`** / **`validate_failure_summary_path`**) — **HS18**-aligned minimal **`replay_manifest.json`** plus harness **`summary.json`** on early failure; gates in **`write_event_lineage_artifacts`** / **`write_failure_summary`** (**`failure_pipeline_contract:`** prefix); **`test_failure_pipeline_contract.py`**. **`replay`/`validate_run`** unchanged; **not** incident ops plane. |
| Improvement pipeline (canary → promote / rollback) | §10 | **56** | **§10.F–H:** **`benchmark/benchmark_manifest_contract`**, **`benchmark/benchmark_checkpoint_contract`**, **`benchmark/benchmark_aggregate_summary_contract`** (**`BENCHMARK_MANIFEST_CONTRACT`**, **`validate_benchmark_manifest_*`**, **`BENCHMARK_CHECKPOINT_CONTRACT`**, **`validate_benchmark_checkpoint_*`**, **`BENCHMARK_AGGREGATE_SUMMARY_CONTRACT`**, **`validate_benchmark_aggregate_summary_*`**) gates on **`run_benchmark`** for **`benchmark-manifest.json`**, **`benchmark-checkpoint.json`**, and harness **`summary.json`** (success + abort failure; **`benchmark_aggregate_summary_contract:`** / **`benchmark_*_contract:`** prefixes); **`replay.py`** shares **`BENCHMARK_MANIFEST_CONTRACT`**; **`test_benchmark_manifest_contract.py`**, **`test_benchmark_checkpoint_contract.py`**, **`test_benchmark_aggregate_summary_contract.py`**. **§10.J:** **`benchmark/orchestration_benchmark_jsonl_contract`** (**`ORCHESTRATION_BENCHMARK_RESUME_CONTRACT`**, **`validate_orchestration_benchmark_resume_dict`**, **`ORCHESTRATION_BENCHMARK_ERROR_CONTRACT`**, **`validate_orchestration_benchmark_error_dict`**) gates **`benchmark_resume`** / **`benchmark_error`** **`orchestration.jsonl`** lines before **`append_jsonl`** (**`orchestration_benchmark_*_contract:`** prefixes); **`test_orchestration_benchmark_jsonl_contract.py`**. **HS25–HS28** + §13 **C/D** unchanged; **not** canary-rollout **controller service**. |

### §10.A — Strategy overlay (**24%** for this repository)

**Master §10 intent:** strategy choices that affect production must be recorded and link to promotion evidence, not only live agent chatter.

**Completed here (artifact honest scope):**

- **`STRATEGY_OVERLAY_CONTRACT`** (`sde.strategy_overlay_proposal.v1`) documents **`strategy/proposal.json`** fields checked before **`write_json`** (**`requires_promotion_package`** / **`applied_autonomy`** as JSON booleans; **`proposal_ref`** when either flag demands a production handoff, matching **HS32**).
- **`validate_strategy_proposal_dict`** / **`validate_strategy_proposal_path`** return stable **`strategy_overlay_*`** error tokens.
- **`write_organization_artifacts`** raises **`ValueError`** with prefix **`strategy_overlay_contract:`** on validation failure.

Regression: **`test_strategy_overlay_contract.py`**, **`test_public_export_surface.py`** (exports **`strategy_overlay_contract`**).

**Not claimed in this row:** `CareerStrategyAgent`, dynamic task portfolios, or portfolio optimization **services**.

### §10.B — Production pipeline plan artifact (**50%** for this repository)

**Master §10 intent:** the guarded/phased harness emits a reproducible minimal plan graph before downstream completion artifacts.

**Completed here (harness `project_plan.json` honest scope):**

- **`PRODUCTION_PIPELINE_PLAN_CONTRACT`** (`sde.production_pipeline_plan.v1`) documents the **`plan_version`** + **`steps`** list shape used by **`write_completion_artifacts`** (not the richer **`project_plan.json`** schema enforced by **`project_schema.validate_project_plan`** for **`sde project run`**).
- **`validate_harness_project_plan_dict`** / **`validate_harness_project_plan_path`** return stable **`harness_project_plan_*`** error tokens.
- **`write_completion_artifacts`** raises **`ValueError`** with prefix **`production_pipeline_plan_contract:`** on validation failure.

Regression: **`test_production_pipeline_plan_contract.py`**, **`test_public_export_surface.py`** (exports **`production_pipeline_plan_contract`**).

**Not claimed in this row:** cross-run plan optimization, portfolio-level scheduling, or hosted pipeline orchestration.

### §10.C — Retry / repeat profile (**58%** for this repository)

**Master §10 intent:** multi-attempt runs expose a stable aggregate envelope for tests and tooling, not only opaque lists of run directories.

**Completed here (repeat-profile honest scope):**

- **`RETRY_PIPELINE_REPEAT_CONTRACT`** (`sde.retry_pipeline_repeat_profile.v1`) documents the **`execute_single_task(..., repeat>=2)`** return shape: **`repeat`**, **`task`**, **`mode`**, **`runs`**, **`all_runs_no_pipeline_error`**, **`validation_ready_all`**.
- **`validate_repeat_profile_result`** returns stable **`repeat_profile_*`** error tokens (no-op when **`repeat`** is **< 2**).
- **`execute_single_task`** raises **`ValueError`** with prefix **`retry_pipeline_contract:`** if the assembled envelope is inconsistent (should be unreachable for normal pipeline returns).

Regression: **`test_retry_pipeline_repeat_contract.py`**, **`test_public_export_surface.py`** (exports **`retry_pipeline_contract`**), **`test_cto_gates.py`** (**`repeat=2`** smoke).

**Not claimed in this row:** centralized reason codes across services, cross-tenant retry budgets, or automated escalation workflows.

### §10.D — Failure path artifacts (replay manifest + failure summary) (**50%** for this repository)

**Master §10 intent:** when a run fails or is torn down early, containment and replay still rest on inspectable, machine-checkable envelopes—not only log lines.

**Completed here (artifact-shape honest scope):**

- **`REPLAY_MANIFEST_CONTRACT`** (`sde.replay_manifest.v1`) documents the **`replay_manifest.json`** fields aligned with **HS18** (required **`contract_version`**, **`sources[0].path`/`sha256`**, **`chain_root`**, plus **`schema_version`** / **`run_id`**); **`window`**, **`projection_version`**, **`passed`**, and **`built_at`** are optional when absent and validated when present.
- **`validate_replay_manifest_dict`** / **`validate_replay_manifest_path`** return stable **`replay_manifest_*`** error tokens.
- **`write_event_lineage_artifacts`** raises **`ValueError`** with prefix **`failure_pipeline_contract:`** if the manifest fails validation before **`write_json`**.
- **`FAILURE_PIPELINE_SUMMARY_CONTRACT`** (`sde.failure_pipeline_summary.v1`) documents the early-failure **`summary.json`** shape from **`write_failure_summary`** (**`runId`**, **`mode`**, **`runStatus: failed`**, **`partial`**, **`error`**, **`provider`**, **`model`**).
- **`validate_failure_summary_dict`** / **`validate_failure_summary_path`** return stable **`failure_summary_*`** error tokens; **`write_failure_summary`** raises with the same **`failure_pipeline_contract:`** prefix on validation failure.

Regression: **`test_failure_pipeline_contract.py`**, **`test_public_export_surface.py`** (exports **`failure_pipeline_contract`**), **`test_event_lineage_replay_manifest.py`** (**HS18** minimal manifest fixtures).

**Not claimed in this row:** hosted rollback controllers, cross-tenant incident workflows, or automated containment orchestration.

### §10.E — Run manifest (single-task anchor) (**54%** for this repository)

**Master §10 intent:** each isolated attempt must leave a deterministic, replayable anchor—not only implicit process state.

**Completed here (manifest honest scope):**

- **`RUN_MANIFEST_CONTRACT`** (`sde.run_manifest.v1`) documents **`run-manifest.json`** fields aligned with **`replay_rerun`** (**`schema`**, **`run_id`**, **`mode`** ∈ {**`baseline`**, **`guarded_pipeline`**, **`phased_pipeline`**}, non-blank **`task`**, optional **`project_step_id`** / **`project_session_dir`** when present as non-blank strings).
- **`validate_run_manifest_dict`** / **`validate_run_manifest_path`** return stable **`run_manifest_*`** error tokens.
- **`execute_single_task`** raises **`ValueError`** with prefix **`run_manifest_contract:`** if the in-memory manifest fails validation before **`write_json`**.
- **`replay.py`** imports the same **`RUN_MANIFEST_CONTRACT`** constant (exposed as **`RUN_MANIFEST_SCHEMA`** for backward compatibility).

Regression: **`test_run_manifest_contract.py`**, **`test_public_export_surface.py`** (exports **`run_manifest_contract`**), **`test_runner_artifacts.py`** (manifest fields on disk).

**Not claimed in this row:** distributed saga orchestration, cross-run state reconciliation **services**, or automated recovery controllers.

### §10.F — Benchmark aggregate manifest

**Master §10 intent:** multi-task evaluation and improvement loops need a resumable, machine-checkable run anchor—not only ad-hoc directory state.

**Completed here (benchmark-manifest honest scope):**

- **`BENCHMARK_MANIFEST_CONTRACT`** (`sde.benchmark_manifest.v1`) documents **`benchmark-manifest.json`** fields aligned with **`run_benchmark`** / **`replay`** (**`schema`**, **`run_id`**, non-blank **`suite_path`**, **`mode`** ∈ {**`baseline`**, **`guarded_pipeline`**, **`both`**}, **`tasks`** list of **`taskId`**/**`prompt`** rows, optional **`max_tasks`** (**`null`** or non-negative int), required boolean **`continue_on_error`**).
- **`validate_benchmark_manifest_dict`** / **`validate_benchmark_manifest_path`** return stable **`benchmark_manifest_*`** error tokens.
- **`run_benchmark`** raises **`ValueError`** with prefix **`benchmark_manifest_contract:`** if the manifest dict fails validation before **`write_json`**, and validates again when **resuming** from disk before continuing.
- **`replay.py`** imports the same **`BENCHMARK_MANIFEST_CONTRACT`** constant (exposed as **`BENCHMARK_MANIFEST_SCHEMA`** for backward compatibility).

Regression: **`test_benchmark_manifest_contract.py`**, **`test_public_export_surface.py`** (exports **`benchmark_manifest_contract`**), **`test_benchmark_harvest.py`** / **`test_validate_run_api.py`** (aggregate layouts).

**Not claimed in this row:** hosted canary controllers, fleet-wide promotion orchestration, or automated rollback **services**.

### §10.G — Benchmark checkpoint (resume progress)

**Master §10 intent:** long benchmark runs must persist inspectable progress—not only final **`summary.json`** outcomes.

**Completed here (checkpoint honest scope):**

- **`BENCHMARK_CHECKPOINT_CONTRACT`** (`sde.benchmark_checkpoint.v1`) documents **`benchmark-checkpoint.json`** fields aligned with **`run_benchmark`** (**`schema`**, **`run_id`**, **`suite_path`**, **`mode`** ∈ {**`baseline`**, **`guarded_pipeline`**, **`both`**}, optional **`max_tasks`** (**`null`** or non-negative int), boolean **`continue_on_error`**, **`completed_task_ids`** as a list of non-blank strings, boolean **`finished`**, non-negative int **`updated_at_ms`**).
- **`validate_benchmark_checkpoint_dict`** / **`validate_benchmark_checkpoint_path`** return stable **`benchmark_checkpoint_*`** error tokens.
- **`run_benchmark`** raises **`ValueError`** with prefix **`benchmark_checkpoint_contract:`** if a checkpoint body fails validation before **`write_json`**, and validates the checkpoint read from disk before **resume** proceeds.

Regression: **`test_benchmark_checkpoint_contract.py`**, **`test_public_export_surface.py`** (exports **`benchmark_checkpoint_contract`**), **`test_benchmark_harvest.py`** (resume / finished paths).

**Not claimed in this row:** cross-region checkpoint replication, hosted progress planes, or automated benchmark fleet schedulers.

### §10.H — Benchmark aggregate summary

**Master §10 intent:** benchmark outcomes must be written in a predictable envelope for **`validate_run`**, reporting, and harvest tooling—not only ad-hoc JSON.

**Completed here (aggregate ``summary.json`` honest scope):**

- **`BENCHMARK_AGGREGATE_SUMMARY_CONTRACT`** (`sde.benchmark_aggregate_summary.v1`) documents the **`run_benchmark`** **`summary.json`** discriminant: common **`runId`** / **`suitePath`** / **`mode`** ∈ {**`baseline`**, **`guarded_pipeline`**, **`both`**}; **`runStatus: failed`** with **`error.type`** / **`error.message`** on abort, else non-blank **`verdict`** plus **`perTaskDeltas`** list for success-shaped bodies from **`build_summary`** (contract id is documentation-only until a future on-disk **`schemaVersion`** field).
- **`validate_benchmark_aggregate_summary_dict`** / **`validate_benchmark_aggregate_summary_path`** return stable **`benchmark_aggregate_summary_*`** error tokens.
- **`run_benchmark`** raises **`ValueError`** with prefix **`benchmark_aggregate_summary_contract:`** if either success or failure **`summary.json`** body fails validation before **`write_json`**.

Regression: **`test_benchmark_aggregate_summary_contract.py`**, **`test_public_export_surface.py`** (exports **`benchmark_aggregate_summary_contract`**), **`test_validate_run_api.py`** (aggregate **`summary.json`**).

**Not claimed in this row:** hosted benchmark analytics warehouse, cross-tenant verdict aggregation, or SLA-backed evaluation **services**.

### §10.I — Orchestration run-start (JSONL audit line)

**Master §10 intent:** the compact **`orchestration.jsonl`** stream must begin with a machine-checkable **`run_start`** record for **`execute_single_task`** runs—not only implicit logger context.

**Completed here (first-line honest scope):**

- **`ORCHESTRATION_RUN_START_CONTRACT`** (`sde.orchestration_run_start.v1`) documents the payload built by **`append_orchestration_run_start`**: non-blank **`run_id`**, **`type: run_start`**, **`mode`** ∈ {**`baseline`**, **`guarded_pipeline`**, **`phased_pipeline`**}, non-blank **`provider`** / **`model`** (contract id is documentation-only until a future on-line **`schema`** field).
- **`validate_orchestration_run_start_dict`** returns stable **`orchestration_run_start_*`** error tokens.
- **`append_orchestration_run_start`** raises **`ValueError`** with prefix **`orchestration_run_start_contract:`** if the assembled dict fails validation before **`append_jsonl`**.

Regression: **`test_orchestration_run_start_contract.py`**, **`test_public_export_surface.py`** (exports **`orchestration_run_start_contract`**).

**Not claimed in this row:** hosted trace indexing **services** or a single on-disk **`schemaVersion`** envelope for all **`orchestration.jsonl`** line types.

### §10.J — Benchmark orchestration JSONL (resume + error lines)

**Master §10 intent:** aggregate benchmark runs that append to **`orchestration.jsonl`** must emit inspectable, machine-checkable records for resume and failure paths—not only stderr or logger lines.

**Completed here (harness-line honest scope):**

- **`ORCHESTRATION_BENCHMARK_RESUME_CONTRACT`** (`sde.orchestration_benchmark_resume.v1`) documents the **`benchmark_resume`** line: non-blank **`run_id`**, **`type: benchmark_resume`**, non-negative int **`pending_task_count`**.
- **`ORCHESTRATION_BENCHMARK_ERROR_CONTRACT`** (`sde.orchestration_benchmark_error.v1`) documents the **`benchmark_error`** line: non-blank **`run_id`**, **`type: benchmark_error`**, non-blank **`error_type`**, **`error_message`** as a string (may be empty).
- **`validate_orchestration_benchmark_resume_dict`** / **`validate_orchestration_benchmark_error_dict`** return stable **`orchestration_benchmark_resume_*`** / **`orchestration_benchmark_error_*`** error tokens.
- **`run_benchmark`** raises **`ValueError`** with prefix **`orchestration_benchmark_resume_contract:`** or **`orchestration_benchmark_error_contract:`** if the assembled dict fails validation before **`append_jsonl`**.

Regression: **`test_orchestration_benchmark_jsonl_contract.py`**, **`test_public_export_surface.py`** (exports **`orchestration_benchmark_jsonl_contract`**).

**Not claimed in this row:** unified **`orchestration.jsonl`** envelope with on-disk **`schemaVersion`**, or hosted trace pipelines.

### §10.K — Orchestration stage-event (flattened trace line)

**Master §10 intent:** each **`stage_event`** row written from pipeline **`TraceEvent`** data must be structurally predictable for audits and downstream parsers—not only a mirror of arbitrary **`traces.jsonl`** blobs.

**Completed here (flattened-line honest scope):**

- **`ORCHESTRATION_STAGE_EVENT_CONTRACT`** (`sde.orchestration_stage_event.v1`) documents the flattened line built in **`append_orchestration_stage_events`**: non-blank **`run_id`**, **`type: stage_event`**, non-blank **`stage`**, int **`retry_count`** ≥ **0**, **`errors`** as a list of strings (empty allowed), non-blank ISO-like **`started_at`** / **`ended_at`**, int **`latency_ms`** ≥ **0**, and when present **`attempt`** as int / **`model_error`** as string (optional flattened **`agent`** / **`model`** / **`raw_response_excerpt`** left unvalidated for shape diversity).
- **`validate_orchestration_stage_event_line_dict`** returns stable **`orchestration_stage_event_*`** error tokens.
- **`append_orchestration_stage_events`** raises **`ValueError`** with prefix **`orchestration_stage_event_contract:`** if any assembled line fails validation before **`append_jsonl`**.

Regression: **`test_orchestration_stage_event_contract.py`**, **`test_public_export_surface.py`** (exports **`orchestration_stage_event_contract`**).

**Not claimed in this row:** hosted trace analytics **services** (native **`traces.jsonl`** row shape is **§10.N**).

### §10.L — Orchestration run-error (single-task failure line)

**Master §10 intent:** when **`execute_single_task`** fails before traces, or after traces when final output is not JSON, the **`orchestration.jsonl`** stream must still carry a machine-checkable **`run_error`** record—not only **`summary.json`** / logger text.

**Completed here (failure-line honest scope):**

- **`ORCHESTRATION_RUN_ERROR_CONTRACT`** (`sde.orchestration_run_error.v1`) documents the **`run_error`** line: non-blank **`run_id`**, **`type: run_error`**, **`mode`** ∈ {**`baseline`**, **`guarded_pipeline`**, **`phased_pipeline`**}, non-blank **`error_type`**, **`error_message`** as a string (may be empty), optional non-blank string **`detail`** (e.g. **`output_parse_failed`**), and no keys outside the allow-list.
- **`validate_orchestration_run_error_dict`** returns stable **`orchestration_run_error_*`** error tokens.
- **`_run_single_attempt`** (**`single_task`**) raises **`ValueError`** with prefix **`orchestration_run_error_contract:`** if either assembled **`run_error`** body fails validation before **`append_jsonl`**.

Regression: **`test_orchestration_run_error_contract.py`**, **`test_public_export_surface.py`** (exports **`orchestration_run_error_contract`**).

**Not claimed in this row:** hosted incident pipelines or **`append_jsonl`** writes to **`orchestration.jsonl`** outside the gated **`single_task`** / **`persist_traces`** / **`run_benchmark`** / **`write_success_artifact_layer`** paths.

### §10.M — Orchestration run-end (success closure line)

**Master §10 intent:** when a single-task run completes structured output successfully, the **`orchestration.jsonl`** stream should close with a machine-checkable **`run_end`** envelope—not only **`summary.json`** and disk artifacts.

**Completed here (success-line honest scope):**

- **`ORCHESTRATION_RUN_END_CONTRACT`** (`sde.orchestration_run_end.v1`) documents the **`run_end`** line: non-blank **`run_id`**, **`type: run_end`**, **`artifacts`** as a map of non-blank string keys to non-blank string paths, optional **`output_refusal`** (**`null`** or object), optional **`checks`** (**`null`** or list), and no keys outside the allow-list.
- **`validate_orchestration_run_end_dict`** returns stable **`orchestration_run_end_*`** error tokens.
- **`write_success_artifact_layer`** raises **`ValueError`** with prefix **`orchestration_run_end_contract:`** if the assembled **`run_end`** body fails validation before **`append_jsonl`**.

Regression: **`test_orchestration_run_end_contract.py`**, **`test_public_export_surface.py`** (exports **`orchestration_run_end_contract`**).

**Not claimed in this row:** deep validation of **`checks`** element shapes, or hosted observability pipelines (**`traces.jsonl`** line shape for gated writers is **§10.N**).

### §10.N — Traces JSONL (`TraceEvent` row)

**Master §10 intent:** each **`traces.jsonl`** row emitted by **`persist_traces`** or the benchmark harness must match the pipeline **`TraceEvent`** envelope—not only unstructured log fragments.

**Completed here (per-line honest scope):**

- **`TRACES_JSONL_EVENT_CONTRACT`** (`sde.traces_jsonl_event.v1`) documents the allow-listed keys and scalar/list shapes aligned with **`libs/sde_types/types.py`** **`TraceEvent`** / **`Score`** (**`mode`** ∈ {**`baseline`**, **`guarded_pipeline`**, **`phased_pipeline`**}, non-blank **`run_id`** / **`task_id`** / **`model`** / **`provider`** / **`stage`** / ISO-like **`started_at`** / **`ended_at`**, non-negative ints for latency/tokens/retry, non-negative **`estimated_cost_usd`**, **`errors`** as list of strings, **`score`** with boolean **`passed`** plus numeric **`reliability`** / **`validity`**, optional **`metadata`** object or **`null`**).
- **`validate_traces_jsonl_event_dict`** returns stable **`traces_jsonl_event_*`** error tokens.
- **`persist_traces`** and **`run_benchmark`** (**`on_task_events`** path) raise **`ValueError`** with prefix **`traces_jsonl_event_contract:`** if any event dict fails validation before **`append_jsonl`**.

Regression: **`test_traces_jsonl_event_contract.py`**, **`test_public_export_surface.py`** (exports **`traces_jsonl_event_contract`**), **`test_benchmark_harvest.py`** (synthetic **`TraceEvent`** rows).

**Not claimed in this row:** hosted trace indexing, cross-run trace analytics, or schema versioning on **`traces.jsonl`** files.

---

## P4 — §15 Production architecture (what runs on the laptop)

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Local runtime (Python, deterministic FSMs) | §15 | **68** | This repo’s strength for **CLI** scope — contracts on runner outputs reinforce determinism; still not a pinned worker image / fleet runtime. |
| Orchestration (leases, arbitration order, sharding) | §15 | **46** | Leases/worktrees/session scheduler; not shard hierarchy + admission at scale. |
| Observability (OTel, forensics bundles) | §15 | **48** | **`orchestration.jsonl`**: **`run_start`** (**§10.I**), **`run_error`** (**§10.L**), flattened **`stage_event`** (**§10.K**), **`run_end`** (**§10.M**), **`benchmark_resume`** / **`benchmark_error`** (**§10.J**); **`traces.jsonl`** row contract (**§10.N**); `run.log`, Stage 1 export APIs; **no** OpenTelemetry + ops gateway as in master §15. |
| Memory (policy-driven triple store) | §15 | **30** | Same as §8; **HS21–HS24** strengthen run-local memory **evidence**, not triple-store **services**. |
| Identity and authorization (per-action identity, tokens) | §15 | **30** | **HS29–HS32** + plan-lock/reviewer artifacts; **not** cryptographic IAM plane. |
| Storage (Postgres event store, projections, vector) | §15 | **0** | **No** Postgres / vector / projection DB in `src/`; persistence is **JSON/JSONL files** (`libs/storage/storage.py`). |

---

## P5 — §12 Event-sourced architecture

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Replay (fail-closed on manifest mismatch) | §12 | **50** | `workflow_pipelines/production_pipeline_task_to_promote/replay.py` + **HS18** `replay_manifest.json`; fail-closed **for CLI runs**, not multi-tenant store SLOs. |
| Event store (append-only, ordering, idempotency) | §12 | **36** | `event_store/run_events.jsonl` + **HS17/HS20**; **not** Postgres append-only + hash-chain **service**. |
| Learning lineage (mandatory chain for promotion) | §12 | **35** | Lineage layers + learning artifacts; platform-wide invalidation without lineage **not** enforced. |
| Auditability (hash-chain, periodic scans) | §12 | **30** | Manifest digests + validation; **no** operational hash-chain / periodic integrity **service**. |

---

## P6 — §14 / §26 Success criteria (metrics and hard gates)

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Stability metrics (unsafe rate, replay drift, rollback drills) | §14, §26 | **28** | Some local signals; **§26.5** items like `MandatoryChaosSuitePass` **not** implemented (no chaos harness). |
| Error reduction metrics | §14 | **18** | Partial via summaries; not KPI program. |
| Hard release gates (§14 numeric thresholds) | §14 | **24** | Thresholds exist in master; **not** a continuously scored production program in-repo. |
| Extended binary gates (§26.5) | §26 | **14** | Adds `CriticalPolicyDriftIncidents`, `MandatoryChaosSuitePass` vs §14; **no** automated score engine / weekly windows. |
| Capability growth metrics | §14 | **12** | **Missing** as automated dashboards. |
| Transfer learning metrics | §14 | **6** | **Missing**. |

---

## P7 — §4 Core components (named system parts)

Rows ordered **end-user impact**: trust and execution path first, then data planes, then long-horizon strategy.

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Safety controller (guardrails, veto, rollback) | §4, §11 | **58** | **HS01–HS32** + static gates + kill-switch lineage (**HS19**); still **not** centralized veto **service** + automated rollback. |
| Orchestrator (federated state-machine coordination) | §4 | **57** | `orchestrator` + `sde` CLI + project driver/scheduler; **not** federated multi-shard control plane. |
| Evaluation service (offline + online + regression + promotion) | §4, §13 | **65** | §10.A–N (**`benchmark/*`** + **`runner/orchestration_*_contract`** + **`runner/traces_jsonl_event_contract`**) + §13.A–D; `validate`, reports + promotion artifacts; **not** full evaluation **service** + live shadow plane. |
| Observability (traces / logs / metrics / replay / lineage) | §4, §15 | **50** | **`orchestration.jsonl`** contracts: **`run_start`** (**§10.I**), **`run_error`** (**§10.L**), **`stage_event`** (**§10.K**), **`run_end`** (**§10.M**), **`benchmark_resume`** / **`benchmark_error`** (**§10.J**); **`traces.jsonl`** (**§10.N**); logs, session status/export; **not** OpenTelemetry + gateway **as specified**. |
| Role agents (execution, review, evaluation, learning, practice, management) | §4, §5 | **22** | **Behavior** in prompts/pipeline stages; no `agents/*` packages or isolated credentials. |
| Memory system (episodic / semantic / skill) | §4, §8 | **32** | Local artifacts + **HS21–HS24**; **not** three durable typed stores. |
| Event store (immutable source of truth) | §4, §12 | **36** | Same as P5; run-local event log + gates, **not** platform store. |
| Learning service (reflection, adaptation governance) | §4, §9 | **34** | `self_evolve` / learning JSONL + **HS25–HS28**; **not** policy-governed learning **service**. |
| Identity and authorization plane | §4, §15 | **30** | **HS29–HS32** artifact checks; not cryptographic IAM plane. |
| Objective policy engine (arbitration / reward shaping) | §4, §11 | **22** | Gate scores + static analysis; no **OPE** service / §24.3 arbitration contract file. |
| Practice engine (skill-gap remediation) | §4, §9 | **22** | **HS27** `practice/task_spec.json`; still **not** dedicated practice **service** + quota plane. |
| Career strategy layer | §4 | **5** | **Missing** as layer; roadmap text only. |

---

## P7b — §8 Memory architecture

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Write policy (provenance, quarantine, approvals) | §8 | **34** | **HS21** retrieval provenance, **HS22** quarantine; not memory-lifecycle **mutator service**. |
| Memory types (episodic / semantic / skill) | §8 | **30** | Artifact shapes + **HS23** skill surface; not three durable stores. |
| Retrieval policy (two-stage, routing, freshness) | §8 | **18** | Provenance gate only; **missing** two-stage ranker / routing **engine**. |
| Memory lifecycle (hot/warm/cold, compaction) | §8 | **10** | **Missing** as operational tiers. |
| Memory quality metrics | §8 | **18** | **HS24** `memory/quality_metrics.json`; not continuous metrics **product**. |

---

## P7c — §9 Learning and evolution engine

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Reflection loop chain | §9 | **35** | Reflection bundles + roadmap-review flows; not RCA **service**. |
| Learning updates (classes + validation + lineage) | §9 | **34** | JSONL + evolve + **HS25–HS28**; not signed update governance. |
| Skill gap detection | §9 | **24** | **HS27** + heuristics; not normalized taxonomy **service**. |
| Causal closure contract | §9 | **30** | **HS25** `learning/reflection_bundle.json` gate; **not** standalone closure **engine**. |
| Practice loop + protected practice capacity | §9 | **18** | **HS27** artifact; **missing** quota-protected practice **plane**. |
| Capability improvement over windows | §9 | **15** | **Missing** as automated measurement. |

---

## P8 — §5 Agent organization

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Reviewer / Evaluator agents | §5 | **35** | Review/verify stages; evaluator authority **partial** vs master. |
| Interaction contracts (no self-approval, schema handoffs, lease+heartbeat, role registry) | §5 | **40** | Schema validation + leases (session); **no** canonical cryptographic role registry / global lease enforcement. |
| Junior / Mid / Senior / Architect agent roles | §5 | **20** | Not packaged; embodied loosely in pipeline. |
| Learning / Practice agents | §5 | **20** | Learning hooks exist; practice agent **not** standalone. |
| Manager / Specialist / CareerStrategy agents | §5 | **5** | **Missing** as first-class roles. |

---

## P8b — §6 Agent lifecycle

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Autonomy levels + trust progression | §6 | **25** | Risk/token budgets in gates; not full trust matrix product. |
| Promotion rules (thresholds, suites, lineage, committee) | §6 | **24** | **HS26** + **`promotion_eval_contract`** (**§13.C**) on **`lifecycle/promotion_package.json`**; **no** governance **service** or committee automation. |
| Recertification + decay | §6 | **15** | Capability decay in master; **not** backed by capability-graph service. |
| Lifecycle stages graph | §6 | **10** | Documented in master; **not** automated progression engine. |
| Demotion logic | §6 | **10** | **Minimal** automation vs master. |
| Stagnation detection + intervention ladder | §6 | **10** | **Missing** as automated governor. |

---

## P8c — §7 Capability model

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Dependency-aware promotion / eligibility | §7 | **25** | Plan `depends_on` + scheduler; not capability-node graph. |
| Scoring, confidence, decay | §7 | **15** | Partially mirrored in gate scores; not graph-backed. |
| Capability graph (nodes, edges, L0–L5) | §7 | **10** | **Missing** service; local signals only. |
| Transfer learning measurement | §7 | **10** | **Missing** as explicit measurement plane. |

---

## P8d — §3 Human professional evolution model (behaviors)

| Feature / theme | Master § | % done | Notes |
|-----------------|----------|--------|--------|
| Feedback loops (review → reflection → gated updates) | §3 | **35** | Partial via verifier/review JSON + learning harness files. |
| Human growth loop (task → … → capability) | §3 | **35** | Reflected in guarded/phased pipelines + project driver; not institution-wide. |
| Institutional memory (typed stores + policy) | §3 | **25** | Run/session artifacts + memory-related hard-stops; not durable memory **services**. |
| Human → agent behavior mapping | §3 | **30** | Implicit in orchestrator modes; no distinct agent packages per role. |
| Deliberate practice from verified gaps | §3 | **20** | Practice/skills in master; local practice loop mostly **not** productized. |
| Career progression model | §3 | **15** | Conceptual mapping only; no `lifecycle-governance` service. |
| Mentorship operating model (assignment, cadence, quality scores) | §3 | **15** | Review artifacts + Stage 1 intake; no mentor assignment **service** or quality scoring plane. |
| Performance review cycle (windows, committee, plans) | §3 | **10** | Evaluation windows not automated as master describes. |

---

## P9 — §16 Scalability strategy

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Multi-agent scaling (federated partitions, fair scheduling) | §16 | **30** | Parallel worktrees + caps; not federated orchestrator. |
| Replay scaling (projections, bounded windows) | §16 | **20** | Partial read-only summaries (`project status` phases); not projection **service**. |
| Event scaling (retention, compaction, replay SLOs) | §16 | **15** | **Missing** platform ops. |
| Memory scaling (utility-aware policies) | §16 | **10** | **Missing**. |

---

## P9b — §22 Service boundaries (named services)

Rows ordered **closest to user-visible quality and throughput** first; back-office and simulation last.

| Service | Master §22 | % done | Notes |
|---------|--------------|--------|--------|
| `safety-controller` | §22 | **52** | Gates + static analysis approximate. |
| `evaluation` | §22 | **42** | Local benchmark/validate/report. |
| `orchestrator` | §22 | **57** | Python package + CLI; not full shard/deadlock plane. |
| `quota-scheduler` | §22 | **30** | Token/time budgets in runner; not global quota plane. |
| `model-router` | §22 | **25** | Ollama + env overrides; not quota/risk router service. |
| `observability-gateway` | §22 | **27** | Files + exports; not gateway product. |
| `event-store` | §22 | **32** | Run-local logs; not durable service. |
| `identity-authz` | §22 | **25** | Local attestation / reviewer policy only. |
| `memory-lifecycle` | §20–§22 | **30** | **HS21–HS24** enforce memory evidence paths; **no** long-running lifecycle **mutator service**. |
| `memory-poisoning-sentinel` (master §20 / §26) | §20, §26 | **22** | Quarantine + quality gates overlap **HS22/HS24**; **not** dedicated sentinel **runtime** from diagram. |
| `learning-update` | §22 | **32** | Harness + **HS25–HS28**; not signed rollout **service**. |
| `reflection-rca` | §22 | **22** | Reflection bundles + **HS25**; not RCA **service**. |
| `objective-policy-engine` | §22 | **22** | Gate logic only; **no** §24.3 `objective_arbitration` contract artifact in-repo. |
| `projection-query` | §22 | **15** | Status/read helpers; not query service. |
| `canary-rollout` | §22 | **30** | **HS28** + **`online_eval_shadow_contract`** (**§13.D**) on **`learning/canary_report.json`**; **not** rollout **controller service**. |
| `policy-management` | §22 | **10** | **Missing** signed bundle registry. |
| `lifecycle-governance` | §22 | **12** | **HS26** artifacts only; **missing** decision **service**. |
| `capability-graph` | §22 | **12** | **HS23** `capability/skill_nodes.json`; **missing** graph **service**. |
| `storage-lifecycle-manager` (§19C) | §19C | **8** | Event/memory growth controls **not** a named manager service; disk JSONL only. |
| `autonomy-sla-monitor` (master §20 / §28) | §20, §28 | **8** | **Missing** as product; success metrics not wired to SLA **monitor**. |
| `binary-release-gate-engine` (§26 P0) | §26 | **22** | Gates approximate spirit; **no** signed evidence engine per §26.2. |
| `incident-ops` | §22 | **15** | Docs/runbooks; not service. |
| `chaos-simulator` | §22 | **5** | **Missing** (no harness in tree). |
| Boundary contracts (versioned comms, single-writer rules) | §22 | **18** | Python schemas + gate evidence; **no** `contracts/` tree + cross-service RPC enforcement. |

---

## P9c — §23 Full build order (Stages A–J)

| Stage | Master §23 | % done | Notes |
|-------|--------------|--------|--------|
| H — Evaluation, resilience, security hardening | §23 | **38** | Tests + gates; chaos/adversarial suites **thin**. |
| D — Orchestration hierarchy + multi-agent topology | §23 | **36** | Session scheduler + worktrees; not full hierarchy. |
| C — Event, projection, observability backbone | §23 | **32** | Local only; forensics tooling partial. |
| B — Deterministic runtime + identity core | §23 | **25** | No deterministic worker image + crypto IAM. |
| G — Learning engine + causal closure | §23 | **25** | Partial local; no closure engine service. |
| A — Foundations and contract freeze | §23 | **20** | Contracts not CI-frozen as master describes. |
| F — Memory governance + defense | §23 | **24** | **HS21–HS24** give gate-level defense; **missing** dedicated Memory Poisoning Sentinel + repair **services** (master §23.F exit). |
| E — Capability + lifecycle governance | §23 | **15** | **Missing** services. |
| I — Curriculum + cold-start | §23 | **15** | Benchmark JSONL; not curriculum **product**. |
| Global Go/No-Go (§23 end) | §23 | **15** | Not satisfied for full master program. |
| J — Long-horizon evolution + federation readiness | §23 | **10** | **Mostly missing**. |

---

## P10 — §17 Implementation roadmap (phases 0–4 + repo spine note)

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Repository implementation spine (this repo) | §17 | **75** | **Aligned** with `UNDERSTANDING-THE-CODE.md` + **`src/guardrails_and_safety/`** (**HS01–HS32**) + `src/workflow_pipelines/production_pipeline_task_to_promote/` per master §17; **not** the full §21 service monorepo. |
| Phase 0 — Core runtime | §17 | **62** | CLI + **32** hard-stops + replayable task loop meet **much** of Phase 0 **locally**; still not durable platform exits. |
| Phase 0.5 — Contract freeze (roadmap governance) | §17 | **14** | Master requires **Phase 0.5** before scale; repo has **Python** schemas + gates but **no** repo-root **`contracts/`** CI freeze as specified. |
| Phase 2 — Multi-agent evolution | §17 | **40** | Worktrees/parallel + **HS29–HS32**; crypto IAM + full contracts **incomplete**. |
| Phase 1 — Single agent evolution | §17 | **36** | Memory/learning/capability **artifacts** improved vs prior estimate; durable services **still** thin. |
| Phase 3 — Autonomous learning | §17 | **34** | **HS25–HS28** add learning-plane **evidence**; automated rollback + adaptation control plane **mostly missing**. |
| Phase 4 — Organization intelligence | §17 | **10** | **Largely missing**. |

---

## P10b — §19 Consolidated improvements (selected named gaps)

| Named item | Master § | % done | Notes |
|------------|----------|--------|--------|
| Executable permission matrix | §19A | **35** | Gates + CLI flags; not full matrix service. |
| Objective arbitration contract | §19A | **20** | Partially reflected in gates; not standalone contract+engine. |
| Adaptation control plane + learning FSM | §19B | **30** | Local runner FSM stronger than learning plane. |
| Identity/authz plane | §19B | **25** | Same as IAM rows. |
| Incident operations + forensics | §19B | **20** | Runbooks/docs; not `incident-ops` service. |
| Versioned machine-validated contracts + CI | §19B | **12** | Python schemas + gate evidence; repo-root **`contracts/`** tree **absent** (see **§24.3** table in P10d). |
| Stagnation/drift governor + lifecycle governance | §19B | **15** | **Missing** services. |
| Projection/query + schema registry + upcaster | §19B | **10** | **Missing** tools/services. |
| §19C missing components (OPE, adaptation plane, causal closure engine, LGS, permission matrix, projection, schema registry, IAM, incident console, stagnation governor, mentorship ops, career strategy) | §19C | **5–20** each | See **P9b** (incl. **storage lifecycle**, **sentinel**, **SLA monitor**); no separate deployable for each. |
| §19D P1 hardening | §19D | **30** | Resource caps partial; signed bundles / full lineage **incomplete**. |
| §19D P0 blockers | §19D | **25** | Policy freeze / event contract v1 / role registry / recovery FSM / binary gates **not** all closed as program. |
| §19D P2 production confidence | §19D | **25** | Partial docs/tests; drills not fully institutionalized. |
| §19E exit-to-production rule | §19E | **20** | **Cannot** be claimed met for full master scope. |

---

## P10c — §20–21 Topology and repository layout

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Missing-area coverage map items | §20 | **15–40** each | Same as service rows; highest where orchestrator/gates overlap. |
| Production component topology (control/data/learning/eval/ops planes) | §20 | **20** | Conceptual match to **stubs** and local flows; not deployed topology. |
| Structural rules (contract ownership, promotion lineage) | §21 | **25** | Enforced **locally** for runs/sessions; not org-wide. |
| Target monorepo layout (`contracts/`, `services/`, `agents/`, `runtime/`, `libraries/`, `infra/`, `tests/` pillars) | §21 | **15** | Actual repo is **Python-centric** under `src/`; master layout **not** realized. |

---

## P10d — §24–27 Closure, security, reliability, scalability plans

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Security hardening plan execution | §25 | **36** | Static gates + tests; not full §25 program (mTLS, prompt gateway, threshold sigs, etc.). |
| Reliability / resilience plan execution | §26 | **34** | Retries/timeouts + gate-backed rollback **story**; **no** §26.2 P0/P1 **contract engines** as separate products. |
| Scalability / performance plan execution | §27 | **26** | Local constraints only; **no** §27 KPI dashboard plane. |
| Production closure plan (§24 gaps → remediations) | §24 | **20** | Architecture items **open**; mandatory **§24.3** contract packages **not** present as versioned artifacts in-repo (see table below). |

### §24.3 mandatory contract artifacts (presence vs master)

Master §24.3 names versioned contracts; **none** exist today as **`contracts/**` files** (repository glob / `find` check 2026-04-20). Scores are **0** for “as shipped artifacts”; ideas partially exist only in Python gate logic.

| Contract (master §24.3) | % done | Notes |
|-------------------------|--------|--------|
| `contracts/policy/objective_arbitration.v1.json` | **0** | Arbitration logic scattered in gates; **no** standalone signed decision artifact contract. |
| `contracts/service/common_rpc.v1.json` | **0** | **No** inter-service RPC contract file. |
| `contracts/orchestrator/hierarchy.v1.json` | **0** | Scheduler behavior in code; **no** hierarchy contract file. |
| `contracts/orchestrator/deadlock.v1.json` | **0** | **No** deadlock contract artifact. |
| `contracts/runtime/deterministic_worker.v1.json` | **0** | **No** pinned worker image contract in-repo. |
| `contracts/policy/policy_bundle.v2.json` | **0** | **No** policy bundle registry file format in-repo. |

---

## P10e — §28 Production readiness program (100-point model)

| Feature | Master § | % done | Notes |
|---------|----------|--------|--------|
| Weighted scoring model (§28.3 categories) | §28 | **15** | Informally approximated by this table only. |
| Hard gates (OpenP0/OpenP1, lineage completeness) | §28 | **20** | Partial local analogs; not program-operational. |
| Readiness tracker schema + governance cadence | §28 | **10** | **Not** implemented as automated score tracker in repo. |

---

## P11 — §1–2 Intent, vision, constraints (strategic framing)

| Feature / theme | Master § | % done | Notes |
|-----------------|----------|--------|--------|
| Policy-gated autonomy + rollback-first safety | §2 | **42** | Strong **local** gate story (`src/guardrails_and_safety/`); no signed policy bundles / atomic rollback service. |
| Event-sourced evidence + replay narrative | §1–2 | **42** | Run-local `run_events.jsonl` + `replay_manifest.json` + **HS17–HS20**; **not** Postgres-backed platform store. |
| Longitudinal capability growth (vs one-shot demos) | §1 | **27** | Directionally supported via project session, reviews, gates; no org-wide capability service. |
| Local-first / `local-prod` production profile | §2, §15 | **32** | Local CLI + profiles in prose; full **`local-prod`** infra as code **not** shipped. |
| Role-based progression + trust controls | §2 | **22** | Lifecycle/promotion **specified** in master; local gates only partially encode trust. |
| One-shot production readiness (P0/P1, replay manifests) | §2, §19D | **27** | Partial replay/validate; P0/P1 checklist **not** closed as a program. |

---

## Changelog

- **2026-04-20 (percentages + evidence):** Re-scored feature tables for **current** repo reality (**215** Part A `src`+`libs` `.py`/`.md` paths and **69** `test_*.py` files per **`test_architecture_test_file_inventory.py`**); refreshed evidence snapshot; nudged §10–§13 / P4–P7 / P9–P11 rows where JSONL + benchmark contracts materially strengthen the local spine while Postgres / **`contracts/`** / OTel / chaos remain absent.
- **2026-04-19 (layout spec):** Linked [`repository-layout-from-completion-inventory.md`](repository-layout-from-completion-inventory.md) as the canonical map (`src/<section_snake>/` + row folders + `src/` inventory + TBD mappings); **2026-04-20:** wording updated post-migration (Part A live tree + Part C legacy keys).
- **2026-04-19 (evidence pass):** Added **tree-verified snapshot** (HS01–HS32, test file count, absent `contracts/` / Postgres / OTel / chaos); expanded **§10 strategy overlay**, **§26.5 gates**, **§19C storage lifecycle**, **§20 sentinel/SLA/gate engine** rows; **§24.3 contract artifact table** (all **0%** as files); nudged percentages where **`src/guardrails_and_safety/`** materially covers memory, events, learning, and org slices.
- **2026-04-20 (layout migration):** Python tree moved to `src/<section>/<row>/` + `libs/`; see `CHANGELOG.md` and `docs/architecture/adr-gates-hs-row-mapping.md`.
- **2026-04-20 (doc):** “What this file is” now names repo-root **`libs/`**; cross-checks explicitly include **[`repository-layout-from-completion-inventory.md`](repository-layout-from-completion-inventory.md)** Part A and **`libs/`** alongside **`src/`**. *(Superseded counts: an intermediate edit listed **47** tests / **173** paths; CI now enforces **69** tests and **215** Part A paths — see evidence snapshot above.)*
- **2026-04-20 (§11.A):** **Review gating + evaluator authority** marked **100%** for repo-local scope: **`review_findings`** + **HS15** blocker/pass honesty + schema **1.1** / **`REQUIRED_REVIEW_KEYS`** update.
- **2026-04-19 (§11.B + inventory):** **Risk budgets + permission matrix** to **58%** (**`hard_stop_schedule`**, **`test_hard_stop_schedule.py`**); evidence snapshot **175** Part A paths / **48** `test_*.py` files; §11.A clarified (CTO **`cto_publish`** path vs test stubs for **`review.json`**).
- **2026-04-19 (§11.C + inventory):** **Autonomy boundaries** to **68%** — **`token_context`** expiry fields + **HS06** / **HS30** expiry enforcement + **`parse_iso_utc`**; evidence snapshot **176** Part A paths / **49** `test_*.py` files.
- **2026-04-19 (§11.D + inventory):** **Dual control** to **52%** — **`program/dual_control_ack.json`**, **HS08** dual-ack rules, guarded **`completion_layer`** stub writer, **`gates_manifest`** completion path; evidence snapshot **177** Part A paths / **50** `test_*.py` files.
- **2026-04-19 (§11.E + inventory):** **Rollback rules** to **48%** — **`policy_bundle_rollback`**, **`program/policy_bundle_rollback.json`**, **`validate_execution_run_directory`** hook; evidence snapshot **179** Part A paths / **51** `test_*.py` files.
- **2026-04-19 (§13.A + inventory):** **Offline evaluation** to **58%** — **`benchmark/offline_eval_contract`**, **`read_suite`** structural gate, **`test_offline_eval_suite_contract.py`**; evidence snapshot **181** Part A paths / **52** `test_*.py` files.
- **2026-04-19 (§13.B + inventory):** **Regression testing** to **52%** — **`benchmark/regression_surface_contract`**, **`test_regression_surface_contract.py`**; evidence snapshot **183** Part A paths / **53** `test_*.py` files.
- **2026-04-19 (§13.C + inventory):** **Promotion evaluation** to **40%** — **`benchmark/promotion_eval_contract`**, gate in **`write_evolution_artifacts`**, **`test_promotion_eval_package_contract.py`**; evidence snapshot **185** Part A paths / **54** `test_*.py` files.
- **2026-04-19 (§13.D + inventory):** **Online evaluation** (shadow/canary artifact) to **28%** — **`benchmark/online_eval_shadow_contract`**, gate in **`write_evolution_artifacts`**, **`test_online_eval_shadow_contract.py`**; evidence snapshot **187** Part A paths / **55** `test_*.py` files.
- **2026-04-19 (§10.A + inventory):** **Strategy overlay** to **22%** — **`benchmark/strategy_overlay_contract`**, gate in **`write_organization_artifacts`**, **`test_strategy_overlay_contract.py`**; evidence snapshot **189** Part A paths / **56** `test_*.py` files.
- **2026-04-19 (§10.B + inventory):** **Production pipeline** to **48%** — **`benchmark/production_pipeline_plan_contract`**, gate in **`write_completion_artifacts`**, **`test_production_pipeline_plan_contract.py`**; evidence snapshot **191** Part A paths / **57** `test_*.py` files.
- **2026-04-19 (§10.C + inventory):** **Retry pipeline** to **57%** — **`benchmark/retry_pipeline_contract`**, gate on **`execute_single_task`** repeat envelope, **`test_retry_pipeline_repeat_contract.py`**; evidence snapshot **193** Part A paths / **58** `test_*.py` files.
- **2026-04-19 (§10.D + inventory):** **Failure pipeline** to **48%** — **`benchmark/failure_pipeline_contract`**, gates on **`write_event_lineage_artifacts`** / **`write_failure_summary`**, **`test_failure_pipeline_contract.py`**; evidence snapshot **195** Part A paths / **59** `test_*.py` files.
- **2026-04-19 (§10.E + inventory):** **Deterministic state machines** to **52%** — **`benchmark/run_manifest_contract`**, gate on **`execute_single_task`** before **`run-manifest.json`**, **`test_run_manifest_contract.py`**; evidence snapshot **197** Part A paths / **60** `test_*.py` files; **P7** evaluation row notes §10.A–E.
- **2026-04-19 (§10.F + inventory):** **Improvement pipeline** to **45%** — **`benchmark/benchmark_manifest_contract`**, gate on **`run_benchmark`** manifest write + resume, **`test_benchmark_manifest_contract.py`**; evidence snapshot **199** Part A paths / **61** `test_*.py` files; **P7** evaluation row notes §10.A–F.
- **2026-04-19 (§10.G + inventory):** **Improvement pipeline** to **50%** — **`benchmark/benchmark_checkpoint_contract`**, gate on **`run_benchmark`** **`benchmark-checkpoint.json`** writes + resume read, **`test_benchmark_checkpoint_contract.py`**; evidence snapshot **201** Part A paths / **62** `test_*.py` files; **P7** evaluation row notes §10.A–G.
- **2026-04-19 (§10.H + inventory):** **Improvement pipeline** to **52%** — **`benchmark/benchmark_aggregate_summary_contract`**, gate on **`run_benchmark`** **`summary.json`** (success + abort), **`test_benchmark_aggregate_summary_contract.py`**; evidence snapshot **203** Part A paths / **63** `test_*.py` files; **P7** evaluation row notes §10.A–H.
- **2026-04-19 (§10.I + inventory):** **Deterministic state machines** to **54%** — **`runner/orchestration_run_start_contract`**, gate on **`append_orchestration_run_start`** before **`orchestration.jsonl`** append, **`test_orchestration_run_start_contract.py`**; **P4** / **P7** observability rows note **`run_start`** contract; evidence snapshot **205** Part A paths / **64** `test_*.py` files; **P7** evaluation row notes §10.A–I.
- **2026-04-19 (§10.J + inventory):** **Improvement pipeline** to **54%** — **`benchmark/orchestration_benchmark_jsonl_contract`**, gates on **`run_benchmark`** **`benchmark_resume`** / **`benchmark_error`** **`orchestration.jsonl`** lines, **`test_orchestration_benchmark_jsonl_contract.py`**; **P4** / **P7** observability rows note harness orchestration lines; evidence snapshot **207** Part A paths / **65** `test_*.py` files; **P7** evaluation row notes §10.A–J.
- **2026-04-19 (§10.K + inventory):** **Deterministic state machines** to **56%** — **`runner/orchestration_stage_event_contract`**, gate on each **`stage_event`** line before **`append_orchestration_stage_events`**, **`test_orchestration_stage_event_contract.py`**; **P4** / **P7** observability rows note **`stage_event`** contract; evidence snapshot **209** Part A paths / **66** `test_*.py` files; **P7** evaluation row notes §10.A–K.
- **2026-04-19 (§10.L + inventory):** **Deterministic state machines** to **58%** — **`runner/orchestration_run_error_contract`**, gate on **`run_error`** lines before **`single_task`** **`orchestration.jsonl`** appends, **`test_orchestration_run_error_contract.py`**; **P4** / **P7** observability rows note **`run_error`** contract; evidence snapshot **211** Part A paths / **67** `test_*.py` files; **P7** evaluation row notes §10.A–L.
- **2026-04-19 (§10.M + inventory):** **Deterministic state machines** to **60%** — **`runner/orchestration_run_end_contract`**, gate on **`run_end`** before **`write_success_artifact_layer`** **`orchestration.jsonl`** append, **`test_orchestration_run_end_contract.py`**; **P4** / **P7** observability rows note **`run_end`** contract; evidence snapshot **213** Part A paths / **68** `test_*.py` files; **P7** evaluation row notes §10.A–M.
- **2026-04-19 (§10.N + inventory):** **Deterministic state machines** to **62%** — **`runner/traces_jsonl_event_contract`**, gate on **`TraceEvent`**-shaped dicts before **`persist_traces`** / **`run_benchmark`** **`traces.jsonl`** appends, **`test_traces_jsonl_event_contract.py`**; **P4** / **P7** observability rows note **`traces.jsonl`** contract; evidence snapshot **215** Part A paths / **69** `test_*.py` files; **P7** evaluation row notes §10.A–N.
- **2026-04-19 (later):** Reordered all tables and sections by **CTO / end-user implementation priority** (P1–P11); within each table, rows sorted **highest user benefit first**. Master § references kept on every row.
- **2026-04-19:** Initial inventory derived from [`../AI-Professional-Evolution-Master-Architecture.md`](../AI-Professional-Evolution-Master-Architecture.md) sections §1–§28; percentages are **repo-grounded estimates** (review quarterly or when `src/` changes materially).
