# Testing Strategy

| Layer | Purpose | Command |
|---|---|---|
| Contract/unit | Event validation, signatures, pure mapping rules | `./scripts/validate.sh` |
| Frappe app | DocType validation, permissions, hooks, APIs | `bench --site baobab.localhost run-tests --app baobab_erp` |
| Integration | MariaDB, Redis, workers, scheduler, signed inbound events | Compose test environment |
| Compatibility | Pinned Frappe/ERPNext upgrade validation | Required for `upstream.lock.yaml` changes |
| Security | Secret scanning, CodeQL, dependency review | GitHub workflows |

Tests must include duplicate delivery, retry exhaustion, missing tenant context, contradictory tenant/entity mappings, cross-tenant access attempts, permission denial, schema-version compatibility, and transactional outbox behaviour before the related features are promoted from extension points to production flows.
