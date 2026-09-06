#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${repo_root}"

# baobab-dev ships a PEP 668 externally-managed system Python; this installs only our
# own local editable package into it, which is the standard exception to that guard.
pip install --break-system-packages -q -e modules

if command -v mvn >/dev/null 2>&1; then
  mvn -q -f idempiere/extensions package
else
  echo "mvn not found; skipping OSGi extension build (Java/Maven capability required)." >&2
fi

echo "Baobab ERP development environment ready."
echo "Run ./scripts/validate.sh for the fast test suite, or"
echo "  docker compose up  # to start the full iDempiere + PostgreSQL runtime"
