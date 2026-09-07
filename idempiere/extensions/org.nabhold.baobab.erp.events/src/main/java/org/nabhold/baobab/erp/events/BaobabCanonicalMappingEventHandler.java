package org.nabhold.baobab.erp.events;

import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.lang.reflect.Method;
import org.nabhold.baobab.erp.mapping.CanonicalMappingResolver;
import org.nabhold.baobab.erp.mapping.CanonicalMappingResolver.MappingNotFoundException;
import org.osgi.service.event.Event;
import org.osgi.service.event.EventHandler;
import org.osgi.util.tracker.ServiceTracker;

/**
 * Reacts to a real, iDempiere-fired PO_POST_CREATE/PO_POST_UPADTE event on C_BPartner by
 * resolving its canonical Party identity through the registered CanonicalMappingResolver
 * OSGi service (ADR-ERP-007). These topics fire asynchronously, after the triggering
 * transaction has committed (see org.compiere.model.PO#processAfterSave), so the blocking
 * HTTP call this triggers never runs inside a document transaction (ADR-ERP-004,
 * INV-ERP-EXT-011).
 *
 * <p>This bundle has no compile-time dependency on any iDempiere class: the event's
 * "tableName" property is a plain String set by iDempiere's own EventManager, and the
 * only iDempiere-shaped value this class touches -- the PO's record id -- is read via a
 * single reflective call to its public {@code get_ID()} method, since org.compiere.model.PO
 * is not available at compile time (see idempiere/README.md for why: no iDempiere Maven
 * artifacts exist, and building against iDempiere's own Tycho/p2 target platform is the
 * exact blocker that has deferred the REST API plugin work, per ADR-ERP-005).
 */
final class BaobabCanonicalMappingEventHandler implements EventHandler {

    private static final String TABLE_NAME_PROPERTY = "tableName";
    private static final String EVENT_DATA_PROPERTY = "event.data";

    private static final Logger LOG = System.getLogger(BaobabCanonicalMappingEventHandler.class.getName());

    private final ServiceTracker<CanonicalMappingResolver, CanonicalMappingResolver> tracker;
    private final CanonicalMappingResolver resolver;
    private final String tenantId;

    /** Production constructor: the resolver is looked up lazily from the tracker on every
     * event, since the mapping bundle's service may come and go independently of this one. */
    BaobabCanonicalMappingEventHandler(
            ServiceTracker<CanonicalMappingResolver, CanonicalMappingResolver> tracker, String tenantId) {
        this.tracker = tracker;
        this.resolver = null;
        this.tenantId = tenantId;
    }

    /** Test constructor: bypasses OSGi service tracking entirely. */
    BaobabCanonicalMappingEventHandler(CanonicalMappingResolver resolver, String tenantId) {
        this.tracker = null;
        this.resolver = resolver;
        this.tenantId = tenantId;
    }

    @Override
    public void handleEvent(Event event) {
        if (tenantId == null || tenantId.isBlank()) {
            LOG.log(Level.WARNING, "baobab.tenant.id is not set; ignoring {0}", event.getTopic());
            return;
        }

        Object tableNameProperty = event.getProperty(TABLE_NAME_PROPERTY);
        if (!(tableNameProperty instanceof String tableName) || tableName.isBlank()) {
            LOG.log(Level.WARNING, "Event {0} has no tableName property; ignoring", event.getTopic());
            return;
        }

        int recordId;
        try {
            recordId = readRecordId(event.getProperty(EVENT_DATA_PROPERTY));
        } catch (ReflectiveOperationException e) {
            LOG.log(Level.WARNING, "Could not read record id from event " + event.getTopic(), e);
            return;
        }

        CanonicalMappingResolver activeResolver = resolveActiveResolver();
        if (activeResolver == null) {
            LOG.log(Level.WARNING, "CanonicalMappingResolver service is not available; ignoring {0} for {1}#{2}",
                    event.getTopic(), tableName, recordId);
            return;
        }

        try {
            String canonicalId = activeResolver.resolveToCanonical(tenantId, tableName, recordId);
            LOG.log(Level.INFO, "Resolved {0}#{1} to canonical id {2} for tenant {3}",
                    tableName, recordId, canonicalId, tenantId);
        } catch (MappingNotFoundException e) {
            LOG.log(Level.INFO, "No canonical mapping yet for {0}#{1} (tenant {2}): {3}",
                    tableName, recordId, tenantId, e.getMessage());
        }
    }

    private CanonicalMappingResolver resolveActiveResolver() {
        return tracker != null ? tracker.getService() : resolver;
    }

    /** Calls the no-arg {@code get_ID()} method that every org.compiere.model.PO subclass
     * exposes, without requiring that class at compile time. */
    private static int readRecordId(Object po) throws ReflectiveOperationException {
        if (po == null) {
            throw new NoSuchMethodException("event has no \"" + EVENT_DATA_PROPERTY + "\" property");
        }
        Method getId = po.getClass().getMethod("get_ID");
        return (Integer) getId.invoke(po);
    }
}
