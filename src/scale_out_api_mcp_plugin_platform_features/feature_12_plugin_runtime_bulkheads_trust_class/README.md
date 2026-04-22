# Feature 12: plugin/runtime bulkheads by trust class

This folder contains isolated trust-class bulkhead gate logic.

## Components
- `runtime.py`: trust-class segmentation and boundary checks.
- `contracts.py`: strict report contract validation.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces trust-class policy, segmented pools, class-level quotas/isolation, cross-class leakage controls, boundary audit controls, containment tests, safe reclassification, and trust-class telemetry.
- Blocks release on any failed bulkhead gate check.
- Uses a single executable command for `preflight` and `ci`.
