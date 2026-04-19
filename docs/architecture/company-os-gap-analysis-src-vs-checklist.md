# Company OS gap analysis (checklist vs actual `src/`)

This document compares the full Company OS checklist to what is currently implemented in code, focused on the `src/` tree and adjacent repo structure.

Status labels:

- `implemented`: materially present in code paths
- `partial`: scaffold, harness, or local-only slice exists
- `missing`: not implemented as a real code surface in this repo

Scope note:

- This is a code reality check, not a roadmap.
- Many missing items do have version plans under `docs/versioning/plans/`, but plan presence is not implementation.

## Evidence snapshot (repo shape)

- Python **3.11** for local **`uv`** and CI: repo-root **`.python-version`**, **`pyproject.toml`** `requires-python`, **`.github/workflows/ci.yml`**
- Present core runtime: `src/orchestrator`, `src/sde_pipeline`, `src/sde_gates`, `src/sde_modes`, `src/sde_foundations`
- Missing top-level implementation trees: no `src/contracts/`, no `src/services/`, no `tools/`, no `infra/`
- Tests are mainly unit tests under `src/orchestrator/tests/unit/`

## Section-by-section checklist status

## 1) End-to-end delivery story (Tier 2.1)

- Stage 1 machine-runnable intake: `partial`
  - Evidence:
    - Intake scaffold + merge anchor validation: `orchestrator/api/project_intake_scaffold.py`, `project_intake_util.py`
    - Invalid reviewer output rejection: `project_validate.py` + `intake_doc_review_errors(...)`
    - Bounded revise-loop state + deterministic local auto-regeneration: `project_intake_revise.py` (`retry_allowed` -> `blocked_human`, updates digest/workbook/autogen artifact on failures)
    - Plan-lock readiness + lock artifact: `project_plan_lock.py` (`project_plan_lock.json`)
    - Runtime lock enforcement: `project_driver.py` (`enforce_plan_lock`, optional `require_non_stub_reviewer` when lock is enforced; forwarded from `continuous_run.run_continuous_project_session` and CLI `project run` / `continuous`)
    - Preflight lock enforcement: `project_validate.py` (`require_plan_lock`)
    - Operator visibility: `project_status.py` (`plan_lock` block + glance fields/red flags, including reviewer policy/source signals)
    - Planner vs reviewer separation proof at lock: `reviewer_identity.json` (`role=reviewer`, actor matches `doc_review.reviewer`, attestation + reviewed_at required) and reviewer actor differs from planner actor (`planner_identity.json`); `reviewed_at` consistency enforced within bounded skew
    - Optional strict reviewer policy in lock/preflight/runtime: `--require-non-stub-reviewer` on `project plan-lock` and `project validate --require-plan-lock`, and (with `--enforce-plan-lock`) on `project run` / `continuous` project mode, rejects `attestation_type=local_stub` with fail-closed reason `reviewer_identity_attestation_stub_disallowed`; CLI also honors `SDE_REQUIRE_NON_STUB_REVIEWER` when those commands apply strict policy (API defaults unchanged for local/tests)
    - Policy-aware reviewer proof summary persisted in lock: `project_plan_lock.json.reviewer_proof_summary` includes `local_stub_allowed` + `attestation_policy_ok`, and `project_status.status_at_a_glance` surfaces these with `reviewer_signal_source`
    - Intake lineage manifest + hash checks at lock: `project_plan_lock.py` (`intake/lineage_manifest.json`)
    - CI wall-clock SLO on Stage 1 preflight: `scripts/run-stage1-suite.sh` + `STAGE1_SUITE_MAX_SECONDS` in `.github/workflows/ci.yml`
    - Legacy harness completion artifacts: `sde_pipeline/runner/completion_layer.py`
  - Remaining gap:
    - No independent planner/reviewer model execution boundary with real credentials/service-backed attestation
    - Revise loop is still local deterministic regeneration; not yet integrated with model-driven autonomous re-planning/doc regeneration
    - No production observability pipeline/service for `doc_review` latency + retry SLOs (session-local metrics + `project status` + optional `intake/stage1_observability_export.json` from `export-stage1-observability`; no hosted pipeline)
- LearningFirstProfile minimum learning events: `partial`
  - Evidence: `program/learning_events.jsonl` harness writer in completion layer
  - Gap: no durable policy-enforced learning event service
