# Persona Agent Platform Release Gate Specification (Single Production Exit)

## Purpose
Define non-ambiguous release gate terms and numeric thresholds used by all implementation docs. This program has **one** production promotion after all criteria are met (no MVP release train).

**Normative tie-breaks:** `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` (includes `agentevals` floors, parity definition, gate packet layout).

## Authoritative Terms
- `production_workflow_manifest`: the version-controlled list in **`docs/implementation/production-workflow-manifest.md`** of every workflow in scope for production, derived from `docs/personas` and `docs/more_personas` per `docs/implementation/2026-04-13-persona-agent-platform-implementation-roadmap.md`. **100%** of this manifest must pass gates for production exit.
- `critical_workflows`: **same set** as the production workflow manifest for SLO and parity purposes (no separate “small critical subset”).
- `critical_slos`: Safety, Availability, Workflow Reliability, and Observability.
- `soak_window`: 24 continuous hours and at least 500 canary runs across manifest workflows (scale minimums up if manifest size requires; EM + SRE may raise floor, never lower without written exception).
- `incident_free`: zero Sev1/Sev2 incidents and no unresolved Sev3 incidents in the soak window.

## Evidence and Sampling Rules
- No gate can pass without evidence mapped to **every** workflow in the production workflow manifest.
- SLO/gate claims require documented sample size and window.
- Telemetry completeness must be >=99% for sampled runs or evidence is invalid.
- Promotion packets must attach **promptfoo** results for the pinned suite revision, **DeepEval** / **RAGAS** outputs (or signed **RAGAS N/A** per playbook), and **either** (a) **agentevals** scores on OTel traces for the sampled runs **or** (b) a **Tech Lead-signed** full re-run evaluation proving the **same** pass/fail bar—per `docs/implementation/2026-04-13-persona-agent-platform-delivery-process.md` and `docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md`.

## No-Repeat-Failure Contract (Production Exit)
- **Schema:** JSON payloads MUST validate against `docs/implementation/schemas/normalized-failure-signature.schema.json` (`schema_version` **1.0.0** until superseded by signed manifest note).
- **Hashing, deduplication, alias policy, and `critical` definition:** `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` §6–§5 (normative).
- **Ownership:** **Data/Memory DRI** and **Safety Owner** approve any change to `schema_version`, regex table for normalization, or `criticality` enum; updates are versioned with the production workflow manifest row set.
- **Automated proof (production exit):** for every **`critical`** signature (see doc-precedence §5) that has ever been recorded for a `workflow_id`, a subsequent run that would reproduce the same `signature_hash` MUST either (a) inject failure-memory context into planner and reviewer prompts before first tool call, (b) route to **reviewer escalation** state before tool execution, or (c) execute a **registered prevention check** that blocks progression—verified by CI replay tests named in the gate packet `MANIFEST.json`.
- **Non-goals:** this contract does **not** claim all mistakes are impossible; it claims **controlled handling** for **critical** signatures per doc-precedence §5.

## Rollback Trigger Matrix
- Trigger immediate rollback when:
  - any confirmed unsafe-action miss occurs, or
  - successful run completion rate is <99% for two consecutive 15-minute windows.
- On rollback trigger:
  - freeze promotion,
  - demote to prior stable runtime/policy bundle,
  - run post-rollback smoke plus safety replay suite before re-promotion.

## Waiver Policy Limits
- Safety gate is non-waivable for production promotion.
- Any non-safety waiver requires owner, expiry, mitigation, and one renewal maximum.
- Waiver reuse beyond one renewal requires EM stop-ship review.
