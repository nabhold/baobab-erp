# Integration Architecture

## Inbound

Trade and Pulse send versioned JSON event envelopes over HTTPS. Sensitive machine events
use `HMAC-SHA256` in `X-Baobab-Signature`, verified by `modules/security`. The receiver
(`modules/inbox`) verifies the raw body, deduplicates on `event_id`, and records the event
for processing; a duplicate delivery is acknowledged, not reprocessed.

## Outbound

ERP state changes record a row in `baobab.event_outbox` (`modules/outbox`) in the same
database transaction as the operational change. A scheduler drains pending/retry rows
through `modules/integration`'s webhook transport with bounded exponential backoff
(`outbox.service.backoff_seconds`); exhausted events move to a dead-letter state for
operator action.

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

`modules/integration.idempiere_client.UnconfiguredIdempiereClient` and the OSGi bundles'
`BaobabContextResolver`/`BaobabMappingResolver` deliberately fail closed today; wiring a
real iDempiere-facing implementation is tracked in `architecture/conformance.yaml` against
ADR-ERP-005 and ADR-ERP-007.
