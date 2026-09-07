# Integration Architecture

## Inbound

Trade and Pulse send versioned JSON event envelopes over HTTPS to `POST /events/inbound`
on the `baobab-app` service (`modules/application/server.py`). Sensitive machine events
use `HMAC-SHA256` in `X-Baobab-Signature`, verified by `modules/security` before the
envelope is even parsed. The receiver (`modules/inbox`, backed by
`modules/inbox/postgres_store.py`) deduplicates on `event_id` and records the event; a
duplicate delivery gets a 200 response, not reprocessing.

## Outbound

ERP state changes record a row in `baobab.event_outbox` (`modules/outbox`, backed by
`modules/outbox/postgres_store.py`) in the same database transaction as the operational
change -- `record()` deliberately does not commit, so the caller's transaction covers
both. `modules/application/dispatch_worker.py` drains pending/retry rows through
`modules/integration`'s webhook transport with bounded exponential backoff
(`outbox.service.backoff_seconds`); exhausted events move to a dead-letter state for
operator action. The worker runs to completion and exits -- run it on a schedule (cron, a
systemd timer) rather than as a long-lived daemon.

## APIs

- `modules/integration.idempiere_client` is the only module aware of iDempiere's actual
  API shape; every other module deals in canonical types.
- `RestIdempiereClient` talks to iDempiere's REST API (the
  `com.trekglobal.idempiere.rest.api` / `bxservice/idempiere-rest` plugin): one-step
  JWT login (`POST /auth/tokens` with client/role/org/warehouse), automatic token
  refresh (`POST /auth/refresh`) and one re-login retry on an unexpected 401, then
  `GET/POST/PUT /models/{table}(/{id})`. Verified against that project's OpenAPI spec,
  not assumed; see the module docstring and `tests/unit/test_idempiere_client.py`
  (which runs against a real local HTTP server reproducing the spec's request/response
  shapes, not a mocked urllib).
- Add narrow, whitelisted operations for Baobab orchestration or stable business
  commands, not a 1:1 mirror of iDempiere windows/tabs.
- Service identities receive the narrowest role set possible (`modules/identity`);
  administrator credentials are never used by other engines.
- Every integration request carries tenant, legal-entity, correlation, and authenticated
  actor/service context, resolved through `modules/context` before any business logic
  runs.

Pulse supplies signals and opportunities. It cannot write iDempiere tables directly; an
ERP command handler decides whether and how intelligence becomes an operational record.

## From inside iDempiere

Code running inside iDempiere's own JVM (the OSGi bundles in `idempiere/extensions/`)
has no direct access to the `baobab` Postgres schema either -- it reaches the same
context/mapping resolution logic over HTTP, calling baobab-app's
`GET /context/resolve(-tenant)` and `GET /mapping/resolve(-canonical)` endpoints. The
shared `org.nabhold.baobab.erp.integration` bundle (`BaobabAppClient`, a small
dependency-free JSON parser) is the one place that knows how to make that call;
`context`, `mapping` and `events` each depend on it rather than duplicating HTTP/JSON
handling. This keeps "who touches the `baobab` schema" answered the same way from both
sides of the process boundary: only `modules/`, via baobab-app.

The `events` bundle is the other direction: a real iDempiere-fired event, not a
Baobab-initiated call. It registers a plain `org.osgi.service.event.EventHandler` for
iDempiere's own `adempiere/po/postCreate`/`adempiere/po/postUpdate` topics (filtered to
`C_BPartner`, `M_Product`, `C_Order` and `C_Invoice` -- ADR-ERP-007 §170's near-term
mapping-matrix slice; `C_Payment`, `M_InOut` and `M_Warehouse` are in that matrix too,
just not wired yet), which fire asynchronously, after the record's own transaction has
committed. When one fires, it first calls the registered `ContextResolver` service
(from `context`) to turn the changed record's own `AD_Client_ID`/`AD_Org_ID` into a
tenant -- `GET /context/resolve-tenant`, the reverse of `context`'s usual direction --
then calls the registered `CanonicalMappingResolver` service (from `mapping`) to resolve
the record's canonical identity for that tenant -- `GET /mapping/resolve-canonical`,
the same call `mapping` already makes, just triggered by iDempiere itself instead of a
test. Resolving the tenant per event, rather than assuming one tenant for the whole
process, is required by ADR-ERP-003's default deployment topology
(`ERP_SHARED_INSTANCE_DEDICATED_CLIENT`): one iDempiere runtime commonly hosts several
`AD_Client`s (tenants) at once, so a process-wide tenant would silently misattribute (or
drop) every other tenant's events.

## Status

The HTTP layer (including `/context/resolve(-tenant)` and `/mapping/resolve*`),
outbox/inbox, and their Postgres-backed stores are wired end-to-end and covered by
`tests/integration/` against a real database. `BaobabContextResolver` and
`BaobabMappingResolver` now call those endpoints for real, tested against a real local
HTTP server reproducing baobab-app's exact response shapes (not mocked) -- see each
bundle's `src/test/java/.../*ResolverTest.java`. `RestIdempiereClient` is a real, spec-verified
implementation, tested the same way against a fake server reproducing the
`bxservice/idempiere-rest` spec -- but not yet against a real running iDempiere
instance, because that REST API plugin **is not part of the pinned
`idempiereofficial/idempiere` image**. It's a separate OSGi bundle that has to be built
(Maven/Tycho) into a p2 repository and installed into a running instance through
iDempiere's p2 provisioning tooling. `idempiere/Dockerfile` now does the installation
half of that (a real, verified `update-prd.sh` invocation, gated on a p2 repository
being present at `idempiere/vendor/rest-api-p2/`); the build-the-p2-repository half
still isn't done, since it needs network access this environment doesn't have -- see
`idempiere/rest-api/README.md` for exactly what's confirmed working, what's still
missing, and how to supply one. See also `idempiere/README.md` and
`architecture/conformance.yaml` against ADR-ERP-005 and ADR-ERP-013.
