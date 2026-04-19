#!/bin/sh
# Point this repository at tracked git hooks (.githooks).
set -ef
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
git config core.hooksPath .githooks
echo "Set core.hooksPath to .githooks (pre-push bumps minor version by default)."
echo "Tip: SKIP_VERSION_BUMP=1 git push  — skip the version bump for one push."
