#!/usr/bin/env python3
"""
Orchestrates Cursor CLI (`agent`) for this repository only.

Security: subprocess uses argv list with shell=False; the prompt is a single argv
element (no interpolation of untrusted input). Prerequisite files are validated at startup.

Run: python3 scripts/cursor_phase_orchestrator.py [--first-phase-only] [--smoke] [--background]

CLI (optional, parsed before env-backed config):
- `--first-phase-only` — sets one outer round and one fix / one test pass (four `agent` calls) unless env overrides.
- `--smoke` — validates repo files and `agent --help` only; does not invoke the orchestration loop (no API key needed).
- `--background` — exit immediately after spawning a **detached** session (`start_new_session`); child logs to
  `docs/implementation/orchestrator-logs/orchestrator-daemon-<utc>.log` and writes `orchestrator-daemon.pid`. Ignored with `--smoke`.

Authentication: use `agent login` (stored session) and/or `CURSOR_API_KEY` from the Cursor dashboard.
The script runs `agent status` before the loop; if neither applies, it exits with a clear error.

Normative agent behavior: every prompt includes `docs/personas/software-engineer.md` (always-on rules, Phases 0–19)
alongside the phased checklist — checklist = **what**, persona = **how** (unless doc-precedence says otherwise).

Environment (optional):
- CURSOR_ORCHESTRATOR_APPLY_CHANGES — default "1". Set to "0" for dry-run: agent -p only
  (no --force; no applied file writes per Cursor headless docs).
- CURSOR_ORCHESTRATOR_OUTER_ROUNDS — default **0** = unlimited for **stopping** (run until `PROGRAM_COMPLETE`).
  A positive value is a **milestone label only** in prompts; the loop **keeps going** past it until `PROGRAM_COMPLETE`.
  The absolute counter still rolls over at 100000 outer rounds (log + reset) so the process never exits for “cap reached.”
- CURSOR_ORCHESTRATOR_AUTH_POLL_SEC — seconds between auth checks when waiting for `agent login` / key (default **45**).
- CURSOR_ORCHESTRATOR_CLI_POLL_SEC — seconds between `agent --help` retries when CLI is missing (default **30**).
- CURSOR_ORCHESTRATOR_AGENT_TIMEOUT_SEC — max wall seconds per `agent` invocation (**0** or unset = no limit). On timeout the child is killed, logged, and the orchestrator continues.
- CURSOR_ORCHESTRATOR_FIX_PASSES — default 3, max 15.
- CURSOR_ORCHESTRATOR_TEST_PASSES — default 3, max 15.
- CURSOR_ORCHESTRATOR_NICE — extra `nice(2)` increment for this Python process (0–39). Empty in foreground = **0**.
  In `--background` / `--background-runner` mode, empty defaults to **10** so the long loop yields CPU to interactive work.
- CURSOR_ORCHESTRATOR_AGENT_NICE — optional override for each `agent` child only; if unset, matches `CURSOR_ORCHESTRATOR_NICE`
  (including the background default).
- CURSOR_ORCHESTRATOR_STEP_COOLDOWN_SEC — non-negative float; **sleep** after each agent invocation to reduce sustained load (default **0**).
- CURSOR_ORCHESTRATOR_RLIMIT_AS_MB — optional soft/hard address-space cap in MiB (best-effort via `setrlimit(RLIMIT_AS)`;
  may be ignored on some platforms; minimum **256** if set).

Resilience: non-zero `agent` exit codes and Python errors during a step are **logged** and the orchestrator **continues**
to the next step; only **Ctrl+C** (SIGINT) or SIGTERM stops the process. Invocation transcripts go under
`docs/implementation/orchestrator-logs/`; incidents append to `docs/implementation/cursor-phase-orchestrator-issues.md`.

See: https://cursor.com/docs/cli/headless
"""

from __future__ import annotations

import math
import os
import signal
import subprocess
import sys
import time
import traceback
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path


_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent

DOCS_ROOT = REPO_ROOT / "docs"
CHECKLIST_PATH = REPO_ROOT / "docs" / "implementation" / "2026-04-13-persona-agent-platform-phased-checklist.md"
SOFTWARE_ENGINEER_PERSONA_PATH = REPO_ROOT / "docs" / "personas" / "software-engineer.md"
DOC_PRECEDENCE_PATH = REPO_ROOT / "docs" / "implementation" / "2026-04-13-persona-agent-platform-doc-precedence.md"
RELEASE_GATE_SPEC_PATH = REPO_ROOT / "docs" / "implementation" / "2026-04-13-persona-agent-platform-release-gate-spec.md"
ORCHESTRATOR_LOG_PATH = REPO_ROOT / "docs" / "implementation" / "cursor-phase-orchestrator-round-log.md"
ORCHESTRATOR_RUNS_DIR = REPO_ROOT / "docs" / "implementation" / "orchestrator-logs"
ISSUES_LOG_PATH = REPO_ROOT / "docs" / "implementation" / "cursor-phase-orchestrator-issues.md"
README_PATH = REPO_ROOT / "README.md"
MANIFEST_PATH = REPO_ROOT / "docs" / "implementation" / "production-workflow-manifest.md"
EXECUTION_PLAYBOOK_PATH = (
    REPO_ROOT / "docs" / "implementation" / "2026-04-13-persona-agent-platform-execution-playbook.md"
)

AGENT_CMD = "agent"
APPLY_FILE_CHANGES = os.environ.get("CURSOR_ORCHESTRATOR_APPLY_CHANGES", "1") != "0"
AGENT_FLAGS: tuple[str, ...] = ("-p", "--force") if APPLY_FILE_CHANGES else ("-p",)


