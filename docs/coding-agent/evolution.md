# Coding-Agent V6 Specification — Learning, Evaluation, and Lifecycle

## In plain words

- **V6 is “get better on purpose, with guardrails.”** Reflection after rough patches, **practice**, **canary** tries, and **promotion** only with evidence — not silent self-rewrite of core policy.
- Uses **memory (V5)** and **events (V4)** so learning stays **linked to real runs**.

## Goal

Deliver **policy-gated learning**, **evaluation**, and **agent lifecycle** mechanics from [docs/architecture/AI-Professional-Evolution-Master-Architecture.md](../architecture/AI-Professional-Evolution-Master-Architecture.md): **§6 Agent Lifecycle**, **§9 Learning & Evolution Engine**, **§13 Evaluation Framework**, **§11 Guardrails** (review gating, risk budgets), and **§17 Phase 1–3** themes (single-agent evolution through autonomous learning with bounded risk).

**Architecture traceability:** **§6**, **§9**, **§11**, **§13**, **§14** (promotion / hard gates where applicable), **§17 Phases 1–3**, **§19** improvements around causal closure and adaptation control plane.

## Relationship to Prior Versions

- **V4** supplies events and replay for **lineage**: `event -> reflection -> update -> evaluation` (master §6 promotion rules).
- **V5** supplies **memory** inputs to reflection and practice.
- **V6** defines **LearningAgent** / **EvaluatorAgent** / **PracticeAgent** contracts and **promotion** evidence packages—not narrative progression.

`balanced_gates.hard_stops` for evolution-enabled runs **must** include **HS01–HS28** (V6 adds **HS25–HS28**).

## Priority Order

**Evaluator fail and safety veto** beat autonomous update application (master §15 arbitration order: `SafetyController veto > Evaluator fail > Reviewer pass`).

## External research alignment (self-training, promotion, canary)

