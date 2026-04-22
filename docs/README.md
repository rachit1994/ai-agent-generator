# Project Docs: Start Here

If you are new to this repo, this file is your quick starting point.

In plain English: this project is a structured system for building and validating an AI-agent architecture in small, testable, fail-closed steps. The repo tracks feature completeness honestly, enforces strict quality gates, and keeps implementation work aligned with a master architecture.

## What this project is trying to do
- Define a full target architecture for an AI agent system.
- Implement that architecture feature-by-feature in code.
- Require strong contract checks and negative-path tests so invalid states fail closed.
- Track progress with explicit completion percentages and evidence-backed notes.

## How to think about the docs
- The architecture doc describes the destination.
- The playbook describes the execution loop used to build features.
- The DoD policy defines quality gates that must pass before claiming completion.
- The completion tracker shows current status, what improved, and what gaps remain.

## Read in this order
1. `UNDERSTANDING-THE-CODE.md`  
   Start here for codebase orientation and naming context.
2. `AI-Professional-Evolution-Master-Architecture.md`  
   Read this to understand the intended end-state architecture.
3. `ai-agent-feature-completion-playbook.md`  
   Read this to understand the expected implementation workflow.
4. `SDE-Task-Execution-DoD-Policy.md`  
   Read this to understand what "done" means in this repo.
5. `master-architecture-feature-completion.md`  
   Use this as the live progress dashboard and gap log.

## Practical usage by role
- If you are implementing a feature: read architecture -> playbook -> DoD policy -> relevant row in tracker.
- If you are reviewing work: use DoD policy + tracker notes to verify evidence and fail-closed behavior.
- If you are planning next work: start with the tracker to find highest-impact incomplete features.

## Ground rules for updates
- Keep descriptions honest: no score inflation without test and artifact evidence.
- When a feature changes, update both implementation and tracker notes.
- Keep this README newcomer-friendly and in everyday language.
