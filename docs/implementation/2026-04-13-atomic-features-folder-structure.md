# Atomic features folder structure

This document defines a **Python** layout: a **single root for all product behavior** (`features/`), where **each feature is one importable package**, **pytest tests live under that package’s `tests/` directory**, and **work is expressed as a shallow tree**: methods contain ordered steps; each step names the atomic features it composes.

---

## Goals

- **One place to look** for “what the system does”: `features/`.
- **Atomic features**: one folder = one user-observable or one contract-stable capability (small enough to name without “and”).
- **Colocated tests**: every automated test for a feature lives **inside that feature’s folder** (no parallel `tests/features/...` mirror tree).
- **Compact execution map**: humans and agents read one outline; the filesystem is the source of truth for boundaries.

This document is **Python-first** (importable packages, **pytest**). Wire discovery and import path to `pyproject.toml` / `pytest.ini` (for example `testpaths`, `pythonpath`) when you add code.

Non-goals: choosing packaging/build backends beyond “standard `src` or flat `features/` layout”; pin that in `pyproject.toml` when the app ships.

---

## Canonical layout (repository root)

```text
.
├── features/                          # all product behavior (atomic units)
│   ├── _shared/                       # optional: tiny helpers used by 2+ features (keep minimal)
│   │   ├── README.md                  # why something is shared; promotion rules back into a feature
│   │   └── ...
│   │
│   ├── <feature_snake_case>/          # one atomic feature = one importable package (PEP 8)
│   │   ├── __init__.py                # public surface: re-export the primary entrypoint(s)
│   │   ├── <feature_snake_case>.py    # main implementation (split modules if needed; same feature)
│   │   ├── types.py                   # optional: TypedDict, dataclasses, Protocols — feature-local only
│   │   ├── py.typed                   # optional: mark package typed if you use type hints at boundary
│   │   ├── tests/                     # ALL automated tests for this feature (required convention)
│   │   │   ├── __init__.py            # optional: empty, if you want tests as a subpackage
│   │   │   ├── conftest.py            # optional: fixtures scoped to this feature only
│   │   │   ├── test_<feature_snake_case>.py
│   │   │   └── ...
│   │   └── README.md                  # optional: invariant list + links to specs (keep short)
│   │
│   └── ...                            # more features, each sibling folder
│
├── docs/                              # design, ADRs, runbooks (this repo today)
├── scripts/                           # orchestration, codegen, CI glue (may be non-Python)
├── evidence/                          # human/CI artifacts (packets, screenshots), not unit tests
├── pyproject.toml                       # pytest, ruff/mypy, package metadata when code exists
└── README.md
```

### Rules

| Rule | Detail |
|------|--------|
| **Feature = folder** | `features/<name>/` is the boundary. No “half a feature” split across two folders. |
| **Tests = inside feature** | Only `features/<name>/tests/` (repo-wide convention; pytest discovers `test_*.py` here). |
| **No cross-feature imports in tests** | Prefer fakes/fixtures in the same `tests/` tree or `_shared/testing/` with explicit review. |
| **Naming** | **snake_case** package directories (valid Python imports, PEP 8). Public callables are **snake_case** (`run_read_yaml_config`). |
| **`_shared/`** | Exception: cross-cutting helpers **without** a product “feature” identity. If it grows a contract, **promote** it to `features/<something>/`. |

---

## Atomic feature: definition

An **atomic feature** satisfies as many of these as practical:

1. **Single sentence** — “This feature does X when Y.”
2. **Single failure owner** — when it breaks, one folder explains/fixes it.
3. **Single test suite root** — `features/<name>/tests/`.
4. **Stable public API** — `__init__.py` re-exports a small surface; keep implementation modules “private by convention” (`_impl.py`, leading underscore names) where useful.

If you cannot name it without “and”, split into two features **or** introduce a **method** (workflow) that composes them (see below).

---

## Compact execution map (methods, steps, features)

This is the **human/agent outline**. It is intentionally tiny. The filesystem under `features/` remains authoritative.

### Shape

```text
<method_name>:
  - step_one()
  - step_two()
  - step_three()

step_one():
  - feature_a()
  - feature_b()

step_two():
  - feature_c()

step_three():
  - feature_a()
  - feature_d()
```

### Meaning

