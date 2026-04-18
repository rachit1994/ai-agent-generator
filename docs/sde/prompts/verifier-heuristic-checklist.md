# Verifier heuristic checklist (local SDE)

**Purpose:** Improve first-pass quality from the executor **before** CTO gates, inspired by common “skills” / reviewer patterns (e.g. OpenHands security onboarding, SWE-agent review loops). The Python verifier remains a **lightweight heuristic**; `sde_gates` stays authoritative for strict scores.

## Blocking (fail `passed` today)

- Empty or whitespace-only executor output.

## Hints only (non-blocking; surfaced in `verifier_report.hints`)

- Presence of `eval(` or `exec(` in generated code — high risk for untrusted input paths.
- Very large single-line blobs — may indicate pasted secrets or log dumps.

## Planner / executor prompt hygiene (upstream-style)

When editing `sde_modes/modes/guarded_pipeline/prompts.py`, keep:

- Explicit “no prose / no fences” rules for code-only stages.
- Short threat-model line: treat task inputs as untrusted unless stated otherwise.
- Edge-case and validation expectations in the planner doc stage.

See also [`../multi-agent-build.md`](../multi-agent-build.md) for role boundaries.
