package org.nabhold.baobab.erp.context;

/**
 * Foundation-stage {@link ContextResolver}. The real implementation queries the
 * mapping store owned by {@code modules/mapping} (see ADR-ERP-007) instead of
 * iDempiere tables directly; wiring that call is tracked in
 * architecture/conformance.yaml against ADR-ERP-002 and is not yet connected.
 */
final class BaobabContextResolver implements ContextResolver {

    @Override
    public ResolvedContext resolve(String tenantId, String legalEntityId) throws ContextResolutionException {
        if (tenantId == null || tenantId.isBlank() || legalEntityId == null || legalEntityId.isBlank()) {
            throw new ContextResolutionException("tenantId and legalEntityId are both required");
        }
        throw new ContextResolutionException(
                "No mapping backend is wired yet; resolution must fail closed rather than guess");
    }
}