| Concept | Maps to |
|---------|---------|
| **method** | End-to-end workflow or use case (e.g. `run_phase`, `deploy_release`, `handle_webhook`). Often lives in `scripts/` or a thin `methods/` package that **only composes** features. |
| **step()** | Ordered stage inside the method. **No business logic duplication**: a step module calls feature entrypoints. |
| **feature_x()** | Callable exported from `features/<feature_x>/__init__.py` (for example `from features.feature_x import run_...`) (atomic capability). |

### Example (illustrative names)

```text
cursor_phase_orchestration:
  - load_manifest()
  - validate_gate()
  - emit_evidence()

load_manifest():
  - read_yaml_config()
  - resolve_paths()

validate_gate():
  - schema_validate_gate_packet()
  - check_required_evidence()

emit_evidence():
  - write_gate_packet()
  - log_structured_summary()
```

Folder correspondence (import paths mirror names):

```text
features/read_yaml_config/
features/resolve_paths/
features/schema_validate_gate_packet/
features/check_required_evidence/
features/write_gate_packet/
features/log_structured_summary/

scripts/cursor_phase_orchestrator.py   # method: thin CLI/orchestrator (or keep a small non-Python driver if needed)
```

---

## Optional: `methods/` next to `features/`

If orchestration grows beyond scripts, add a dedicated tree **without** burying logic in features:

```text
methods/
├── cursor_phase_orchestration/
│   ├── __init__.py              # exports run() (or main entry)
│   ├── steps/
│   │   ├── load_manifest.py     # imports features.* only; no duplicated domain rules
│   │   ├── validate_gate.py
│   │   └── emit_evidence.py
│   └── tests/                   # integration: order + wiring (still colocated to this method)
│       └── test_cursor_phase_orchestration.py
```

**Contract:** `methods/*` may import many `features/*`; `features/*` must **not** import `methods/*` (avoids cycles).

---

## Test types inside a feature folder

Keep **all** of these under the same feature directory:

| Kind | Suggested path | Notes |
|------|----------------|-------|
| Unit | `features/<f>/tests/test_<f>_unit.py` | Pure, fast, hermetic; prefer one primary `test_<f>.py` if small. |
| Contract | `features/<f>/tests/test_<f>_contract.py` | IO boundaries: parsers, serializers, HTTP clients (mocked at boundary). |
| Characterization | `features/<f>/tests/test_<f>_golden.py` | Approved golden files under `tests/data/` inside the same feature folder. |

**Integration tests that span multiple features** belong under the **method** (or a `suites/integration/` folder at repo root) — not inside a single atomic feature folder — so feature folders stay honest about scope.

---

## `__init__.py` exports (per feature)

Each `features/<name>/__init__.py` should re-export:

- **One primary entry** — the callable steps invoke (e.g. `run_read_yaml_config`).
- **Types consumers need** — only if part of the public contract (`TypedDict`, `Protocol`, etc.).

Everything else stays import-private (nested modules, leading underscores) unless you intentionally widen the API.

---

## Adding a new atomic feature (checklist)

1. Pick **one sentence** for the capability.
2. Create `features/<snake_case_name>/` with `__init__.py`.
3. Add implementation module(s) (`<name>.py` or split as needed).
4. Add `tests/` with at least one `test_*.py` that would fail if the sentence is false.
5. Wire it into the relevant **step** in the compact map (and into code if applicable).
6. If two features share code, extract to `_shared/` **or** merge features if the boundary was wrong.

---

## Relation to this repository (today)

As of this document, the repo mixes **documentation** with **orchestration scripts**. For a **Python** codebase, add **`features/`** as the default home for atomic capabilities described in `docs/superpowers/specs/` and `docs/implementation/`. Orchestrators (for example under `scripts/` or `methods/`) should stay **thin**: import from `features.*` and express control flow only.

---

## Quick reference

```text
features/<atomic_feature>/       # snake_case directory = import package
  __init__.py                    # public re-exports
  <atomic_feature>.py            # implementation (+ more modules if needed)
  tests/
    test_<atomic_feature>.py     # all tests for this feature only

method outline (documentation or comments):
  method_name:
    - step_one()
    - step_two()
  step_one():
    - feature_one()
    - feature_two()
```

**pytest:** set `testpaths` to include `features` (and `methods` if used) so `tests/test_*.py` under each package is collected. Use `pythonpath = ["."]` or a `src/` layout in `pyproject.toml` so `import features.<name>` resolves consistently in CI and local runs.

This keeps the **outline compact**, the **filesystem explicit**, and **tests co-located** with the smallest shippable unit of behavior.
