# AI Professional Evolution System

This repo is a practical attempt to build a production-grade AI agent system in a disciplined way.

In everyday terms: we are building an agent platform that can do work, learn from results, and improve over time, while staying safe and auditable. We do that by combining strict contracts, fail-closed checks, and test-backed progress tracking.

## What you will find here
- `src/`: Python implementation of architecture slices (runtime modules, contracts, tests).
- `docs/`: architecture source-of-truth, execution playbook, quality policy, and completion tracker.
- `libs/`: shared packages used across modules.

## Quick start
```bash
uv sync --group dev
uv run pytest
```

Python version is pinned by `.python-version` and CI.

## Read this first (recommended order)
1. `docs/README.md`  
   Fast orientation to the docs and how they fit together.
2. `docs/UNDERSTANDING-THE-CODE.md`  
   Practical map of the codebase and runtime entry points.
3. `docs/AI-Professional-Evolution-Master-Architecture.md`  
   The full target architecture ("where we are going").
4. `docs/ai-agent-feature-completion-playbook.md`  
   The required implementation loop ("how work is executed").
5. `docs/SDE-Task-Execution-DoD-Policy.md`  
   The strict Definition of Done and quality gates.
6. `docs/master-architecture-feature-completion.md`  
   The live progress tracker with completion percentages and gaps.

## Core idea
The system is designed around this loop:

`Task -> Execute -> Review -> Evaluate -> Learn -> Improve`

Every step is expected to be:
- deterministic where possible,
- evidence-backed,
- fail-closed on invalid or unsafe inputs.

## How to contribute safely
- Keep changes small and scoped to one feature slice when possible.
- Add both positive and negative-path tests.
- Treat contracts as strict interfaces, not suggestions.
- Update relevant docs when behavior or completion claims change.

## Current maturity
This repository includes substantial local runtime and validation logic, but many capabilities are still in progress relative to the full architecture blueprint.
