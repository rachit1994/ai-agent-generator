# Feature 19: end-to-end plugin observability (API->MCP->runtime)

This folder contains isolated end-to-end plugin observability gate logic.

## Components
- `runtime.py`: correlation/span/taxonomy/SLI/trace/dashboard/retention/continuity checks.
- `contracts.py`: strict report contract and evidence refs.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces correlation propagation API->MCP->runtime, stage-level spans/events, normalized errors/outcomes, plugin+tenant SLIs/SLOs, cross-boundary trace stitching, dashboards/alerts, retention policy, and continuity test coverage.
- Blocks release on any failed observability gate check.
- Uses one executable command for `preflight` and `ci`.
