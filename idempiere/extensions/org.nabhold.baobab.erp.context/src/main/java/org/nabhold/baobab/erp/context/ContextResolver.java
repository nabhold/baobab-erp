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

    record ResolvedContext(int adClientId, int adOrgId) {
    }

    class ContextResolutionException extends Exception {
        public ContextResolutionException(String message) {
            super(message);
        }
    }
}
