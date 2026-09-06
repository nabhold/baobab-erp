-- Backs modules/mapping: CanonicalEntity <-> iDempiere native record (ADR-ERP-007).
-- The canonical identity is a Baobab UUID; native_table/native_id are iDempiere-local
-- and never leak out as a cross-engine identifier.
CREATE TABLE baobab.entity_mapping (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       TEXT NOT NULL,
    canonical_type  TEXT NOT NULL,
    canonical_id    UUID NOT NULL,
    native_table    TEXT NOT NULL,
    native_id       INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'superseded')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX entity_mapping_canonical_active_unique
    ON baobab.entity_mapping (tenant_id, canonical_type, canonical_id)
    WHERE status = 'active';

CREATE UNIQUE INDEX entity_mapping_native_active_unique
    ON baobab.entity_mapping (tenant_id, native_table, native_id)
    WHERE status = 'active';
