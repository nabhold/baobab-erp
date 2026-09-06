#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

python -m compileall -q modules tests

PYTHONPATH=modules python -m unittest discover -s tests/unit -p 'test_*.py'
PYTHONPATH=modules python -m unittest discover -s tests/security -p 'test_*.py'
PYTHONPATH=modules python -m unittest discover -s tests/tenancy -p 'test_*.py'
PYTHONPATH=modules python -m unittest discover -s tests/contract -p 'test_*.py'
PYTHONPATH=modules python -m unittest discover -s tests/architecture -p 'test_*.py'

python - <<'PY'
import json
from pathlib import Path

for path in Path(".").rglob("*.json"):
    if "/target/" in str(path) or "/.git/" in str(path):
        continue
    json.loads(path.read_text())
print("JSON validation passed")
PY

if command -v mvn >/dev/null 2>&1; then
  mvn -q -f idempiere/extensions package
else
  echo "mvn not found; skipping OSGi extension build" >&2
fi

if [[ "${SKIP_COMPOSE_VALIDATION:-0}" != "1" ]] && command -v docker >/dev/null 2>&1; then
  DB_PASS=validation DB_ADMIN_PASS=validation \
  BAOBAB_EVENT_SIGNING_SECRET=validation \
  docker compose -f compose.yaml config --quiet
fi
