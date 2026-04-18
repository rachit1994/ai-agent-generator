# Company OS — versioned delivery plans

**In plain words:** each **missing feature** from the [full delivery checklist](../architecture/company-os-full-delivery-checklist.md) is a **version** with its own plan under [`plans/`](plans/). Every plan uses the same sections so you can confirm **(a)** the version is **completed** (shipped artifacts) and **(b)** it is **working** (verified in CI / `local-prod` / reference runs).

## How to use

1. Open **[`INDEX.md`](INDEX.md)** for a sortable table of all plans (slug → title).
2. Pick a plan in [`plans/`](plans/). Work through **§4 Deliverables**, then **§5 Completion confirmation**, then **§6 Working verification**.
3. Use **§9 Version sign-off** when attaching evidence in your tracker (PR links, CI job names, run IDs).

## Regenerate plans from the checklist spine

Plans are generated for consistency and to stay aligned with the checklist. After changing [`_generate_plans.py`](_generate_plans.py):

```bash
python3 docs/versioning/_generate_plans.py
```

Then edit individual files in [`plans/`](plans/) for implementation-specific notes (the footer marks them as safe to edit in place).

## Version ID families

| Prefix | Meaning |
|--------|---------|
| `OSV-STORY-*` | Tier **2.1** end-to-end delivery story (checklist §1). |
| `OSV-LADDER-*` | V1–V7 **evidence** ladder (checklist §2). |
| `OSV-CONTRACTS-*` | Published contracts + tooling (§3). |
| `OSV-SVC-*` | Deployable services (§4). |
| `OSV-ORCH-*` | Platform orchestration beyond current CLI (§5). |
| `OSV-WORKER-*` | Deterministic worker + sandbox (§6). |
| `OSV-AGENT-*` | Agent packages / career wiring (§7). |
| `OSV-LIB-*` | Shared SDKs (§8 libraries). |
| `OSV-DATA-*` | Data plane (§8 data / §9 overlap where noted in checklist). |
| `OSV-INFRA-*` | `local-prod`, backup, storage (§9). |
| `OSV-PRODUCT-*` | UI + runbooks (§10). |
| `OSV-TEST-*` | Test pillars (§12). |
| `OSV-GOV-*` | ADRs, threat models, forensics (§13). |
| `OSV-READY-*` | Readiness + scheduled metrics (§14). |
| `OSV-EXTRACT-*` | Extraction drills + tenancy (§15). |

## Related docs

- [Company OS full delivery checklist](../architecture/company-os-full-delivery-checklist.md)
- [Architecture goal completion](../architecture/architecture-goal-completion.md)
- [Operating system folder structure (target)](../architecture/operating-system-folder-structure.md)
- [Action plan (product story)](../onboarding/action-plan.md)
