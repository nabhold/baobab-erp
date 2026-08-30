# Integration Architecture

## Inbound

Trade and Pulse send versioned JSON envelopes over HTTPS. Sensitive machine events use `HMAC-SHA256` in `X-Baobab-Signature`. The receiver verifies the raw body, inserts a unique inbox record, acknowledges duplicates, and queues processing.

The event ID is the idempotency key. Correlation IDs follow a business operation across engines; causation IDs may link derived events.

## Outbound

ERP state changes create an outbox record in the same database transaction as the operational change. A scheduler queues delivery. Delivery uses bounded retries with exponential backoff and jitter, then moves exhausted events to a dead-letter state for operator action.

Transport configuration is not hard-coded in the app. Endpoint allowlists, authentication material, timeouts, and retry ceilings belong in site/deployment configuration.

## APIs

- Use standard Frappe resource APIs for native DocTypes when their permission and validation semantics are sufficient.
- Add whitelisted methods only for Baobab orchestration or stable business commands.
- Service users receive narrow roles; administrator credentials are never used by other engines.
- Every integration request carries tenant, legal-entity, correlation, and authenticated actor/service context.

Pulse supplies signals and opportunities. It cannot write ERPNext tables directly; an ERP command handler decides whether and how intelligence becomes an Opportunity, Project input, forecast annotation, or other operational record.
