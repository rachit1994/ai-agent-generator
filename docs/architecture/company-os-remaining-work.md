# Company OS remaining work (actual, repo-grounded)

**Path to “100%” (pick a milestone):** read **[`company-os-path-to-100-percent.md`](company-os-path-to-100-percent.md)** first — it separates **whole-checklist (M0)**, **Tier 2.1 story (M1)**, **OSV-STORY-01 in-repo (M2 / S1a)**, and **literal Stage 1 north star (S1b)** so implementation work maps to an honest completion claim.

This document lists what is still left to reach the full Company OS scope from `company-os-full-delivery-checklist.md`, based on current code and docs in this repository.

It intentionally focuses on **remaining work only**:

- `missing`: no real implementation surface exists
- `partial`: some implementation exists, but checklist acceptance is still not met

## A) Remaining Tier 2.1 (product story) work

## Fully missing in Tier 2.1

- Stage 3 separation of duties with independent planner/reviewer identities and no self-approval boundary
- True contract-step gating across shared API/DB/schema contracts with cross-lane blocking based on review evidence
- Stage 6 operational learning loop with durable causal closure/practice/canary/promotion and independent evaluator signals
- Stage 7 durable platform event store (append-only, replay-integrity, fail-closed behavior at platform scope)
- Stage 8 durable memory platform (episodic/semantic/skill stores with policy-governed retrieval/write lifecycle)

## Partial in Tier 2.1 (still left)

- Stage 1 machine-runnable intake
  - independent reviewer identity boundary with real credentials/service-backed attestation still missing at **platform** scope (S1a policy: [ADR 0001](../adrs/0001-s1a-reviewer-attestation-policy.md); local artifacts + strict CLI/env for production-style runs; API defaults stay permissive for local/tests)
  - fully autonomous model-driven revise/regeneration loop still missing ([ADR 0002](../adrs/0002-s1a-model-assisted-revise-deferred.md); current revise loop is deterministic local artifact regeneration only)
  - durable platform-grade lineage/event store for Stage 1 artifacts still missing (session-local manifest + CI wall-clock SLO exist)
  - production-grade observability service for doc-review/revise SLOs still missing (current metrics are session-local JSONL + status summary, with reviewer policy/source glance fields only)
- LearningFirstProfile enforcement is local/harness-level, not policy-backed durable service behavior
- Stage 2 parallel lanes are local scheduler/worktree-level; durable lane queues/federated coordination still missing
- Lease/heartbeat enforcement is session-local; global non-bypass ownership across all mutation paths still missing
- Stage 4 verification and Stage 5 DoD are local/session-level; platform-wide enforcement semantics still missing
- Continuous CTO gates are strong locally but not enforced across absent service boundaries

## B) Remaining version-ladder work (V1-V7)

- V2-V7 still not complete at platform level (current coverage is local/session harness-heavy)
- Durable evidence requirements for V4/V5/V6/V7 remain open:
  - V4 durable lineage platform
  - V5 durable memory services
  - V6 operational reflection/practice/canary/promotion
  - V7 live multi-agent IAM/federation coordination safety

## C) Remaining Tier 2.2 (master OS) work

## Fully missing platform foundations

- `src/contracts/` published contract tree
- Contract lifecycle tooling:
  - `tools/contract-lint`
  - `tools/schema-upcaster`
- Service-level contract ownership paths for policy activation and high-risk approval tokens

## Fully missing deployable services

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

## Fully missing orchestrator-platform items

- Inter-service RPC contract (`common_rpc.v1.json`) used in real inter-service calls
- Hierarchy/deadlock contracts operational under true multi-lane service load
- Platform scheduler routing across services/agents with global precedence rules

## Fully missing execution plane

- Deterministic worker image/build pipeline
- Isolated sandbox runtime with policy-injected limits
- Worker resource/network/filesystem/egress policy enforcement
- Remote/optional runtimes as productized execution paths

## Fully missing agent package layer

- Distinct certifiable role packages (junior/mid/senior/architect/reviewer/evaluator/learning/practice/manager/specialist/career-strategy)
- Career/progression/recertification/stagnation wiring with measurable lifecycle signals

## Fully missing SDK/library layer

- event-sdk
- contract-validator
- lineage-sdk
- policy-eval-sdk
- memory-sdk

## D) Remaining cross-cutting product/infra/test/governance work

## Data plane

- seed-curriculum productized content/versioning
- benchmark-suites productized suite management/versioning
- replay-manifests catalog tied to durable event store

## Infra and local-prod

- Complete `local-prod` profile as checked-in config (storage/secrets/backups/monitoring/SLOs/alerts)
- backup/restore drills with evidence
- storage choices pinned/operated from architecture requirements

## Product surfaces

- UI/dashboard for runs, lanes, quarantine, promotions, incidents
- Runbooks synchronized to shipped failure modes across real services (currently only partial/local scope)

## Testing pillars

- Integration tests for real service boundaries
- E2E full-stack reference programs (UI/API/DB/tests/deploy smoke)
- Replay tests against durable store + golden manifests
- Chaos tests for scheduler/store/worker fault injection
- Security tests for authz bypass/token replay/lease escape at platform scope
- Promotion lifecycle state-transition tests

## Governance/readiness/extraction

- ADR program tied to major contract/service decisions (comprehensive set still missing)
- Threat models per shipped trust boundary
- Incident forensics tool operational on real telemetry (`tools/incident-forensics`)
- Readiness/KPI dashboards fed by observability gateway
- Scheduled capability/error/transfer/stability metrics with retention
- Microservice extraction contract drills for every service
- Multi-tenant/org IAM/quota/isolation boundaries

## Current practical interpretation

- The local SDE spine is materially stronger and now includes Stage 1 lock/preflight/revise controls.
- Full Company OS completion remains blocked primarily by absent multi-service platform components and durable infra/data planes.
- To **close a “100%” milestone in this repo**, execute the **M2 / S1a** backlog in [`company-os-path-to-100-percent.md`](company-os-path-to-100-percent.md) §4 (**B1–B5**) and update this file + the [gap analysis](company-os-gap-analysis-src-vs-checklist.md) when each row is done.
