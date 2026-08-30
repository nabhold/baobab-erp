# ADR-0003: Map Canonical Identities to Native ERPNext Records

- Status: Accepted
- Date: 2026-08-30

## Decision

Keep ERPNext DocTypes authoritative for ERP operations. Store explicit mappings from Baobab canonical IDs to native record names in a Baobab-owned DocType. Do not replace Company, Customer, Supplier, Item, Warehouse, Employee, User, Cost Centre, Project, or Location semantics wholesale.

## Consequences

Integration remains resilient to display-name changes and preserves upstream behaviour. Mapping lifecycle, uniqueness, reconciliation, and audit become explicit responsibilities.
