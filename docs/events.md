# Canonical Events

Per ADR-ERP-006, ERP events:

- describe meaningful business facts (`erp.<noun>.<verb>.v1`, e.g.
  `erp.purchase-order.completed.v1`);
- use canonical Baobab identity, never an iDempiere native ID;
- carry an explicit Context (`tenant_id`, `entity_id`, `correlation_id`);
- are recorded transactionally through `modules/outbox` before being published;
- support at-least-once delivery — consumers must be idempotent (`modules/inbox`
  demonstrates the required pattern on the receiving side);
- evolve through explicit schema versions (`contracts/events/envelope.schema.json`).

## Envelope

The common envelope shape is `modules/events/envelope.py::EventEnvelope`, validated
against `contracts/events/envelope.schema.json`. Every example under
`contracts/events/examples/` is checked against both in
`tests/contract/test_envelope_examples.py` — the schema and the code that actually
parses events are not allowed to drift apart.

## Delivery

`modules/outbox.service.dispatch_pending` drains pending/retry rows through an
`EventTransport`; `modules/integration.delivery_transport.deliver` is the concrete
webhook-based transport, signing every payload with `modules/security.signing.sign_body`.
Failed deliveries retry with exponential backoff (`outbox.service.backoff_seconds`, capped
at one hour) up to `outbox.service.MAX_ATTEMPTS` before moving to a dead-letter state.
