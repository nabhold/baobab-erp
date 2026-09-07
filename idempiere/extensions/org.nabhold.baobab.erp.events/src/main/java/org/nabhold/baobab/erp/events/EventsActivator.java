package org.nabhold.baobab.erp.events;

import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.util.Dictionary;
import java.util.Hashtable;
import org.nabhold.baobab.erp.context.ContextResolver;
import org.nabhold.baobab.erp.mapping.CanonicalMappingResolver;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;
import org.osgi.service.event.EventConstants;
import org.osgi.service.event.EventHandler;
import org.osgi.util.tracker.ServiceTracker;

/**
 * Subscribes {@link BaobabCanonicalMappingEventHandler} to iDempiere's own
 * PO_POST_CREATE/PO_POST_UPADTE OSGi events for C_BPartner. Uses {@link ServiceTracker}s
 * for ContextResolver and CanonicalMappingResolver rather than direct
 * {@code getServiceReference} calls at start() time, since OSGi does not guarantee this
 * bundle starts after org.nabhold.baobab.erp.context/.mapping.
 */
public final class EventsActivator implements BundleActivator {

    private static final String TOPIC_PO_POST_CREATE = "adempiere/po/postCreate";
    private static final String TOPIC_PO_POST_UPDATE = "adempiere/po/postUpdate";
    private static final String FILTER_C_BPARTNER = "(tableName=C_BPartner)";

    private static final Logger LOG = System.getLogger(EventsActivator.class.getName());

    private ServiceTracker<ContextResolver, ContextResolver> contextTracker;
    private ServiceTracker<CanonicalMappingResolver, CanonicalMappingResolver> mappingTracker;

    @Override
    public void start(BundleContext context) {
        LOG.log(Level.INFO, "Baobab ERP events bundle starting");
        contextTracker = new ServiceTracker<>(context, ContextResolver.class, null);
        contextTracker.open();
        mappingTracker = new ServiceTracker<>(context, CanonicalMappingResolver.class, null);
        mappingTracker.open();

        BaobabCanonicalMappingEventHandler handler =
                new BaobabCanonicalMappingEventHandler(contextTracker, mappingTracker);

        Dictionary<String, Object> properties = new Hashtable<>();
        properties.put(EventConstants.EVENT_TOPIC, new String[] {TOPIC_PO_POST_CREATE, TOPIC_PO_POST_UPDATE});
        properties.put(EventConstants.EVENT_FILTER, FILTER_C_BPARTNER);
        context.registerService(EventHandler.class.getName(), handler, properties);
    }

    @Override
    public void stop(BundleContext context) {
        LOG.log(Level.INFO, "Baobab ERP events bundle stopping");
        if (contextTracker != null) {
            contextTracker.close();
        }
        if (mappingTracker != null) {
            mappingTracker.close();
        }
    }
}
