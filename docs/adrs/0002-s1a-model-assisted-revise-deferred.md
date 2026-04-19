# ADR 0002 — S1a revise loop: deterministic regeneration only; model-assisted path deferred

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-19 |
| **Context** | [company-os-path-to-100-percent.md](../architecture/company-os-path-to-100-percent.md) §4 **B2**; OSV-STORY-01 revise loop |

## Context

[`project_intake_revise.py`](../../src/orchestrator/api/project_intake_revise.py) implements a **bounded** revise loop: failed **`doc_review`** increments attempts, applies **deterministic local regeneration** of intake artifacts, and transitions to **`blocked_human`** at the retry cap. That is machine-runnable, hermetic in CI, and aligned with fail-closed gates.

Checklist “north star” wording can be read as requiring a **separate model-backed reviewer/regenerator** for every transition. That capability is not implemented in this repository for OSV-STORY-01.

## Decision

1. For **OSV-STORY-01 / S1a**, the **only** supported revise/regeneration behavior remains **deterministic local regeneration** (no calls to implementation/support models in the revise path).
2. **Model-assisted** doc review application, LLM rewrite of findings, or autonomous replanning is **explicitly out of scope** for this version and is deferred to a **future OSV story** (or Tier 2.1+ product milestone) with its own fixtures, provider boundaries, and CI policy.
3. The version plan **§3 Scope** is updated to name this deferral so S1a sign-off does not silently claim autonomous model intake.

## Consequences

- B2 in §4 is **closed for S1a** on the **ADR + scope text** interpretation, not on “model path merged in this repo.”
- Demos and cold-start scripts that use **`scaffold-intake`** / **`intake-revise`** remain valid evidence for S1a without network keys.
- When the program adopts **S1b**-style literal checklist wording, add a new version plan and implementation work; do not reinterpret this ADR as shipping model revise under OSV-STORY-01.

## References

- [`project_intake_revise.py`](../../src/orchestrator/api/project_intake_revise.py)
- [`docs/versioning/plans/story-01-stage1-intake.md`](../versioning/plans/story-01-stage1-intake.md) — §3 out-of-scope
