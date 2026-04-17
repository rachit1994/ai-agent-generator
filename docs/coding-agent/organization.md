# Coding-Agent V7 Specification — Multi-Agent, Identity, and Organization Intelligence

## Goal

Complete the **multi-agent**, **identity/authorization**, **federated orchestration**, and **organization-level** objectives of [docs/AI-Professional-Evolution-Master-Architecture.md](../AI-Professional-Evolution-Master-Architecture.md): **§5 Agent Organization Model**, **§15** (identity, federated orchestration), **§16 Scalability Strategy**, and **§17 Phase 2–4** (multi-agent evolution through organization intelligence).

**Architecture traceability:** **§5**, **§15** (IAM, orchestration), **§16**, **§17 Phases 2–4**, **§19** items (identity plane, federated orchestration, career strategy layer).

## Relationship to Prior Versions

- **V6** defines **single-aggregate** lifecycle and learning; **V7** scales to **many agents** with **leases**, **heartbeats**, and **role contracts**.
- **V4** events must record **actor identity** and **authorization scope** for every tool action (master §15).

`balanced_gates.hard_stops` for multi-agent production runs **must** include **HS01–HS32** (V7 adds **HS29–HS32**).

## Priority Order

**Coordination safety and identity correctness** outrank raw multi-agent throughput (master §17 Phase 2 exit: throughput without quality/safety regression).

## External research alignment (evaluator isolation at scale)

Multi-agent self-improvement amplifies **credit assignment** and **evaluator gaming** risks. Keep **LearningAgent**, **EvaluatorAgent**, and **implementor** roles on **separate IAM principals** (Constitutional AI / RLAIF separation of critique vs action—[arXiv:2212.08073](https://arxiv.org/abs/2212.08073)); record all **cross-shard** learning or training jobs with the same **event + replay** requirements as [events.md](events.md). See [docs/research/self-improvement-research-alignment.md](../research/self-improvement-research-alignment.md) §3 (organization row).

## End-User Features (Minimum 3)

### Feature 1 — Single-writer leases with heartbeat

- **Outcome:** No two agents mutate the same aggregate; split-brain prevented by lease expiry and recovery events.
- **Artifacts:** `coordination/lease_table.json` (logical); events `lease_acquired`, `lease_released`, `heartbeat`.
- **Evidence:** Reliability; **HS29** if mutation under expired or foreign lease.

### Feature 2 — Permission matrix enforcement per action

- **Outcome:** Every tool call carries authenticated actor, stage, risk tier; denials are explicit and logged (executable matrix per master §19.A).
- **Artifacts:** `iam/permission_matrix.json` versioned; `iam/action_audit.jsonl`.
- **Evidence:** Governance; **HS30** if high-risk action without expiring approval token when matrix requires.

### Feature 3 — Federated orchestration partitions

- **Outcome:** Workload domains shard to avoid control-plane bottlenecks (master §16); cross-shard calls use contracts only.
- **Artifacts:** `orchestration/shard_map.json`, cross-shard `handoff_envelope.json`.
- **Evidence:** Reliability + Delivery; **HS31** if undocumented cross-shard side effect.

### Feature 4 (bonus) — Career strategy proposals without self-approval

- **Outcome:** `CareerStrategyAgent` proposes trajectories; promotions still flow through V6 packages (master §5).
- **Artifacts:** `strategy/proposal.json` with `requires_promotion_package: true`.
- **Evidence:** **HS32** if strategy proposal applies autonomy or policy change directly.

## Hard-Stop Gates (V7 Additive)

| ID | Condition | Detection |
|----|-----------|-----------|
| HS29 | **Mutation without valid lease** | Write event lacks `lease_id` matching active `lease_table` entry |
| HS30 | **High-risk action** without **approval token** | `iam/action_audit` shows `risk: high` and missing `approval_token_id` |
| HS31 | **Cross-shard side effect** without **handoff envelope** | External state changed with no `handoff_envelope` event chain |
| HS32 | **Strategy self-approval** | Autonomy or policy field changed by same `actor_id` as strategy proposal without V6 promotion package |

## Validation Matrix

| Gate theme | Primary evidence | Supporting |
|------------|------------------|------------|
| Safety / IAM | HS29–HS32, `iam/action_audit.jsonl` | Safety veto events |
| Reliability | lease + heartbeat metrics | §14 resource / deadlock controls |
| Replay | all V7 decisions as V4 events | `replay_manifest.json` |

## Execution Profiles

1. **SplitBrainProfile** — Two writers attempt lease; one must fail closed with HS29.
2. **HighRiskDenyProfile** — Action without token; denied with HS30.
3. **OrgShardProfile** — Multi-shard handoff; HS31 on covert cross-shard write fixture.

## Acceptance Criteria

1. Role registry from master §5 is mirrored as machine-readable `roles/registry.json` (or equivalent) with conformance tests.
2. Phase 4 “organization intelligence” behaviors that are **in scope for this repo** are listed as **optional capabilities** with explicit out-of-repo dependencies (no fake completeness).
3. Master §17 Phase 2–4 exit language reflected in **go/no-go checklist** rows tied to HS29–HS32.

## Definition of Done for This V7 Doc

- Maps organization-scale goals to **testable** gates; defers undeclared services explicitly.
- HS29–HS32 consistent with V4 identity requirements.
- Linked from [docs/README.md](../README.md) and [README.md](../../README.md).
