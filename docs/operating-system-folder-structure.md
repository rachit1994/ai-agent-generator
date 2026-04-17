# AI Professional Evolution OS - Master-Aligned Folder Structure

This is the operating-system style repository layout aligned to
`AI-Professional-Evolution-Master-Architecture.md` (Sections 20-23).
It preserves atomic components with minimal interdependence while matching the
master architecture service boundaries and contracts exactly.

## Alignment Principles

- `local-prod` is the only production runtime profile.
- All cross-component communication is contract-first and versioned.
- Every service is independently deployable and extraction-ready.
- Promotion, autonomy, memory mutation, and policy activation are single-owner
  concerns (no bypass paths).
- Event lineage is mandatory: `event -> reflection -> learning update -> evaluation -> rollout`.

## Master-Aligned Target Layout

```text
repo/
|- docs/
|  |- AI-Professional-Evolution-Master-Architecture.md
|  |- operating-system-folder-structure.md
|  |- swarm-token-and-system-requirements-math.md
|  |- runbooks/
|  |- adrs/
|  \- threat-models/
|
|- src/
|  |- contracts/
|  |- event/
|  |  |- event_envelope.v1.json
|  |  |- event_integrity.v1.json
|  |  \- replay_manifest.v1.json
|  |- policy/
|  |  |- objective_arbitration.v1.json
|  |  \- policy_bundle.v2.json
|  |- lifecycle/
|  |  |- lifecycle_stage.v1.json
|  |  \- promotion_decision.v1.json
|  |- capability/
|  |  |- capability_node.v1.json
|  |  \- certification_state.v1.json
|  |- authz/
|  |  |- role_stage_risk_matrix.v1.json
|  |  \- approval_token.v1.json
|  |- service/
|  |  \- common_rpc.v1.json
|  |- orchestrator/
|  |  |- hierarchy.v1.json
|  |  \- deadlock.v1.json
|  \- runtime/
|     \- deterministic_worker.v1.json
|
|  |- services/
|  |- orchestrator/
|  |  |- api/
|  |  |- runtime/
|  |  |- tests/
|  |  \- README.md
|  |- objective-policy-engine/
|  |- lifecycle-governance/
|  |- identity-authz/
|  |- policy-management/
|  |- event-store/
|  |- projection-query/
|  |- memory-lifecycle/
|  |- capability-graph/
|  |- reflection-rca/
|  |- learning-update/
|  |- canary-rollout/
|  |- evaluation/
|  |- safety-controller/
|  |- model-router/
|  |- quota-scheduler/
|  |- observability-gateway/
|  |- incident-ops/
|  \- chaos-simulator/
|
|  |- agents/
|  |- junior-agent/
|  |- midlevel-agent/
|  |- senior-agent/
|  |- architect-agent/
|  |- reviewer-agent/
|  |- evaluator-agent/
|  |- learning-agent/
|  |- practice-agent/
|  |- manager-agent/
|  |- specialist-agent/
|  \- career-strategy-agent/
|
|  |- runtime/
|  |- deterministic-worker/
|  |  |- image/
|  |  |- sandbox/
|  |  |- policies/
|  |  \- tests/
|  \- profile/
|     \- local-prod/
|
|  |- libraries/
|  |- event-sdk/
|  |- contract-validator/
|  |- lineage-sdk/
|  |- policy-eval-sdk/
|  \- memory-sdk/
|
|  |- data/
|  |- seed-curriculum/
|  |- benchmark-suites/
|  \- replay-manifests/
|
|  |- infra/
|  |- local-prod/
|  |- backup-restore/
|  \- monitoring/
|
|  |- tests/
|  |- unit/
|  |- integration/
|  |- e2e/
|  |- replay/
|  |- chaos/
|  |- security/
|  \- promotion/
|
|  \- tools/
|     |- contract-lint/
|     |- schema-upcaster/
|     \- incident-forensics/
|
\- outputs/
   \- runs/<run-id>/
```

## This repository (SDE orchestrator snapshot)

The tree above is the **target** OS layout. In *this* repo today, the pieces that exist map as follows (so paths stay stable without inventing parallel trees):

| Target (master doc) | Current path in this repo |
|---------------------|---------------------------|
| `src/services/orchestrator/` service shell | `src/services/orchestrator/` — contains **`orchestrator/api/`** (public surface), **`orchestrator/runtime/`** (implementation), **`tests/`**, `README.md` per service atomicity rules. |
| Orchestrator `api/` + `runtime/` | **`src/services/orchestrator/orchestrator/api/`** and **`…/orchestrator/runtime/`** — import package **`orchestrator`**; published wheel name **`sde`** with `sde` / `agent` CLI scripts (`pyproject.toml`). |
| `outputs/runs/<run-id>/` | **Repository root** `outputs/runs/<run-id>/` only (gitignored). The CLI resolves this via `orchestrator.runtime.utils.outputs_base()`; do not add a second `outputs/` tree under `src/`. |
| `src/data/` … benchmark suites | `data/` at repo root (e.g. `data/benchmark-tasks.jsonl`). |
| Coding-agent extension specs | `docs/coding-agent/*.md` only — no `docs/vN/` directories. |
| SDE baseline (CLI contract) | `docs/sde/` |

As more master-aligned services land, add them under `src/services/<name>/` using the same `api/`, `runtime/`, `tests/` pattern.

## Service Atomicity Rules

- Every service contains `api/`, `runtime/`, `tests/`, and `README.md`.
- `api/` is the only import surface for other services.
- Behavior-changing deploys require policy bundle version bumps.
- Service must pass contract conformance tests before deployment.
- Service `README.md` must include extraction/deployment steps.

## Non-Bypass Ownership Rules

- Only `memory-lifecycle` may mutate memory.
- Only `lifecycle-governance` may change promotion/autonomy state.
- Only `policy-management` may activate policy bundles.
- Only `safety-controller` can issue final veto on high-risk actions.
- Only `identity-authz` issues and validates scoped approval tokens.

## Microservice Extraction Contract

To extract any service (example: `services/learning-update/`) into a standalone
deployment unit:

1. Copy the service folder unchanged.
2. Copy required contracts from `src/contracts/` (declared in service `README.md`).
3. Copy referenced SDKs from `src/libraries/` only.
4. Wire through `src/contracts/service/common_rpc.v1.json`.
5. Register with `src/services/orchestrator` and `src/services/identity-authz`.
6. Validate with `src/tools/contract-lint/` in fail-closed mode.

If these rules are satisfied, extraction is direct and does not require internal
code from unrelated services.
