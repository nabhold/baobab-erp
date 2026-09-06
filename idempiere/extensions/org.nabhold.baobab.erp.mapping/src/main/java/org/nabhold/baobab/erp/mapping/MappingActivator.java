package org.nabhold.baobab.erp.mapping;

import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;

public final class MappingActivator implements BundleActivator {

    private static final Logger LOG = System.getLogger(MappingActivator.class.getName());

    @Override
    public void start(BundleContext context) {
        LOG.log(Level.INFO, "Baobab ERP mapping bundle starting");
        context.registerService(CanonicalMappingResolver.class, new BaobabMappingResolver(), null);
    }

    @Override
    public void stop(BundleContext context) {
        LOG.log(Level.INFO, "Baobab ERP mapping bundle stopping");
    }
}
