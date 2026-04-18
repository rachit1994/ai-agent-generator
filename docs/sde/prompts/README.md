# MVP Prompt Playbook

**In plain words:** **copy-paste prompts** for building the MVP inside an AI-assisted editor. Follow **`00-master-sequence.md`** in order; **do not skip** phase gates — each step assumes the last one really finished.

This playbook provides a numbered sequence of prompts you can paste into Cursor
to build the MVP end-to-end with balanced granularity.

Model policy for prompt execution:

- Use `qwen3:14b` for implementation/coding prompts.
- Use `gemma 4` for planning/review/support prompts.
- Implement in Python (`src/orchestrator/runtime` package and `pytest`-based validation).

## How to Run

1. Open `00-master-sequence.md`.
2. Copy Prompt 01 into Cursor and run it.
3. Verify completion using the mapped phase checklist.
4. Only continue when the current phase gate is green.
5. Repeat sequentially until Prompt 24 is complete.

## Verifier and gates

- Heuristic verifier checklist (for prompt and `verify_core` alignment): [`verifier-heuristic-checklist.md`](verifier-heuristic-checklist.md).
