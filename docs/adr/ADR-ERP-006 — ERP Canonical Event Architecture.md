# ADR-ERP-006 — ERP Canonical Event Architecture

**Status:** Accepted  
**Decision class:** ERP / Event Architecture / Integration / Messaging / Reliability / Interoperability  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`, Baobab event infrastructure and consuming engines  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-005  
**Date:** 2026-09-02

---

# 1. Decision

The Baobab ERP Engine SHALL participate in the wider platform through a **canonical, contract-first, asynchronous event architecture**.

ERP events SHALL:

- describe meaningful business facts;
- use canonical Baobab identity;
- carry explicit Context;
- remain independent of iDempiere table structure;
- be recorded transactionally through an outbox;
- support at-least-once delivery;
- require idempotent consumption;
- support replay and reconciliation;
- preserve causal and correlation lineage;
- respect tenant isolation;
- respect market and regional data policy;
- evolve through explicit schema versions;
- remain independent of the physical messaging technology.

The architectural flow SHALL be:

```text
ERP business transaction
        │
        ├── native ERP state
        │
        └── canonical event intent
                 │
                 ▼
         Transactional Outbox
                 │
              COMMIT
                 │
                 ▼
          Event Publisher
                 │
                 ▼
        Event Transport Layer
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
    Medusa      CP      Intelligence
       │
       ▼
 other consumers
```

The event transport SHALL NOT define event semantics.

---

# 2. Governing principle

The fundamental rule is:

> **Events describe what happened in the business, not what happened in an iDempiere table.**

Therefore:

```text
GOOD

erp.purchase-order.completed.v1
erp.goods-receipt.completed.v1
erp.supplier-invoice.posted.v1
erp.payment-allocated.v1
```

and not:

```text
BAD

c_order.updated
c_invoice.changed
m_inout.row-created
ad_client.modified
```

---

# 3. Event architecture versus database replication

Canonical events are an interoperability mechanism.

Database replication is an infrastructure mechanism.

They SHALL remain separate.

```text
PostgreSQL replication
        │
        └── availability / recovery

Canonical events
        │
        └── business interoperability
```

PostgreSQL WAL, CDC or replica streams SHALL NOT become the Baobab canonical event contract.

---

# 4. Event contract authority

Machine-readable asynchronous contracts SHALL be maintained under:

```text
nabhold/shared
```

using:

```text
AsyncAPI 3.1.x
```

as the organisational asynchronous API description format.

Individual engines SHALL implement these contracts.

---

# 5. AsyncAPI ownership

Recommended structure:

```text
nabhold/shared/

contracts/
└── events/
    ├── asyncapi.yaml
    │
    ├── common/
    │   ├── envelope.schema.json
    │   ├── context.schema.json
    │   ├── money.schema.json
    │   └── references.schema.json
    │
    ├── erp/
    │   └── v1/
    │       ├── purchase-order-completed.schema.json
    │       ├── goods-receipt-completed.schema.json
    │       ├── supplier-invoice-posted.schema.json
    │       └── payment-allocated.schema.json
    │
    ├── trade/
    ├── content/
    └── control-plane/
```

Exact repository layout MAY evolve.

Contract ownership SHALL not.

---

# 6. Transport independence

The canonical contract SHALL not require a specific broker.

Permitted future implementations may include:

```text
Kafka
NATS
AMQP
AWS EventBridge
AWS SNS/SQS
other approved transport
```

Consumers SHALL depend on:

```text
event contract
```

rather than:

```text
broker-specific message representation
```

---

# 7. CloudEvents alignment

The Baobab event envelope SHALL align with CloudEvents concepts where they fit Baobab requirements.

Core concepts include:

```text
id
source
type
subject
time
dataschema
datacontenttype
data
```

Baobab SHALL add its own governed contextual metadata where necessary.

CloudEvents alignment does not mean that CloudEvents defines Baobab's business taxonomy.

---

# 8. Canonical event envelope

Conceptually:

```json
{
  "specversion": "1.0",
  "id": "<uuid>",
  "source": "baobab://erp/engine-instances/<uuid>",
  "type": "com.nabhold.baobab.erp.supplier-invoice.posted.v1",
  "subject": "canonical-entity/<uuid>",
  "time": "2026-09-02T04:00:00Z",
  "datacontenttype": "application/json",
  "dataschema": "baobab://contracts/erp/supplier-invoice-posted/v1",
  "tenantid": "<uuid>",
  "legalentityid": "<uuid>",
  "marketid": "<uuid>",
  "engineid": "<uuid>",
  "engineinstanceid": "<uuid>",
  "correlationid": "<uuid>",
  "causationid": "<uuid>",
  "traceid": "...",
  "data": {}
}
```

The final physical naming of extension attributes SHALL be standardised in `nabhold/shared`.

---

# 9. Event ID

Every event SHALL have one globally unique immutable:

```text
event_id
```

generated when the event intent is created.

It SHALL NOT change when:

```text
publication retries
broker retries
consumer retries
cross-region forwarding
event replay
```

occur.

---

# 10. Event ID versus business entity ID

These are distinct.

```text
event_id
```

identifies:

> This occurrence.

```text
subject
```

identifies:

> The canonical business entity concerned.

---

# 11. Example

Invoice:

```text
canonical invoice ID
    019...
```

may produce:

```text
event A
    invoice-created

event B
    invoice-completed

event C
    invoice-posted

event D
    invoice-reversed
