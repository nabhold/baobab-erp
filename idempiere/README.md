# iDempiere Runtime and Extensions

This directory holds everything specific to running iDempiere as the Baobab ERP engine
and extending it. See ADR-ERP-001 and ADR-ERP-004 for the accepted architecture.

## Layout

| Path | Purpose |
|---|---|
| `Dockerfile` | Builds a deployable image from the pinned upstream iDempiere release plus this repository's OSGi extension bundles |
| `extensions/` | Baobab-owned OSGi bundles, one Maven module per bundle, under the `org.nabhold.baobab.erp.*` namespace |
| `features/` | Feature/repository groupings for installing extension bundles as a set (placeholder until more than two bundles exist) |
| `patches/` | Reserved for unavoidable upstream patches; empty by policy — see below |

## Extend, do not fork

Baobab does not maintain a long-lived fork of iDempiere core. Every Baobab behaviour is
implemented as a separately deployable OSGi bundle installed alongside upstream iDempiere,
using supported extension points (event handlers, model validators, web services, OSGi
services). `idempiere/patches/` exists only for the exceptional case described in
ADR-ERP-004: a patch requires its own ADR demonstrating that no supported extension
mechanism can satisfy the requirement. It is empty because no such case has arisen.

## Namespaces

```text
org.nabhold.baobab.erp.core
org.nabhold.baobab.erp.context
org.nabhold.baobab.erp.mapping
org.nabhold.baobab.erp.integration
org.nabhold.baobab.erp.events
org.nabhold.baobab.erp.reconciliation
org.nabhold.baobab.erp.security
org.nabhold.baobab.erp.provisioning
```

Two bundles exist today (`context`, `mapping`) as working examples of the pattern: an
`Activator` registering an OSGi service, a narrow interface expressing the ADR's contract,
and a foundation-stage implementation that fails closed rather than fabricating behaviour.
The remaining namespaces are reserved and unimplemented; do not create empty placeholder
bundles for them before there is a real extension point to fill.

## Building

```bash
cd idempiere/extensions
mvn -q package
```

Each module produces a manifest-complete OSGi bundle jar under `target/`. `Dockerfile`
builds these itself (a `maven:3.9-eclipse-temurin-17` stage) and copies the jars straight
into the pinned image's plugins directory (`/opt/idempiere/plugins`) — `docker build -f
idempiere/Dockerfile .` is self-contained, no separate `mvn package` step required first.
A p2/feature repository (`features/`) is unnecessary at two bundles; see that
directory's README for when it would be worth adding.

## Third-party plugins are not automatic

Copying a jar into the plugins directory (as `Dockerfile` does for our own bundles) only
works for plugins that ship as a plain OSGi bundle. Some third-party plugins — notably
the REST API (`com.trekglobal.idempiere.rest.api`, see
`modules/integration/idempiere_client.py`) — are distributed as source that must be
built with Maven/Tycho and installed into a running instance through iDempiere's own p2
provisioning tooling (`update-rest-extensions.sh` in
[bxservice/idempiere-rest](https://github.com/bxservice/idempiere-rest)), not by copying
a jar at image-build time. That installation is not yet wired into `Dockerfile` or
`compose.yaml`; until it is, `idempiere` in this repository's runtime has no REST API to
answer `RestIdempiereClient`'s requests, even though the client itself is real and
tested. Tracked in `architecture/conformance.yaml` against ADR-ERP-005 and ADR-ERP-013.

## Runtime dependency

iDempiere 13 "Orion" LTS targets Java 17 and PostgreSQL. Both extension modules compile
against Java 17 and OSGi Core R6, matching iDempiere's own Equinox runtime.
