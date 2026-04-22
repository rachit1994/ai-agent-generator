# Feature 13: sandbox hardening (egress allowlists, cgroups, limits)

This folder contains isolated sandbox hardening gate logic.

## Components
- `runtime.py`: sandbox hardening checks for egress, limits, isolation, syscall/fs restrictions, timeout-kill semantics, adversarial tests, and policy validation.
- `contracts.py`: strict report contract validation.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces deny-by-default egress policy, cgroup/resource controls, restricted syscall/filesystem surface, timeout/kill behavior, denied-operation auditing, adversarial test coverage, and policy version validation.
- Blocks release on any failed sandbox hardening gate check.
- Uses one executable command for `preflight` and `ci`.