def _read_positive_int_env(name: str, default: int, max_val: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        n = int(raw, 10)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive integer, got {raw!r}") from exc
    if n < 1:
        raise ValueError(f"{name} must be a positive integer, got {raw!r}")
    if n > max_val:
        raise ValueError(f"{name} must be <= {max_val} (refuse huge values that look like typos), got {n}")
    return n


ABSOLUTE_MAX_OUTER_ROUNDS = 100_000


def _read_outer_rounds_cap_from_env() -> int | None:
    """
    None = no numeric milestone in prompts (“session” wording only).
    Env 0 or empty/unset: None. Positive N = show “round X of N” in prompts until X exceeds N; the loop **never** stops for this cap.
    """
    raw = os.environ.get("CURSOR_ORCHESTRATOR_OUTER_ROUNDS")
    if raw is None or str(raw).strip() == "":
        return None
    try:
        n = int(str(raw).strip(), 10)
    except ValueError as exc:
        raise ValueError(f"CURSOR_ORCHESTRATOR_OUTER_ROUNDS must be integer, got {raw!r}") from exc
    if n == 0:
        return None
    if n < 0:
        raise ValueError(f"CURSOR_ORCHESTRATOR_OUTER_ROUNDS must be >= 0, got {n}")
    if n > ABSOLUTE_MAX_OUTER_ROUNDS:
        raise ValueError(
            f"CURSOR_ORCHESTRATOR_OUTER_ROUNDS must be <= {ABSOLUTE_MAX_OUTER_ROUNDS}, got {n}",
        )
    return n


MAX_OUTER_ROUNDS_CAP: int | None = _read_outer_rounds_cap_from_env()
FIX_PASSES = _read_positive_int_env("CURSOR_ORCHESTRATOR_FIX_PASSES", 3, 15)
TEST_PASSES = _read_positive_int_env("CURSOR_ORCHESTRATOR_TEST_PASSES", 3, 15)
MAX_CHECKLIST_STEPS_PER_BUILD_PASS = 8
MAX_PROMPT_BYTES = 240 * 1024
STEPS_PER_ROUND = 1 + FIX_PASSES + TEST_PASSES + 1

_active_agent_child: subprocess.Popen | None = None
_ADVISORY_OUTER_CAP_LOGGED = False

_SMOKE_MODE = False
_FIRST_PHASE_ONLY = False
_BACKGROUND_RUNNER = False


def apply_cli_flags_and_reload_cycle_config() -> None:
    """Parse argv once per process (main only). Sets env for --first-phase-only, then reloads cycle counters."""
    global MAX_OUTER_ROUNDS_CAP, FIX_PASSES, TEST_PASSES, STEPS_PER_ROUND
    global _SMOKE_MODE, _FIRST_PHASE_ONLY, _BACKGROUND_RUNNER
    _BACKGROUND_RUNNER = "--background-runner" in sys.argv
    while "--background-runner" in sys.argv:
        sys.argv.remove("--background-runner")
    _SMOKE_MODE = "--smoke" in sys.argv
    _FIRST_PHASE_ONLY = "--first-phase-only" in sys.argv
    if _FIRST_PHASE_ONLY:
        os.environ.setdefault("CURSOR_ORCHESTRATOR_OUTER_ROUNDS", "1")
        os.environ.setdefault("CURSOR_ORCHESTRATOR_FIX_PASSES", "1")
        os.environ.setdefault("CURSOR_ORCHESTRATOR_TEST_PASSES", "1")
    for flag in ("--smoke", "--first-phase-only"):
        while flag in sys.argv:
            sys.argv.remove(flag)
    MAX_OUTER_ROUNDS_CAP = _read_outer_rounds_cap_from_env()
    FIX_PASSES = _read_positive_int_env("CURSOR_ORCHESTRATOR_FIX_PASSES", 3, 15)
    TEST_PASSES = _read_positive_int_env("CURSOR_ORCHESTRATOR_TEST_PASSES", 3, 15)
    STEPS_PER_ROUND = 1 + FIX_PASSES + TEST_PASSES + 1
    _assert_positive_config()


def _assert_positive_config() -> None:
    if FIX_PASSES < 1 or TEST_PASSES < 1 or MAX_CHECKLIST_STEPS_PER_BUILD_PASS < 1:
        raise RuntimeError("Orchestrator numeric config must be positive")


_assert_positive_config()


def _outer_round_line(outer_index: int) -> str:
    cap = MAX_OUTER_ROUNDS_CAP
    if cap is None or outer_index > cap:
        return (
            f"- **Orchestrator session round:** {outer_index} "
            f"(runs until a build pass prints exactly `PROGRAM_COMPLETE` on its own line; "
            f"outer index rolls over after {ABSOLUTE_MAX_OUTER_ROUNDS} rounds; stop manually with Ctrl+C)"
        )
    return f"- **Orchestrator outer round:** {outer_index} of {cap} (milestone label; loop continues until `PROGRAM_COMPLETE`)"


def build_orchestration_context_block(outer_index: int) -> str:
    if not isinstance(outer_index, int) or outer_index < 1 or outer_index > ABSOLUTE_MAX_OUTER_ROUNDS:
        raise ValueError(f"outer_index must be integer in [1, {ABSOLUTE_MAX_OUTER_ROUNDS}], got {outer_index!r}")
    return f"""## Where you are working

- **Repository root:** {REPO_ROOT}
- **Program documentation root (read entire tree for context):** {DOCS_ROOT}
- **Phased checklist (normative task list — follow to the letter):** {CHECKLIST_PATH}
- **Software engineer persona (lifecycle steps, gates, artifacts — follow every pass):** {SOFTWARE_ENGINEER_PERSONA_PATH}
- **Doc precedence (conflicts — checklist intro + §1 stack):** {DOC_PRECEDENCE_PATH}
- **Release gate spec (precedence #2 after doc-precedence):** {RELEASE_GATE_SPEC_PATH}
- **Program summary:** {README_PATH}
- **Production workflow manifest (inventory / `workflow_id` authority for this program):** {MANIFEST_PATH}
- **Execution playbook (contributor order, corner cases):** {EXECUTION_PLAYBOOK_PATH}
{_outer_round_line(outer_index)}

## Role

You implement or verify **this repository only**, against the phased checklist **and** the execution model in **{SOFTWARE_ENGINEER_PERSONA_PATH}** (always-on rules; Phases 0–19 with gates and artifacts; senior loop). Prefer **evidence over narrative**: every “done” or “pass” claim needs a **machine-checkable pointer** (file path + section, command you ran, test name, CI link, or artifact path). Human-only gates are **not** done until named roles produce artifacts — use **BLOCKED**.

## Anti-garbage rules (hard)

- **No speculative stack:** Do not add dependencies, services, frameworks, or repo layout churn unless a **checklist step you are executing** explicitly requires it.
- **No drive-by refactors:** Touch **only** files needed for the steps you list; do not “clean up” unrelated modules.
- **No inventing scope:** If the checklist does not ask for it, do not build it “because it is best practice.”
- **No fake evidence:** Do not claim commands ran or tests passed without actually running them in this environment when the task requires execution.

## Global behavior

1. **Load context without context collapse:** Default to {CHECKLIST_PATH} and **{SOFTWARE_ENGINEER_PERSONA_PATH}** plus **only** files your task names or your evidence references. **Exception — full-tree read:** when the **task** below tells you to load all of {DOCS_ROOT}, do that **once** for that invocation, then work narrowly. On later passes the same outer round, **incremental** reads only unless you hit a contradiction.
2. **Bounded batches:** A single invocation does **not** implement a whole phase unless every item is trivial documentation. The **build** task caps substantive checklist items per pass (see **NEXT_STEPS** cap there). Finish the program across **many** orchestrator invocations.
3. **What vs how:** Use {CHECKLIST_PATH} for **which** program phases and numbered steps to execute (order, exit checks, appendices). Use {SOFTWARE_ENGINEER_PERSONA_PATH} for **how** to work (memory first, clarification gate, evidence, tenancy/path jail, validators/reviewer gates; Phases 0–19 when they apply to the slice). If persona and checklist conflict, follow **{DOC_PRECEDENCE_PATH}** then checklist; never skip checklist work by citing persona alone.
4. **Conflicts:** If two docs disagree, resolve per the checklist intro: **{DOC_PRECEDENCE_PATH}** first, then **{RELEASE_GATE_SPEC_PATH}**, then the rest. Never use “precedence” to **skip** checklist work — either implement, prove N/A with checklist-allowed sign-off, or **BLOCKED**.
5. **Repo truth:** Re-read files from disk; do not rely on chat memory for checklist text, manifest rows, or schemas.
6. **Conventions:** Match this repo’s formatting, test runner, and layout; keep diffs small and reviewable.
7. **BLOCKED** (human-only or unreachable gates — one line each, own line):
   `BLOCKED | <phase + step or exit id> | <reason> | <named role + action>`
8. **Scope:** Obey the **current task section** below; do not open the **next** program phase unless that task tells you to."""


def prompt_build_next_phase(context_block: str) -> str:
    return f"""{context_block}

## Task: implement the **next** incomplete phase (build pass)

### Required opening (before edits)

Output this block first (fill in):

```text
PHASE_FOCUS: Phase <n> — <one-line title from checklist>
EXIT_CHECK: <verbatim or tight paraphrase of that phase’s exit check>
NEXT_STEPS: <checklist numbers you will execute this pass, e.g. “Phase 3 — steps 4–7”> (cap: **≤ {MAX_CHECKLIST_STEPS_PER_BUILD_PASS}** substantive steps; split across rounds if larger)
PERSONA_TRACE: <persona phase numbers 0–19 you are applying this pass + one clause each mapping to checklist work>
EVIDENCE_GAP: <one sentence: what is missing in repo vs exit check>
```

### What to do

0. **Full documentation load (this pass only):** recursively read **every** file under {DOCS_ROOT}, then {README_PATH}, then {CHECKLIST_PATH}, then **{SOFTWARE_ENGINEER_PERSONA_PATH}** (even if already under `docs/`, re-anchor on this file). This is the **one** expensive tree read for this outer round’s build pass.
1. Pick **the first phase** in document order whose **exit check** is **not** fully satisfied **with evidence** in the repo (artifacts, tests, docs, manifest rows, ADRs — as the checklist demands for that phase).
2. List **NEXT_STEPS** as **at most {MAX_CHECKLIST_STEPS_PER_BUILD_PASS}** substantive numbered checklist items you will complete **in this invocation** (lowest numbers first). Documentation-only steps may be grouped, but do **not** exceed the cap with large code items — split across orchestrator rounds instead.
3. Execute **only** those listed steps **in ascending order**, **to the letter** (sub-bullets count; “All phases” / appendix rules apply when relevant). Do **not** execute later steps in the same phase that you omitted from **NEXT_STEPS**. Honor **{SOFTWARE_ENGINEER_PERSONA_PATH}** always-on rules and the **gates/artifacts** for every persona phase you listed in **PERSONA_TRACE** (smallest sufficient scope; **BLOCKED** if a gate needs a human owner).
4. For each step you complete, leave an **evidence trail** (path, command, or doc section) you could paste into a gate packet; avoid “trust me” summaries.
5. Keep edits **minimal and local**; run the **narrowest** lint/tests the repo defines after substantive code changes.
6. If more steps remain in the phase after this pass: end with **Resume next:** and a comma-separated list of **remaining checklist numbers** (same phase only).

### Stop conditions

- **PROGRAM_COMPLETE:** If **every** phase through Phase 10 (including cross-phase discipline where it is exit criteria) is satisfied with evidence, output a line **exactly** `PROGRAM_COMPLETE` and follow with a **10-line max** bullet list of **primary evidence paths** (no new scope).
- Human gates: **BLOCKED** lines + continue **machine-doable** work only; never mark a human gate “done.”"""


def prompt_fix_remainder(context_block: str, fix_round: int) -> str:
    if not isinstance(fix_round, int) or fix_round < 1 or fix_round > FIX_PASSES:
        raise ValueError(f"fix_round must be integer in [1, {FIX_PASSES}], got {fix_round!r}")
    return f"""{context_block}

## Task: gap analysis and fixes (**remediation pass {fix_round} of {FIX_PASSES}**)

### Anchor

State **CURRENT_PHASE:** (name/number) — same phase as this outer round’s build pass (or the phase you have been closing). If ambiguous, prefer the **lowest** phase number that still has open machine work.

### What to do

1. Refresh: read {CHECKLIST_PATH}, **{SOFTWARE_ENGINEER_PERSONA_PATH}**, and paths your table cites; re-read {DOCS_ROOT} **only** if you must reconcile a contradiction — **do not** reload the entire tree by default (prevents shallow fixes after context overflow).
2. Build a **markdown table** (minimum rows: **exit check** for CURRENT_PHASE, plus **each** open numbered step you still own). Columns: **Ref** (e.g. “P3 § exit”, “P3 step 8”) | **Status** (done / partial / open) | **Evidence** (path, test, command — or `none`) | **Gap** (one short clause).
3. Triage order: **failing build or tests** → **checklist mismatch in behavior or artifacts** → **missing docs, manifest, schemas, ADR** → **polish only**.
4. Implement **only** fixes for CURRENT_PHASE. **Do not** start the **next** phase’s greenfield features here.
5. After any code change: list **Files touched:** as bullets; run the **smallest** proving commands (lint/unit) available in the repo.
6. If **no** row has Status `open` **and** no machine-actionable **Gap** remains for CURRENT_PHASE: print one line **NO_MACHINE_WORK** exactly, then one sentence naming the exit-check row; **do not** edit unrelated files.

### Anti-patterns

- Do not output **NO_MACHINE_WORK** while any row shows **open** or Evidence `none` for a required checklist item.
- Do not “fix” the next phase because it feels more interesting."""


def prompt_verify_with_tests(context_block: str, test_round: int) -> str:
    if not isinstance(test_round, int) or test_round < 1 or test_round > TEST_PASSES:
        raise ValueError(f"test_round must be integer in [1, {TEST_PASSES}], got {test_round!r}")
    if test_round == 1:
        coverage_gap_step = (
            "4. **Coverage gap:** If the exit check has **no** automated proof in this repo, add the **smallest** "
            "hermetic test or script hook that would fail on regression; no skipped tests; avoid real network and "
            "non-deterministic clocks unless already repo-standard."
        )
    else:
        coverage_gap_step = (
            f"4. **Coverage gap:** This is pass **{test_round}** — do **not** add new test **files** or parallel suites "
            "unless **verify_tests_1** this round documented a **still-open** gap; otherwise only **run** commands "
            "and fix failures."
        )
    return f"""{context_block}

## Task: prove the phase with **automated tests** (**verification pass {test_round} of {TEST_PASSES}**)

### What to do

1. State **VERIFY_PHASE:** (name/number) and quote or tightly paraphrase that phase’s **exit check** from {CHECKLIST_PATH}. Align proof depth with **{SOFTWARE_ENGINEER_PERSONA_PATH}** (e.g. Phase 5 implementation gates, Phase 6–7 review/testing expectations) where they exceed checklist wording — still **BLOCKED** instead of fake green.
2. **Discover commands** from {README_PATH}, `package.json`, `pyproject.toml`, `Makefile`, or `.github/workflows/*` — list the **exact** shell commands you **will** run (copy-pasteable, cwd noted).
3. **Execute** every listed command from **{REPO_ROOT}** (or documented subdir). Record **PASS/FAIL** each. On FAIL: capture **one** minimal locator (test name + file:line or stderr head ≤20 lines), fix root cause, re-run the **same** command list until green or **BLOCKED** (environment/service you cannot fix here).
{coverage_gap_step}
5. **Flakes:** Follow phased checklist “flakes” rule: **≤3** deterministic retries per workflow/command per run; then **stop** and treat as defect (do not infinite-retry).
6. If this phase requires **manifest-wide** or **dual-backend** evidence you cannot run locally, **BLOCKED** each missing class with owner role — do not fake green.
7. **Stability:** Re-running the **same** command list after fixes must converge; if the same failure repeats after a reasonable fix attempt, **BLOCKED** with “needs human / infra” instead of random edits.

### Output (exact tail sections)

Close with:

```text
### Commands run
- <cwd> <command> → PASS|FAIL
...

### Verification summary
EXIT_CHECK: <which>
RESULT: PASS | FAIL | BLOCKED
MAPPING: <how each exit bullet is proven — test id / command / artifact path>
```"""


def _document_round_heading_slug(outer_index: int) -> str:
    cap = MAX_OUTER_ROUNDS_CAP
    if cap is None or outer_index > cap:
        return f"outer_round_{outer_index}_session"
    return f"outer_round_{outer_index}_of_{cap}"


def prompt_document_phase(context_block: str, outer_index: int) -> str:
    slug = _document_round_heading_slug(outer_index)
    cap = MAX_OUTER_ROUNDS_CAP
    if cap is None or outer_index >= cap:
        carryover_suffix = f" at the start of session round {outer_index + 1}"
    else:
        carryover_suffix = f" at the start of outer round {outer_index + 1}"
    return f"""{context_block}

## Task: document this outer round (**phase documentation pass**)

### What to do

1. **Append only** to {ORCHESTRATOR_LOG_PATH} (create with a single `#` title line if missing). New section heading format:
   `## {slug} — <UTC ISO-8601 date> — cursor-phase-orchestrator`
   Use real UTC clock (e.g. `2026-04-13T22:15:00Z`).
2. Under that heading, in **this order**, use `###` subheadings:
   - **Phase focus:** phase number(s) + one line each on intent.
   - **Completed:** bullets of **observable** outcomes (file paths, PRs, behaviors); **no** vague adjectives.
   - **Commands / tests:** bullets of commands run this round with **PASS|FAIL** (or **n/a** if none).
   - **Goal status:** one token **MET** | **PARTIAL** | **NOT_MET** for the active phase’s **exit check**, plus **Evidence:** sub-bullets (paths, test names, § refs).
   - **BLOCKED:** paste every **BLOCKED** line from this round, or the word **None**.
   - **Carryover:** what the **next** orchestrator invocation should do first (normally **build_next_phase**{carryover_suffix}) — include **checklist numbers**.
   - **Persona:** one line: which **{SOFTWARE_ENGINEER_PERSONA_PATH}** phase numbers (0–19) advanced with new evidence this round (or **None**).
3. Keywords for grep: `PHASE`, `PASS`, `FAIL`, `BLOCKED`, `MET`, `NOT_MET`, `{CHECKLIST_PATH}`, `software-engineer`.

### Do not

- Edit {CHECKLIST_PATH} from this task unless the build/fix passes explicitly changed it.
- Truncate, deduplicate, or “pretty reformat” the log — **append new content at end of file only** so history stays auditable.
- Invent round outcomes you did not observe in this outer round’s steps."""


def assert_readable_file(absolute_path: Path, label: str) -> None:
    if not absolute_path.is_file():
        raise FileNotFoundError(f"{label} not found or not a regular file: {absolute_path}")
    if not os.access(absolute_path, os.R_OK):
        raise PermissionError(f"{label} is not readable: {absolute_path}")


def assert_repo_preconditions() -> None:
    if not REPO_ROOT.is_dir():
        raise FileNotFoundError(f"Repository root is not a directory: {REPO_ROOT}")
    if not DOCS_ROOT.is_dir():
        raise FileNotFoundError(f"docs/ directory missing or not a directory: {DOCS_ROOT}")
    assert_readable_file(CHECKLIST_PATH, "Phased checklist")
    assert_readable_file(SOFTWARE_ENGINEER_PERSONA_PATH, "Software engineer persona")
    assert_readable_file(DOC_PRECEDENCE_PATH, "Doc precedence")
    assert_readable_file(RELEASE_GATE_SPEC_PATH, "Release gate spec")
    assert_readable_file(README_PATH, "README")
    assert_readable_file(MANIFEST_PATH, "Production workflow manifest")
    assert_readable_file(EXECUTION_PLAYBOOK_PATH, "Execution playbook")
    log_dir = ORCHESTRATOR_LOG_PATH.parent
    if not log_dir.is_dir():
        raise FileNotFoundError(
            f"Orchestrator log directory missing (create docs/implementation first): {log_dir}"
        )
    ORCHESTRATOR_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    if not ISSUES_LOG_PATH.exists():
        ISSUES_LOG_PATH.write_text(
            "# Orchestrator issues and non-fatal failures\n\n"
            "Append-only log written when `agent` exits non-zero, prompts fail, or uncaught errors occur.\n\n",
            encoding="utf-8",
        )


def utc_stamp_compact() -> str:
    """Microseconds reduce filename collisions when invocations run back-to-back."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")


def _clamp_nice_delta(delta: int) -> int:
    if delta < 0:
        return 0
    if delta > 39:
        return 39
    return delta


def orchestrator_nice_increment() -> int:
    """Extra nice(2) priority for this process (higher = lower scheduling priority on Unix)."""
    raw = os.environ.get("CURSOR_ORCHESTRATOR_NICE", "").strip()
    if raw == "":
        default = 10 if _BACKGROUND_RUNNER else 0
        return _clamp_nice_delta(default)
    try:
        return _clamp_nice_delta(int(raw, 10))
    except ValueError:
        return 0


def agent_nice_increment() -> int:
    raw = os.environ.get("CURSOR_ORCHESTRATOR_AGENT_NICE", "").strip()
    if raw != "":
        try:
            return _clamp_nice_delta(int(raw, 10))
        except ValueError:
            return orchestrator_nice_increment()
    return orchestrator_nice_increment()


def apply_orchestrator_nice_from_env() -> None:
    inc = orchestrator_nice_increment()
    if inc <= 0:
        return
    try:
        os.nice(inc)
    except OSError as exc:
        append_issues_markdown(
            "ORCHESTRATOR_NICE_FAILED",
            f"Could not raise nice by {inc}: {exc}\n",
        )


def redirect_stdio_to_daemon_log() -> None:
    """Append-only line-buffered log so detached runs stay auditable without a TTY."""
    raw = os.environ.get("CURSOR_ORCHESTRATOR_DAEMON_LOG", "").strip()
    if not raw:
        raise RuntimeError("CURSOR_ORCHESTRATOR_DAEMON_LOG is required for --background-runner")
    path = Path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    log_f = path.open("a", encoding="utf-8", buffering=1)
    sys.stdout = log_f
    sys.stderr = log_f
    try:
        log_f.reconfigure(line_buffering=True)
    except (AttributeError, OSError, ValueError):
        pass


def maybe_apply_address_space_limit_from_env() -> None:
    """Best-effort virtual memory cap for this Python process (platform-dependent)."""
    raw = os.environ.get("CURSOR_ORCHESTRATOR_RLIMIT_AS_MB", "").strip()
    if not raw:
        return
    try:
        import resource
    except ImportError:
        append_issues_markdown("RLIMIT_AS_SKIPPED", "`resource` module unavailable on this platform.\n")
        return
    try:
        mb = int(raw, 10)
    except ValueError:
        append_issues_markdown("RLIMIT_AS_BAD_ENV", f"CURSOR_ORCHESTRATOR_RLIMIT_AS_MB must be integer, got {raw!r}\n")
        return
    if mb < 256:
        append_issues_markdown(
            "RLIMIT_AS_REFUSED",
            f"CURSOR_ORCHESTRATOR_RLIMIT_AS_MB={mb} below minimum 256 MiB; not applied.\n",
        )
        return
    limit = mb * 1024 * 1024
    try:
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    except OSError as exc:
        append_issues_markdown(
            "RLIMIT_AS_FAILED",
            f"setrlimit(RLIMIT_AS) not applied: {exc}\n",
        )


def _read_step_cooldown_seconds() -> float:
    raw = os.environ.get("CURSOR_ORCHESTRATOR_STEP_COOLDOWN_SEC", "").strip()
    if raw == "":
        return 0.0
    try:
        sec = float(raw)
    except ValueError:
        return 0.0
    if sec < 0.0 or not math.isfinite(sec):
        return 0.0
    if sec > 3600.0:
        return 3600.0
    return sec


def _step_cooldown_if_configured() -> None:
    sec = _read_step_cooldown_seconds()
    if sec > 0.0:
        time.sleep(sec)


def _make_agent_child_preexec_nice(increment: int) -> Callable[[], None]:
    def _lower_agent_priority() -> None:
        try:
            os.nice(increment)
        except OSError:
            pass

    return _lower_agent_priority


def try_spawn_background_detached_parent() -> bool:
    """
    If argv contains --background, spawn a child in a new session with stdout/stderr to a log file.
    Parent prints pid + paths and exits 0. Child is started with --background-runner.
    """
    argv = sys.argv[1:]
    if "--background-runner" in argv:
        return False
    if "--background" not in argv:
        return False
    if "--smoke" in argv:
        sys.stderr.write("--background is ignored with --smoke (foreground preflight only).\n")
        while "--background" in sys.argv:
            sys.argv.remove("--background")
        return False

    script = Path(__file__).resolve()
    repo = str(REPO_ROOT)
    ORCHESTRATOR_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = ORCHESTRATOR_RUNS_DIR / f"orchestrator-daemon-{utc_stamp_compact()}.log"
    child_env = os.environ.copy()
    child_env["CURSOR_ORCHESTRATOR_DAEMON_LOG"] = str(log_path.resolve())
    # So daemon log lines appear promptly under `tail -f` (no inherited block buffering).
    child_env.setdefault("PYTHONUNBUFFERED", "1")

    args: list[str] = [sys.executable, str(script)]
    for a in sys.argv[1:]:
        if a == "--background":
            continue
        args.append(a)
    args.append("--background-runner")

    log_f = log_path.open("a", encoding="utf-8", buffering=1)
    try:
        proc = subprocess.Popen(
            args,
            cwd=repo,
            env=child_env,
            stdin=subprocess.DEVNULL,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except OSError as exc:
        log_f.close()
        sys.stderr.write(f"Failed to spawn detached orchestrator: {exc}\n")
        sys.stderr.flush()
        raise SystemExit(1) from exc
    log_f.close()

    pid_path = ORCHESTRATOR_RUNS_DIR / "orchestrator-daemon.pid"
    pid_path.write_text(f"{proc.pid}\n{log_path.resolve()}\n", encoding="utf-8")
    out = getattr(sys, "__stdout__", sys.stdout)
    out.write(
        "Detached orchestrator started.\n"
        f"  pid={proc.pid}\n"
        f"  log={log_path.resolve()}\n"
        f"  pid_file={pid_path.resolve()}\n"
        "Stop with: kill <pid> (SIGTERM) or kill -INT <pid> (same as Ctrl+C in foreground).\n",
    )
    out.flush()
    return True


def append_issues_markdown(title: str, detail: str) -> None:
    """Append a section so failures are auditable even when the orchestrator keeps running."""
    try:
        ISSUES_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not ISSUES_LOG_PATH.exists():
            ISSUES_LOG_PATH.write_text(
                "# Orchestrator issues and non-fatal failures\n\n",
                encoding="utf-8",
            )
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        block = f"\n## {stamp} — {title}\n\n{detail.rstrip()}\n\n---\n"
        with open(ISSUES_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(block)
    except OSError as exc:
        sys.stderr.write(f"Warning: could not append issues log: {exc}\n")
        sys.stderr.flush()


def output_declares_program_complete(agent_text: str) -> bool:
    """Match the phased checklist: a single line exactly `PROGRAM_COMPLETE`."""
    for line in agent_text.splitlines():
        if line.strip() == "PROGRAM_COMPLETE":
            return True
    return False


def _read_cli_poll_sec() -> float:
    raw = os.environ.get("CURSOR_ORCHESTRATOR_CLI_POLL_SEC", "").strip()
    if raw == "":
        return 30.0
    try:
        sec = float(raw)
    except ValueError:
        return 30.0
    if sec < 5.0 or not math.isfinite(sec):
        return 5.0
    return min(sec, 3600.0)


def _read_auth_poll_sec() -> float:
    raw = os.environ.get("CURSOR_ORCHESTRATOR_AUTH_POLL_SEC", "").strip()
    if raw == "":
        return 45.0
    try:
        sec = float(raw)
    except ValueError:
        return 45.0
    if sec < 10.0 or not math.isfinite(sec):
        return 10.0
    return min(sec, 3600.0)


def _read_optional_agent_timeout_sec() -> float | None:
    raw = os.environ.get("CURSOR_ORCHESTRATOR_AGENT_TIMEOUT_SEC", "").strip()
    if raw == "" or raw == "0":
        return None
    try:
        sec = float(raw)
    except ValueError:
        return None
    if sec <= 0.0 or not math.isfinite(sec):
        return None
    return min(sec, 7 * 24 * 3600.0)


def _try_run_agent_help_subprocess() -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            [AGENT_CMD, "--help"],
            cwd=REPO_ROOT,
            encoding="utf-8",
            timeout=20,
            shell=False,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None


def _agent_help_output_usable(result: subprocess.CompletedProcess[str]) -> bool:
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    return result.returncode == 0 or bool(out or err)


def _emit_cli_wait_retry(detail: str, issues_title: str, attempt: int, poll: float) -> None:
    if attempt == 1 or attempt % 5 == 0:
        append_issues_markdown(issues_title, detail + "\n")
    sys.stderr.write(f"\n{detail}\nSleeping {poll:.0f}s (Ctrl+C to abort).\n")
    sys.stderr.flush()
    time.sleep(poll)


def wait_until_agent_cli_resolvable() -> None:
    """Poll until `agent --help` works — avoids exiting when PATH or install finishes slightly later."""
    poll = _read_cli_poll_sec()
    attempt = 0
    while True:
        attempt += 1
        result = _try_run_agent_help_subprocess()
        if result is None:
            detail = (
                f"Attempt {attempt}: `{AGENT_CMD}` not on PATH. "
                "Install Cursor CLI: https://cursor.com/docs/cli/installation — orchestrator will retry."
            )
            _emit_cli_wait_retry(detail, "CLI_WAITING_FILE_NOT_FOUND", attempt, poll)
            continue
        if _agent_help_output_usable(result):
            return
        detail = (
            f"Attempt {attempt}: `{AGENT_CMD} --help` returned {result.returncode} with no usable output; retrying."
        )
        _emit_cli_wait_retry(detail, "CLI_WAITING_BAD_HELP", attempt, poll)


def agent_cli_reports_logged_in() -> bool:
    """True when `agent login` has stored a session (no CURSOR_API_KEY needed for local runs)."""
    try:
        result = subprocess.run(
            [AGENT_CMD, "status"],
            cwd=REPO_ROOT,
            encoding="utf-8",
            timeout=45,
            shell=False,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    if result.returncode != 0:
        return False
    combined = (result.stdout or "") + (result.stderr or "")
    lower = combined.lower()
    return "logged in" in lower and "@" in combined


def wait_until_agent_authenticated_for_apply() -> None:
    """Poll until API key or `agent login` session exists — no manual restart after `agent login`."""
    if not APPLY_FILE_CHANGES or _SMOKE_MODE:
        return
    poll = _read_auth_poll_sec()
    attempt = 0
    while True:
        attempt += 1
        if os.environ.get("CURSOR_API_KEY"):
            return
        if agent_cli_reports_logged_in():
            return
        detail = (
            f"Attempt {attempt}: not authenticated (no CURSOR_API_KEY; `agent status` not logged in). "
            "Set CURSOR_API_KEY or run `agent login` — see https://cursor.com/docs/cli/reference/authentication — "
            "orchestrator will retry without exiting."
        )
        if attempt == 1 or attempt % 10 == 0:
            append_issues_markdown("AUTH_WAITING", detail + "\n")
        sys.stderr.write(f"\n{detail}\nSleeping {poll:.0f}s (Ctrl+C to abort).\n")
        sys.stderr.flush()
        time.sleep(poll)


def _forward_signal_to_agent(signum: int, _frame: object | None) -> None:
    global _active_agent_child
    proc = _active_agent_child
    if proc is not None and proc.poll() is None:
        try:
            proc.send_signal(signum)
        except ProcessLookupError:
            pass


def _on_signal_exit(signum: int, frame: object | None) -> None:
    _forward_signal_to_agent(signum, frame)
    raise SystemExit(130 if signum == signal.SIGINT else 143)


def install_signal_handlers() -> None:
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _on_signal_exit)


def _write_agent_transcript(transcript_path: Path, label: str, code: int, text: str) -> None:
    header = f"# invocation: {label}\n# exit_code: {code}\n\n"
    try:
        transcript_path.write_text(header + text, encoding="utf-8")
    except OSError as exc:
        append_issues_markdown(f"TRANSCRIPT_WRITE_FAILED | {label}", f"{exc}\n\n```\n{text[:4000]}\n```")


def _communicate_agent_process(
    proc: subprocess.Popen,
    label: str,
    timeout_sec: float | None,
) -> tuple[int, bytes]:
    try:
        if timeout_sec is not None:
            raw_out, _ = proc.communicate(timeout=timeout_sec)
        else:
            raw_out, _ = proc.communicate()
    except subprocess.TimeoutExpired:
        append_issues_markdown(
            f"AGENT_TIMEOUT | {label}",
            f"Exceeded CURSOR_ORCHESTRATOR_AGENT_TIMEOUT_SEC={timeout_sec}; child killed.\n",
        )
        try:
            proc.kill()
        except OSError:
            pass
        try:
            raw_out, _ = proc.communicate(timeout=45)
        except (OSError, subprocess.TimeoutExpired):
            raw_out = b""
        prefix = f"[orchestrator] agent timed out after {timeout_sec}s wall clock\n\n".encode("utf-8")
        return 124, prefix + (raw_out or b"")
    code = 1 if proc.returncode is None else int(proc.returncode)
    return code, raw_out or b""


def run_agent_capture(label: str, prompt: str) -> tuple[int, str]:
    """
    Run `agent`, capture combined stdout/stderr for PROGRAM_COMPLETE detection and issue logs.
    Also writes a per-invocation transcript under orchestrator-logs/.
    """
    encoded = prompt.encode("utf-8")
    byte_len = len(encoded)
    if byte_len > MAX_PROMPT_BYTES:
        raise ValueError(
            f"Prompt for {label} exceeds MAX_PROMPT_BYTES ({byte_len} > {MAX_PROMPT_BYTES}); "
            "shorten prompts or raise cap deliberately."
        )
    global _active_agent_child
    safe = "".join(c if c.isalnum() or c in "-._" else "_" for c in label)[:120]
    transcript_path = ORCHESTRATOR_RUNS_DIR / f"{utc_stamp_compact()}_{safe}.txt"
    agent_nice = agent_nice_increment()
    preexec: Callable[[], None] | None = None
    if sys.platform != "win32" and agent_nice > 0:
        preexec = _make_agent_child_preexec_nice(agent_nice)
    proc = subprocess.Popen(
        [AGENT_CMD, *AGENT_FLAGS, prompt],
        cwd=str(REPO_ROOT),
        shell=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=os.environ.copy(),
        preexec_fn=preexec,
    )
    timeout_sec = _read_optional_agent_timeout_sec()
    _active_agent_child = proc
    try:
        code, raw_b = _communicate_agent_process(proc, label, timeout_sec)
    finally:
        _active_agent_child = None
    text = raw_b.decode("utf-8", errors="replace")
    _write_agent_transcript(transcript_path, label, code, text)
    return code, text


def build_steps_for_outer_round(outer_index: int) -> list[tuple[str, str]]:
    context = build_orchestration_context_block(outer_index)
    steps: list[tuple[str, str]] = [("build_next_phase", prompt_build_next_phase(context))]
    for r in range(1, FIX_PASSES + 1):
        steps.append((f"fix_remainder_{r}", prompt_fix_remainder(context, r)))
    for r in range(1, TEST_PASSES + 1):
        steps.append((f"verify_tests_{r}", prompt_verify_with_tests(context, r)))
    steps.append(("document_phase", prompt_document_phase(context, outer_index)))
    return steps


def _invoke_agent_step(invocation_count: int, outer: int, label: str, prompt: str) -> bool:
    """Run one agent step. Returns True if this step was build_next_phase and output declares PROGRAM_COMPLETE."""
    tag = f"{outer}/{label}"
    sys.stdout.write(
        f"\n--- starting agent: invocation {invocation_count} {tag} (repo={REPO_ROOT}) ---\n",
    )
    sys.stdout.flush()
    try:
        code, agent_text = run_agent_capture(tag, prompt)
    except Exception as exc:
        tb = traceback.format_exc()
        append_issues_markdown(
            f"ORCHESTRATOR_EXCEPTION | {tag}",
            f"**{type(exc).__name__}:** {exc}\n\n```\n{tb}\n```",
        )
        sys.stderr.write(f"\nOrchestrator: exception during {tag} (logged); continuing.\n{tb}\n")
        sys.stderr.flush()
        code = -1
        agent_text = str(exc)

    if code != 0:
        tail = agent_text if len(agent_text) <= 12000 else f"{agent_text[:6000]}\n…\n{agent_text[-4000:]}"
        append_issues_markdown(
            f"AGENT_NONZERO_EXIT | {tag} | exit_code={code}",
            f"Transcript file should exist under `{ORCHESTRATOR_RUNS_DIR}` for this timestamp.\n\n```\n{tail}\n```",
        )
        sys.stderr.write(
            f"\nOrchestrator: agent exited with code {code} ({tag}); logged to issues file; continuing.\n",
        )
        sys.stderr.flush()

    sys.stdout.write(f"\n========== invocation {invocation_count} {tag} exit={code} ==========\n")
    sys.stdout.write(agent_text)
    if not agent_text.endswith("\n"):
        sys.stdout.write("\n")
    sys.stdout.flush()

    _step_cooldown_if_configured()
    return label == "build_next_phase" and output_declares_program_complete(agent_text)


def run_orchestration_loop() -> tuple[int, int]:
    """Returns (last_outer_round, total_invocations)."""
    global _ADVISORY_OUTER_CAP_LOGGED
    invocation_count = 0
    program_complete = False
    outer = 0
    while not program_complete:
        outer += 1
        if outer > ABSOLUTE_MAX_OUTER_ROUNDS:
            append_issues_markdown(
                "ABSOLUTE_OUTER_CAP_ROLLOVER",
                f"Reached {ABSOLUTE_MAX_OUTER_ROUNDS} outer rounds without `PROGRAM_COMPLETE`; "
                "resetting outer index to 0 and continuing (no user intervention).\n",
            )
            sys.stderr.write(
                f"\nOrchestrator: absolute outer cap rollover after {ABSOLUTE_MAX_OUTER_ROUNDS} rounds; continuing.\n",
            )
            sys.stderr.flush()
            outer = 0
            continue
        if MAX_OUTER_ROUNDS_CAP is not None and outer > MAX_OUTER_ROUNDS_CAP and not _ADVISORY_OUTER_CAP_LOGGED:
            _ADVISORY_OUTER_CAP_LOGGED = True
            append_issues_markdown(
                "OUTER_ROUND_CAP_EXCEEDED_CONTINUING",
                f"CURSOR_ORCHESTRATOR_OUTER_ROUNDS={MAX_OUTER_ROUNDS_CAP} milestone passed; "
                "continuing until `PROGRAM_COMPLETE` (configured cap does not stop the loop).\n",
            )
            sys.stderr.write(
                f"\nOrchestrator: outer milestone {MAX_OUTER_ROUNDS_CAP} passed; continuing until PROGRAM_COMPLETE.\n",
            )
            sys.stderr.flush()
        sys.stdout.write(f"\n>>> outer round {outer} — {STEPS_PER_ROUND} agent step(s)\n")
        sys.stdout.flush()
        for label, prompt in build_steps_for_outer_round(outer):
            invocation_count += 1
            if _invoke_agent_step(invocation_count, outer, label, prompt):
                program_complete = True
                sys.stdout.write(
                    "\nDetected `PROGRAM_COMPLETE` in build pass output; "
                    "finishing this outer round, then stopping.\n",
                )
                sys.stdout.flush()
        if program_complete:
            sys.stdout.write("\nProgram marked complete (`PROGRAM_COMPLETE`). Orchestrator exiting normally.\n")
            sys.stdout.flush()
            break
    return outer, invocation_count


def main() -> None:
    apply_cli_flags_and_reload_cycle_config()
    if _BACKGROUND_RUNNER:
        redirect_stdio_to_daemon_log()
    assert_repo_preconditions()
    maybe_apply_address_space_limit_from_env()
    apply_orchestrator_nice_from_env()
    wait_until_agent_cli_resolvable()
    wait_until_agent_authenticated_for_apply()
    install_signal_handlers()

    apply_note = " (file writes enabled)\n" if APPLY_FILE_CHANGES else " (dry-run: no --force; agent will not apply edits)\n"
    mode_parts: list[str] = []
    if _SMOKE_MODE:
        mode_parts.append("--smoke (preflight only)")
    if _FIRST_PHASE_ONLY:
        mode_parts.append("--first-phase-only (single outer round)")
    if _BACKGROUND_RUNNER:
        mode_parts.append("--background-runner (detached session; stdio → daemon log)")
    mode_note = f"  mode: {'; '.join(mode_parts)}\n" if mode_parts else ""

    outer_cap_note = (
        f"until PROGRAM_COMPLETE (outer index rolls over every {ABSOLUTE_MAX_OUTER_ROUNDS} rounds; no early stop)"
        if MAX_OUTER_ROUNDS_CAP is None
        else (
            f"milestone label {MAX_OUTER_ROUNDS_CAP} in prompts; **no stop** until PROGRAM_COMPLETE "
            f"(rollover every {ABSOLUTE_MAX_OUTER_ROUNDS} rounds)"
        )
    )
    steps_note = f"{STEPS_PER_ROUND} steps per outer round (build + fix×{FIX_PASSES} + verify×{TEST_PASSES} + document)"
    cooldown_note = _read_step_cooldown_seconds()
    nice_orch = orchestrator_nice_increment()
    nice_agent = agent_nice_increment()
    sys.stdout.write(
        "Cursor phase orchestrator (coding-agent repo)\n"
        f"  repo: {REPO_ROOT}\n"
        f"  docs (read full tree on build pass only; see prompts): {DOCS_ROOT}\n"
        f"  checklist: {CHECKLIST_PATH}\n"
        f"  persona (lifecycle): {SOFTWARE_ENGINEER_PERSONA_PATH}\n"
        f"  round log: {ORCHESTRATOR_LOG_PATH}\n"
        f"  issues log: {ISSUES_LOG_PATH}\n"
        f"  invocation transcripts: {ORCHESTRATOR_RUNS_DIR}/\n"
        f"  agent: {AGENT_CMD} {' '.join(AGENT_FLAGS)}{apply_note}"
        f"{mode_note}"
        f"  outer rounds: {outer_cap_note}\n"
        f"  fix passes / test passes: {FIX_PASSES} / {TEST_PASSES}\n"
        f"  {steps_note}\n"
        f"  max steps per build pass: {MAX_CHECKLIST_STEPS_PER_BUILD_PASS}\n"
        f"  nice (orchestrator / agent child): {nice_orch} / {nice_agent}\n"
        f"  step cooldown after each agent call: {cooldown_note}s\n"
        "  env: CURSOR_ORCHESTRATOR_APPLY_CHANGES, CURSOR_ORCHESTRATOR_OUTER_ROUNDS (milestone only; 0=unlabeled), "
        "CURSOR_ORCHESTRATOR_FIX_PASSES, CURSOR_ORCHESTRATOR_TEST_PASSES, CURSOR_ORCHESTRATOR_NICE, "
        "CURSOR_ORCHESTRATOR_AGENT_NICE, CURSOR_ORCHESTRATOR_STEP_COOLDOWN_SEC, CURSOR_ORCHESTRATOR_RLIMIT_AS_MB, "
        "CURSOR_ORCHESTRATOR_AUTH_POLL_SEC, CURSOR_ORCHESTRATOR_CLI_POLL_SEC, CURSOR_ORCHESTRATOR_AGENT_TIMEOUT_SEC\n\n"
    )
    sys.stdout.flush()

    if _SMOKE_MODE:
        sys.stdout.write("Smoke OK: repository preconditions and `agent --help` passed; skipping agent loop.\n")
        sys.stdout.flush()
        return

    outer_done, invocations = run_orchestration_loop()
    sys.stdout.write(
        f"\nOrchestrator session end: {outer_done} outer round(s), {invocations} agent invocation(s).\n",
    )
    sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print(__doc__ or "", end="")
        raise SystemExit(0)
    if try_spawn_background_detached_parent():
        raise SystemExit(0)
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        sys.stderr.write(f"{exc}\n")
        if exc.__cause__ is not None:
            sys.stderr.write(f"Cause: {exc.__cause__}\n")
        try:
            append_issues_markdown(
                "FATAL_ORCHESTRATOR_CRASH",
                f"**{type(exc).__name__}:** {exc}\n\n```\n{traceback.format_exc()}\n```",
            )
        except OSError:
            pass
        raise SystemExit(1) from exc
