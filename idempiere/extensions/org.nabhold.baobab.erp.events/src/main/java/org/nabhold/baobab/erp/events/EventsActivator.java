package org.nabhold.baobab.erp.events;

import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.util.Dictionary;
import java.util.Hashtable;
import org.nabhold.baobab.erp.mapping.CanonicalMappingResolver;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;
import org.osgi.service.event.EventConstants;
import org.osgi.service.event.EventHandler;
import org.osgi.util.tracker.ServiceTracker;

/**
 * Subscribes {@link BaobabCanonicalMappingEventHandler} to iDempiere's own
 * PO_POST_CREATE/PO_POST_UPADTE OSGi events for C_BPartner. Uses a {@link ServiceTracker}
 * for CanonicalMappingResolver rather than a direct {@code getServiceReference} call at
 * start() time, since OSGi does not guarantee this bundle starts after
 * org.nabhold.baobab.erp.mapping.
 */
public final class EventsActivator implements BundleActivator {

    /** System property naming the tenant this iDempiere instance serves; see
     * BaobabMappingResolver.BASE_URL_PROPERTY for the matching pattern and gap note. */
    static final String TENANT_ID_PROPERTY = "baobab.tenant.id";

    private static final String TOPIC_PO_POST_CREATE = "adempiere/po/postCreate";
    private static final String TOPIC_PO_POST_UPDATE = "adempiere/po/postUpdate";
    private static final String FILTER_C_BPARTNER = "(tableName=C_BPartner)";

    private static final Logger LOG = System.getLogger(EventsActivator.class.getName());

    private ServiceTracker<CanonicalMappingResolver, CanonicalMappingResolver> tracker;

    @Override
    public void start(BundleContext context) {
        LOG.log(Level.INFO, "Baobab ERP events bundle starting");
        tracker = new ServiceTracker<>(context, CanonicalMappingResolver.class, null);
        tracker.open();

        BaobabCanonicalMappingEventHandler handler = new BaobabCanonicalMappingEventHandler(
                tracker, System.getProperty(TENANT_ID_PROPERTY));

        Dictionary<String, Object> properties = new Hashtable<>();
        properties.put(EventConstants.EVENT_TOPIC, new String[] {TOPIC_PO_POST_CREATE, TOPIC_PO_POST_UPDATE});
        properties.put(EventConstants.EVENT_FILTER, FILTER_C_BPARTNER);
        context.registerService(EventHandler.class.getName(), handler, properties);
    }

    @Override
    public void stop(BundleContext context) {
        LOG.log(Level.INFO, "Baobab ERP events bundle stopping");
        if (tracker != null) {
            tracker.close();
        }
    }
}
