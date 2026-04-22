# Feature 20: per-plugin/per-tenant cost attribution and caps

This folder contains isolated cost-attribution and cap-enforcement gate logic.

## Components
- `runtime.py`: metering/aggregation/cap checks.
- `contracts.py`: strict report contract and evidence refs.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces plugin+tenant metering pipeline, normalized billable units, near-real-time attribution, hard/soft caps with admission enforcement, cap-breach response contracts, report/export generation, anomaly/burn-rate detection, and concurrency cap test coverage.
- Blocks release on any failed cost-attribution gate check.
- Uses one executable command for `preflight` and `ci`.
