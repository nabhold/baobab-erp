package org.nabhold.baobab.erp.context;

/**
 * Resolves an inbound Baobab {@code tenantId}/{@code legalEntityId} pair to the
 * iDempiere {@code AD_Client_ID}/{@code AD_Org_ID} pair authorised to act on their
 * behalf, per ADR-ERP-002. Never assume {@code tenantId == AD_Client_ID}.
 */
public interface ContextResolver {

    /**
     * @throws ContextResolutionException if the mapping is missing, inactive, or
     *         ambiguous. Resolution fails closed: it never guesses.
     */
    ResolvedContext resolve(String tenantId, String legalEntityId) throws ContextResolutionException;

    /**
     * The reverse direction: given the AD_Client_ID/AD_Org_ID a piece of iDempiere-native
     * code is already running under, resolve the Baobab tenant/legal-entity that owns it.
     * Needed because ADR-ERP-003's default topology (ERP_SHARED_INSTANCE_DEDICATED_CLIENT)
     * has one iDempiere runtime hosting several AD_Clients (tenants) at once, so code
     * inside that runtime cannot assume a single tenant for the whole process.
     *
     * @throws ContextResolutionException if the mapping is missing, inactive, or
     *         ambiguous. Resolution fails closed: it never guesses.
     */
    TenantIdentity resolveTenant(int adClientId, int adOrgId) throws ContextResolutionException;

    record ResolvedContext(int adClientId, int adOrgId) {
    }

    record TenantIdentity(String tenantId, String legalEntityId) {
    }

    class ContextResolutionException extends Exception {
        public ContextResolutionException(String message) {
            super(message);
        }
    }
}