```

Each has a different `event_id`.

All may reference the same canonical invoice subject.

---

# 12. Source

`source` SHALL identify the canonical producing deployment sufficiently to establish provenance.

It SHALL include or resolve to:

```text
Engine
EngineInstance
```

It SHALL NOT merely contain:

```text
hostname
container ID
pod name
IP address
```

because those are ephemeral infrastructure identities.

---

# 13. Subject

`subject` SHALL normally identify the canonical entity whose lifecycle the event describes.

Example:

```text
canonical supplier invoice UUID
```

not:

```text
C_Invoice_ID = 1000027
```

---

# 14. Event type

Event types SHALL use a stable namespace.

Recommended semantic form:

```text
com.nabhold.baobab.<domain>.<event>.v<major>
```

Example:

```text
com.nabhold.baobab.erp.supplier-invoice.posted.v1
```

A shorter transport alias MAY exist, but canonical contracts SHALL have one authoritative event type.

---

# 15. Event names are past tense

Events describe facts.

Therefore:

```text
purchase-order.completed
supplier-invoice.posted
payment.allocated
```

not:

```text
complete-purchase-order
post-invoice
allocate-payment
```

Those latter forms are commands.

---

# 16. Command/event distinction

```text
COMMAND

PostSupplierInvoice
       │
       ▼
      ERP
       │
       ▼

EVENT

SupplierInvoicePosted
```

A command may fail.

An emitted domain event represents something that has already occurred.

---

# 17. Event time

`time` SHALL represent the relevant occurrence timestamp defined by the event contract.

ERP events may additionally expose:

```text
document_date
accounting_date
posted_at
```

where semantically required.

These SHALL NOT be collapsed into one timestamp.

---

# 18. Context

Every tenant-scoped canonical event SHALL carry enough immutable Context to identify its business boundary.

At minimum where applicable:

```text
tenant_id
legal_entity_id
market_id
engine_id
engine_instance_id
```

Optional dimensions MAY include:

```text
digital_estate_id
organisation_id
jurisdiction
```

when relevant.

---

# 19. Context is historical

Event Context represents the context at the time of the event.

If a tenant later:

```text
changes market
moves EngineInstance
changes capability binding
```

the historical event SHALL NOT be rewritten.

---

# 20. EngineInstance provenance

An event created by:

```text
ERP-AF-SOUTH-01
```

retains that EngineInstance identity even if the tenant later migrates to:

```text
ERP-THAMANI-01
```

This is necessary for audit and reconciliation.

---

# 21. Canonical identity

Payload references SHOULD use canonical identifiers.

Example:

```json
{
  "supplier_id": "<canonical-party-uuid>",
  "invoice_id": "<canonical-invoice-uuid>"
}
```

not:

```json
{
  "c_bpartner_id": 1000021,
  "c_invoice_id": 1000522
}
```

---

# 22. Native references

Native ERP references MAY be retained internally for diagnostics and reconciliation.

They SHALL NOT be required for ordinary consumer processing.

---

# 23. Event categories

Baobab SHALL distinguish at least:

```text
Domain Events
Integration Events
Control Plane Events
Operational Events
```

These categories SHALL not be conflated.

---

# 24. ERP domain event

An ERP domain event describes something meaningful inside the ERP domain.

Example:

```text
SupplierInvoicePosted
```

---

# 25. Integration event

An integration event is a canonical externally consumable representation of a relevant domain fact.

Not every internal ERP domain event needs to become an integration event.

---

# 26. Control Plane event

Examples:

```text
engine-instance.activated
capability-binding.changed
mapping.activated
tenant.suspended
```

These belong to the Control Plane domain.

ERP may consume them.

ERP does not own them.

---

# 27. Operational event

Examples:

```text
backup.failed
publisher.degraded
outbox.backlog-threshold-exceeded
```

These belong primarily to observability/operations.

They SHALL NOT be confused with business events.

---

# 28. Event publication threshold

Before publishing an ERP event externally, ask:

> Would another bounded context reasonably care that this business fact occurred?

If no:

```text
keep it internal
```

This prevents event-stream pollution.

---

# 29. Transactional outbox

Canonical ERP events resulting from ERP transactions SHALL use the transactional outbox pattern.

Required sequence:

```text
BEGIN
   │
   ├── ERP business mutation
   │
   └── INSERT outbox event
   │
COMMIT
```

Only after commit:

```text
outbox publisher
       │
       ▼
event transport
```

---

# 30. Atomicity

The critical invariant is:

```text
ERP state committed
       ⇔
event intent committed
```

for events describing that transaction.

---

# 31. Forbidden dual write

This SHALL NOT occur:

```text
BEGIN ERP transaction

UPDATE invoice

publish broker message

COMMIT ERP
```

because broker publication and PostgreSQL commit do not share the same reliable transaction boundary.

---

# 32. Outbox persistence

Recommended conceptual fields:

```text
event_id
event_type
subject_id

tenant_id
legal_entity_id
market_id

engine_id
engine_instance_id

correlation_id
causation_id
trace_id

schema_uri
schema_version

payload

occurred_at
created_at

state
attempt_count
next_attempt_at
last_attempt_at
published_at
last_error
```

---

# 33. Outbox lifecycle

Recommended states:

```text
pending
   ↓
claimed
   ↓
publishing
   ↓
published
```

Failure:

```text
publishing
   ↓
retry
   ↓
pending
```

Terminal operational exception:

```text
dead_letter
```

---

# 34. Outbox claiming

Multiple publisher workers SHALL be able to process the outbox safely.

The implementation SHALL prevent two workers from independently treating the same record as a new event.

Database locking/claiming strategy SHALL be implementation-defined and concurrency-tested.

---

# 35. Publication does not change event identity

Retry:

```text
attempt 1
attempt 2
attempt 3
```

still publishes:

```text
same event ID
```

---

# 36. Delivery semantics

Baobab SHALL design consumers for:

```text
at-least-once delivery
```

Meaning:

```text
duplicate delivery is possible
event loss after committed publication intent is unacceptable
```

---

# 37. Exactly-once claims

Baobab SHALL NOT describe the whole distributed platform as "exactly once."

Broker-level transactional capabilities do not automatically provide exactly-once business effects across:

```text
iDempiere
Medusa
Payload
Control Plane
external services
```

The platform SHALL instead achieve correct effects through:

```text
durable event identity
idempotency
transactional inbox/outbox
reconciliation
```

---

# 38. Consumer idempotency

Every consumer of financially or operationally material events SHALL be idempotent.

Conceptually:

```text
event arrives
      │
      ▼
