package org.nabhold.baobab.erp.mapping;

import java.util.Map;
import org.nabhold.baobab.erp.integration.BaobabAppClient;
import org.nabhold.baobab.erp.integration.BaobabAppClientException;
import org.nabhold.baobab.erp.integration.BaobabAppNotFoundException;

/**
 * Resolves canonical <-> native mappings by calling baobab-app's
 * {@code /mapping/resolve} and {@code /mapping/resolve-canonical} endpoints, backed
 * by {@code modules/mapping}'s Postgres-backed store (ADR-ERP-007). This bundle has
 * no direct database access of its own -- baobab-app is the only thing that touches
 * the {@code baobab} schema.
 */
final class BaobabMappingResolver implements CanonicalMappingResolver {

    /** System property naming baobab-app's base URL; see BaobabContextResolver's
     * matching property for the same default and the ADR-ERP-002 gap note. */
    static final String BASE_URL_PROPERTY = "baobab.app.base.url";
    private static final String DEFAULT_BASE_URL = "http://baobab-app:8000";

    private final BaobabAppClient client;

    BaobabMappingResolver() {
        this(new BaobabAppClient(System.getProperty(BASE_URL_PROPERTY, DEFAULT_BASE_URL)));
    }

    BaobabMappingResolver(BaobabAppClient client) {
        this.client = client;
    }

    @Override
    public NativeRecordRef resolveToNative(String tenantId, String canonicalType, String canonicalId)
            throws MappingNotFoundException {
        Map<String, Object> body;
        try {
            body = client.get("/mapping/resolve?tenant_id=" + BaobabAppClient.encodeQueryParam(tenantId)
                    + "&canonical_type=" + BaobabAppClient.encodeQueryParam(canonicalType)
                    + "&canonical_id=" + BaobabAppClient.encodeQueryParam(canonicalId));
        } catch (BaobabAppNotFoundException e) {
            throw new MappingNotFoundException(
                    "No active mapping for tenantId=" + tenantId + " canonicalType=" + canonicalType
                            + " canonicalId=" + canonicalId);
        } catch (BaobabAppClientException e) {
            throw new MappingNotFoundException("Could not resolve mapping via baobab-app: " + e.getMessage());
        }

        Object table = body.get("table");
        Number recordId = (Number) body.get("record_id");
        if (table == null || recordId == null) {
            throw new MappingNotFoundException("baobab-app response missing table/record_id: " + body);
        }
        return new NativeRecordRef(table.toString(), recordId.intValue());
    }

    @Override
    public String resolveToCanonical(String tenantId, String nativeTable, int nativeId)
            throws MappingNotFoundException {
        Map<String, Object> body;
        try {
            body = client.get("/mapping/resolve-canonical?tenant_id=" + BaobabAppClient.encodeQueryParam(tenantId)
                    + "&table=" + BaobabAppClient.encodeQueryParam(nativeTable)
                    + "&record_id=" + nativeId);
        } catch (BaobabAppNotFoundException e) {
            throw new MappingNotFoundException(
                    "No active mapping for tenantId=" + tenantId + " table=" + nativeTable + " id=" + nativeId);
        } catch (BaobabAppClientException e) {
            throw new MappingNotFoundException("Could not resolve mapping via baobab-app: " + e.getMessage());
        }

        Object canonicalId = body.get("canonical_id");
        if (canonicalId == null) {
            throw new MappingNotFoundException("baobab-app response missing canonical_id: " + body);
        }
        return canonicalId.toString();
    }
}
