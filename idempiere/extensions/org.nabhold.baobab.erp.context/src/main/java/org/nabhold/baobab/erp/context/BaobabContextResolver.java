package org.nabhold.baobab.erp.context;

import java.util.Map;
import org.nabhold.baobab.erp.integration.BaobabAppClient;
import org.nabhold.baobab.erp.integration.BaobabAppClientException;
import org.nabhold.baobab.erp.integration.BaobabAppNotFoundException;

/**
 * Resolves tenant/legal-entity context by calling baobab-app's
 * {@code /context/resolve} endpoint, backed by {@code modules/context}'s
 * Postgres-backed store (ADR-ERP-002). This bundle has no direct database access of
 * its own -- baobab-app is the only thing that touches the {@code baobab} schema.
 */
final class BaobabContextResolver implements ContextResolver {

    /** System property naming baobab-app's base URL; defaults to the Compose service
     * name/port from compose.yaml. Not yet exposed through OSGi ConfigurationAdmin --
     * see architecture/conformance.yaml against ADR-ERP-002. */
    static final String BASE_URL_PROPERTY = "baobab.app.base.url";
    private static final String DEFAULT_BASE_URL = "http://baobab-app:8000";

    private final BaobabAppClient client;

    BaobabContextResolver() {
        this(new BaobabAppClient(System.getProperty(BASE_URL_PROPERTY, DEFAULT_BASE_URL)));
    }

    BaobabContextResolver(BaobabAppClient client) {
        this.client = client;
    }

    @Override
    public ResolvedContext resolve(String tenantId, String legalEntityId) throws ContextResolutionException {
        if (tenantId == null || tenantId.isBlank() || legalEntityId == null || legalEntityId.isBlank()) {
            throw new ContextResolutionException("tenantId and legalEntityId are both required");
        }

        Map<String, Object> body;
        try {
            body = client.get("/context/resolve?tenant_id=" + BaobabAppClient.encodeQueryParam(tenantId)
                    + "&entity_id=" + BaobabAppClient.encodeQueryParam(legalEntityId));
        } catch (BaobabAppNotFoundException e) {
            throw new ContextResolutionException(
                    "No active mapping for tenantId=" + tenantId + " legalEntityId=" + legalEntityId);
        } catch (BaobabAppClientException e) {
            throw new ContextResolutionException("Could not resolve context via baobab-app: " + e.getMessage());
        }

        Number adClientId = (Number) body.get("ad_client_id");
        Number adOrgId = (Number) body.get("ad_org_id");
        if (adClientId == null || adOrgId == null) {
            throw new ContextResolutionException("baobab-app response missing ad_client_id/ad_org_id: " + body);
        }
        return new ResolvedContext(adClientId.intValue(), adOrgId.intValue());
    }

    @Override
    public TenantIdentity resolveTenant(int adClientId, int adOrgId) throws ContextResolutionException {
        Map<String, Object> body;
        try {
            body = client.get("/context/resolve-tenant?ad_client_id=" + adClientId + "&ad_org_id=" + adOrgId);
        } catch (BaobabAppNotFoundException e) {
            throw new ContextResolutionException(
                    "No active mapping for adClientId=" + adClientId + " adOrgId=" + adOrgId);
        } catch (BaobabAppClientException e) {
            throw new ContextResolutionException("Could not resolve tenant via baobab-app: " + e.getMessage());
        }

        Object tenantId = body.get("tenant_id");
        Object entityId = body.get("entity_id");
        if (tenantId == null || entityId == null) {
            throw new ContextResolutionException("baobab-app response missing tenant_id/entity_id: " + body);
        }
        return new TenantIdentity(tenantId.toString(), entityId.toString());
    }
}
