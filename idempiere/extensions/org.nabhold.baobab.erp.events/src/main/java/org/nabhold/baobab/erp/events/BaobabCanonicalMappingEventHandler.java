package org.nabhold.baobab.erp.events;

import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.lang.reflect.Method;
import org.nabhold.baobab.erp.context.ContextResolver;
import org.nabhold.baobab.erp.context.ContextResolver.ContextResolutionException;
import org.nabhold.baobab.erp.context.ContextResolver.TenantIdentity;
import org.nabhold.baobab.erp.mapping.CanonicalMappingResolver;
import org.nabhold.baobab.erp.mapping.CanonicalMappingResolver.MappingNotFoundException;
import org.osgi.service.event.Event;
import org.osgi.service.event.EventHandler;
import org.osgi.util.tracker.ServiceTracker;

/**
 * Reacts to a real, iDempiere-fired PO_POST_CREATE/PO_POST_UPADTE event on C_BPartner by
 * deriving the owning tenant from the changed record's own AD_Client_ID/AD_Org_ID
 * (ContextResolver.resolveTenant, ADR-ERP-002) and then resolving its canonical Party
 * identity (CanonicalMappingResolver.resolveToCanonical, ADR-ERP-007). The tenant is
 * derived per event, never assumed for the whole process, because ADR-ERP-003's default
 * topology (ERP_SHARED_INSTANCE_DEDICATED_CLIENT) has one iDempiere runtime hosting
 * several AD_Clients (tenants) at once. Both resolutions are real HTTP calls to
 * baobab-app; PO_POST_CREATE/PO_POST_UPADTE fire asynchronously, after the triggering
 * transaction has committed (see org.compiere.model.PO#processAfterSave), so neither
 * runs inside a document transaction (ADR-ERP-004, INV-ERP-EXT-011).
 *
 * <p>This bundle has no compile-time dependency on any iDempiere class: the event's
 * "tableName" property is a plain String set by iDempiere's own EventManager, and the
 * only iDempiere-shaped values this class touches -- the PO's record id, AD_Client_ID
 * and AD_Org_ID -- are read via reflective calls to its public {@code get_ID()},
 * {@code getAD_Client_ID()} and {@code getAD_Org_ID()} methods, since
 * org.compiere.model.PO is not available at compile time (see idempiere/README.md for
 * why: no iDempiere Maven artifacts exist, and building against iDempiere's own
 * Tycho/p2 target platform is the exact blocker that has deferred the REST API plugin
 * work, per ADR-ERP-005).
 */
final class BaobabCanonicalMappingEventHandler implements EventHandler {

    private static final String TABLE_NAME_PROPERTY = "tableName";
    private static final String EVENT_DATA_PROPERTY = "event.data";

    private static final Logger LOG = System.getLogger(BaobabCanonicalMappingEventHandler.class.getName());

    private final ServiceTracker<ContextResolver, ContextResolver> contextTracker;
    private final ServiceTracker<CanonicalMappingResolver, CanonicalMappingResolver> mappingTracker;
    private final ContextResolver contextResolver;
    private final CanonicalMappingResolver mappingResolver;

    /** Production constructor: both resolvers are looked up lazily from their trackers on
     * every event, since either bundle's service may come and go independently. */
    BaobabCanonicalMappingEventHandler(
            ServiceTracker<ContextResolver, ContextResolver> contextTracker,
            ServiceTracker<CanonicalMappingResolver, CanonicalMappingResolver> mappingTracker) {
        this.contextTracker = contextTracker;
        this.mappingTracker = mappingTracker;
        this.contextResolver = null;
        this.mappingResolver = null;
    }

    /** Test constructor: bypasses OSGi service tracking entirely. */
    BaobabCanonicalMappingEventHandler(ContextResolver contextResolver, CanonicalMappingResolver mappingResolver) {
        this.contextTracker = null;
        this.mappingTracker = null;
        this.contextResolver = contextResolver;
        this.mappingResolver = mappingResolver;
    }

    @Override
    public void handleEvent(Event event) {
        Object tableNameProperty = event.getProperty(TABLE_NAME_PROPERTY);
        if (!(tableNameProperty instanceof String tableName) || tableName.isBlank()) {
            LOG.log(Level.WARNING, "Event {0} has no tableName property; ignoring", event.getTopic());
            return;
        }

        Object po = event.getProperty(EVENT_DATA_PROPERTY);
        int recordId;
        int adClientId;
        int adOrgId;
        try {
            recordId = invokeIntGetter(po, "get_ID");
            adClientId = invokeIntGetter(po, "getAD_Client_ID");
            adOrgId = invokeIntGetter(po, "getAD_Org_ID");
        } catch (ReflectiveOperationException e) {
            LOG.log(Level.WARNING, "Could not read record/client/org id from event " + event.getTopic(), e);
            return;
        }

        ContextResolver activeContextResolver = contextTracker != null ? contextTracker.getService() : contextResolver;
        if (activeContextResolver == null) {
            LOG.log(Level.WARNING, "ContextResolver service is not available; ignoring {0} for {1}#{2}",
                    event.getTopic(), tableName, recordId);
            return;
        }

        String tenantId;
        try {
            TenantIdentity tenant = activeContextResolver.resolveTenant(adClientId, adOrgId);
            tenantId = tenant.tenantId();
        } catch (ContextResolutionException e) {
            LOG.log(Level.INFO, "No tenant mapping yet for AD_Client_ID={0} AD_Org_ID={1}: {2}",
                    adClientId, adOrgId, e.getMessage());
            return;
        }

        CanonicalMappingResolver activeMappingResolver = mappingTracker != null ? mappingTracker.getService() : mappingResolver;
        if (activeMappingResolver == null) {
            LOG.log(Level.WARNING, "CanonicalMappingResolver service is not available; ignoring {0} for {1}#{2}",
                    event.getTopic(), tableName, recordId);
            return;
        }

        try {
            String canonicalId = activeMappingResolver.resolveToCanonical(tenantId, tableName, recordId);
            LOG.log(Level.INFO, "Resolved {0}#{1} to canonical id {2} for tenant {3}",
                    tableName, recordId, canonicalId, tenantId);
        } catch (MappingNotFoundException e) {
            LOG.log(Level.INFO, "No canonical mapping yet for {0}#{1} (tenant {2}): {3}",
                    tableName, recordId, tenantId, e.getMessage());
        }
    }

    /** Calls a no-arg int-returning method that every org.compiere.model.PO subclass
     * exposes, without requiring that class at compile time. */
    private static int invokeIntGetter(Object po, String methodName) throws ReflectiveOperationException {
        if (po == null) {
            throw new NoSuchMethodException("event has no \"" + EVENT_DATA_PROPERTY + "\" property");
        }
        Method getter = po.getClass().getMethod(methodName);
        return (Integer) getter.invoke(po);
    }
}
