# ADR 0001 — S1a reviewer attestation: local stub vs strict production policy

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-04-19 |
| **Context** | [company-os-path-to-100-percent.md](../architecture/company-os-path-to-100-percent.md) §4 **B1**; OSV-STORY-01 Stage 1 lock-readiness |

## Context

Stage 1 intake uses on-disk **`reviewer_identity.json`** plus **`doc_review.json`** so the orchestrator can fail closed on schema, reviewer/planner separation, and attestation shape. For local development and CI, **`attestation_type: local_stub`** is valid when **`allow_local_stub_attestation`** is true (default Python API and non-strict CLI).

Production-style policy requires a **non-local** attestation path; the repository does not yet ship a pluggable verifier that calls an external identity or signing service.

## Decision

1. **S1a (M2 in-repo)** explicitly allows **`local_stub`** when strict flags are **off**, matching today’s **`evaluate_project_plan_lock_readiness`** / **`write_project_plan_lock`** defaults (`allow_local_stub_attestation=True`).
2. **Strict reviewer policy** for CLI and selected flows is **in scope** and already implemented: **`--require-non-stub-reviewer`**, together with **`--require-plan-lock`** / **`--enforce-plan-lock`**, and **`SDE_REQUIRE_NON_STUB_REVIEWER`** (see [`docs/sde/project-driver.md`](../sde/project-driver.md) Stage 1 section).
3. A **pluggable external attestation verifier** (interface + service adapter + tests against a fake verifier) is **deferred** to a **future version plan** when a concrete production identity provider is chosen.

## Consequences

- Operators who need production-grade attestation **must** enable the strict path (CLI flags and/or env) where the driver or validate runs; defaults stay permissive so golden tests and local scaffolding do not require network or secrets.
- Checklist language that implies “always non-stub in every environment” is **not** claimed for S1a; it is **S1b / program** work unless narrowed by a separate checklist ADR.
- B1 in §4 is **closed for S1a** on the **ADR + existing strict gates** interpretation, not on “adapter shipped in this repo.”

## References

- [`project_plan_lock.py`](../../src/orchestrator/api/project_plan_lock.py) — readiness and attestation checks
- [`docs/runbooks/stage1-intake-failures.md`](../runbooks/stage1-intake-failures.md)
