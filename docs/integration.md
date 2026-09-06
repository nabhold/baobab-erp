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
- Add narrow, whitelisted operations for Baobab orchestration or stable business
  commands, not a 1:1 mirror of iDempiere windows/tabs.
- Service identities receive the narrowest role set possible (`modules/identity`);
  administrator credentials are never used by other engines.
- Every integration request carries tenant, legal-entity, correlation, and authenticated
  actor/service context, resolved through `modules/context` before any business logic
  runs.

Pulse supplies signals and opportunities. It cannot write iDempiere tables directly; an
ERP command handler decides whether and how intelligence becomes an operational record.

## Status

The HTTP layer, outbox/inbox, and their Postgres-backed stores are wired end-to-end and
covered by `tests/integration/` against a real database. What's still a fail-closed
placeholder: `modules/integration.idempiere_client.UnconfiguredIdempiereClient` (no code
anywhere calls iDempiere's own REST/JSON-RPC API yet) and the OSGi bundles'
`BaobabContextResolver`/`BaobabMappingResolver` (nothing inside iDempiere calls them).
Tracked in `architecture/conformance.yaml` against ADR-ERP-005, ADR-ERP-002 and
ADR-ERP-007.