event_id already processed?
      │
   ┌──┴──┐
  yes    no
   │      │
 ignore   process
          │
          ▼
   record event_id
```

---

# 39. Transactional inbox

Where processing an event changes local durable state, the preferred pattern SHALL be:

```text
BEGIN

check inbox(event_id)

if absent:
    perform local mutation
    insert inbox(event_id)

COMMIT
```

---

# 40. Inbox record

Conceptually:

```text
event_id
event_type
source
received_at
processed_at
processing_state
consumer
correlation_id
payload_hash
```

Payload duplication SHOULD be avoided unless required for audit/recovery.

---

# 41. Inbox uniqueness

The database SHALL enforce uniqueness on:

```text
consumer + event_id
```

or equivalent consumer-processing identity.

Correctness SHALL not depend solely on an in-memory cache.

---

# 42. Ordering

Baobab SHALL NOT promise global event ordering.

Global ordering is expensive, unnecessary and constrains scalability.

Ordering guarantees SHALL be scoped.

---

# 43. Aggregate ordering

Where ordering matters, events SHOULD be ordered for a suitable aggregate.

Examples:

```text
invoice
purchase order
payment
```

Thus:

```text
InvoiceCreated
InvoiceCompleted
InvoicePosted
InvoiceReversed
```

SHOULD preserve useful ordering for that invoice.

---

# 44. Partition key

Where the event transport supports partitioning, the preferred partition key SHOULD normally be:

```text
canonical aggregate/subject ID
```

when aggregate ordering is required.

---

# 45. Tenant partitioning

Tenant ID SHALL NOT automatically be the partition key.

A large tenant could otherwise create a hot partition.

Partitioning policy SHALL balance:

```text
ordering requirements
throughput
tenant isolation
operational distribution
```

---

# 46. Sequence number

Where a domain requires stronger detection of missing/reordered aggregate events, events MAY include:

```text
aggregate_version
```

or:

```text
sequence
```

Example:

```text
invoice 123:

v1 created
v2 completed
v3 posted
v4 reversed
```

---

# 47. Sequence semantics

An aggregate version SHALL represent domain mutation ordering.

It SHALL NOT be confused with:

```text
event schema version
```

---

# 48. Schema version

Event type version identifies contract compatibility.

Example:

```text
supplier-invoice.posted.v1
```

The `v1` represents the event schema contract generation.

---

# 49. Breaking schema changes

Breaking changes SHALL produce a new major event version.

Example:

```text
supplier-invoice.posted.v1
supplier-invoice.posted.v2
```

---

# 50. Non-breaking schema evolution

Compatible additions MAY remain in the existing major version where contract rules permit.

Examples:

```text
new optional field
new optional metadata
```

Consumers SHALL tolerate unknown optional fields.

---

# 51. Schema registry

Baobab SHOULD maintain a canonical schema registry through source-controlled contracts.

The initial authority SHALL be:

```text
nabhold/shared
```

A runtime schema-registry product MAY later be introduced.

It SHALL NOT become the conceptual source of truth.

---

# 52. Schema URI

`dataschema` SHOULD identify the canonical schema/version.

It SHALL not point to an unstable branch such as:

```text
/main/latest.json
```

for immutable historical events.

---

# 53. Contract immutability

Once an event schema version is released and used in production, it SHALL be immutable except for non-semantic corrections that cannot alter validation or interpretation.

---

# 54. AsyncAPI validation

CI SHALL validate:

```text
AsyncAPI syntax
message schemas
references
examples
channel declarations
operation declarations
```

before contract changes merge.

---

# 55. Compatibility checking

CI SHOULD detect breaking schema changes.

A pull request SHALL not silently mutate:

```text
v1
```

into an incompatible contract.

---

# 56. Producer contract testing

`baobab-erp` SHALL test that emitted events conform to the canonical schema.

This SHALL include actual serialization.

---

# 57. Consumer contract testing

Critical consumers SHOULD validate representative canonical messages during CI.

---

# 58. Event taxonomy

Initial ERP event families SHOULD include:

```text
purchase-order.*
goods-receipt.*
supplier-invoice.*
customer-invoice.*
payment.*
inventory.*
accounting.*
business-partner.*
```

Only implemented business capabilities SHALL receive event contracts.

---

# 59. Purchase-order events

Candidate lifecycle events:

```text
erp.purchase-order.created.v1
erp.purchase-order.completed.v1
erp.purchase-order.closed.v1
erp.purchase-order.voided.v1
```

Do not emit lifecycle states that have no stable canonical meaning.

---

# 60. Goods-receipt events

Candidate events:

```text
erp.goods-receipt.completed.v1
erp.goods-receipt.reversed.v1
```

A draft row creation normally does not need external publication.

---

# 61. Supplier-invoice events

Candidate events:

```text
erp.supplier-invoice.created.v1
erp.supplier-invoice.completed.v1
erp.supplier-invoice.posted.v1
erp.supplier-invoice.voided.v1
erp.supplier-invoice.reversed.v1
```

Whether `created` is externally useful SHALL be determined by actual consumer requirements.

---

# 62. Payment events

Candidate events:

```text
erp.payment.created.v1
erp.payment.completed.v1
erp.payment.allocated.v1
erp.payment.reversed.v1
```

Payment events SHALL minimise sensitive banking information.

---

# 63. Inventory events

ERP SHALL NOT automatically publish every inventory storage mutation.

Preferred semantic events include:

```text
erp.inventory.received.v1
erp.inventory.adjusted.v1
erp.inventory.transferred.v1
```

where ERP is authoritative for that fact.

---

# 64. Accounting events

Accounting events require particular restraint.

Candidate events:

```text
erp.document.posted.v1
erp.accounting-period.closed.v1
erp.accounting-period.reopened.v1
```

Publishing every journal-line mutation as a general platform event is discouraged.

---

# 65. Ledger extraction

Analytics requiring detailed ledger data SHOULD use a governed analytical/export pipeline rather than turning every accounting row into a broad integration event.

---

# 66. Business-partner events

ERP SHOULD not claim canonical Party ownership merely because it has a `C_BPartner`.

Events SHALL make clear whether they represent:

```text
ERP representation created
ERP representation changed
```

rather than:

```text
canonical Party created
```

unless ERP actually owns that canonical operation.

---

# 67. Ownership affects event naming

If ERP merely materialises a canonical Party:

Preferred:

```text
erp.business-partner-representation.created.v1
```

rather than implying:

```text
party.created.v1
```

The latter belongs to whichever bounded context owns canonical Party creation.

---

# 68. Event ownership

Only the authoritative domain SHOULD emit the authoritative event for a fact.

Multiple engines SHALL NOT independently publish contradictory:

```text
product.created
```

events for the same canonical product.

---

# 69. Medusa relationship

For commerce:

```text
Trade Engine
     │
     ├── owns commerce order lifecycle
     │
     ▼
