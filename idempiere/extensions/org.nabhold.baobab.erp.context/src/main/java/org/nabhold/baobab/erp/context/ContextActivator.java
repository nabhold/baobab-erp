package org.nabhold.baobab.erp.context;

import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;

/**
 * Registers the Baobab context-resolution service into iDempiere's OSGi runtime.
 * Production wiring replaces the {@link System.Logger} placeholder with iDempiere's
 * own logging facility (CLogger) once this bundle is installed against a running
 * instance rather than built standalone.
 */
public final class ContextActivator implements BundleActivator {

    private static final Logger LOG = System.getLogger(ContextActivator.class.getName());

    @Override
    public void start(BundleContext context) {
        LOG.log(Level.INFO, "Baobab ERP context bundle starting");
        context.registerService(ContextResolver.class, new BaobabContextResolver(), null);
    }

    @Override
    public void stop(BundleContext context) {
        LOG.log(Level.INFO, "Baobab ERP context bundle stopping");
    }
}
