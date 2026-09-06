# Changelog

All notable changes follow Keep a Changelog and Semantic Versioning.

## [Unreleased]

### Changed

- Replaced the Frappe/ERPNext foundation-stage scaffold with an iDempiere-based
  foundation, per ADR-ERP-001 through ADR-ERP-020. No tenant, financial, or
  transactional data ever existed against the previous scaffold; see
  `docs/migration/erpnext-removal-report.md` for what was removed and why removal was
  safe now rather than deferred.
- Added `idempiere/extensions` (Baobab OSGi bundles), `modules/` (framework-free
  application-service layer), `db/migrations` (Baobab-owned Postgres schema),
  `migration/` (scaffolding for a future ERPNext-source migration), and
  `architecture/conformance.yaml` (an honest ADR conformance ledger).

## [0.1.0] - 2026-08-30

### Added

- Initial Frappe/ERPNext v16 engine foundation.
- Baobab custom app boundaries and mapping/event DocTypes.
- Bench, Docker Compose, Codespaces, CI, security, testing, and architecture documentation.
