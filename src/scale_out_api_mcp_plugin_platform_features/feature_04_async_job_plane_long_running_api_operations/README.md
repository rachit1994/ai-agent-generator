# Feature 04: async job plane for long-running API operations

This folder contains isolated async job plane gate logic for long-running API workflows.

## Components
- `runtime.py`: lifecycle contract + async plane health checks.
- `contracts.py`: strict report contract + canonical evidence references.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces durable queue/lifecycle/recovery, worker heartbeat, DLQ, retry backoff, queue metrics, and cancel/timeout semantics.
- Blocks release on any failed async-plane gate check.
- Uses one executable command in both `preflight` and `ci` modes.
