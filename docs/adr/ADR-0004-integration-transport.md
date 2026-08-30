# ADR-0004: REST and Signed Events Before a Broker

- Status: Accepted
- Date: 2026-08-30

## Decision

Use HTTPS REST/Frappe APIs, webhooks, signed JSON events, an idempotent inbox, and a transactional outbox. Do not introduce Kafka or another broker until measured throughput, ordering, replay, or availability requirements exceed this design.

## Consequences

The system has fewer moving parts and clear contracts. Delivery is at least once, so consumers must be idempotent. Broker adoption remains possible behind the outbox boundary later.
