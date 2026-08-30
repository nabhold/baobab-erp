# ADR-0005: Use MariaDB for the ERP Engine

- Status: Accepted
- Date: 2026-08-30

## Context

Baobab's wider platform may use PostgreSQL, but ERPNext's mature and supported deployment path is MariaDB. Database uniformity is not worth breaking upstream compatibility.

## Decision

Use the supported MariaDB line for Frappe/ERPNext. Do not make ERPNext share a PostgreSQL database with other engines. Integration occurs through contracts, not cross-database queries.

## Consequences

Baobab operates more than one database technology across engines, while each engine keeps the database best supported by its underlying product.