canonical trade event
     │
     ▼
ERP
     │
     ├── creates ERP representation
     ├── accounting/procurement consequences
     │
     ▼
canonical ERP events
```

---

# 70. No event ping-pong

The architecture SHALL prevent:

```text
Medusa emits A
ERP consumes A
ERP emits B
Medusa interprets B as new A
Medusa emits A again
...
```

Causation metadata and explicit ownership SHALL prevent feedback loops.

---

# 71. Causation ID

When event B results from event A:

```text
A.event_id
      │
      ▼
B.causation_id
```

SHALL preserve immediate causal lineage where applicable.

---

# 72. Correlation ID

All events in one broader business workflow SHOULD share:

```text
correlation_id
```

Example:

```text
customer order
     ↓
ERP representation
     ↓
invoice
     ↓
payment
```

---

# 73. Correlation is not causation

```text
correlation
```

answers:

> Which broader workflow are these related to?

```text
causation
```

answers:

> Which specific command/event directly caused this event?

They SHALL remain distinct.

---

# 74. Trace ID

`trace_id` supports operational distributed tracing.

It SHALL NOT replace:

```text
correlation_id
event_id
canonical entity ID
```

---

# 75. Payload strategy

An event SHALL contain enough information for its intended consumers to react reliably.

But:

> An event is not a database dump.

---

# 76. Event-carried state

For high-value integrations, events SHOULD generally include important immutable/current facts relevant to the event.

Example:

```json
{
  "invoice_id": "...",
  "supplier_id": "...",
  "status": "posted",
  "document_date": "2026-09-02",
  "accounting_date": "2026-09-02",
  "currency": "ZAR",
  "total": "12500.00"
}
```

This reduces unnecessary synchronous callbacks.

---

# 77. Thin-event exception

A deliberately thin event MAY contain mostly identity when:

```text
payload sensitivity is high
state changes rapidly
consumer must retrieve authoritative current state
```

The contract SHALL make this deliberate.

---

# 78. Event payload versus API representation

The event schema SHALL not automatically equal the corresponding REST resource schema.

REST represents:

```text
current queryable resource
```

Event represents:

```text
fact at a point in time
```

---

# 79. Personal data

Personally identifiable information SHALL be minimised in canonical events.

If consumers only need:

```text
customer_id
```

do not publish:

```text
name
email
phone
address
```

merely because ERP contains them.

---

# 80. Financial data classification

ERP event schemas SHALL classify fields according to Baobab data-classification policy.

Examples may include:

```text
public
internal
tenant-confidential
financial-confidential
regulated
```

---

# 81. Sensitive credentials

Events SHALL NEVER contain:

```text
passwords
API secrets
private keys
authentication tokens
full payment credentials
```

---

# 82. Market and residency

Event routing SHALL respect:

```text
Market
jurisdiction
data classification
ResidencyPolicy
EngineInstance
```

where applicable.

---

# 83. Event routing does not infer residency from Market

Example:

```text
Market = Uganda
```

does not itself establish:

```text
event must remain physically in Uganda
```

Residency policy makes that determination.

---

# 84. Cross-region event flow

A cross-region event bridge SHALL evaluate whether:

```text
event metadata
payload
consumer
destination region
```

are permitted by policy.

---

# 85. Metadata-only routing

Where sensitive payload cannot leave a region, Baobab MAY emit a reduced cross-region notification containing canonical identifiers and permitted metadata.

The authoritative payload remains regional.

---

# 86. Encryption

Event transport SHALL use encryption in transit across appropriate boundaries.

Persistent broker/event storage SHALL use approved encryption at rest.

---

# 87. Event authorization

A consumer SHALL only subscribe to event families it is authorised to consume.

Access SHALL be scoped by:

```text
domain
event family
tenant where appropriate
environment
```

---

# 88. Tenant isolation

A consumer authorised for Tenant A SHALL not receive Tenant B's confidential event stream unless its role explicitly requires multi-tenant processing.

---

# 89. Platform services

Certain platform services MAY legitimately consume multi-tenant events.

Examples:

```text
Control Plane reconciliation
platform observability
authorised Intelligence services
```

Such access SHALL be privileged and audited.

---

# 90. Topic/channel topology

Physical channel naming SHALL be defined separately from semantic event naming.

A possible initial strategy:

```text
baobab.erp.events.v1
```

with routing metadata.

Another may use event-family channels.

The canonical contract SHALL permit transport evolution.

---

# 91. Avoid topic explosion

Baobab SHALL NOT automatically create:

```text
one topic per tenant per event type
```

unless operational or regulatory requirements justify it.

At scale this becomes difficult to manage.

---

# 92. Avoid one universal event stream without controls

Likewise:

```text
everything from every engine
      ↓
