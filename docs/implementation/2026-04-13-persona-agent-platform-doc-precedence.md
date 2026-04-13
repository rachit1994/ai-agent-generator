# Documentation Precedence and Zero-Gap Norms (Persona Agent Platform)

## Purpose
This file removes interpretation gaps when following **only** repository documentation for the **Persona Agent Platform** program (single production exit, full manifest, dual `Ollama` + `vLLM` evidence). Where another file disagrees, **this file wins** for the items listed in §2.

## 1) Authoritative document stack (read order for conflicts)
1. This file — **precedence, literals, and undefined terms** closed here first.
2. `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md` — promotion numerics and soak rules.
3. `docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md` — contributor order and corner cases.
4. `docs/implementation/2026-04-13-persona-agent-platform-implementation-roadmap.md` — phase order and acceptance bullets.
5. `docs/implementation/2026-04-13-persona-agent-platform-tech-decisions.md` — library defaults and parity dimensions.
6. `docs/implementation/2026-04-13-persona-agent-platform-delivery-process.md` — gates and evidence shape.
7. `docs/implementation/2026-04-13-persona-agent-platform-metrics-and-slos.md` — rolling SLOs.
8. `docs/superpowers/specs/2026-04-13-persona-agent-platform-design.md` — behavioral contract.
9. `README.md` — program summary (must stay consistent with 1–8; if not, 1–8 win).

## 2) Relationship to `docs/persona-library-full-contract.md`
- That file specifies an **embeddable Python persona library** (YAML factory, SQLite-per-tenant defaults, `Squad` / `launch` surface). It is **not** the persistence, checkpoint, or inventory authority for **this program’s production exit**.
- For **this repository’s production exit**, the **only** normative persona sources are Markdown files under `docs/personas/` and `docs/more_personas/` enumerated in `docs/implementation/production-workflow-manifest.md`, compiled by the program-defined workflow compiler (roadmap Phase 2+).
- **No merge rule is required** to ship production exit: implementers **do not** apply SQLite-default or YAML-authoring rules from the library contract to the platform stack unless an **ADR** explicitly adopts that library as a dependency and maps its storage to Postgres + `langgraph-checkpoint-postgres` per tech decisions.
- If `docs/persona-library-full-contract.md` is updated in the future, it must carry a banner pointing here; platform docs do not inherit its defaults by silence.

## 3) Persona input → `workflow_id` (single rule)
- **Source files:** every `*.md` under `docs/personas/` and `docs/more_personas/` **except** `README.md` and other index-only files listed as excluded in `production-workflow-manifest.md`.
- **`workflow_id`:** repo-relative path without `.md`, with `/` replaced by `.`, rooted at `docs` (example: `docs/personas/sales.md` → `docs.personas.sales`).
- **Compiler may emit multiple ids per file** only after an ADR and manifest update (same PR rule already in manifest doc).

## 4) `100%` manifest gate pass vs `≥99%` cross-backend parity (no contradiction)
- **Per backend, per workflow:** each workflow in the manifest must **pass** all required gates on **Ollama** and again on **vLLM** for production exit. There is **no** “1% allowed gate failure” per workflow.
- **`≥99%` gate outcome parity** (tech decisions): for each workflow, compare the **ordered list of gate outcomes** (pass/fail and reason codes) between backends on the **same pinned inputs** (replay seeds). Lists MUST have **equal length** (same gate count). If lengths differ, treat that workflow’s parity as **0** until fixed—**promotion blocked**. When lengths match, the **Hamming match rate** across the list must be **≥0.99** per workflow, then averaged over manifest rows in the evaluation window must still be **≥0.99**. Any single workflow below **0.99** **blocks** promotion until resolved or waived per release policy (non-safety only).
- **Plain language:** every workflow must pass on both backends; outcomes must **agree** on at least 99% of atomic gate checks when cross-compared. If a workflow passes both sides but disagrees on >1% of checks, treat as **parity defect**, not as permission to ship a failing workflow.

## 5) `critical` failure signatures (no-repeat contract scope)
- **`critical`** means `failure_class` in `schemas/normalized-failure-signature.schema.json` is one of: `policy_violation`, `temporal_violation`, `tool_denied` **with** a non-empty `policy_rule_id`, or `schema_reject` on a **tool argument** boundary.
- **Non-critical** signatures still go to failure memory but **do not** trigger the production **no-repeat-failure** automated proof requirement.
- The library contract’s general caution about “never wrong twice” is **compatible**: the program proves **gated recurrence handling** for **critical** signatures only, not a universal impossibility of error.

