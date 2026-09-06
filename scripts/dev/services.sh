#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${repo_root}"

if [[ -n "${DATABASE_URL:-}" ]] && command -v psql >/dev/null 2>&1; then
  ./db/migrate.sh
else
  echo "DATABASE_URL not set or psql unavailable; skipping schema migration." >&2
fi