one unrestricted topic
```

is rejected.

Security, retention and operational boundaries require deliberate topology.

---

# 93. Recommended logical channels

AsyncAPI MAY model logical channels such as:

```text
erp.purchase-orders
erp.goods-receipts
erp.supplier-invoices
erp.payments
erp.accounting
```

Physical broker binding may map these differently.

---

# 94. Environment isolation

Production events SHALL never share ordinary channels with:

```text
development
test
staging
```

Environment isolation is mandatory.

---

# 95. Replay

Canonical event infrastructure SHALL support controlled replay.

Replay is required for:

```text
new projections
consumer recovery
reconciliation
bug repair
analytics rebuild
```

---

# 96. Replay does not create new events

Replaying event:

```text
E123
```

SHALL normally preserve:

```text
event_id = E123
```

It SHALL not masquerade as a newly occurring business event.

---

# 97. Replay metadata

Transport or consumer metadata MAY indicate:

```text
replayed = true
replay_job_id = ...
```

without altering original business occurrence semantics.

---

# 98. Consumer replay safety

Consumers SHALL be designed so replay does not:

```text
double-pay supplier
double-post invoice
double-reserve inventory
send duplicate irreversible instruction
```

---

# 99. Event retention

Retention SHALL vary by event class.

Factors include:

```text
audit need
replay need
financial retention
privacy
storage cost
regulation
```

One universal retention period SHALL not be assumed.

---

# 100. Broker retention versus archival retention

These SHALL be separate concepts.

```text
broker retention
      │
      └── operational replay

event archive
      │
      └── long-term audit/reconstruction
```

---

# 101. Canonical event archive

Financially significant events SHOULD have durable archival according to retention policy.

The broker itself SHALL not necessarily be the permanent archive.

---

# 102. Immutable archive

Archived canonical events SHOULD be immutable.

Corrections occur through new events, not historical mutation.

---

# 103. Event correction

If an erroneous business fact is reversed:

```text
InvoicePosted
      ↓
InvoiceReversed
```

Do not delete:

```text
InvoicePosted
```

from history.

---

# 104. Tombstones

Technical tombstone mechanisms MAY be used by particular transports/projections.

They SHALL not erase financial audit history where retention requires preservation.

---

# 105. Dead-letter handling

Events that cannot be processed after bounded retries SHALL enter a recoverable failure workflow.

Conceptually:

```text
event
  ↓
consumer
  ↓
retry
  ↓
retry exhausted
  ↓
dead-letter / quarantine
```

---

# 106. Dead-letter is not disposal

A dead-letter event remains unresolved work.

It SHALL have:

```text
owner
failure reason
first failure time
latest failure time
attempt count
correlation
resolution status
```

---

# 107. Poison messages

Schema-invalid or malicious messages SHALL be quarantined without repeatedly destabilising consumers.

---

# 108. Schema validation failure

A canonical producer emitting an invalid event is a producer defect.

It SHALL trigger operational alerting.

Consumers SHOULD not silently reinterpret malformed messages.

---

# 109. Missing Mapping

If ERP consumes an event referencing a canonical entity with no required native mapping:

```text
MAPPING_NOT_FOUND
```

SHALL become a reconciliation state.

ERP SHALL not guess the mapping.

---

# 110. Deferred processing

Some missing-dependency failures MAY enter:

```text
waiting_for_dependency
```

rather than immediate dead-letter.

Example:

```text
order event arrives
before required product mapping
```

if eventual dependency arrival is expected.

---

# 111. Retry classification

Failures SHALL be classified.

```text
TRANSIENT
    network outage
    temporary database issue

DEPENDENCY
    mapping not yet available

PERMANENT BUSINESS
    invalid state transition

SECURITY
    unauthorized context

SCHEMA
    invalid event contract
```

Retry policy SHALL depend on class.

---

# 112. No infinite retry

Permanent errors SHALL not retry forever.

Infinite retries create invisible operational debt.

---

# 113. Backoff

Transient retries SHOULD use bounded exponential backoff with jitter.

Exact timing belongs to implementation policy.

---

# 114. Reconciliation

Events SHALL complement—not replace—reconciliation.

Distributed systems can fail in unexpected ways.

Baobab SHALL be able to ask:

```text
Was canonical order X represented in ERP?

Did ERP invoice Y produce its expected event?

Did Trade consume event Z?

Are any outbox records unpublished?

Are any inbox events unresolved?
```

---

# 115. Reconciliation identifiers

Canonical entity IDs, event IDs, correlation IDs and mappings SHALL provide the join points for reconciliation.

---

# 116. Reconciliation service

A future cross-engine reconciliation service MAY consume metadata from:

```text
Trade
ERP
Control Plane
event infrastructure
```

without owning the underlying business state.

---

# 117. Outbox monitoring

Required metrics SHOULD include:

```text
outbox_pending_total
outbox_oldest_pending_seconds
outbox_publish_failures_total
outbox_dead_letter_total
outbox_publish_latency
```

---

# 118. Consumer monitoring

Required metrics SHOULD include:

```text
events_received_total
events_processed_total
events_duplicate_total
events_failed_total
events_dead_letter_total
consumer_lag
processing_duration
```

---

# 119. Cardinality discipline

Metrics SHALL avoid unbounded labels such as:

```text
event_id
invoice_id
customer_id
```

Logs/traces can carry detailed identifiers where policy permits.

---

# 120. Structured logs

Event processing logs SHOULD include:

```text
event_id
event_type
correlation_id
causation_id
engine_instance_id
consumer
outcome
```

Tenant identifiers SHALL be handled according to observability policy.

---

# 121. Trace continuity

Where supported:

```text
API command
     ↓
