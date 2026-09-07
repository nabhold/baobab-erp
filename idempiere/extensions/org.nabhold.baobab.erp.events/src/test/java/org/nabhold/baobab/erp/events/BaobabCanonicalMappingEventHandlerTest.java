package org.nabhold.baobab.erp.events;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.nabhold.baobab.erp.mapping.CanonicalMappingResolver;
import org.osgi.service.event.Event;

/**
 * Exercises BaobabCanonicalMappingEventHandler against a real org.osgi.service.event.Event
 * (not a mock) and a small recording CanonicalMappingResolver double -- this class's own
 * job is proving the handler extracts tenantId/tableName/recordId correctly from a real
 * event and calls (or correctly skips) the resolver, not re-proving BaobabMappingResolver's
 * HTTP wire format, which BaobabMappingResolverTest (in the mapping bundle) already covers
 * against a real local HTTP server. FakeNativePO stands in for org.compiere.model.PO, which
 * isn't available at compile time; it exposes only the one method the handler calls
 * reflectively.
 */
class BaobabCanonicalMappingEventHandlerTest {

    private static final String TOPIC = "adempiere/po/postCreate";
    private static final String CANONICAL_ID = "e4a8ccd4-21cb-43b7-915f-1434d9aef07a";

    private static Event bPartnerEvent(Object po) {
        Map<String, Object> properties = new HashMap<>();
        properties.put("tableName", "C_BPartner");
        properties.put("event.data", po);
        return new Event(TOPIC, properties);
    }

    @Test
    void resolvesCanonicalIdOnRealEvent() {
        RecordingResolver resolver = RecordingResolver.returning(CANONICAL_ID);
        BaobabCanonicalMappingEventHandler handler = new BaobabCanonicalMappingEventHandler(resolver, "nabhold");

        handler.handleEvent(bPartnerEvent(new FakeNativePO(1001)));

        assertEquals("nabhold", resolver.tenantId);
        assertEquals("C_BPartner", resolver.table);
        assertEquals(1001, resolver.recordId);
    }

    @Test
    void missingMappingDoesNotThrow() {
        RecordingResolver resolver = RecordingResolver.notFound();
        BaobabCanonicalMappingEventHandler handler = new BaobabCanonicalMappingEventHandler(resolver, "nabhold");

        handler.handleEvent(bPartnerEvent(new FakeNativePO(999999)));

        assertTrue(resolver.called, "resolver should still have been called");
    }

    @Test
    void blankTenantIdSkipsResolutionEntirely() {
        RecordingResolver resolver = RecordingResolver.returning(CANONICAL_ID);
        BaobabCanonicalMappingEventHandler handler = new BaobabCanonicalMappingEventHandler(resolver, null);

        handler.handleEvent(bPartnerEvent(new FakeNativePO(1001)));

        assertFalse(resolver.called, "resolver must not be called without a tenant id");
    }

    @Test
    void missingTableNamePropertySkipsResolutionEntirely() {
        RecordingResolver resolver = RecordingResolver.returning(CANONICAL_ID);
        BaobabCanonicalMappingEventHandler handler = new BaobabCanonicalMappingEventHandler(resolver, "nabhold");
        Event eventWithoutTableName = new Event(TOPIC, Map.of("event.data", new FakeNativePO(1001)));

        handler.handleEvent(eventWithoutTableName);

        assertFalse(resolver.called, "resolver must not be called without a tableName property");
    }

    @Test
    void missingEventDataSkipsResolutionEntirely() {
        RecordingResolver resolver = RecordingResolver.returning(CANONICAL_ID);
        BaobabCanonicalMappingEventHandler handler = new BaobabCanonicalMappingEventHandler(resolver, "nabhold");
        Event eventWithoutData = new Event(TOPIC, Map.of("tableName", "C_BPartner"));

        handler.handleEvent(eventWithoutData);

        assertFalse(resolver.called, "resolver must not be called without a PO to read the record id from");
    }

    /** Stands in for org.compiere.model.PO: only the reflectively-called method matters. */
    static final class FakeNativePO {
        private final int id;

        FakeNativePO(int id) {
            this.id = id;
        }

        public int get_ID() {
            return id;
        }
    }

    /** Records the arguments resolveToCanonical was called with; never touches the network. */
    static final class RecordingResolver implements CanonicalMappingResolver {
        private final String canonicalId;
        private final boolean notFound;
        boolean called;
        String tenantId;
        String table;
        int recordId;

        private RecordingResolver(String canonicalId, boolean notFound) {
            this.canonicalId = canonicalId;
            this.notFound = notFound;
        }

        static RecordingResolver returning(String canonicalId) {
            return new RecordingResolver(canonicalId, false);
        }

        static RecordingResolver notFound() {
            return new RecordingResolver(null, true);
        }

        @Override
        public NativeRecordRef resolveToNative(String tenantId, String canonicalType, String canonicalId) {
            throw new UnsupportedOperationException("not used by this handler");
        }

        @Override
        public String resolveToCanonical(String tenantId, String nativeTable, int nativeId)
                throws MappingNotFoundException {
            this.called = true;
            this.tenantId = tenantId;
            this.table = nativeTable;
            this.recordId = nativeId;
            if (notFound) {
                throw new MappingNotFoundException("no mapping for " + nativeTable + "#" + nativeId);
            }
            return canonicalId;
        }
    }
}
