# Coding-Agent — Execution extension

## In plain words

- **Read this when** you need to know what a **trusted run** must produce (folders, JSON files, scores) and which **automatic checks** cannot be skipped.
- **Hard-stops HS01–HS06** mean: if any one fails, the run must **not** be treated as successful — full stop.
- **Balanced gates** mean: we score **reliability, delivery, and governance** together instead of pretending one number tells the whole story.
- **This is V1** — every later version (V2–V7) must stay inside these safety and evidence rules.

## Goal

**Global precedence:** V1 (this spec, HS01–HS06) is the **non-bypassable trust base** for all later coding-agent extensions. Nothing in V2–V7 may trade away execution safety, token/context integrity, or balanced gate evidence for speed or learning volume. See [action-plan.md](../onboarding/action-plan.md) §2.

Deliver the coding-agent **execution extension** as a local-first orchestration runtime that can:
- run long tasks reliably,
- run the same task multiple times with reproducible artifacts,
- write multiple output files per run,
- complete task execution with a review step,
- keep CTO production gates in active validation mode.

## External research alignment (execution as verifiable substrate)

Downstream self-learning and self-training (see [research doc](../research/self-improvement-research-alignment.md)) assume **honest traces**, **token/context integrity** (HS03, HS06), and **structured review** (`review.json`). **Self-Refine**-style loops ([arXiv:2303.17651](https://arxiv.org/abs/2303.17651)) only work if each refinement is **logged**; **DSVD**-style checks ([arXiv:2503.03149](https://arxiv.org/abs/2503.03149)) can optionally tighten high-risk generations **before** they are written to `outputs/`. This extension is the **evidence layer** those methods depend on.

## Scope

In scope:
- long-running orchestration flow with retries, timeouts, and bounded resource use.
- repeatable run execution (`N` repeated runs for the same task/config).
- multi-artifact output generation in a single run directory.
- structured completion review with pass/fail outcome and reason codes.
- gate-validation reporting against CTO criteria.
- strict balanced evaluation (reliability, delivery, governance) plus hard-stop blockers.
- token and context handling with observable evidence in `token_context.json`.

Out of scope:
- automatic production gate claim (`100/100`) and autonomous release promotion.
- cloud-first runtime dependencies for critical execution loops.
- cross-machine distributed scheduler.
- new top-level repository folders beyond what this doc maps under existing layout.

## Why this extension exceeds the baseline (evidence-backed deltas)

Baseline contracts are in `docs/sde/what.md` and `docs/sde/implementation-contract.md`. This document extends them with measurable upgrades:

| Dimension | Baseline (SDE) | Execution extension |
|-----------|-----|-----|
| Run horizon | Timeboxed short runs | Long-window execution with checkpointed trace events |
| Repetition | Single-run focus | Isolated per-attempt outputs under repeatable execution |
| Outputs | Primary single-file paths (`answer.txt`, `generated_script.py`) plus guarded artifacts | Mandatory multi-file `outputs/` plus same baseline-compatible files when pipeline produces them |
| Review | Verifier stage and `verifier_report.json` | Mandatory structured `review.json` with gate snapshot and remediation |
| Token/context | Per-task token cap in run config | Per-stage input/output budgets, `token_context.json`, no silent truncation |
| Readiness | Verdict from benchmark metrics | Strict balanced scores plus hard-stops; CTO gates remain `validating` until evidence thresholds pass |

This extension stays aligned with orchestrator code under `src/orchestrator/runtime/`; it does not require the full master OS service tree to exist before validation.

## Folder-Structure Compliance

This extension does not introduce a new repository layout. It aligns with:
- `docs/architecture/operating-system-folder-structure.md` for long-term target boundaries.
- Current baseline implementation roots: `src/`, `docs/`, `data/`, `outputs/`.
- Local SDE demos: `demo_apps/` (gitignored at repo root); tracked seed at `docs/templates/sde-demo/`.
- Implementation sequencing and parallel lanes: [`docs/sde/pipeline-plan.md`](../sde/pipeline-plan.md); multi-agent code map: [`docs/sde/multi-agent-build.md`](../sde/multi-agent-build.md).

### Path mapping (execution extension artifacts)

All run-scoped artifacts stay under:

`outputs/runs/<run-id>/`

| Path | Purpose |
|------|---------|
| `summary.json` | Aggregated result, metrics, balanced scores |
| `traces.jsonl` | Stage-ordered events for replay and audit |
| `orchestration.jsonl` | Pipeline-level control flow and retries |
| `review.json` | Completion review, hard-stop results, `gate_snapshot` |
| `token_context.json` | Token budgets, usage, context policy applications |
| `outputs/` | Multiple generated task files (required for multi-file delivery proof) |
| `report.md` | Human-readable report (baseline-compatible; this extension may add sections) |
| `run.log` | Stdlib ``logging`` narrative (planner, prompts, executor excerpts, errors) |

Optional baseline-aligned files remain allowed when the pipeline emits them: `answer.txt`, `generated_script.py`, `planner_doc.md`, `executor_prompt.txt`, `verifier_report.json`.

Contract JSON schemas may live in a dedicated `contracts/` tree when implemented (see master OS layout in `docs/architecture/operating-system-folder-structure.md`); this spec defines required logical fields so validators can be added without ambiguity.

Runtime validation helper (for CI and local checks): `sde_gates.validate_execution_run_directory` must return `ok: true` and `validation_ready: true` on a reference green run.

## Functional Requirements

1. Long-run stability:
   - runtime supports task windows that exceed short one-shot flows.
   - progress is checkpointed in trace events so a long run is auditable.
2. Repeat execution:
   - runner supports repeated execution (`--repeat` or equivalent config field).
   - each attempt stores isolated artifacts and summary metrics.
3. Multi-file write support:
   - one run can emit many files (for example: code, tests, notes, review report).
   - file writes are deterministic and tied to a run id.
4. Task completion and review:
   - execution ends with structured review status:
     - `completed_review_pass`
     - `completed_review_fail`
     - `incomplete`
   - review output includes missing checks and remediation hints.
5. CTO gates validation mode:
   - gate state is tracked as `validating`, `pass`, or `fail`.
   - V1 default posture is `validating` until evidence thresholds are met.
6. Token handling:
   - each stage enforces an input-token budget and output-token budget.
   - budget breaches fail closed with explicit reason codes (no silent truncation).
   - token usage is recorded per stage and per run for gate validation.
7. Context handling:
   - runtime applies a deterministic context policy when prompt/context nears model limits.
   - policy order is explicit: prioritize required instructions, then recent task state, then historical context.
   - overflow is handled by structured summarization/compression with provenance references.

## How the runtime drives a full-stack task (concrete flow)

The action plan ([action-plan.md](../onboarding/action-plan.md) §2) describes the end-to-end delivery. V1 execution owns the **foundational loop** that every later version builds on:

```
User prompt
  → Orchestrator creates run_id, output directory
  → Selects mode (baseline or guarded_pipeline)
  → For each pipeline stage:
      Pre-check: token budget (HS06), context overflow (HS03)
      Execute: LLM call with stage-specific persona
      Post-check: output schema validation, safety scan (HS04)
      Trace: emit to traces.jsonl (HS05)
  → Reviewer stage: produces review.json (HS01)
  → Gate sweep: balanced scores + hard-stops
  → Terminal state: pass / fail / incomplete with reasons
```

**Agents as junior engineers:** Each pipeline stage's LLM call uses a **role persona** (planner, implementor, reviewer). The orchestrator is deterministic Python — it enforces order, budgets, and gates. The LLM is the junior who does the creative work; the orchestrator is the process that keeps the junior honest. See [action-plan.md](../onboarding/action-plan.md) §3 for the full role table.

**Continuous gates, not final checkpoint:** Token checks happen **before** every LLM call. Schema validation happens **after** every LLM output. The balanced gate score is computed at run end, but individual hard-stops block progress **immediately** when violated.

**Multi-file delivery:** A full-stack task produces code, tests, docs, configs. All go under `outputs/runs/<run-id>/outputs/`. The `review.json` → `artifact_manifest` lists every expected file with `present: boolean`.

## Non-Functional Requirements

- Determinism: same input + config should produce reproducible control flow.
- Observability: every stage emits machine-readable traces and summary artifacts.
- Safety: fail closed on malformed outputs, unsafe actions, and contract violations.
- Performance: bounded retries, timeout caps, and resource budget accounting.
- Context-window safety: context size is preflight-checked before model calls.
- Token predictability: runs expose planned vs actual token usage by stage.

## Strict Balanced Gate Model

V1 readiness uses three equal-weight categories plus a composite. Profile: **Strict**.

### Category scores (0–100 each)

Inputs are taken from `summary.json`, `traces.jsonl`, `orchestration.jsonl`, `review.json`, and `token_context.json`.

1. **Reliability**
   - Measures: run completion without unhandled failure, timeout/retry discipline, trace continuity, repeat-run consistency of control-flow markers.
   - Minimum for V1 readiness: **>= 85**.

2. **Delivery**
   - Measures: required artifacts present, multi-file output under `outputs/` when task demands it, review status alignment with verifier outcomes, task acceptance checks satisfied.
   - Minimum for V1 readiness: **>= 85**.

3. **Governance**
   - Measures: safety/refusal compliance, schema validity, token/context integrity, gate snapshot completeness, no hard-stop violations.
   - Minimum for V1 readiness: **>= 85**.

### Composite score

- `composite = round((reliability + delivery + governance) / 3)`.
- Minimum for V1 readiness: **>= 90**.

### Pass logic

V1 is **validation-ready** only when:
- `reliability >= 85` AND `delivery >= 85` AND `governance >= 85` AND `composite >= 90`, AND
- every **hard-stop** gate is satisfied (see below).

If any hard-stop fails, V1 readiness is **blocked** regardless of category scores.

Scoring implementation may use weighted sub-metrics within each category; this spec requires the rolled-up three scores and composite to be written to `summary.json` under a `balanced_gates` object (see required fields).

## Hard-Stop Gates

Any single violation blocks V1 readiness. Detection must be artifact-backed.

| ID | Condition | Detection |
|----|-----------|-----------|
| HS01 | Missing or invalid `review.json` | File absent or JSON schema validation fails |
| HS02 | Missing or invalid `token_context.json` | File absent or required keys missing |
| HS03 | Untracked context truncation | `token_context.json` shows truncation without a logged summarization step and provenance reference |
| HS04 | Safety or refusal-policy failure | `review.json` or `traces.jsonl` records `unsafe` or policy refusal with no clean terminal state |
| HS05 | Missing replay-critical lineage | `traces.jsonl` missing monotonic stage sequence or `orchestration.jsonl` missing entries for each model stage invocation |
| HS06 | Silent token budget breach | actual tokens exceed budget without `fail_closed` terminal reason in traces |

## Output Contract (Per Run)

Required artifacts in `outputs/runs/<run-id>/`:
- `summary.json` (high-level result, metrics, `balanced_gates`)
- `traces.jsonl` (ordered stage and action trace)
- `orchestration.jsonl` (pipeline-level events)
- `review.json` (completion review and gate snapshot)
- `token_context.json` (token budgets, usage, context reductions, overflow handling)
- `report.md` (human-readable report; baseline-compatible)
- `run.log` (human-readable pipeline narrative via stdlib logging)
- `outputs/` directory for generated task files (multiple files allowed when task requires)

## Artifact Contract Hardening

### `summary.json` — required `balanced_gates` object

```json
{
  "balanced_gates": {
    "reliability": 0,
    "delivery": 0,
    "governance": 0,
    "composite": 0,
    "threshold_profile": "strict",
    "hard_stops": [
      { "id": "HS01", "passed": true },
      { "id": "HS02", "passed": true },
      { "id": "HS03", "passed": true },
      { "id": "HS04", "passed": true },
      { "id": "HS05", "passed": true },
      { "id": "HS06", "passed": true }
    ]
  }
}
```

- All four scores are integers 0–100.
- `hard_stops` must include one object per ID `HS01`..`HS06`; each entry includes `id`, `passed` (boolean), and optional `evidence_ref` (path or trace line id).

### `review.json` — required fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Contract version, e.g. `1.0` |
| `run_id` | string | Matches directory `<run-id>` |
| `status` | string | `completed_review_pass` \| `completed_review_fail` \| `incomplete` |
| `reasons` | array | Machine-readable reason codes |
| `required_fixes` | array | Actionable remediation items |
| `gate_snapshot` | object | Per-gate `validating` \| `pass` \| `fail` with evidence pointers |
| `artifact_manifest` | array | List of required relative paths and `present` boolean |
| `completed_at` | string | ISO-8601 timestamp |

### `token_context.json` — required fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Contract version |
| `run_id` | string | Matches `<run-id>` |
| `model_context_limit` | number | Declared context window used for preflight |
| `stages` | array | Per-stage: `name`, `input_token_budget`, `output_token_budget`, `planned_input_tokens`, `actual_input_tokens`, `actual_output_tokens`, `budget_status` |
| `context_policy` | object | Ordered priority list and version hash for determinism |
| `reductions` | array | Each summarization: `stage`, `removed_ref`, `summary_ref`, `provenance_id` |
| `truncation_events` | array | Empty if none; any entry must pair with a reduction with matching `provenance_id` |

## Review Model

Review evaluates:
- requirement satisfaction,
- artifact completeness,
- schema validity,
- policy and guardrail compliance.

Review result must include the required `review.json` fields above.

## CTO gate validation (execution extension)

Gate categories tracked for strict execution:
- reliability gates,
- safety gates,
- replay/auditability gates,
- resource-budget gates,
- token-budget and context-window gates.

Policy:
- V1 can ship as "validation-ready" when strict balanced thresholds pass and all hard-stops pass.
- V1 cannot claim "production-grade complete" while any required gate remains `validating`.

## Validation Matrix (Gates to Evidence)

| Gate theme | Primary evidence | Supporting evidence |
|------------|------------------|---------------------|
| Reliability | `summary.json` `balanced_gates.reliability`, `traces.jsonl` | `orchestration.jsonl` |
| Delivery | `review.json` `artifact_manifest`, `outputs/` listing | `summary.json` |
| Safety | `review.json` `reasons`, `gate_snapshot` | `traces.jsonl` |
| Replay/auditability | `traces.jsonl`, `orchestration.jsonl` | `summary.json` |
| Resource budget | `summary.json` metrics | `orchestration.jsonl` timeouts |
| Token budget | `token_context.json` `stages[].budget_status` | `traces.jsonl` |
| Context window | `token_context.json` `reductions`, `truncation_events` | `traces.jsonl` |

## Execution Profiles

Profiles prove V1 behavior without changing folder layout.

1. **LongRunProfile**
   - Single task with extended timeouts and checkpoint expectations in `traces.jsonl`.
   - Acceptance: run completes with continuous stage sequence and `review.json` terminal status not `incomplete` unless documented in `reasons`.

2. **RepeatProfile**
   - Same task and config executed `N >= 2` times; each run id has isolated `outputs/runs/<run-id>/`.
   - Acceptance: per-run `balanced_gates` and hard-stops emitted; cross-run scores may be aggregated in a separate benchmark summary (optional).

3. **MultiFileProfile**
   - Task requires `outputs/` to contain `>= 2` distinct files beyond fixed artifact names.
   - Acceptance: `review.json` `artifact_manifest` lists each file with `present: true`.

## Acceptance Criteria

This extension is accepted when all conditions are true:
1. A single task can run with long-window settings and produce full artifacts (LongRunProfile).
2. The same task can run multiple times with isolated run outputs (RepeatProfile).
3. A run can write multiple generated files in one execution when required (MultiFileProfile).
4. Every run ends with a structured `review.json` and explicit `status`.
5. `summary.json` includes `balanced_gates` meeting strict thresholds and hard-stops all passed.
6. `token_context.json` shows deterministic handling: no HS03 or HS06 violations.
7. Gate snapshot in `review.json` shows real validation progress (not placeholder data).

## Definition of done for this document

- Requirements are explicit and testable.
- Output and review contracts are unambiguous.
- Baseline deltas and strict balanced + hard-stop model are documented.
- CTO gate status is clearly represented as in-progress validation until thresholds pass.
- Specification path: `docs/coding-agent/execution.md` (alongside `docs/sde/` baseline docs).
- Document is linked from `README.md`.
- Later coding-agent extension specs and reading order are indexed in `docs/README.md`.
