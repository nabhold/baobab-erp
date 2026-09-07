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

Four bundles exist today:

- `context` and `mapping`: an `Activator` registering an OSGi service, a narrow
  interface expressing the ADR's contract, and a real implementation that calls
  baobab-app's HTTP API (`/context/resolve`, `/mapping/resolve*`) and fails closed on
  any error rather than guessing.
- `integration`: a library bundle (no `Activator`, no OSGi service of its own) that
  `context` and `mapping` both depend on. It's the one place that knows how to reach
  baobab-app over HTTP and parse its (small, flat) JSON responses -- everything inside
  iDempiere's JVM that needs the `baobab` Postgres schema goes through this, since it
  has no direct database access of its own.
- `events`: the first bundle that *consumes* other bundles' OSGi services rather than
  just sharing a library -- it tracks `context`'s `ContextResolver` and `mapping`'s
  `CanonicalMappingResolver` (each via a `ServiceTracker`, since OSGi doesn't guarantee
  bundle start order) and registers a plain `org.osgi.service.event.EventHandler` for
  iDempiere's own `adempiere/po/postCreate`/`adempiere/po/postUpdate` topics, filtered to
  `C_BPartner`, `M_Product`, `C_Order` and `C_Invoice` -- the near-term slice ADR-ERP-007
  §170's own Definition-of-Done checklist names (Party, Product, PurchaseOrder/SalesOrder,
  Supplier/CustomerInvoice); `C_Payment`, `M_InOut` and `M_Warehouse` are in that ADR's
  full mapping matrix but not yet in its checklist, so adding them is a one-line filter
  change whenever a real consumer needs them -- the handler itself reads "tableName"
  generically and was never coupled to any one table. These two topics are iDempiere's
  *asynchronous* model-change events -- they fire on iDempiere's own EventAdmin dispatch
  thread, after the triggering transaction has committed -- so the resulting blocking
  HTTP calls to baobab-app never run inside a document transaction (ADR-ERP-004,
  INV-ERP-EXT-011). On every such event it first derives the owning tenant from the
  changed record's own `AD_Client_ID`/`AD_Org_ID` (`ContextResolver.resolveTenant`, the
  reverse of `context`'s usual direction), then resolves the record's canonical identity
  (`CanonicalMappingResolver.resolveToCanonical`). Deriving the tenant per record, rather
  than assuming one tenant for the whole process, matters because ADR-ERP-003's default
  topology (`ERP_SHARED_INSTANCE_DEDICATED_CLIENT`) has one iDempiere runtime hosting
  several `AD_Client`s (tenants) at once. This closes the ADR-ERP-007 gap that used to
  read "no extension point inside iDempiere invokes the registered
  CanonicalMappingResolver service during a real request yet" -- for these four tables,
  one now genuinely does, correctly, across every tenant sharing the instance. It needs no
  iDempiere Maven artifact at compile time: iDempiere's own `AbstractEventHandler` is
  built entirely on the standard OSGi `org.osgi.service.event.EventHandler` contract
  (verified directly against `github.com/idempiere/idempiere`), which is on Maven Central
  under the same `org.osgi` groupId as `org.osgi.core`. The only iDempiere-shaped values
  this bundle touches -- a changed record's numeric id, `AD_Client_ID` and `AD_Org_ID` --
  are read via reflective calls to the PO object's `get_ID()`, `getAD_Client_ID()` and
  `getAD_Org_ID()` methods, since `org.compiere.model.PO` itself isn't on the compile
  classpath.

The remaining namespaces are reserved and unimplemented; do not create empty placeholder
bundles for them before there is a real extension point to fill.

All three resolver-backed bundles read baobab-app's base URL from the
`baobab.app.base.url` system property, defaulting to `http://baobab-app:8000` (the
Compose service name/port from `compose.yaml`, so the default already works for that
topology unmodified). Overriding it in a real deployment means passing
`-Dbaobab.app.base.url=...` to iDempiere's own JVM launch, which isn't wired up here yet
-- it depends on the pinned base image's own entrypoint/launcher mechanism. `events` needs
no comparable per-tenant configuration of its own: it derives the tenant per event from
data already on the record, over the same already-defaulted baobab-app connection.

## Building

```bash
cd idempiere/extensions
mvn -q package
```

Each module produces a manifest-complete OSGi bundle jar under `target/`. `Dockerfile`
builds these itself (a `maven:3.9-eclipse-temurin-17` stage) and copies the jars straight
into the pinned image's plugins directory (`/opt/idempiere/plugins`) — `docker build -f
idempiere/Dockerfile .` is self-contained, no separate `mvn package` step required first.
A p2/feature repository (`features/`) is unnecessary at four bundles; see that
directory's README for when it would be worth adding.

`mvn test` (or `mvn package`, which runs tests first) exercises `context`'s and
`mapping`'s HTTP calls to baobab-app against a real local server
(`com.sun.net.httpserver.HttpServer`, part of the JDK, no extra test dependency)
reproducing baobab-app's actual response shapes -- not mocked. `events`' tests build a
real `org.osgi.service.event.Event` (also not mocked) against small recording
`ContextResolver`/`CanonicalMappingResolver` doubles, since its own job is proving it
extracts AD_Client_ID/AD_Org_ID/table/record id correctly from a real event and derives
the tenant per event, not re-proving `context`'s or `mapping`'s already-tested HTTP wire
format. `idempiere/Dockerfile`'s build stage passes `-DskipTests` since CI's
`build-extensions` job already runs them separately for faster feedback.

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

iDempiere 13 "Orion" LTS targets Java 17 and PostgreSQL. All four extension modules
compile against Java 17 and OSGi Core R6, matching iDempiere's own Equinox runtime.
`events` additionally compiles against the standard OSGi compendium APIs
`org.osgi.service.event` and `org.osgi.util.tracker` (both on Maven Central, both
provided by iDempiere's own Equinox runtime, so neither is bundled into our jar).
