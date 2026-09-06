-- Backs modules/context: resolves (tenant_id, entity_id) to an active (AD_Client_ID,
-- AD_Org_ID) pair. tenant_id is never assumed equal to AD_Client_ID (ADR-ERP-002).
CREATE TABLE baobab.tenant_mapping (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       TEXT NOT NULL,
    entity_id       TEXT NOT NULL,
    ad_client_id    INTEGER NOT NULL,
    ad_org_id       INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX tenant_mapping_active_unique
    ON baobab.tenant_mapping (tenant_id, entity_id)
    WHERE status = 'active';
