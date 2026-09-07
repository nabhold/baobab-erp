-- Enforces, at the database, an invariant the forward direction already assumed:
-- one active (AD_Client_ID, AD_Org_ID) pair belongs to exactly one tenant/entity.
-- Needed for the reverse direction (AD_Client_ID/AD_Org_ID -> tenant_id/entity_id)
-- added to modules/context to support ADR-ERP-003's default
-- ERP_SHARED_INSTANCE_DEDICATED_CLIENT topology, where one iDempiere runtime hosts
-- several AD_Clients (tenants) at once, so a single process-wide tenant can never be
-- correct -- the tenant must be derived per record from its own AD_Client_ID/AD_Org_ID.
CREATE UNIQUE INDEX tenant_mapping_native_active_unique
    ON baobab.tenant_mapping (ad_client_id, ad_org_id)
    WHERE status = 'active';
