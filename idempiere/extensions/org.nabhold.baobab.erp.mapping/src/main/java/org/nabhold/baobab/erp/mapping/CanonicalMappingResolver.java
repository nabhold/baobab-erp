package org.nabhold.baobab.erp.mapping;

/**
 * Translates a canonical entity into its iDempiere native record key, and back,
 * through an explicit {@code Mapping}/{@code ExternalReference} lookup (ADR-ERP-007).
 * A missing mapping is a business exception, never a lazily-created record.
 */
public interface CanonicalMappingResolver {

    /** Mappings are scoped per tenant (db/migrations/0003_create_entity_mapping.sql);
     * omitting tenantId here would risk resolving another tenant's mapping. */
    NativeRecordRef resolveToNative(String tenantId, String canonicalType, String canonicalId)
            throws MappingNotFoundException;

    String resolveToCanonical(String tenantId, String nativeTable, int nativeId) throws MappingNotFoundException;

    record NativeRecordRef(String table, int recordId) {
    }

    class MappingNotFoundException extends Exception {
        public MappingNotFoundException(String message) {
            super(message);
        }
    }
}
