#!/bin/sh
# Point this repository at tracked git hooks (.githooks).
set -ef
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
git config core.hooksPath .githooks
echo "Set core.hooksPath to .githooks (pre-push bumps minor version by default)."
