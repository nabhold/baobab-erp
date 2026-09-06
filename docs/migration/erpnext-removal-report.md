# ERPNext Removal Report (Phase 29/30)

## Why removal happened now, not after a staged migration

The wider Baobab migration programme (this document's sibling phases) assumes ERPNext is
a live production system with tenants, financial history, and open transactions that must
be audited, migrated, reconciled, and only then decommissioned. That was never true for
`nabhold/baobab-erp`: the repository held a Frappe/ERPNext *foundation-stage scaffold*
only. No Frappe site was ever created against it in a shared environment, no `Company`,
tenant, customer, supplier, invoice, or stock entry ever existed, and no other Baobab
engine ever integrated against it in production. Phases 1 (audit) and 10–28 (staged
migration, reconciliation, stabilisation, archival) therefore do not apply — there was
nothing to extract, reconcile, or archive. Removal and replacement happened in the same
change as adopting iDempiere, per ADR-ERP-001.

## What was removed

| Removed | Replacement |
|---|---|
| `apps/baobab_erp/` (Frappe custom app: DocTypes, hooks, whitelisted methods) | `idempiere/extensions/` (OSGi bundles) + `modules/` (framework-free application services) |
| `deploy/Dockerfile` (built `frappe/erpnext` image) | `idempiere/Dockerfile` (built `idempiereofficial/idempiere` image) |
| `deploy/compose.yaml` (MariaDB, Redis cache/queue, Bench backend/frontend/websocket/workers/scheduler) | `compose.yaml` (PostgreSQL, iDempiere) |
| `scripts/dev/bootstrap.sh` (Bench init, `bench get-app`, `bench new-site`) | `scripts/dev/bootstrap.sh` (`pip install -e modules`, `mvn package`) |
| `scripts/dev/start.sh` (`bench start`) | Removed outright; no equivalent dev server exists yet because the application-service HTTP layer is not built (tracked in `architecture/conformance.yaml`) |
| `upstream.lock.yaml` pins for Frappe/ERPNext/MariaDB/Redis | Pins for iDempiere/PostgreSQL |
| `docs/architecture/`, `docs/development/`, `docs/operations/` (Frappe/ERPNext-specific) | `docs/architecture.md`, `docs/development.md`, `docs/operations.md`, `docs/integration.md`, `docs/events.md`, `docs/tenancy.md`, `docs/security.md`, `docs/testing.md`, `docs/provisioning.md`, `docs/releases.md` |
| `.devcontainer` MariaDB/Redis services and Frappe ports | PostgreSQL service; Java/Maven build step |
| `.github/workflows/ci.yml`, `foundation.yml` referencing `deploy/Dockerfile` | Updated to `idempiere/Dockerfile`, plus a Maven/OSGi build job |
| `.github/dependabot.yml` docker ecosystem at `/deploy` | Docker ecosystem at `/idempiere`, plus a new Maven ecosystem at `/idempiere/extensions` |
| README/CONTRIBUTING/SECURITY/CHANGELOG/CODEOWNERS Frappe/ERPNext/Bench references | Rewritten for iDempiere/OSGi/PostgreSQL |

ADR-0001 through ADR-0005 (the original Frappe/ERPNext ADRs) are kept for history and
marked superseded in `docs/adr/README.md`, rather than deleted, per normal ADR practice.

## What did not need archival

Per Phase 28, historical records required for audit, tax, or legal evidence must be
preserved before deletion. None exist for this repository: no financial transaction,
customer record, or stock movement was ever created against the removed scaffold, so
there is nothing to migrate into an archive.

## Verification

`tests/architecture/test_no_erpnext_dependency.py` is a standing fitness function
(Phase 30) that fails CI if the case-insensitive strings `erpnext`, `frappe`, or `bench`
appear anywhere in the repository outside this documentation and the superseded ADRs. It
runs as part of `./scripts/validate.sh`.

## Control Plane state

No ERPNext `EngineInstance`, `Mapping`, or `CapabilityBinding` was ever registered with
`nabhold/baobab-cp` for this repository, so there is nothing to retire there either.
