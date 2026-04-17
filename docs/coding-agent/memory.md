# Coding-Agent V5 Specification — Memory System

## In plain words

- **V5 is “remember across tasks, safely.”** Not a free-form scratchpad — **rules** for what may be stored, **where it came from**, and how to **quarantine** bad or conflicting facts.
- Memory writes tie back to **events (V4)** when both are enabled so changes stay **traceable**.

## Goal

Implement the **policy-governed memory subsystem** described in [docs/architecture/AI-Professional-Evolution-Master-Architecture.md](../architecture/AI-Professional-Evolution-Master-Architecture.md) **§8 Memory Architecture** and **§3 / §9** feedback loops: **episodic**, **semantic**, and **skill** memory with explicit **write/retrieve policy**, **provenance**, **confidence**, and **quality metrics**—without unconstrained self-modification (master **§2 Non-Goals**).

**Architecture traceability:** **§8** (types, retrieval, write, lifecycle, quality), **§18** mitigations (memory corruption), **§17 Phase 1** (memory subsystem for single-agent evolution).

## Relationship to Prior Versions

- **V4** event store carries **memory write proposals** and **accepted memory facts** as typed events with lineage.
- **V5** defines memory **stores**, **policies**, and **hard-stops** for read/write paths.

`balanced_gates.hard_stops` for memory-enabled runs **must** include **HS01–HS24** (V5 adds **HS21–HS24**).

## Priority Order

**Provenance and write policy** outrank recall breadth. A high-recall answer without provenance is worse than a bounded abstention under policy.

## External research alignment (selective promotion and self-supervision)

- **S3FT — selective self-to-supervised fine-tuning** ([NAACL 2025 Findings](https://aclanthology.org/2025.findings-naacl.349/)): when promoting facts from **model-generated** content into long-lived memory, prefer **dual evidence** (e.g. human + passing tests, or two independent verifiers) over naive “always accept model text.”
- **Mind the Gap** ([OpenReview ICLR 2025](https://openreview.net/pdf?id=mtJSMcF3ek)): memory writes used for downstream **training** should be **gap-aware**—if verification is weak, keep rows in **quarantine** (HS22 path below) instead of the active graph.

See [docs/research/self-improvement-research-alignment.md](../research/self-improvement-research-alignment.md) §2.6–§3.

## End-User Features (Minimum 3)

### Feature 1 — Typed memory with provenance links

- **Outcome:** Every retrieved memory chunk cites event or document `provenance_id`; users trust “where this came from.”
- **Artifacts:** `memory/retrieval_bundle.json` per query with `chunks[]` and `provenance_id` each.
- **Evidence:** Governance; **HS21** if served chunk lacks provenance when policy requires it.

### Feature 2 — Quarantine and contradiction handling

- **Outcome:** Conflicting writes do not silently merge; contradictions surface to review or Evaluator path.
- **Artifacts:** `memory/quarantine.jsonl`, `memory/contradiction_reports/<id>.json`.
- **Evidence:** **HS22** if two active facts contradict policy resolution without a recorded resolution event.

### Feature 3 — Skill memory tied to capability nodes

- **Outcome:** “What this agent is certified to do” is backed by skill records and decay/recert rules (master §6 / §8 lifecycle).
- **Artifacts:** `capability/skill_nodes.json` (logical); updates via V4 events only.
- **Evidence:** Delivery + Governance; **HS23** if autonomy expansion without matching skill evidence.

### Feature 4 (bonus) — Memory quality metrics

- **Outcome:** Operators see staleness, contradiction rate, and retrieval precision proxies (per §8 Memory Quality Metrics).
- **Artifacts:** `memory/quality_metrics.json` rolling window.
- **Evidence:** Reliability; **HS24** if metrics missing while memory path enabled in production profile.

## Hard-Stop Gates (V5 Additive)

| ID | Condition | Detection |
|----|-----------|-----------|
| HS21 | **Retrieval without provenance** when policy mandates | `memory/retrieval_bundle.json` missing `provenance_id` on any chunk |
| HS22 | **Unresolved contradiction** | Two active facts in scope without `contradiction_resolved` event |
| HS23 | **Autonomy or permission expansion** without **skill / capability evidence** | Permission matrix update event without prerequisite capability events |
| HS24 | **Memory quality metrics absent** in `local-prod` profile with memory enabled | Config flag `memory_enabled_production: true` but no `memory/quality_metrics.json` emit |

## How memory supports full-stack delivery (concrete flow)

Memory enables the system to get better **across** runs. See [action-plan.md](../onboarding/action-plan.md) §2 Stage 8.

```
Run N builds a Next.js + Express app. During implementation:
  - Auth middleware step fails review twice (JWT expiry edge case)
  - Reviewer finding: "missing token refresh handling"
  - Learning event captured in learning_events.jsonl

After Run N completes:
  - Reflection (V6) extracts root cause → episodic memory write:
      "Next.js + Express auth: always handle JWT refresh in middleware"
      provenance: run_N, step_review_id_7, learning_event_id_12

Run N+1 builds a different app (React + Express):
  - Planner receives memory retrieval for "auth middleware" context
  - retrieval_bundle.json includes the episodic memory with provenance
  - Planner's question_workbook includes "JWT refresh handling?"
  - Implementor receives the lesson as context for auth steps
  → Fewer review failures on auth-related code

If conflicting memory exists:
  - Old memory: "always use session-based auth"
  - New memory: "stateless JWT preferred for API-first"
  → Contradiction detected → quarantine.jsonl
  → Resolution event required before either is served (HS22)
```

**Institutional memory, not scratchpad:** Every memory write has provenance (which run, which event, which review). Memories without provenance are rejected (HS21). This prevents the system from "remembering" hallucinated facts.

## Memory Types (Contract Summary)

| Type | Purpose | Write path |
|------|---------|------------|
| Episodic | Task/run segments, outcomes | LearningAgent proposal → Evaluator → append event |
| Semantic | Stable facts, glossaries | Same + contradiction checks |
| Skill | Capability certifications | Promotion pipeline events only (no self-write) |

## Validation Matrix

| Gate theme | Primary evidence | Supporting |
|------------|------------------|------------|
| Governance | HS21–HS24, quarantine files | `review.json` / platform review artifact |
| Reliability | quality metrics, decay jobs | `orchestration.jsonl` |
| Replay | memory writes as events | V4 `replay_manifest.json` |

## Acceptance Criteria

1. Write/retrieve policies are machine-checkable (config + tests).
2. At least one injected contradiction triggers **HS22** or explicit resolution flow in harness.
3. Master §8 each subsection has a **checkbox row** in internal release checklist pointing to this spec section.

## Definition of Done for This V5 Doc

- Aligns with master §8, §18 memory risks, §17 Phase 1.
- HS21–HS24 do not weaken V1–V4 stops.
- Linked from [docs/README.md](../README.md) and [README.md](../../README.md).
