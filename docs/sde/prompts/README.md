# MVP Prompt Playbook

This playbook provides a numbered sequence of prompts you can paste into Cursor
to build the MVP end-to-end with balanced granularity.

Model policy for prompt execution:

- Use `qwen2.5:7b-instruct` for implementation/coding prompts.
- Use `gemma 4` for planning/review/support prompts.
- Implement in Python (`src/services/orchestrator/orchestrator/runtime` package and `pytest`-based validation).

## How to Run

1. Open `00-master-sequence.md`.
2. Copy Prompt 01 into Cursor and run it.
3. Verify completion using the mapped phase checklist.
4. Only continue when the current phase gate is green.
5. Repeat sequentially until Prompt 24 is complete.
