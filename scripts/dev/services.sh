#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -d "${repo_root}/.bench" ]]; then
  cd "${repo_root}/.bench"
  bench use "${FRAPPE_SITE_NAME:-baobab.localhost}" >/dev/null
fi
