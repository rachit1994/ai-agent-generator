#!/usr/bin/env bash
set -euo pipefail

# Stage 1 intake verification subset (OSV-STORY-01).
#
# Operator + CLI semantics: docs/UNDERSTANDING-THE-CODE.md (Stage 1 intake section)
# Stage 1 flags (validate / run / continuous, SDE_REQUIRE_NON_STUB_REVIEWER): same file, project driver section
#
# Optional wall-clock SLO: when STAGE1_SUITE_MAX_SECONDS is set to a non-negative integer,
# the script exits 1 if total wall time (including pytest startup) exceeds that budget.
# CI sets this in .github/workflows/ci.yml (Python 3.11 via setup-uv).

start_epoch=$(date +%s)

uv run pytest \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_intake_scaffold.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_intake_util.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_intake_revise.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_plan_lock.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_validate.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_status.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_stage1_observability_export.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_project_stop.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_stage1_golden_flow.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_stage1_cold_start_demo.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_stage1_runbook_consistency.py \
  src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit/test_stage1_suite_script.py -q

end_epoch=$(date +%s)
elapsed=$((end_epoch - start_epoch))

if [[ -n "${STAGE1_SUITE_MAX_SECONDS:-}" ]]; then
  if ! [[ "${STAGE1_SUITE_MAX_SECONDS}" =~ ^[0-9]+$ ]]; then
    echo "run-stage1-suite: STAGE1_SUITE_MAX_SECONDS must be decimal digits only, got: ${STAGE1_SUITE_MAX_SECONDS}" >&2
    exit 2
  fi
  if ((STAGE1_SUITE_MAX_SECONDS < 1)); then
    echo "run-stage1-suite: STAGE1_SUITE_MAX_SECONDS must be >= 1 when set (wall time uses whole seconds)" >&2
    exit 2
  fi
  if ((elapsed > STAGE1_SUITE_MAX_SECONDS)); then
    echo "run-stage1-suite: wall-clock SLO breached: ${elapsed}s > ${STAGE1_SUITE_MAX_SECONDS}s" >&2
    exit 1
  fi
fi
