# Pinned upstream iDempiere release plus Baobab OSGi extension bundles.
# See idempiere/README.md and ADR-ERP-001 / ADR-ERP-004.
ARG IDEMPIERE_IMAGE=idempiereofficial/idempiere:13-release

FROM ${IDEMPIERE_IMAGE}

# Verify this path against the pinned base image before a production build; it follows
# the Equinox convention used by the official image at the time this was written, but is
# not guaranteed stable across upstream releases.
ARG IDEMPIERE_PLUGINS_DIR=/opt/idempiere-server/plugins

COPY extensions/org.nabhold.baobab.erp.context/target/org.nabhold.baobab.erp.context-*.jar ${IDEMPIERE_PLUGINS_DIR}/
COPY extensions/org.nabhold.baobab.erp.mapping/target/org.nabhold.baobab.erp.mapping-*.jar ${IDEMPIERE_PLUGINS_DIR}/
