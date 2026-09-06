# Imports

Import adapters that create or update iDempiere records from validated `staging/` data,
recording the resulting `Mapping`/`ExternalReference` for each imported record (see
`db/migrations/0003_create_entity_mapping.sql`). Every migrated object must be traceable
back to its source ERPNext ID, canonical UUID, target iDempiere ID, migration batch, and
validation result (Phase 13). Empty until there is real transformed data to import. See
`../README.md`.
