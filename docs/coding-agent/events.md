# Coding-Agent V4 Specification — Event Store, Replay, and Lineage

## Goal

Satisfy the **event-sourced execution and audit spine** of [docs/AI-Professional-Evolution-Master-Architecture.md](../AI-Professional-Evolution-Master-Architecture.md) **§12 Event-Sourced Architecture**, **§15 Production Architecture** (storage/orchestration foundations), and **§17 Phase 0 — Core Runtime** exit themes: append-only events, **replay fail-closed**, **replay manifests**, and **kill switch** visibility—while inheriting V1–V3 contracts wherever coding-agent runs still apply.

**Architecture traceability:** Master sections **§12**, **§14** (stability / replay drift), **§15** (local runtime, storage), **§17 Phase 0**, **§19.D P0** (Event Store Contract v1, release gates).

## Relationship to Prior Versions

- **V1–V3** remain the contracts for **task delivery**, planning, and completion evidence (`outputs/runs/<run-id>/`, `.agent/sde/`).
- **V4** adds **platform-level** event contracts: every state-changing decision that affects autonomy, policy, or promotion **must** be reconstructible from the event log under a published manifest.

For runs that include both delivery and platform events, `summary.json` → `balanced_gates.hard_stops` **must** include **HS01–HS20** (V4 adds **HS17–HS20** below). Coding-only runs may omit HS17–HS20 only when explicitly marked `run_class: coding_only` in `summary.json`.

## Priority Order

**Safety and replay integrity** outrank throughput. No batching or indexing optimization may skip manifest verification or reorder events outside the contract.

## External research alignment (lineage for self-training)

Self-training methods (**STaR**, **ReST^EM**, **ReST-MCTS\***) assume every accepted training example is **attributable** and **replayable** ([arXiv:2203.14465](https://arxiv.org/abs/2203.14465), [arXiv:2312.06585](https://arxiv.org/abs/2312.06585), [arXiv:2406.03816](https://arxiv.org/abs/2406.03816)). This spec’s **event envelopes**, **replay manifests**, and **HS17–HS20** exist so that any future “train from own traces” pipeline can answer: *which event ids built this weight delta?* See [docs/research/self-improvement-research-alignment.md](../research/self-improvement-research-alignment.md) §2.2–§3.

## End-User Features (Minimum 3)

### Feature 1 — Replayable history of “why the system did X”

- **Outcome:** Operators and auditors can rebuild decisions from events; disputes use evidence, not chat logs.
- **Artifacts:** `event_store/` append log (logical path; physical store per §15); `replay_manifest.json` per bounded window.
- **Evidence:** Governance + Reliability; **HS18** if replay diverges.

### Feature 2 — Kill switch and safety veto lineage

- **Outcome:** Emergency stop and safety overrides are first-class events with actor and reason.
- **Artifacts:** `traces.jsonl` / platform event types `kill_switch_activated`, `safety_veto`; link to `event_id`.
- **Evidence:** §11 dual control themes; **HS19** if veto without lineage.

### Feature 3 — Contract-frozen event schema (Phase 0.5 alignment)

- **Outcome:** Phase scale-up follows **Phase 0.5 contract freeze** from master §17; incompatible writes are rejected.
- **Artifacts:** `schema_registry/` version pins; event `contract_version` on each envelope.
- **Evidence:** **HS17** on unsupported or unparsable contract version at write time.

### Feature 4 (bonus) — Idempotent command handling

- **Outcome:** Retries do not duplicate side effects; same idempotency keys converge.
- **Artifacts:** Event envelope fields `command_id`, `idempotency_key`, dedupe markers in projections.
- **Evidence:** **HS20** on duplicate side effect without dedupe proof.

## Hard-Stop Gates (V4 Additive)

| ID | Condition | Detection |
|----|-----------|-----------|
| HS17 | **Unsupported** `contract_version` or schema reject on write | Event append rejected or shadow-written without fail-closed (latter violates) |
| HS18 | **Replay drift**: manifest hash / projection mismatch vs source log | Automated replay job emits `drift_count > 0` for critical aggregates |
| HS19 | **Safety veto / kill switch** without **event + actor** | Trace shows action blocked but no matching platform event |
| HS20 | **Duplicate side effect** without idempotency resolution | Same `command_id` produces two committed external mutations |

## Required Artifacts (Platform)

| Artifact | Purpose |
|----------|---------|
| `replay_manifest.json` | Window bounds, event hash chain root, projection version, `passed` boolean |
| `event_envelope.schema.json` | Canonical fields: `event_id`, `aggregate_id`, `causation_id`, `contract_version`, `payload`, `occurred_at` |
| `kill_switch_state.json` | Current latch, `updated_at`, `last_event_id` |

## CTO / Release Alignment (Master §14)

V4 validation-ready posture for **platform slice** requires, in addition to V1 balanced gates where applicable:

- `ReplayCriticalDriftCount == 0` for manifests marked **critical** in config.
- `UnsafeActionRate` budgets still enforced at orchestration boundary (feeds Governance).

## Execution Profiles

1. **ReplayProfile** — Fixed window replay twice; bit-identical projection hashes.
2. **KillSwitchProfile** — Activate kill switch; verify no autonomous side effects without matching events.
3. **SchemaFreezeProfile** — Write with stale `contract_version`; must fail closed (HS17).

## Validation Matrix

| Gate theme | Primary evidence | Supporting |
|------------|------------------|------------|
| Replay/audit | `replay_manifest.json`, replay job logs | Event store segments |
| Safety lineage | `kill_switch_state.json`, veto events | `traces.jsonl` |
| Governance | HS17–HS20 in `balanced_gates.hard_stops` | Schema registry pins |

## Acceptance Criteria

1. HS17–HS20 defined tests or harnesses exist for platform integration slice.
2. At least one **ReplayProfile** run proves **HS18** detection on injected drift fixture.
3. Master §12 replay and §17 Phase 0 exit themes are explicitly checked off in release checklist doc (cross-link).

## Definition of Done for This V4 Doc

- Maps to master architecture §12, §14 (replay), §15 (foundation), §17 Phase 0, §19.D P0 event items.
- HS17–HS20 are testable; no contradiction with V1–V3 HS01–HS16.
- Linked from [docs/README.md](../README.md) and [README.md](../../README.md).
