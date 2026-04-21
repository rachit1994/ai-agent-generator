# AI Agent Feature Completion Playbook (Source of Truth)

This document is the execution source-of-truth for feature completion.  
If followed exactly, an AI agent should complete one feature end-to-end without human intervention except when blocked by missing credentials, missing infrastructure access, or explicit product decisions.

Primary architecture authority: `docs/AI-Professional-Evolution-Master-Architecture.md`  
Progress tracker authority: `docs/master-architecture-feature-completion.md`

---

## 1) Mission contract

For every feature, the agent must produce a complete outcome across:

- behavior implementation,
- contract/invariant enforcement,
- test proof (positive and negative paths),
- operational evidence artifacts,
- honest completion scoring update.

A feature is not done until all five are complete.

---

## 2) Autonomous execution policy

The agent must continue iterating until one of these terminal states:

- `DONE`: all feature gates pass.
- `BLOCKED-EXTERNAL`: blocked by external dependency (credentials, unavailable service, missing environment).
- `BLOCKED-DECISION`: blocked by unresolved product/policy choice requiring human decision.

Rules:

- Do not stop at analysis.
- Do not stop after partial code changes.
- Do not ask for confirmation between normal implementation steps.
- Resolve test failures and integration issues proactively.
- Keep scope to exactly one feature row per run.

---

## 3) One-feature execution packet (required input)

Before coding, agent must build a packet for exactly one feature:

- `FeatureName`
- `BlueprintSections`
- `CurrentCompletionPercent`
- `PrimaryCodePaths`
- `ContractsAndInvariants`
- `RequiredTests`
- `RequiredEvidenceArtifacts`
- `DoneGates` (binary)
- `KnownRisks`

No packet, no implementation.

---

## 4) Deterministic workflow (must follow in order)

### Phase 0 - Map requirements

1. Parse source-of-truth blueprint sections.
2. Extract explicit requirements and invariants.
3. Convert requirements into binary acceptance gates.

Output: `RequirementMap` and `DoneGates`.

### Phase 1 - Gap assessment

1. Inspect current code, contracts, tests, and artifacts.
2. Compute feature gaps in four buckets:
   - behavior gap
   - contract gap
   - test gap
   - evidence gap

Output: prioritized `GapList`.

### Phase 2 - Red (tests first)

1. Add failing tests for each acceptance gate.
2. Add failing negative tests for malformed/contradictory/unsafe input.
3. Run tests and confirm failures.

Output: reproducible red-state evidence.

### Phase 3 - Green (minimum implementation)

1. Implement minimal code to satisfy failing tests.
2. Enforce fail-closed behavior at all boundaries.
3. Avoid unrelated refactors.

Output: passing targeted tests.

### Phase 4 - Refactor and harden

1. Refactor for clarity while preserving behavior.
2. Remove truthy/implicit pass semantics.
3. Ensure deterministic error paths.
4. Propagate contract-key/schema changes to downstream fixtures and test payload builders.
5. Re-run unit + integration tests.

Output: hardened feature with stable test pass.

### Phase 5 - Operational evidence

Generate required evidence:

- run artifacts,
- logs/traces/events proving transitions,
- validation outputs,
- reproducible commands.

Output: `EvidenceBundle`.

### Phase 6 - Scoring and tracker update

1. Re-score feature using rubric in Section 5.
2. Update `docs/master-architecture-feature-completion.md` row notes and changelog.
3. List exact blockers to next scoring tier.

Output: updated tracker with defensible %.

### Phase 7 - Skeptical review loop

Run a strict reviewer pass:

- attempt to break assumptions,
- identify missing negative tests,
- check blueprint mismatch.

If findings exist, return to Phase 2/3/4 and continue until clean.

Output: final `DONE` or explicit `BLOCKED-*` state.

---

## 5) Completion scoring rubric (mandatory)

- `0%`: no implementation
- `1-24%`: scaffolding only
- `25-44%`: local behavior exists, weak contracts/tests/evidence
- `45-59%`: strong local implementation, major production/governance gaps
- `60-74%`: mostly complete for repo scope, still missing major architecture controls
- `75-89%`: close to blueprint intent, minor high-impact gaps
- `90-99%`: nearly complete, bounded operational hardening remains
- `100%`: all blueprint requirements for this feature are implemented and evidenced

Never set `100%` when any hard gate is unmet.

---

## 6) Definition of done (binary gates)

A feature is `DONE` only if all gates are `true`:

- `G1_RequirementsMapped`
- `G2_BehaviorImplemented`
- `G3_ContractsFailClosed`
- `G4_PositiveTestsPassing`
- `G5_NegativeTestsPassing`
- `G6_IntegrationCoverageSufficient`
- `G7_EvidenceBundleProduced`
- `G8_TrackerUpdatedHonestly`
- `G9_ReviewerPassNoHighSeverityFindings`

If any gate is `false`, status is not done.

---

## 7) Prompt pack (copy/paste)

### Prompt 1 - Feature packet + requirements map

```text
Implement one feature only: <FeatureName>.

Use as authorities:
- docs/AI-Professional-Evolution-Master-Architecture.md sections <BlueprintSections>
- docs/master-architecture-feature-completion.md row <FeatureName>

Produce:
1) One-feature execution packet (FeatureName, sections, code paths, invariants, tests, evidence, done gates).
2) Binary requirement map tied to blueprint text.
3) Prioritized gap list (behavior/contract/test/evidence).

Do not implement code yet.
```

### Prompt 2 - Autonomous TDD implementation loop

```text
Execute this feature end-to-end without pausing:
1) Write failing tests for every acceptance gate and failure mode.
2) Implement minimal code to pass.
3) Harden contracts to fail closed.
4) Re-run tests and integration checks.
5) Generate operational evidence artifacts.
6) Run skeptical review pass.
7) Repeat until all done gates are true.

Stop only on DONE or explicit BLOCKED-EXTERNAL / BLOCKED-DECISION.
When blocked, include exact unblock requirement.
```

### Prompt 3 - Tracker update and honest scoring

```text
Using evidence from implementation and tests:
1) Assign completion % using playbook rubric.
2) Update docs/master-architecture-feature-completion.md row for <FeatureName>.
3) Add changelog entry with why score changed.
4) List blockers to next tier and to 100%.

Reject score inflation based only on local tests.
```

### Prompt 4 - Final validator

```text
Validate <FeatureName> against done gates G1..G9.

Return:
- gate table true/false,
- failing gates with concrete evidence,
- final status: DONE / BLOCKED-EXTERNAL / BLOCKED-DECISION.

If not DONE, specify exact next action and resume execution.
```

---

## 8) No-intervention escalation policy

The agent must self-resolve all internal issues:

- failing tests,
- lint/type failures,
- contract mismatches,
- missing negative-path coverage,
- evidence generation gaps.

The agent may escalate only for:

- missing secret/credential,
- missing external service access,
- contradictory product decisions,
- repository corruption outside feature scope.

Every escalation must include:

- current status,
- exact blocker,
- attempted fixes,
- minimal user action required.

---

## 9) Forbidden behaviors

- claiming done after code changes without evidence,
- skipping red phase in TDD,
- soft-failing invalid state,
- updating completion % without gate proof,
- broad multi-feature edits in a single run,
- stopping because "good enough".

---

## 10) Execution commandment

For each feature:  
`Map -> Gap -> Red -> Green -> Harden -> Evidence -> Score -> Review -> Repeat until DONE`

This loop is mandatory and is the only accepted execution path.
