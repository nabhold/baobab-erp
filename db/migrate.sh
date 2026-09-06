#!/usr/bin/env bash
# Applies db/migrations/*.sql once each, tracked in baobab.schema_migrations.
# Requires psql and DATABASE_URL (postgresql://user:pass@host:port/dbname).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${DATABASE_URL:?Set DATABASE_URL}"

psql "${DATABASE_URL}" -v ON_ERROR_STOP=1 -c "
  CREATE SCHEMA IF NOT EXISTS baobab;
  CREATE TABLE IF NOT EXISTS baobab.schema_migrations (
      filename TEXT PRIMARY KEY,
      applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
  );
"

for migration in "${repo_root}"/db/migrations/*.sql; do
  filename="$(basename "${migration}")"
  already_applied=$(psql "${DATABASE_URL}" -tAc \
    "SELECT 1 FROM baobab.schema_migrations WHERE filename = '${filename}'")
  if [[ "${already_applied}" == "1" ]]; then
    echo "skip  ${filename} (already applied)"
    continue
  fi
  echo "apply ${filename}"
  psql "${DATABASE_URL}" -v ON_ERROR_STOP=1 -f "${migration}"
  psql "${DATABASE_URL}" -v ON_ERROR_STOP=1 -c \
    "INSERT INTO baobab.schema_migrations (filename) VALUES ('${filename}')"
done