ERP transaction
     ↓
outbox
     ↓
event
     ↓
consumer
```

SHOULD remain traceable as one distributed business flow.

---

# 122. Outbox recovery

Database recovery procedures SHALL include outbox recovery.

A restored ERP database with missing event intent is not a complete recovery.

---

# 123. Disaster recovery

After failover:

```text
unpublished outbox events
```

SHALL resume publication safely.

Duplicate publication is acceptable under idempotent semantics.

Silent omission is not.

---

# 124. EngineInstance failover

If DR failover preserves the same logical EngineInstance:

```text
engine_instance_id
```

SHALL remain stable.

Ephemeral infrastructure identity may change.

---

# 125. EngineInstance migration

If workload migrates to a new canonical EngineInstance:

```text
old events → old EngineInstance ID
new events → new EngineInstance ID
```

Canonical business identity remains stable.

---

# 126. Event production during migration

Migration SHALL define the authoritative producer boundary.

The source and target SHALL NOT independently publish conflicting canonical events for the same mutation.

---

# 127. Split-brain protection

Before target becomes authoritative:

```text
source write authority
```

must be fenced or controlled according to the migration protocol.

Event architecture SHALL follow the same authority.

---

# 128. Control Plane interaction

ERP MAY consume events such as:

```text
capability-binding.changed
mapping.changed
tenant.suspended
engine-instance.draining
```

where asynchronous notification is appropriate.

Security-critical state MAY still require synchronous verification or bounded trusted caches.

---

# 129. Tenant suspension

A `tenant.suspended` event alone SHALL NOT be the only security mechanism if delayed consumption could permit continued privileged operations.

Security-sensitive changes require fail-closed design.

---

# 130. Mapping change

Mapping-change events MAY invalidate ERP caches.

The Control Plane remains authoritative.

---

# 131. Payload CMS interaction

Payload SHOULD rarely consume raw ERP event families directly unless a real content use case requires them.

A content projection service may be more appropriate.

This prevents CMS coupling to finance.

---

# 132. Intelligence Engine

The Intelligence Engine MAY consume authorised canonical ERP events for:

```text
analytics
forecasting
anomaly detection
decision support
```

subject to:

```text
tenant authorization
data classification
residency
purpose limitation
```

---

# 133. Intelligence does not become ERP authority

AI-derived conclusions SHALL not mutate financial records merely because the Intelligence Engine consumed ERP events.

Any resulting action SHALL return through an authorised command/workflow.

---

# 134. AI action flow

Correct:

```text
ERP Event
    ↓
Intelligence Engine
    ↓
recommendation
    ↓
approved workflow / command
    ↓
ERP API
```

Not:

```text
ERP Event
    ↓
AI
    ↓
direct ERP database update
```

---

# 135. Event-driven does not mean everything asynchronous

Use synchronous API where the caller needs immediate authoritative validation/result.

Use events where consumers need notification of completed facts.

Example:

```text
POST supplier invoice
      ↓
synchronous acceptance/result
      ↓
later canonical event
```

Both mechanisms are legitimate.

---

# 136. Request/reply over broker

Baobab SHALL not implement ordinary ERP query APIs as convoluted asynchronous request/reply messaging merely to claim to be "event driven."

Use the appropriate interaction model.

---

# 137. Events are not RPC

An event producer SHALL not require a particular consumer to exist for the event to be valid.

Otherwise the event has become disguised RPC.

---

# 138. Consumer autonomy

ERP SHALL not need to know all consumers of:

```text
supplier-invoice.posted
```

This allows future consumers to subscribe without changing ERP.

---

# 139. Event contract ownership

The producer domain owns semantic correctness.

The organisation owns canonical interoperability standards.

Consumers do not redefine producer event semantics locally.

---

# 140. Event documentation

Every event contract SHALL document:

```text
business meaning
producer
trigger
subject
Context
payload fields
schema version
ordering expectations
sensitivity
replay semantics
expected consumers where known
```

---

# 141. Example supplier invoice event

```json
{
  "specversion": "1.0",
  "id": "019c...",
  "source": "baobab://erp/engine-instances/019a...",
  "type": "com.nabhold.baobab.erp.supplier-invoice.posted.v1",
  "subject": "baobab://supplier-invoices/019b...",
  "time": "2026-09-02T04:15:23Z",
  "datacontenttype": "application/json",
  "dataschema": "baobab://contracts/erp/supplier-invoice-posted/v1",

  "tenantid": "019...",
  "legalentityid": "019...",
  "marketid": "019...",
  "engineinstanceid": "019...",

  "correlationid": "019...",
  "causationid": "019...",

  "data": {
    "invoice_id": "019...",
    "supplier_id": "019...",
    "invoice_number": "INV-2026-00147",
    "document_date": "2026-09-01",
    "accounting_date": "2026-09-02",
    "currency": "ZAR",
    "total": "12500.00",
    "status": "posted"
  }
}
```

---

# 142. Example cross-engine choreography

Consider a commerce transaction:

```text
Digital Estate
      │
      ▼
Trade Engine
      │
      │ trade.order.completed
      ▼
Event Transport
      │
      ▼