- True parallel lanes with per-lane queues and bounded concurrency: `partial`
  - Evidence: `orchestrator/api/project_scheduler.py`, `project_parallel.py`, `project_driver.py` with optional parallel worktrees and `max_concurrent_agents`
  - Gap: no durable lane queue platform or distributed coordination surface
- Leases + heartbeats with enforced write ownership: `partial`
  - Evidence: `orchestrator/api/project_lease.py`, lease pruning/heartbeat in `project_driver.py`
  - Gap: enforcement is local/session-centric, not global service boundary enforcement across all writes
- Contract-step gating: `partial`
  - Evidence: plan schema and per-step verification surfaces (`project_schema.py`, `project_verify.py`)
  - Gap: no shared contract service + cross-service dependency gate system
- Separation of duties (planner/implementor/reviewer): `partial`
  - Evidence: verifier/review artifact loops and hard-stop checks exist
  - Gap: no independent credentialed reviewer service or identity isolation plane
- Orchestrated writes through enforcing APIs: `partial`
  - Evidence: orchestrator APIs and session driver own key flows
  - Gap: not all mutation paths are mediated by a single enforceable boundary in a multi-service architecture
- Per-step review loop: `implemented` (local/session level)
  - Evidence: `step_reviews/*.json` flow in completion + hard-stop checks
- Verification from plan with attribution loop: `partial`
  - Evidence: `project_verify.py`, verification bundle surfaces, status/aggregate APIs
  - Gap: still local/session artifact flow; not platform-wide service verification graph
- DoD automation: `partial`
  - Evidence: session-level DoD aggregate (`project_aggregate.py`, `definition_of_done.json`)
  - Gap: no enterprise-scale DoD enforcement across services/releases
- Cross-run learning (causal closure, canary, promotion): `partial`
  - Evidence: `self_evolve.py`, evolution/organization hard-stop surfaces
  - Gap: no durable independent evaluator + promotion pipeline services
- Durable event platform (append-only, replay platform): `partial`
  - Evidence: run-local `event_store/run_events.jsonl` and `replay_manifest.json`
  - Gap: no central durable event platform service
- Durable memory platform: `partial`
  - Evidence: run-local memory artifacts and hard-stop checks
  - Gap: no long-lived memory lifecycle service/policies
- Continuous CTO gates at all boundaries: `partial`
  - Evidence: robust local hard-stops and balanced gates in `sde_gates/`
  - Gap: no service-wide boundary enforcement because service layer is not implemented

### Stage 1 progress note (latest implemented slices)

- Added fail-closed intake anchor semantics (`discovery/doc_review` must be schema-valid to anchor context merge/status).
- Added explicit `doc_review.json` schema rejection in preflight validation.
- Added bounded revise-loop mechanics with deterministic `blocked_human` transition.
- Added plan-lock gate and lock artifact (`project_plan_lock.json`) with structured reasons.
- Added optional plan-lock enforcement in both execution (`project run`) and preflight (`project validate`).
- Added plan-lock state visibility in `project status` and `status_at_a_glance`.
- Added intake lineage manifest (`sha256`) and CI wall-clock budget assertion for the Stage 1 pytest subset.
    - Added session-local `doc_review`/revise metrics JSONL + `project status` summary fields for blocked count / latency trend.
    - `session_events.jsonl` payloads (driver start / tick / terminal) include `intake_lineage_manifest_*` when `intake/lineage_manifest.json` exists (`lineage_manifest_session_event_snapshot`); `project status` embeds the same fields under `session_events` plus glance booleans.
    - `export-stage1-observability` writes `intake/stage1_observability_export.json` (`revise_metrics` + `status_at_a_glance`; schema-validated in tests).
    - `scripts/stage1-cold-start-demo.sh` documents the CLI golden path (mirrors `test_stage1_golden_flow.py`; exercised by `test_stage1_cold_start_demo.py`).
    - S1a backlog **B1/B2** closed by ADR: [0001](../adrs/0001-s1a-reviewer-attestation-policy.md) (attestation policy), [0002](../adrs/0002-s1a-model-assisted-revise-deferred.md) (model revise deferred).

## 2) Version ladder completeness (V1-V7)

- V1 (execution trust): `implemented` for local run classes
- V2 (planning hard-stops): `partial` (real in local harness/session; not full production intake system)
- V3 (review/verify/DoD): `partial` to `implemented` at local/session layer
- V4 (durable lineage): `partial` (run-local lineage artifacts)
- V5 (durable memory): `partial` (run-local memory contracts only)
- V6 (operational learning loop): `partial`
- V7 (live multi-agent + IAM/federation): `partial` at best, no full IAM/federated runtime

