#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

python -m compileall -q apps/baobab_erp/baobab_erp tests
python -m unittest discover -s tests -p 'test_*.py'

python - <<'PY'
import json
from pathlib import Path

for path in Path(".").rglob("*.json"):
    json.loads(path.read_text())
print("JSON validation passed")
PY

if [[ "${SKIP_COMPOSE_VALIDATION:-0}" != "1" ]] && command -v docker >/dev/null 2>&1; then
  DB_ROOT_PASSWORD=validation DB_PASSWORD=validation ADMIN_PASSWORD=validation \
  BAOBAB_EVENT_SIGNING_SECRET=validation \
  docker compose -f deploy/compose.yaml config --quiet
fi