## 6) Normalized failure signature — hash and dedupe (normative)
- **Canonical JSON:** payload MUST validate against `docs/implementation/schemas/normalized-failure-signature.schema.json` with `schema_version` `1.0.0`.
- **Normalization before hash:** trim; lowercase `normalized_message`; replace UUIDs, commit SHAs, absolute paths, and decimal numerals with sentinel tokens `{{uuid}}`, `{{sha}}`, `{{path}}`, `{{num}}` using `docs/implementation/schemas/normalization-regex-table.json` **in array order** (same `schema_version` pinned in gate packet `MANIFEST.json` as `normalization_regex_table_version`).
- **Signature hash:** `SHA-256` over UTF-8 bytes of the **sorted-key** JSON object containing only `schema_version`, `workflow_id`, `failure_class`, `gate_stage`, `normalized_message`, `tool_name`, `policy_rule_id` (empty string allowed), `step_id` if present. **Exclude** `tenant_id` from the hash so the same defect shape dedupes across tenants; **store** `tenant_id` separately for isolation audits.
- **Dedupe:** one row per `signature_hash` per tenant in failure memory; `alias_of` merges human-renamed duplicates (Data/Memory DRI + Safety Owner approval log).

## 7) `agentevals` minimum bars (replaces “thresholds in gate packet” ambiguity)
When promotion or milestone evidence uses **agentevals** on exported OpenTelemetry traces (no Tech Lead substitute path), **all** of the following must hold on the **sampled runs** referenced in the packet:
- **Trace presence:** every scored run has spans for `plan`, `action`, `output` stages (names exact per `docs/implementation/schemas/otel-span-stage-registry.json` in the same commit).
- **Aggregate pass:** `mean(score) >= 0.85` across all agentevals dimensions returned by the pinned config.
- **Worst-workflow floor:** no manifest `workflow_id` may have `mean(score) < 0.75` for that workflow’s runs in the sample.
- **Version pin:** gate packet lists `agentevals` package version, scorer config hash, and OTel exporter version.

If a dimension is intentionally disabled, the packet contains **Quality Owner + Observability DRI** joint one-line rationale and the disabled dimension list; **cannot** disable more than half of dimensions.

## 8) Observability: `baseline` (Phase 6 prerequisite) vs `production_grade` (Phase 8)
**Baseline (required before high-volume stress evidence per roadmap Phase 6):**
- OTel export success **≥99%** for `plan`, `action`, `output` spans over the last **168h** rolling window in the validation environment.
- Dashboards exist with links for: gate pass rate, trace completeness, error rate, p95 latency — each chart scoped by `workflow_id`.
- At least **one** successful end-to-end trace export per manifest workflow in the **last 30 days** (may be synthetic smoke).

**Production-grade (required before Phase 10):**
- All Phase 8 acceptance bullets in the roadmap, including **replay drill** coverage per manifest workflow.
- Stress evidence from Phase 6 is **invalid** for promotion if Phase 8 replay acceptance is later regressed; re-run stress after recovery.

## 9) Dependency matrix — `safety-critical` for inference outage row
For `docs/implementation/2026-04-13-persona-agent-platform-delivery-process.md` dependency matrix: **every** `workflow_id` in the production manifest is **safety-critical** for inference routing: on `Ollama` or `vLLM` `error`/`nil`, the runtime must **either** route to the healthy backend with recorded parity dimensions **or** enter `safe_denied` (no tool execution) until health returns. **No** silent single-backend degradation without EM-written exception in the risk register.

## 10) Gate packet as a versioned artifact
- **Default path (normative):** `evidence/gate-packets/<packet_id>/` at repo root. `packet_id` = `<16-hex-of-merge-commit>_<slug>` (example: `a1b2c3d4e5f67890_phase2-compiler`).
- **Allowed alternative:** immutable CI artifact URL listing the same files, linked from `evidence/gate-packets/README.md` index row for that `packet_id`.
- **Minimum files:** `MANIFEST.json` (see `evidence/gate-packets/README.md`), plus artifacts or links for **promptfoo**, **DeepEval**, **agentevals** (or Tech Lead substitute per playbook), and OTel sample hashes.

## 11) Milestone ↔ phase map (roadmap crosswalk)
| Milestone | Phases included | Notes |
|-----------|-----------------|-------|
| M1 | 1 | Inventory, ADRs, contracts. |
| M2 | 2–4 | Compiler through safety/temporal. |
| M3 | 5–7 | Memory through inference routing. |
| M4 | 8–10 | Observability production-grade through single exit. |

## 12) README pointer fix
- Root `README.md` describes **this platform program**. The opening pointer inside `docs/persona-library-full-contract.md` is **historical**; implementers follow **this** README first, then the execution playbook.