ERP Consumer
      │
      ├── deduplicate
      ├── resolve Context
      ├── resolve mappings
      ├── create ERP representation
      └── commit
              │
              ├── ERP state
              └── outbox
                     │
                     ▼
            erp.customer-invoice.posted
                     │
              ┌──────┼──────┐
              ▼      ▼      ▼
          Trade   Analytics Intelligence
```

No engine reads another engine's database.

---

# 143. Failure example

Suppose ERP commits an invoice but the broker is unavailable.

```text
ERP transaction
      │
      ├── invoice posted
      └── outbox inserted
             │
           COMMIT

broker
  ✕ unavailable
```

Result:

```text
ERP remains correct
event remains pending
```

Later:

```text
broker recovers
      ↓
publisher retries
      ↓
same event ID published
```

This is the required behaviour.

---

# 144. Consumer crash example

Suppose Trade consumes:

```text
erp.invoice.posted
```

and crashes after updating local state but before acknowledging the broker.

Broker redelivers.

Trade sees:

```text
event_id already processed
```

and performs no duplicate business effect.

This is why idempotency is mandatory.

---

# 145. Ordering example

Suppose:

```text
InvoiceCompleted
InvoicePosted
InvoiceReversed
```

are events for invoice X.

All SHOULD use:

```text
partition_key = invoice X canonical ID
```

where the chosen transport supports ordered partitions.

This provides useful invoice-local ordering without requiring global ordering.

---

# 146. Rejected alternative — raw database CDC as canonical events

**Rejected.**

CDC exposes physical persistence rather than business semantics.

---

# 147. Rejected alternative — publish directly from model validator

**Rejected.**

Broker failure would contaminate ERP transaction reliability and create dual-write inconsistency.

---

# 148. Rejected alternative — global exactly-once guarantee

**Rejected.**

It creates a misleading platform guarantee across heterogeneous systems.

---

# 149. Rejected alternative — no consumer idempotency because broker deduplicates

**Rejected.**

Broker delivery guarantees do not guarantee downstream business-effect uniqueness.

---

# 150. Rejected alternative — global event ordering

**Rejected.**

It creates unnecessary scalability constraints.

---

# 151. Rejected alternative — one event per database mutation

**Rejected.**

This creates noise and persistence coupling.

---

# 152. Rejected alternative — one topic per tenant

**Rejected as universal architecture.**

It may be appropriate for exceptional regulated isolation but does not scale as the default topology.

---

# 153. Rejected alternative — one unrestricted global topic

**Rejected.**

It weakens security, residency and operational separation.

---

# 154. Rejected alternative — mutable historical events

**Rejected.**

Corrections are new facts.

---

# 155. Rejected alternative — native ERP IDs as event identity

**Rejected.**

Native IDs are EngineInstance-scoped implementation identifiers.

---

# 156. Rejected alternative — events contain complete ERP records

**Rejected.**

Events SHALL expose required business facts, not database dumps.

---

# 157. Rejected alternative — webhooks as canonical internal messaging

**Rejected.**

Webhooks remain transport adapters for appropriate external consumers.

---

# 158. Rejected alternative — event-driven everything

**Rejected.**

Queries and immediate authoritative commands remain synchronous where appropriate.

---

# 159. Rejected alternative — broker technology in domain contracts

**Rejected.**

Canonical event semantics SHALL survive transport replacement.

---

# 160. Non-negotiable invariants

```text
INV-ERP-EVT-001
ERP canonical events represent business facts.

INV-ERP-EVT-002
Database row changes are not automatically canonical events.

INV-ERP-EVT-003
Canonical events use canonical identifiers.

INV-ERP-EVT-004
Native iDempiere IDs are not required consumer identifiers.

INV-ERP-EVT-005
Every canonical event has an immutable globally unique event ID.

INV-ERP-EVT-006
Event ID and canonical subject ID are distinct.

INV-ERP-EVT-007
Tenant-scoped events carry explicit canonical Context.

INV-ERP-EVT-008
Historical event Context is immutable.

INV-ERP-EVT-009
EngineInstance provenance is retained.

INV-ERP-EVT-010
ERP transaction events use a transactional outbox.

INV-ERP-EVT-011
Broker publication does not occur as an unsafe dual write inside the ERP transaction.

INV-ERP-EVT-012
Committed ERP state and committed event intent are atomic where semantically coupled.

INV-ERP-EVT-013
Delivery assumes at-least-once semantics.

INV-ERP-EVT-014
Consumers are idempotent.

INV-ERP-EVT-015
Financially material consumers use durable deduplication.

INV-ERP-EVT-016
Global ordering is not guaranteed.

INV-ERP-EVT-017
Ordering is scoped to a meaningful aggregate where required.

INV-ERP-EVT-018
Event schema version and aggregate version are distinct.

INV-ERP-EVT-019
Breaking event schema changes create a new major version.

INV-ERP-EVT-020
Released event contracts are immutable.

INV-ERP-EVT-021
Events minimise sensitive data.

INV-ERP-EVT-022
Events never contain secrets or authentication credentials.

INV-ERP-EVT-023
Event routing respects tenant isolation.

INV-ERP-EVT-024
Event routing respects applicable residency policy.

INV-ERP-EVT-025
Market and physical event region remain distinct.

INV-ERP-EVT-026
Replay preserves original event identity.

INV-ERP-EVT-027
Replay must not create duplicate business effects.

INV-ERP-EVT-028
Dead-letter means unresolved, not discarded.

INV-ERP-EVT-029
Permanent failures do not retry forever.

INV-ERP-EVT-030
Missing mappings are never guessed.

INV-ERP-EVT-031
Canonical events complement reconciliation rather than eliminate it.

INV-ERP-EVT-032
ERP does not need to know every event consumer.

