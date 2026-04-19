#!/usr/bin/env bash
# Stage 1 cold-start demo (OSV-STORY-01 §5 / path-to-100 B5).
# Mirrors the success path in src/orchestrator/tests/unit/test_stage1_golden_flow.py::test_stage1_golden_scaffold_revise_lock_validate
#
# Usage (from repo root):
#   ./scripts/stage1-cold-start-demo.sh
# Or reuse a session directory (no cleanup):
#   STAGE1_COLD_START_SESSION_DIR=/path/to/session ./scripts/stage1-cold-start-demo.sh
#
# Exit codes:
#   0 — scaffold, intake-revise, plan-lock (ready), validate --require-plan-lock all succeeded
#   non-zero — first failing command’s exit (set -e)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ -n "${STAGE1_COLD_START_SESSION_DIR:-}" ]]; then
  SESSION="$(cd "${STAGE1_COLD_START_SESSION_DIR}" && pwd)"
  mkdir -p "$SESSION"
else
  SESSION="$(mktemp -d "${TMPDIR:-/tmp}/stage1-cold-start.XXXXXX")"
fi

echo "stage1-cold-start-demo: SESSION_DIR=${SESSION}" >&2

# 1) Scaffold intake stubs (CLI exit 0 = ok)
uv run sde project scaffold-intake \
  --session-dir "$SESSION" \
  --goal "Ship Stage 1 intake golden path" \
  --repo-label "cold-start-demo"

# 2) Minimal lockable plan (same shape as golden test)
cat >"${SESSION}/project_plan.json" <<'EOF'
{
  "schema_version": "1.0",
  "steps": [
    {
      "step_id": "contract-intake",
      "phase": "planning",
      "title": "Lock contract",
      "description": "Define intake contract",
      "depends_on": [],
      "path_scope": [],
      "rollback_hint": "revert contract",
      "contract_step": true
    },
    {
      "step_id": "impl-intake",
      "phase": "implementation",
      "title": "Implement intake",
      "description": "Implement Stage 1 intake handlers",
      "depends_on": ["contract-intake"],
      "path_scope": [],
      "rollback_hint": "revert implementation"
    }
  ]
}
EOF

# 3) Bounded revise / revise_state from doc_review (exit 0 = review_passed)
uv run sde project intake-revise --session-dir "$SESSION" --max-retries 2

# 4) Lineage manifest + lock artifact (exit 0 = ready and locked; 1 = not ready; 2 = hard error)
uv run sde project plan-lock --session-dir "$SESSION"

# 5) Preflight with lock required (exit 0 = ok)
uv run sde project validate \
  --session-dir "$SESSION" \
  --repo-root "$REPO_ROOT" \
  --skip-workspace \
  --require-plan-lock

# 6) Optional structured metrics file (same session; exit 0)
uv run sde project export-stage1-observability --session-dir "$SESSION"

echo "stage1-cold-start-demo: OK (artifacts under ${SESSION})" >&2
