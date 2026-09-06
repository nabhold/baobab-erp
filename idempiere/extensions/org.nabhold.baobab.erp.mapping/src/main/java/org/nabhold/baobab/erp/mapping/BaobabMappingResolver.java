package org.nabhold.baobab.erp.mapping;

/**
 * Foundation-stage {@link CanonicalMappingResolver}. Wiring to the mapping store
 * (shared with {@code modules/mapping}, see db/migrations) is tracked in
 * architecture/conformance.yaml against ADR-ERP-007 and is not yet connected.
 */
final class BaobabMappingResolver implements CanonicalMappingResolver {

    @Override
    public NativeRecordRef resolveToNative(String canonicalType, String canonicalId) throws MappingNotFoundException {
        throw new MappingNotFoundException("No mapping backend is wired yet for type: " + canonicalType);
    }

    @Override
    public String resolveToCanonical(String nativeTable, int nativeId) throws MappingNotFoundException {
        throw new MappingNotFoundException("No mapping backend is wired yet for table: " + nativeTable);
    }
}
