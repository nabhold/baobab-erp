# Baobab ERP Interface Contracts

`nabhold/shared` remains canonical for organisation-wide governance identities and obligations. This directory contains only ERP Engine interface profiles and examples.

- `events/envelope.schema.json` defines the common signed event envelope.
- `events/trade/` and `events/pulse/` are reserved for approved versioned event payload schemas.
- Breaking changes create a new major-version schema; existing schemas remain available while consumers migrate.

Payload schemas must never contain database table names or require another engine to understand ERPNext internals.
