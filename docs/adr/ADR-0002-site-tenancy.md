# ADR-0002: Use a Frappe Site as the ERP Isolation Unit

- Status: Accepted
- Date: 2026-08-30

## Decision

Use one Frappe site per approved tenant boundary. A legal entity is the default boundary, but tenancy remains a separate canonical concept with its own immutable `tenant_id`. ERPNext `Company` is an accounting/legal record and is not, by itself, a sufficient tenant-security boundary.

Multiple Companies in one tenant site require an explicit business and security decision. A cross-tenant shared site is prohibited.

## Consequences

This aligns with native Frappe multi-tenancy and gives strong operational separation without custom row-level tenancy throughout ERPNext. It creates per-site provisioning, migration, backup, and monitoring duties.
