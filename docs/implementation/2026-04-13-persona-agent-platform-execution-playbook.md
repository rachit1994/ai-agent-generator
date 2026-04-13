# Execution Playbook (Any Contributor — Single Production Exit)

## What you are proving
One program, **one** production promotion, **no MVP**, **no phased product reduction**. You finish when **every** row in `docs/implementation/production-workflow-manifest.md` passes all gates on **both** `Ollama` and `vLLM`, with evidence described in `docs/implementation/2026-04-13-persona-agent-platform-delivery-process.md` and `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md`.

## Read in this order (do not skip)
1. `README.md` — stack and non-negotiables.
2. `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` — **conflict resolution, literals, and machine definitions** (read before any other implementation doc if instructions appear to disagree).
3. `docs/implementation/production-workflow-manifest.md` — **scope inventory**. If the table has **zero** data rows per that file’s rules, **stop**: finish Phase 1 inventory before claiming compiler or engine phases complete.
4. `docs/implementation/2026-04-13-persona-agent-platform-implementation-roadmap.md` — **what to build in what order** (includes M1–M4 crosswalk).
5. `docs/implementation/2026-04-13-persona-agent-platform-tech-decisions.md` — **what libraries to use by default**.
6. `docs/implementation/2026-04-13-persona-agent-platform-delivery-process.md` — **how gates and evidence work**.
7. `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md` — **numbers and promotion packet contents**.
8. `docs/superpowers/specs/2026-04-13-persona-agent-platform-design.md` — **behavioral contract** (persona steps, memory, safeguards).
9. `docs/implementation/2026-04-13-persona-agent-platform-quality-self-improvement-advancements.md` — **research techniques** tied to gates.
10. `docs/implementation/2026-04-13-persona-agent-platform-research-and-oss-integration.md` — **papers + OSS** reference.
11. `docs/implementation/2026-04-13-persona-agent-platform-risk-register.md` — **what can go wrong** and owners.
12. `docs/implementation/2026-04-13-persona-agent-platform-metrics-and-slos.md` — **SLOs** you must not break.
13. `docs/implementation/2026-04-13-persona-agent-platform-phased-checklist.md` — **optional** single-page atomic checklist in everyday English (cross-check nothing was skipped).

## Glossary (one line each)
| Term | Meaning |
|------|---------|
| **production_workflow_manifest** | Authoritative list of in-scope workflows; file: `docs/implementation/production-workflow-manifest.md`. |
| **gate packet** | Evidence bundle for a milestone or promotion: tests, traces, promptfoo, agentevals/DeepEval/RAGAS, sign-offs, manifest mapping; layout in `evidence/gate-packets/README.md` and `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` §10. |
| **ADR** | Architecture Decision Record: **required** to swap a **planned baseline** OSS dependency, add Graphiti/Mem0, or exempt Instructor for a step. Minimum fields: context, decision, consequences, owner, rollback, date. |
| **DOR** | Definition of Ready — checklist before starting work on a change (see delivery process). |
| **fail-closed** | If unsure or dependency unhealthy, **stop** unsafe paths; never “best effort” tool execution. |

## If you are stuck (escalation)
- **Schema / compiler / types:** Tech Lead.
- **Safety / policy / temporal proofs:** Safety Owner.
- **Memory / signatures / tenant:** Data/Memory DRI.
- **CI / traces / dashboards:** Observability DRI.
- **Promotion / rollback / soak:** SRE/Operations Owner.
- **Scope or priority conflict:** Engineering Manager.

## Machine prerequisites (before claiming a phase done)
- Python **3.13+**; pinned lockfile committed for app and CI.
- **Postgres** with **pgvector** reachable from dev and CI; migration path documented.
- **Ollama** and **vLLM** available for dual-backend evidence (can be separate machines if parity dimensions are recorded in tech decisions).
- CI can run **promptfoo**, **pytest + DeepEval**, and export or store **OpenTelemetry** for **agentevals**.

## Corner cases and evaluator gaps (no guessing)
| Situation | Required behavior |
|-----------|---------------------|
| **RAGAS not applicable** (no RAG-style retrieval for that test) | Gate packet includes a one-line **N/A** rationale signed by **Quality Owner**; other DeepEval tests still apply. |
| **agentevals** cannot run (incomplete traces, export failure) | Attach **documented substitute**: full re-run evaluation logs meeting the **same** pass/fail criteria, with Tech Lead note in the packet. Silent omission is a **failed** gate. |
| **promptfoo** or CI flake | Up to **3** deterministic retries per workflow per run; then **block** and file a defect—no infinite retry. |
| **Langfuse** not deployed | **Allowed.** OTel + dashboard links still required; do not block on Langfuse. |
| **Instructor** exemption for a step | Only with a **numbered ADR** listing `workflow_id` and step IDs; default remains Instructor. |
| **Graphiti / Mem0** not selected | **Default:** Postgres + pgvector + RLS only; no silent parallel memory store. |

## Definition of Done (personal checklist before you say “phase complete”)
- [ ] Acceptance bullets for the phase in the roadmap are **all** true.
- [ ] Evidence is mapped to **every** manifest row that exists at that point in time.
- [ ] No open **critical** risks in the risk register without an EM-approved waiver.
- [ ] Parity dimensions in tech decisions are updated if you changed models, suite pins, or backends.
