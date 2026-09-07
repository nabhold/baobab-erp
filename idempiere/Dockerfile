# Multi-stage build: compile the Baobab OSGi extension bundles, then stage them into
# the pinned iDempiere runtime image. This is self-contained -- `docker build -f
# idempiere/Dockerfile .` needs no separate `mvn package` step first, since generic
# tooling (including this repository's own foundation/vulnerability-scan workflow)
# invokes `docker build` directly with no knowledge of a Maven prerequisite.
#
# Build context is the repository root (see compose.yaml: context: ., dockerfile:
# idempiere/Dockerfile), so COPY sources below are rooted at the repo root, not at
# this directory.
ARG IDEMPIERE_IMAGE=idempiereofficial/idempiere:13-release

FROM maven:3.9-eclipse-temurin-17 AS extensions-builder
WORKDIR /build
COPY idempiere/extensions/ idempiere/extensions/
RUN mvn -q -B -f idempiere/extensions package -DskipTests

FROM ${IDEMPIERE_IMAGE}

# Pick up upstream Ubuntu security patches the pinned base image itself may be
# behind on (e.g. openssl). This patches OS packages only; it does not touch
# iDempiere or its bundled plugin jars, so it isn't a fork under ADR-ERP-004.
USER root
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Confirmed against idempiere/idempiere-docker's 13-release Dockerfile: IDEMPIERE_HOME
# is /opt/idempiere, IDEMPIERE_PLUGINS_HOME is $IDEMPIERE_HOME/plugins, and the image
# already creates and runs as a non-root "idempiere" user owning that tree.
ARG IDEMPIERE_PLUGINS_DIR=/opt/idempiere/plugins

COPY --from=extensions-builder --chown=idempiere:idempiere /build/idempiere/extensions/org.nabhold.baobab.erp.integration/target/org.nabhold.baobab.erp.integration-*.jar ${IDEMPIERE_PLUGINS_DIR}/
COPY --from=extensions-builder --chown=idempiere:idempiere /build/idempiere/extensions/org.nabhold.baobab.erp.context/target/org.nabhold.baobab.erp.context-*.jar ${IDEMPIERE_PLUGINS_DIR}/
COPY --from=extensions-builder --chown=idempiere:idempiere /build/idempiere/extensions/org.nabhold.baobab.erp.mapping/target/org.nabhold.baobab.erp.mapping-*.jar ${IDEMPIERE_PLUGINS_DIR}/

USER idempiere