INV-ERP-EVT-033
Consumers cannot redefine producer event semantics.

INV-ERP-EVT-034
Transport technology is not part of canonical business semantics.

INV-ERP-EVT-035
Production and non-production event infrastructure are isolated.

INV-ERP-EVT-036
Cross-engine integration never requires direct database access.

INV-ERP-EVT-037
AI consumers do not acquire ERP mutation authority merely by consuming events.

INV-ERP-EVT-038
Corrections are represented through new business facts rather than rewriting historical events.

INV-ERP-EVT-039
Outbox state participates in ERP disaster-recovery procedures.

INV-ERP-EVT-040
Canonical event contracts are machine-readable and compatibility-tested.
```

---

# 161. Initial implementation scope

The first production event implementation SHOULD remain narrow.

Recommended initial events:

```text
erp.purchase-order.completed.v1

erp.goods-receipt.completed.v1

erp.supplier-invoice.posted.v1

erp.payment.completed.v1
```

This provides a meaningful purchase-to-pay vertical slice without prematurely turning the entire ERP into an event source.

---

# 162. Initial transport requirements

Whatever event transport Baobab selects SHALL provide or permit implementation of:

```text
durable publication
consumer groups/subscriptions
retry
dead-letter handling
partition/routing keys
access control
encryption
monitoring
replay
```

The broker choice SHALL be recorded separately.

This ADR intentionally does not select Kafka, NATS, EventBridge or another broker.

---

# 163. Initial publisher requirements

The ERP publisher SHALL support:

```text
multiple workers
safe outbox claiming
bounded batches
retry/backoff
immutable event ID
schema validation
structured logging
metrics
graceful shutdown
```

---

# 164. Initial consumer requirements

ERP's inbound event framework SHALL support:

```text
schema validation
authentication/transport trust
tenant Context validation
event deduplication
Mapping resolution
application service dispatch
transactional inbox
retry classification
dead-letter handling
correlation propagation
```

---

# 165. Acceptance criteria

ADR-ERP-006 SHALL be considered implemented when:

- [ ] AsyncAPI 3.1 contract exists for ERP events.
- [ ] A canonical common event envelope exists.
- [ ] CloudEvents-aligned core attributes are documented.
- [ ] ERP event taxonomy is documented.
- [ ] Events use canonical IDs.
- [ ] Tenant/legal-entity/market Context is represented.
- [ ] EngineInstance provenance is represented.
- [ ] Correlation and causation conventions exist.
- [ ] Transactional outbox exists in ERP.
- [ ] ERP transaction and outbox intent commit atomically.
- [ ] Outbox workers support safe concurrent claiming.
- [ ] Publisher retries preserve event IDs.
- [ ] At-least-once semantics are documented.
- [ ] ERP inbound consumers implement durable deduplication.
- [ ] Transactional inbox exists for materially state-changing consumers.
- [ ] Partition-key strategy is documented.
- [ ] No global-order guarantee is made.
- [ ] Event schemas are versioned.
- [ ] Breaking changes require new event versions.
- [ ] Schema compatibility checks execute in CI.
- [ ] Producer contract tests exist.
- [ ] Consumer contract tests exist for critical flows.
- [ ] Replay semantics are documented and tested.
- [ ] Dead-letter handling is operationally owned.
- [ ] Retry classification exists.
- [ ] Event payload data classification exists.
- [ ] Sensitive fields are minimised.
- [ ] Secrets cannot appear in event schemas.
- [ ] Cross-region event routing obeys residency policy.
- [ ] Production/non-production streams are isolated.
- [ ] Event infrastructure is observable.
- [ ] Outbox backlog alerts exist.
- [ ] Consumer lag/failure monitoring exists.
- [ ] ERP DR tests verify unpublished outbox recovery.
- [ ] Reconciliation can identify missing producer/consumer effects.
- [ ] No consumer depends on an iDempiere table name or primary key.
- [ ] Event contracts remain independent of broker implementation.

---

# 166. Architectural result

The complete ERP interaction model now becomes:

```text
                         BAOBAB PLATFORM

                              │
                ┌─────────────┴─────────────┐
                │                           │
         SYNCHRONOUS                   ASYNCHRONOUS
                │                           │
                ▼                           ▼
         OpenAPI ERP API              AsyncAPI Events
                │                           ▲
                ▼                           │
         Application Layer                  │
                │                           │
                ▼                           │
            iDempiere                       │
                │                           │
                ├──────────────┐            │
                │              │            │
                ▼              ▼            │
          ERP business      Transactional   │
             state            Outbox ───────┘
```

Inbound:

```text
Canonical Event
      │
      ▼
Event Consumer
      │
      ▼
Schema Validation
      │
      ▼
Context Validation
      │
      ▼
Transactional Inbox
      │
      ▼
Mapping Resolver
      │
      ▼
Application Service
      │
      ▼
iDempiere
```

---

# 167. Final governing statement

Baobab's ERP event architecture SHALL preserve three layers of truth:

```text
BUSINESS TRUTH
      │
      │
      ▼
Canonical Event
      │
      │
      ▼
TRANSPORT REPRESENTATION
```

iDempiere determines that an ERP business fact occurred.

Baobab determines how that fact is expressed canonically.

The messaging infrastructure determines how that canonical fact is transported.

Those responsibilities SHALL never collapse into one another.

Therefore:

> **iDempiere owns ERP state. Baobab owns interoperability semantics. The broker owns delivery infrastructure.**

And the most important operational rule remains:

> **A financial transaction must never disappear from the wider platform merely because the message broker happened to be unavailable at the moment the transaction committed.**

That is why the transactional outbox, immutable event identity, idempotent consumption and reconciliation mechanisms are architectural requirements rather than optional integration conveniences.