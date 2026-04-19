#!/usr/bin/env bash
# Refresh docs/versioning/INDEX.md from plans/*.md first-line titles without overwriting any plan file.
# Same as: python3 docs/versioning/_generate_plans.py --index-only
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
exec python3 docs/versioning/_generate_plans.py --index-only