- **STaR / ReST^EM** ([arXiv:2203.14465](https://arxiv.org/abs/2203.14465), [arXiv:2312.06585](https://arxiv.org/abs/2312.06585)): any **train-on-own-traces** step must **filter** on verifier reward (tests, evaluator, human) before the M-step; lineage belongs in the event store ([events.md](events.md)).
- **B-STaR** ([ICLR 2025 PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/c8db30c6f024a3f667232ed7ba5b6d47-Paper-Conference.pdf)): **canary** and **promotion hold** profiles must watch **exploration collapse** and **reward saturation** across iterations—extend `learning/canary_report.json` with diversity / discriminator diagnostics when implementing.
- **Mind the Gap** ([OpenReview ICLR 2025](https://openreview.net/pdf?id=mtJSMcF3ek)): **independent evaluator** and **holdout suites** remain mandatory when verification is weaker than generation on a slice.
- **Constitutional AI** ([arXiv:2212.08073](https://arxiv.org/abs/2212.08073)): reflection bundles are the **principle-guided critique** artifact before promotion.

Full mapping: [docs/research/self-improvement-research-alignment.md](../research/self-improvement-research-alignment.md).

## End-User Features (Minimum 3)

### Feature 1 — Reflection bundle with causal closure

- **Outcome:** Each learning update proposal lists root causes, evidence links, and predicted blast radius before evaluation.
- **Artifacts:** `learning/reflection_bundle.json`, linked `event_id` chain.
- **Evidence:** **HS25** if `causal_closure_checklist` incomplete when policy requires.

### Feature 2 — Promotion / hold / demotion packages

- **Outcome:** Stage changes are explicit packages with independent reviewer/evaluator signals (master §6).
- **Artifacts:** `lifecycle/promotion_package.json`, `lifecycle/hold_package.json`, `lifecycle/demotion_package.json` (only one active transition per aggregate).
- **Evidence:** **HS26** if promotion event lacks committee / independent signal record when required by profile.

### Feature 3 — Practice loop for verified gaps

- **Outcome:** Skill gaps drive **PracticeAgent** workloads with pass/fail evaluation (master §3 deliberate practice mapping).
- **Artifacts:** `practice/task_spec.json`, `practice/evaluation_result.json`.
- **Evidence:** Delivery; **HS27** if practice task runs without prior gap detection artifact.

### Feature 4 (bonus) — Canary / shadow for learning updates

- **Outcome:** Phase 3 “stable experiment-to-adoption” (§17): shadow metrics before promotion of policy or prompt bundles.
- **Artifacts:** `learning/canary_report.json` with `shadow_metrics` and `promote: boolean`.
- **Evidence:** Governance; **HS28** if production promotion of learning bundle without canary artifact when `learning_promotion_requires_canary: true`.

## Hard-Stop Gates (V6 Additive)

| ID | Condition | Detection |
|----|-----------|-----------|
| HS25 | **Causal closure** incomplete for reflection-driven update | Required checklist fields false / missing in `reflection_bundle.json` |
| HS26 | **Promotion** missing **independent approval** record when profile mandates | `promotion_package.json` missing `independent_evaluator_signal_ids[]` |
| HS27 | **Practice** without **verified gap** | `practice/task_spec.json` exists but no `gap_detection_ref` |
| HS28 | **Learning bundle promotion** without **canary** when required | Config true but no `learning/canary_report.json` with `promote: true` lineage |

## Validation Matrix

| Gate theme | Primary evidence | Supporting |
|------------|------------------|------------|
| Governance | HS25–HS28, promotion packages | Safety veto events (V4) |
| Delivery | practice evaluation results | V3 verification where combined |
| Reliability | rolling evaluation windows | §14 metrics feeds |

## How self-improvement and progression work in practice (concrete flow)

This section describes **how** V6 implements the "junior engineers who learn and grow" model. See [action-plan.md](../onboarding/action-plan.md) §2 Stage 6 and §3.

### Learning across runs (how the system gets better)

```
Run N completes (pass or fail):
  → Reflection agent examines:
      - Which steps failed review? Why?
      - Which verification commands failed? Root cause?
      - What learning_events were captured?
      - What was the time/token cost of rework?

  → Reflection bundle produced:
      learning/reflection_bundle.json:
        root_causes: ["auth middleware missed JWT expiry check"]
        evidence_links: [event_id_1, step_review_id_3]
        blast_radius: "auth-related steps in future runs"
        proposed_intervention: "add JWT expiry to reviewer checklist"
        causal_closure_checklist: {
          failure_class: true,
          root_cause_evidence: true,
          intervention_mapped: true,
          post_fix_verified: true (from rerun)
        }

  → If causal_closure complete (HS25 satisfied):
      Lesson enters practice queue or memory (V5)
  → If incomplete:
      Stays in reflection; no promotion of the lesson
```

### Practice loop (how gaps are closed)

```
Reflection identifies gap: "agent consistently fails auth edge cases"
  → PracticeAgent generates targeted tasks:
      practice/task_spec.json:
        gap_detection_ref: reflection_bundle_id
        task: "Implement JWT refresh with expiry, revocation, and race conditions"
        acceptance_criteria: [...]

  → Agent executes practice task (same V1–V3 gates apply)
  → practice/evaluation_result.json: passed or failed

  → If passed: capability node updated, gap marked addressed
  → If failed: gap remains open, practice repeats (bounded)
```

**HS27 enforcement:** Practice tasks cannot exist without a `gap_detection_ref`. Random practice is not permitted — every practice task traces back to a verified weakness.

### Promotion mechanics (how agents earn trust)

```
After sustained performance (rolling window of N runs):
  → Evaluator agent (independent from Implementor/Reviewer) assesses:
      - Step review pass rate
      - Verification pass rate
      - Rework frequency
      - Practice completion rate
      - Learning event quality

  → Promotion package assembled:
      lifecycle/promotion_package.json:
        current_stage: "junior"
        proposed_stage: "mid-level"
        evidence_window: [run_id_1 ... run_id_N]
        independent_evaluator_signal_ids: [eval_id_1]
        capability_scores: { ... }

  → Independent reviewer signs off (HS26: no self-approval)
  → If approved: stage advances, autonomy expands per permission matrix
  → If denied: hold_package.json with reasons and development plan
```

**What promotion means concretely:** A "mid-level" agent gets wider file scope, fewer mandatory review interventions (e.g. review every 3rd step instead of every step), and access to higher-risk operations. But it still cannot self-approve promotions, bypass safety, or write outside its lease.

### Canary for learning updates (how changes are tested)

```
When a policy or prompt change is proposed from reflection:
  → Canary run: same task suite, new policy, shadow mode
      learning/canary_report.json:
        shadow_metrics: { pass_rate, rework_rate, token_cost }
        baseline_metrics: { ... from previous runs }
        promote: true/false (based on regression threshold)

  → If promote: true → policy update applied to future runs
  → If promote: false → change rejected with specific regressions
```

**HS28 enforcement:** When `learning_promotion_requires_canary: true`, no policy/prompt change goes live without a passing canary. This prevents the system from "learning" its way into worse performance.

## Execution Profiles

1. **PromotionHoldProfile** — Signals insufficient; must land in `hold`, never silent promote.
2. **CausalClosureFailProfile** — Incomplete bundle; HS25 blocks update application.
3. **CanaryBlockProfile** — Canary fails; promotion blocked with explicit reasons.

## Acceptance Criteria

1. Arbitration order from master §15 is encoded in orchestrator decision logs (test or spec conformance statement).
2. At least one profile run demonstrates **HS26** on missing independent signal fixture.
3. Master §6 promotion bullets and §9 reflection/update bullets each map to a subsection here (traceability table in implementation checklist).

## Definition of Done for This V6 Doc

- Covers lifecycle + learning + evaluation + Phase 1–3 roadmap intent without claiming unconstrained self-modification.
- HS25–HS28 testable.
- Linked from [docs/README.md](../README.md) and [README.md](../../README.md).
