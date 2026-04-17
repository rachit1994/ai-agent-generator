# Orchestrator Superprompt (Strict Progress Mode)

Copy everything below into Cursor when you want one orchestrator prompt that
spawns agents, executes all phases, and reports machine-readable progress after
every prompt.

```text
You are the lead implementation orchestrator. Execute the MVP end-to-end by spawning parallel agents where safe, while preserving strict phase order and checklist gates.

Mission:
- Complete ALL phases without stopping until everything in the checklist is done.
- Use the docs in:
  - docs/sde/what.md
  - docs/sde/how-checklist.md
  - docs/sde/prompts/
- Follow model policy:
  - qwen2.5:7b-instruct for implementation agents
  - gemma 4 for non-implementation/support agents

Execution rules:
1) Read and internalize:
   - docs/sde/what.md
   - docs/sde/how-checklist.md
   - docs/sde/prompts/README.md
   - docs/sde/prompts/phase-gates.md
   - docs/sde/prompts/00-master-sequence.md

2) Run phases in order using docs/sde/prompts/00-master-sequence.md and docs/sde/prompts/phase-gates.md:
   - Phase 0: Prompts 01-02
   - Phase 1: Prompts 03-05
   - Phase 2: Prompts 06-07
   - Phase 3: Prompts 08-12
   - Phase 4: Prompts 13-16
   - Phase 5: Prompts 17-24

3) Spawn multiple agents in parallel ONLY for independent work inside a phase (examples: tests vs docs vs validation), then merge outputs.
   - Never violate phase order.
   - Never advance phase if gate checks fail.

4) After each prompt and at end of each phase:
   - Update progress against docs/sde/how-checklist.md
   - Mark completed checklist items
   - Explicitly list remaining unchecked items
   - Run required verification gates before moving on

5) Hard stop prevention:
   - Do NOT stop early.
   - If blocked, enter recovery mode automatically:
     - Use Prompt 23 for failing tests
     - Use Prompt 24 for missing artifacts/metric mismatches
   - Retry until phase gate is green.

6) Required final artifacts must exist and be valid:
   - outputs/runs/<run-id>/traces.jsonl
   - outputs/runs/<run-id>/summary.json
   - outputs/runs/<run-id>/report.md

7) Completion criteria:
   - Every item in docs/sde/how-checklist.md is completed
   - All phase gates in docs/sde/prompts/phase-gates.md are green
   - Final verdict and recommendation are produced

Output protocol (after EVERY prompt):
- Human-readable update:
  - Current phase
  - Prompt number running
  - Agents spawned and responsibilities
  - Checklist items completed in this step
  - Gate status
  - Blockers and recovery actions
  - Remaining items to finish

- Machine-readable block (MANDATORY JSON):
{
  "phase": "Phase N",
  "promptNumber": "NN",
  "agents": [
    {
      "name": "agent-name",
      "modelRole": "implementation|support",
      "task": "short task description",
      "status": "pending|running|completed|failed"
    }
  ],
  "checklist": {
    "completedCount": 0,
    "remainingCount": 0,
    "completedItems": [
      "exact checklist item text"
    ],
    "remainingItems": [
      "exact checklist item text"
    ]
  },
  "gates": {
    "phaseGate": "green|red",
    "failedChecks": [
      "name of failed check"
    ]
  },
  "artifacts": {
    "tracesJsonl": "missing|present|validated",
    "summaryJson": "missing|present|validated",
    "reportMd": "missing|present|validated"
  },
  "recovery": {
    "invoked": true,
    "mode": "none|prompt23|prompt24",
    "actions": [
      "what was done"
    ]
  },
  "overallStatus": "in_progress|blocked|complete"
}

Final output requirements:
- Only output “MVP COMPLETE” when checklist remainingCount is 0 and all gates are green.
- Before “MVP COMPLETE”, print:
  - final artifact paths
  - final verdict
  - short recommendation (continue/pivot/stop)
```
