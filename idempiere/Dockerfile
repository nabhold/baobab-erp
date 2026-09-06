# Pinned upstream iDempiere release plus Baobab OSGi extension bundles.
# See idempiere/README.md and ADR-ERP-001 / ADR-ERP-004.
#
# Build context is the repository root (see compose.yaml: context: ., dockerfile:
# idempiere/Dockerfile), so COPY sources below are rooted at the repo root, not at
# this directory.
ARG IDEMPIERE_IMAGE=idempiereofficial/idempiere:13-release

FROM ${IDEMPIERE_IMAGE}

# Confirmed against idempiere/idempiere-docker's 13-release Dockerfile: IDEMPIERE_HOME
# is /opt/idempiere, IDEMPIERE_PLUGINS_HOME is $IDEMPIERE_HOME/plugins, and the image
# already creates and runs as a non-root "idempiere" user owning that tree.
ARG IDEMPIERE_PLUGINS_DIR=/opt/idempiere/plugins

COPY --chown=idempiere:idempiere idempiere/extensions/org.nabhold.baobab.erp.context/target/org.nabhold.baobab.erp.context-*.jar ${IDEMPIERE_PLUGINS_DIR}/
COPY --chown=idempiere:idempiere idempiere/extensions/org.nabhold.baobab.erp.mapping/target/org.nabhold.baobab.erp.mapping-*.jar ${IDEMPIERE_PLUGINS_DIR}/

USER idempiere