## 3) Contracts (versioned/linted/owned)

- `src/contracts/` published schema tree: `missing`
- Objective arbitration/policy bundle activation through single owner path: `missing`
- Role/stage/risk matrix + approval tokens via identity-authz plane: `missing`
- Contract lint tool (`tools/contract-lint`): `missing`
- Schema upcaster tool (`tools/schema-upcaster`): `missing`

## 4) Deployable services (master-aligned)

All listed services are currently `missing` as independently deployable code packages with their own `api/`, `runtime/`, `tests/`, and conformance:

- objective-policy-engine
- lifecycle-governance
- identity-authz
- policy-management
- event-store (durable service)
- projection-query
- memory-lifecycle
- capability-graph
- reflection-rca
- learning-update
- canary-rollout
- evaluation
- safety-controller
- model-router
- quota-scheduler
- observability-gateway
- incident-ops
- chaos-simulator

## 5) Orchestrator and coordination (platform level)

- Inter-service RPC contract (`common_rpc.v1.json`): `missing`
- Hierarchy/deadlock contracts as service-level coordination runtime: `partial`
  - Local scheduler/dependency logic exists, but not as formal inter-service contract/runtime
- Platform scheduler with global precedence across services/agents: `partial`
  - Strong session scheduler exists; no multi-service platform scheduler

## 6) Deterministic worker and sandbox

- Deterministic worker build/image pipeline: `missing`
- Isolated sandbox executor with injected policies: `missing`
- Worker policy enforcement (resource/network/filesystem/egress): `missing`
- Remote/optional runtimes productized: `missing`

## 7) Agent packages and progression

- Distinct agent packages (junior/mid/senior/architect/reviewer/evaluator/etc): `missing`
- Credential-isolated reviewer/evaluator runtime: `missing`
- Career/progression/recertification/stagnation wiring to capability/lifecycle services: `missing`

## 8) Libraries (SDKs)

- event-sdk: `missing`
- contract-validator SDK: `missing`
- lineage-sdk: `missing`
- policy-eval-sdk: `missing`
- memory-sdk: `missing`

## 9) Data plane

- seed-curriculum managed product: `missing`
- benchmark-suites productized versioning: `partial`
  - benchmark runner exists, but not full productized suite management plane
- replay-manifests catalog tied to durable event store: `missing`

## 10) Infra and local-prod

- Full `local-prod` profile with storage/secrets/backups/monitoring as code: `missing`
- Backup-restore drills with evidence: `missing`
- Master-doc storage choices pinned and operated: `missing`

## 11) Product surfaces

- UI/dashboard for runs, lanes, quarantine, promotions, incidents: `missing`
- Operator runbooks synchronized with shipped failure modes: `partial`
  - docs exist in places, but no clear operational runbook suite bound to real services

## 12) Testing pillars

- Integration tests per service boundaries: `missing` (no service layer to test)
- E2E full-stack reference programs: `missing`
- Replay tests on golden manifests against durable store: `missing` (durable store absent)
- Chaos tests (scheduler/store/worker fault injection): `missing`
- Security tests (authz bypass/token replay/lease escape): `partial`
  - some hard-stop/unit coverage exists, but not full security test pillar
- Promotion/lifecycle transition tests: `missing`

## 13) Governance artifacts

- ADR program for major contract/service decisions: `partial`
  - architectural docs exist, but not a complete ADR set tied to shipped services
- Threat models per trust boundary: `missing` as operational practice
- Incident forensics tool operational on real telemetry: `missing`

## 14) Readiness and metrics

- Readiness/KPI dashboards implemented from observability gateway: `missing`
- Scheduled capability growth/error reduction/transfer/stability metrics with retention: `missing`

## 15) Extraction and multi-tenant posture

- Microservice extraction contract drills for each service: `missing`
- Multi-tenant/org boundaries (IAM/quotas/isolation): `missing`

## Bottom line

- Current codebase is a strong local SDE orchestrator spine with meaningful gates and session controls.
- Company OS full scope (Tier 2.1 + Tier 2.2) is not yet implemented.
- Most non-local platform components remain missing in code and exist today primarily as checklist/version-plan backlog items.
- **To reach a declared “100%” without building the whole OS:** follow **[`company-os-path-to-100-percent.md`](company-os-path-to-100-percent.md)** (milestone **M2 / S1a**, backlog **B1–B5**) and update this gap analysis when Stage 1 acceptance shifts from `partial` to `implemented` for each chosen row.
