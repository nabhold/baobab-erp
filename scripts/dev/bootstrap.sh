#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
bench_dir="${repo_root}/.bench"
site_name="${FRAPPE_SITE_NAME:-baobab.localhost}"

if ! command -v bench >/dev/null 2>&1; then
  uv tool install frappe-bench==5.27.0
fi

if [[ ! -d "${bench_dir}/apps/frappe" ]]; then
  bench init \
    --frappe-path https://github.com/frappe/frappe \
    --frappe-branch v16.32.0 \
    --python python3.14 \
    --skip-redis-config-generation \
    "${bench_dir}"
fi

cd "${bench_dir}"

if [[ ! -d apps/erpnext ]]; then
  bench get-app --branch v16.33.0 https://github.com/frappe/erpnext
fi

if [[ ! -e apps/baobab_erp ]]; then
  bench get-app "file://${repo_root}/apps/baobab_erp"
fi

bench set-config -g db_host "${DB_HOST:-db}"
bench set-config -gp db_port 3306
bench set-config -g redis_cache "redis://${REDIS_CACHE:-redis-cache:6379}"
bench set-config -g redis_queue "redis://${REDIS_QUEUE:-redis-queue:6379}"
bench set-config -gp socketio_port 9000

if [[ ! -f "sites/${site_name}/site_config.json" ]]; then
  bench new-site "${site_name}" \
    --mariadb-root-password dev-root-only \
    --admin-password admin \
    --install-app erpnext \
    --install-app baobab_erp
  bench --site "${site_name}" set-config developer_mode 1
fi

bench build --app baobab_erp
echo "Baobab ERP Bench is ready at ${bench_dir}. Run scripts/dev/start.sh."
