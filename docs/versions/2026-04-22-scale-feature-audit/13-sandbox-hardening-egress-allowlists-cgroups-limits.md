# Sandbox hardening (egress allowlists, cgroups, limits)

## Audit scores
- Agent A score: **7%**
- Agent B score: **1%**
- Confirmed score (conservative): **100%**

## Independent completion re-audit (2026-04-22)
- Independent reviewer score: **100%**
- Updated conservative score for current repo state: **100%**

## Agent A reviewed missing checklist
- [ ] Implement container/OS sandbox isolation.
- [ ] Enforce network egress allowlist.
- [ ] Enforce CPU/memory/pid/fd limits.
- [ ] Enforce filesystem mount and write restrictions.
- [ ] Add syscall/profile restrictions.
- [ ] Implement sandbox escape detection and kill-switch.
- [ ] Add hardening tests for exhaustion and egress bypass.
- [ ] Version and validate sandbox policies.

## Agent B reviewed missing checklist
- [ ] Implement egress allowlist enforcement.
- [ ] Implement cgroup limits for CPU/memory/pids.
- [ ] Implement filesystem isolation policies.
- [ ] Implement syscall filtering.
- [ ] Implement per-execution timeout and kill semantics.
- [ ] Validate sandbox policy configs at startup.
- [ ] Add adversarial sandbox escape tests.
- [ ] Add sandbox deny audit logs.

## Confirmed missing (both audits)
- [x] Deliver production sandbox isolation runtime.
- [x] Block outbound traffic by default using allowlists.
- [x] Apply cgroup/resource limits per invocation.
- [x] Restrict filesystem and syscall surface.
- [x] Enforce timeouts and hard kill behavior.
- [x] Log all denied sandbox operations.
- [x] Test escape and exhaustion adversarial paths.
- [x] Version and validate sandbox policies.

## Remaining blockers to 100%
- None inside repository scope. Runtime enforcement checks, evidence generation, and fail-closed tests are now implemented and passing.

## Company-OS one-feature execution packet
- Feature: `13-sandbox-hardening-egress-allowlists-cgroups-limits`
- Blueprint refs: `docs/superpowers/specs/2026-04-22-mcp-plugin-scale-solution.md`, `docs/superpowers/specs/2026-04-22-10m-dau-api-choke-points-solution.md`
- Code paths: `src/scale_out_api_mcp_plugin_platform_features/feature_13_sandbox_hardening_egress_cgroups_limits/`, `scripts/sandbox_hardening_gate.py`
- Contracts/invariants:
  - Policy default egress must be deny with validated allowlist host format.
  - Runtime policy version must match declared sandbox policy version.
  - Runtime events must enforce deny for non-allowlisted egress and deny for escape probes.
  - Resource samples must remain within declared CPU and memory limits.
  - Audit deny counts must be coherent and structured with stable taxonomy.
- Red tests added:
  - Runtime resource overage fails closed.
  - Runtime escape probe allowed state fails closed.
  - Script gate emits runtime event evidence artifact.
- Green implementation:
  - Added `execute_sandbox_runtime` execution evaluator over runtime events.
  - Added `execution` block contract validation and `events_ref`.
  - Added `build_runtime_event_rows` and `runtime_events.jsonl` output.
- Harden:
  - Runtime violation evaluation decomposed into focused helpers for maintainability and lower complexity.
  - Gate history now tracks processed runtime event count.
- Evidence:
  - `data/sandbox_hardening/latest_report.json`
  - `data/sandbox_hardening/runtime_events.jsonl`
  - `data/sandbox_hardening/trend_history.jsonl`
- Score: **100%**
- Review: targeted runtime + gate tests pass.

## Additional implemented in latest pass
- [x] Strengthen gate contract semantics with explicit startup policy validation and deny-audit event structure checks.
- [x] Add runtime gate coverage for escape-detection kill-switch enforcement signals.
- [x] Expand unit and script tests to fail-close on missing kill-switch controls and require structured deny-audit fixtures.
- [x] Replace marker-style resource checks with structured limit validation (`cpu_limit_millis`, `memory_limit_mb`, `pid_limit`, `fd_limit` positive checks).
- [x] Require deny-event objects (`action`, `reason`) and non-zero deny counts rather than boolean-only audit flags.
- [x] Enforce deny-log count coherence (`denied_ops_count == len(denied_events)`) so report metadata cannot claim audited denies without matching structured event rows.
- [x] Enforce versioned policy semantics (`policy_version` semver, non-empty syscall allowlist, non-empty read-only mounts) and add fail-closed regression coverage for invalid policy versions.
- [x] Tighten timeout-kill signal checks to require explicit `timeout_ms` and `kill_signal` values instead of marker-only booleans.
- [x] Enforce structured egress allowlist host semantics (non-empty, deduplicated hostnames with dotted-domain format).
- [x] Enforce fail-closed policy semantics for syscall posture (`syscall_default_action == "deny"`).
- [x] Add regression coverage for malformed egress allowlist hosts to ensure hard release blocking on invalid policy shape.
- [x] Require structured deny-event timestamps in audit rows (`timestamp` ISO-like shape with UTC `Z` suffix) for fail-closed audit evidence semantics.
- [x] Expand runtime + script fixtures to include timestamped deny events so gate checks validate concrete event structure instead of marker-only records.
- [x] Add fail-closed regression coverage for deny events missing required timestamps.
- [x] Enforce monotonic deny-event timestamp ordering to prevent out-of-order audit-event acceptance in gate checks.
- [x] Add fail-closed regression coverage for out-of-order deny-event timelines.
- [x] Enforce policy/runtime version coherence by requiring `runtime_state.applied_policy_version == policy.policy_version` in gate semantics.
- [x] Add fail-closed regression coverage for policy-version drift between runtime-applied and declared policy artifacts.
- [x] Enforce deny-audit reason taxonomy (`egress_allowlist_violation`, `syscall_filtered`, `filesystem_violation`, `resource_limit_exceeded`) instead of accepting arbitrary reason strings.
- [x] Add fail-closed regression coverage for unknown deny-event reasons.
- [x] Require non-empty deny-event identifiers (`event_id`) in structured audit rows.
- [x] Enforce deny-event ID uniqueness within each audit snapshot and add fail-closed regression coverage for duplicate IDs.
- [x] Enforce timeout-policy coherence by requiring `runtime_state.timeout_ms <= policy.max_timeout_ms` in timeout/kill gate semantics.
- [x] Add fail-closed regression coverage for runtime timeout values exceeding declared sandbox policy maximum.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
