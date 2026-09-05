# ADR-ERP-004 — Baobab iDempiere Extension Architecture

**Status:** Accepted  
**Decision class:** ERP / Extension Architecture / Integration / Upgradeability / Events  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`  
**Parent ADRs:** ADR-ERP-001, ADR-ERP-002, ADR-ERP-003  
**Date:** 2026-09-02

---

# 1. Decision

Baobab SHALL extend iDempiere through supported extension mechanisms and separately deployable Baobab-owned OSGi bundles.

Baobab SHALL NOT maintain a long-lived fork of iDempiere core.

The ERP repository SHALL therefore be structured around:

```text
upstream iDempiere
        +
Baobab OSGi extensions
        +
Baobab integration boundary
        +
canonical contracts
```

rather than:

```text
modified private iDempiere source tree
```

Baobab extensions SHALL implement only ERP-local responsibilities.

Canonical platform responsibilities SHALL remain outside iDempiere.

The fundamental ownership rule is:

> **Extend native ERP behaviour where ERP behaviour belongs; translate at the engine boundary where Baobab semantics begin.**

---

# 2. Architectural objectives

This extension architecture SHALL provide:

- clean separation from upstream iDempiere;
- predictable upgrades;
- explicit dependency direction;
- business-intent APIs;
- transactional canonical event publication;
- tenant/context enforcement;
- observability;
- isolation from MedusaJS, Payload CMS and other engines;
- compatibility with the Baobab Control Plane;
- deterministic deployment;
- independent testing;
- reproducible extension packaging.

---

# 3. Architectural boundaries

The ERP implementation SHALL be divided conceptually into four layers.

```text
┌───────────────────────────────────────────────┐
│              Baobab Platform                 │
│ Control Plane / canonical events / contracts │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│       Baobab ERP Anti-Corruption Layer        │
│ context / APIs / mapping / events / adapters  │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│       Baobab iDempiere Extension Layer        │
│ validators / processes / services / plugins   │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│               iDempiere Core                  │
│     AD / ERP domain / persistence / engine    │
└───────────────────────────────────────────────┘
```

Dependencies SHALL point downward.

Upstream iDempiere SHALL never depend on Baobab.

---

# 4. iDempiere remains upstream software

The canonical source of the ERP implementation remains the upstream iDempiere project.

Baobab SHALL treat iDempiere as:

```text
externally maintained enterprise software
```

not:

```text
Baobab application source code
```

Baobab-specific behaviour SHALL therefore be supplied through extensions.

---

# 5. Core modification prohibition

Direct modifications to upstream iDempiere core SHALL be prohibited except:

1. temporary diagnostic patches;
2. emergency security mitigations;
3. patches intended for contribution upstream;
4. explicitly approved exceptional cases documented through a new ADR.

Any permitted temporary patch SHALL have:

```text
owner
reason
upstream issue/reference
expiration/removal plan
affected version
regression tests
```

---

# 6. Why core modification is prohibited

Maintaining changes directly in upstream core causes:

- difficult upgrades;
- merge conflicts;
- security-patch delay;
- undocumented behaviour;
- higher regression risk;
- vendor/community divergence;
- institutional dependence on internal knowledge.

iDempiere's extension ecosystem is explicitly based around installable plugins/features rather than requiring core changes. Current plugin documentation describes deployment through p2 repositories and OSGi lifecycle tooling.

---

# 7. Extension technology

Baobab SHALL use iDempiere's native modular runtime mechanisms, principally:

```text
OSGi bundles
Equinox runtime
iDempiere extension points
Application Dictionary
model validators
processes
service factories
event hooks where appropriate
```

The exact mechanism SHALL be chosen according to responsibility rather than convenience.

---

# 8. Plugin boundaries

The ERP extension SHALL NOT be implemented as one enormous bundle.

A modular package structure SHALL be adopted.

Recommended initial bundles:

```text
org.nabhold.baobab.erp.contract
org.nabhold.baobab.erp.context
org.nabhold.baobab.erp.identity
org.nabhold.baobab.erp.integration
org.nabhold.baobab.erp.application
org.nabhold.baobab.erp.events
org.nabhold.baobab.erp.outbox
org.nabhold.baobab.erp.observability
org.nabhold.baobab.erp.security
```

Additional domain-specific bundles MAY be introduced when justified.

---

# 9. Bundle — `erp.contract`

Purpose:

```text
Baobab-facing ERP types and stable extension interfaces
```

It MAY contain:

- ERP command contracts;
- ERP query contracts;
- event-envelope interfaces;
- context interfaces;
- error codes;
- internal SPI definitions;
- version constants.

It SHALL NOT contain:

- database operations;
- HTTP clients;
- native model mutations;
- Control Plane persistence.

---

# 10. Bundle — `erp.context`

Purpose:

> Convert a trusted resolved Baobab Context into an enforceable native ERP execution context.

Responsibilities:

```text
canonical context validation
EngineInstance validation
tenant/client resolution
organization resolution
principal/service identity context
context propagation
```

It SHALL implement the rules from ADR-ERP-002.

---

# 11. Bundle — `erp.identity`

Purpose:

> Resolve canonical-to-native and native-to-canonical ERP references.

Responsibilities MAY include:

```text
ExternalReference lookup client
Mapping lookup
local bounded mapping cache
native entity reference translation
reverse mapping support
```

It SHALL NOT become the authoritative Mapping database.

`baobab-cp` remains authoritative.

---

# 12. Bundle — `erp.application`

Purpose:

> Implement Baobab ERP use cases in terms of native iDempiere behaviour.

Examples:

```text
CreateSupplierInvoice
PostSupplierInvoice
CreatePurchaseOrder
CompletePurchaseOrder
ReceiveGoods
RegisterPayment
QueryAccountBalance
```

This layer SHALL express business intent.

It SHALL NOT expose arbitrary tables as platform-domain operations.

---

# 13. Bundle — `erp.integration`

Purpose:

> Connect the ERP boundary to permitted external interfaces.

Responsibilities MAY include:

- API adapter;
- Control Plane client;
- canonical contract serializer;
- authorised external command adapters;
- selected native REST adapter;
- integration-specific authentication.

This bundle SHALL function as part of the Anti-Corruption Layer.

---

# 14. Bundle — `erp.events`

Purpose:

> Translate meaningful ERP domain transitions into Baobab canonical events.

It SHALL define:

```text
native transition
      ↓
semantic interpretation
      ↓
canonical event
```

It SHALL NOT publish every database update as an event.

---

# 15. Bundle — `erp.outbox`

Purpose:

> Provide durable transactional event recording.

Responsibilities:

```text
outbox persistence
event identity
event state
publication state
retry metadata
claiming/locking
publisher handoff
```

Its design SHALL preserve atomicity between ERP transaction state and event intent.

---

# 16. Bundle — `erp.observability`

Purpose:

```text
structured logs
metrics
trace correlation
health indicators
integration diagnostics
```

It SHALL not embed tenant-sensitive payloads indiscriminately in logs.

---

# 17. Bundle — `erp.security`

Purpose:

- context enforcement;
- service identity validation;
- client boundary protection;
- organisation checks;
- authorization helpers;
- API boundary security;
- audit hooks.

Security SHALL remain defense-in-depth with native iDempiere roles and Baobab platform authorization both participating where appropriate.

---

# 18. Bundle dependency direction

The dependency graph SHOULD resemble:

```text
contract
   ▲
   │
context
identity
   ▲
   │
application
   ▲
   │
events
outbox
   ▲
   │
integration
```

Cross-cutting security and observability may be consumed through narrow interfaces.

Cyclic bundle dependencies SHALL be avoided.

---

# 19. Upstream dependencies

Baobab bundles SHALL import only iDempiere packages they actually require.

Broad classpath-style coupling SHALL be avoided.

OSGi package imports and required bundles SHALL be explicit.

This is important because upstream modules may move between releases. Current iDempiere migration notes, for example, document functionality being extracted from core into separate bundles in newer development versions.

---

# 20. No undocumented internal dependency

Baobab SHOULD prefer documented/stable extension APIs over direct use of internal implementation classes.

If use of an internal class is unavoidable, it SHALL be:

```text
isolated behind Baobab adapter
documented
covered by compatibility tests
```

This makes future upstream movement easier to absorb.

---

# 21. Application Dictionary first

Where iDempiere Application Dictionary configuration can safely implement a requirement, Baobab SHOULD prefer it over Java customization.

Examples MAY include:

```text
windows
tabs
fields
references
validation rules
process registrations
document types
workflow configuration
roles
```

The guiding order SHALL be:

```text
configuration
    ↓
Application Dictionary
    ↓
plugin extension
    ↓
core change — exceptional
```

---

# 22. Configuration versus code

A requirement SHALL not become Java merely because Java is familiar.

Likewise, complex business behaviour SHALL not be forced into metadata if code provides clearer correctness and testing.

The appropriate mechanism SHALL be selected based on:

```text
complexity
testability
upgrade stability
performance
security
transaction requirements
```

---

# 23. Model validators

iDempiere model validators MAY be used for:

- enforcing ERP-local invariants;
- detecting lifecycle transitions;
- validating contextual constraints;
- triggering creation of semantic event intents.

They SHALL NOT become an uncontrolled global side-effect mechanism.

---

# 24. Model validator restrictions

Validators SHALL:

- execute predictably;
- remain fast;
- avoid remote network calls inside the ERP transaction;
- avoid publishing directly to external brokers;
- avoid hidden cross-engine mutations;
- avoid recursive record modification loops.

Where external integration is required:

```text
validator
    ↓
record outbox event
    ↓
commit
    ↓
asynchronous publisher
```

---

# 25. Remote calls inside transactions

The following is prohibited:

```text
ERP transaction
    ↓
update invoice
    ↓
call Medusa API
    ↓
wait
    ↓
commit ERP
```

because an external dependency would participate implicitly in ERP transaction availability.

Instead:

```text
ERP transaction
    ├── update invoice
    └── insert outbox event
          ↓
        COMMIT

publisher
    ↓
canonical event
```

---

# 26. iDempiere processes

Native ERP processes SHALL be preferred where business operations have meaningful native process semantics.

For example, document completion/posting SHALL invoke the appropriate iDempiere process rather than mutating document status fields directly.

Current iDempiere REST guidance similarly stresses using ERP processes for lifecycle actions because those processes execute underlying validations, inventory effects and accounting behaviour.

---

# 27. No status-field automation

The following pattern is prohibited:

```text
PATCH order
DocStatus = "CO"
```

when iDempiere expects execution of document processing logic.

Baobab SHALL invoke the real ERP operation.

---

# 28. Business intent API

Baobab's external ERP API SHALL expose intent.

Preferred:

```text
POST /erp/v1/purchase-orders/{id}/complete

POST /erp/v1/supplier-invoices/{id}/post

POST /erp/v1/goods-receipts
```

Avoid:

```text
PATCH /erp/v1/c_order/123

POST /erp/v1/ad_process/104
```

Native implementation detail SHALL remain behind the anti-corruption layer.

---

# 29. Native REST API

iDempiere's REST capability MAY be used internally as an integration mechanism where suitable.

It SHALL NOT become Baobab's public ERP contract.

iDempiere security guidance specifically warns that its generic REST interface is highly powerful and recommends placing it behind an API gateway rather than exposing it directly.

---

# 30. Why native REST is insufficient as the Baobab contract

Native REST exposes concepts such as:

```text
table names
record IDs
process IDs
native filters
native model structures
```

Baobab contracts require:

```text
canonical IDs
Context
tenant semantics
stable business resources
canonical errors
canonical event relationships
```

Therefore an anti-corruption layer is mandatory.

---

# 31. Native REST exposure

If native REST is enabled:

```text
internet
   ✕
native ERP REST
```

SHALL NOT be the normal topology.

Instead:

```text
approved internal/gateway boundary
         ↓
controlled subset
         ↓
native ERP REST
```

---

# 32. Native SOAP

Baobab SHALL NOT introduce SOAP as the default new integration contract.

If legacy integration requires iDempiere SOAP:

- it SHALL be isolated behind an adapter;
- its use SHALL be documented;
- consumers SHALL not adopt SOAP-specific ERP identifiers as canonical concepts.

iDempiere's current documentation also indicates SOAP functionality is becoming more modular and separately installable in newer releases, reinforcing that Baobab should not build its architecture around it.

---

# 33. Service users

Native ERP integration SHALL use dedicated service users/roles.

iDempiere's own web-service security guidance recommends dedicated users and restrictive roles for service access.

A service role SHALL receive only required:

```text
processes
models
organizations
permissions
```

---

# 34. No System-role integration

Routine API calls SHALL NOT execute under unrestricted System-level administrative authority.

Privileged maintenance operations SHALL be separated from ordinary business integration.

---

# 35. Anti-Corruption Layer

The Baobab ERP Anti-Corruption Layer SHALL shield the canonical platform from iDempiere-native semantics.

It SHALL translate:

```text
Baobab                    iDempiere

Tenant                →   AD_Client
Organisation          →   AD_Org
Party                 →   C_BPartner
Product               →   M_Product
PurchaseOrder         →   C_Order
Invoice               →   C_Invoice
Payment               →   C_Payment
```

through explicit mapping and application logic.

The arrow means:

```text
representation mapping
```

not:

```text
ontological equivalence
```

---

# 36. Translation ownership

Baobab's ERP adapter owns translation.

Neither:

```text
Medusa
Payload
Digital Estate
```

SHALL need to understand:

```text
C_BPartner
C_Order
C_Invoice
AD_Client
AD_Org
```

---

# 37. Canonical command example

External command:

```json
{
  "tenant_id": "<uuid>",
  "legal_entity_id": "<uuid>",
  "supplier_id": "<canonical-party-uuid>",
  "invoice_number": "INV-2026-0101",
  "currency": "ZAR",
  "lines": []
}
```

Internal adapter resolves:

```text
tenant → AD_Client
supplier → C_BPartner
currency → C_Currency
```

before invoking native ERP operations.

---

# 38. Native IDs in API responses

Native IDs MAY be retained internally for diagnostics.

Ordinary external API consumers SHALL receive canonical IDs.

Native references SHOULD only be exposed through explicitly labelled administrative/diagnostic fields when necessary.

---

# 39. Domain ownership

iDempiere remains authoritative for ERP domain facts including:

```text
general ledger
accounts payable
accounts receivable
ERP inventory accounting
ERP procurement
ERP financial documents
payments
accounting postings
business partners in ERP context
```

---

# 40. Control Plane ownership

iDempiere SHALL NOT own:

```text
canonical tenant identity
canonical LegalEntity identity
EngineInstance registry
IsolationProfile
CapabilityBinding
canonical Market registry
canonical Mapping authority
platform routing
```

---

# 41. Medusa ownership

The ERP extension SHALL NOT duplicate Medusa's commerce authority.

Examples of commerce concerns that remain with the Trade Engine:

```text
shopping carts
commerce checkout
customer commerce experience
commerce promotions
sales channels
commerce pricing presentation
```

Financial consequences may subsequently be represented in ERP through canonical integration.

---

# 42. Payload ownership

The ERP extension SHALL NOT become a CMS.

It SHALL not own:

```text
editorial pages
rich marketing copy
web layouts
campaign content
media composition
SEO content
```

Payload remains the content authority.

---

# 43. No cross-engine Java dependencies

`baobab-erp` SHALL NOT import MedusaJS or Payload implementation packages.

Interaction is exclusively through:

```text
canonical APIs
canonical events
shared schemas
```

---

# 44. Outbox requirement

Every canonical ERP event resulting from a committed ERP business transaction SHALL be recorded durably before external publication.

The preferred pattern is:

```text
BEGIN

ERP mutation

Outbox INSERT

COMMIT
```

followed by:

```text
publisher
    ↓
event transport
```

---

# 45. Why outbox

Without an outbox:

```text
ERP commit succeeds
event publish fails
```

creates integration inconsistency.

Conversely:

```text
event publish succeeds
ERP transaction rolls back
```

publishes a false business event.

Transactional outbox removes this dual-write window.

---

# 46. Outbox table

A Baobab-owned ERP extension table SHOULD conceptually include:

```text
event_id UUID
event_type
aggregate_type
canonical_subject_id
tenant_id
legal_entity_id
market_id
engine_instance_id
payload
schema_version
correlation_id
causation_id
trace_id
occurred_at
created_at
publication_state
attempt_count
next_attempt_at
published_at
last_error
```

Exact physical design SHALL be defined in the implementation specification.

---

# 47. Outbox identifiers

`event_id` SHALL be generated at event creation time and SHALL remain unchanged across retries.

The broker-assigned ID SHALL NOT replace the canonical event ID.

---

# 48. Outbox state

Recommended states:

```text
pending
publishing
published
retry
dead_letter
```

Transitions SHALL be auditable.

---

# 49. Outbox transaction boundary

The outbox record SHALL be inserted using the same PostgreSQL transaction as the ERP mutation whenever the event describes that mutation.

This is non-negotiable for financially material events.

---

# 50. Publisher process

The publisher MAY execute:

- in a dedicated worker;
- in a dedicated OSGi service;
- through an external publisher with safe database access;

provided transaction and ownership boundaries remain correct.

Preferred architecture:

```text
iDempiere extension
      ↓
outbox
      ↓
Baobab ERP publisher
      ↓
event transport
```

---

# 51. Publisher SHALL not mutate ERP business state

The publisher's principal responsibility is delivery.

ERP business effects SHALL already be committed before publication.

---

# 52. At-least-once delivery

Canonical ERP events SHALL assume:

```text
at-least-once
```

delivery.

Consumers SHALL therefore be idempotent.

Exactly-once semantics across distributed engines SHALL not be assumed.

---

# 53. Event semantic threshold

An event SHALL represent a meaningful domain fact.

Good:

```text
erp.purchase-order.completed.v1
erp.supplier-invoice.posted.v1
erp.payment-allocated.v1
erp.goods-receipt.completed.v1
```

Poor:

```text
erp.c_invoice.updated.v1
erp.row.changed.v1
```

---

# 54. Event detection versus event meaning

Native model validators MAY detect that something changed.

The `events` application layer SHALL decide whether the change corresponds to a canonical domain event.

Therefore:

```text
database change
    ≠
canonical event
```

---

# 55. Canonical event envelope

All ERP events SHALL use the organisation-wide event envelope from `nabhold/shared`.

At minimum:

```json
{
  "id": "<uuid>",
  "type": "erp.supplier-invoice.posted.v1",
  "source": {
    "engine": "<uuid>",
    "engine_instance": "<uuid>"
  },
  "subject": "<canonical-entity-uuid>",
  "time": "2026-09-02T00:00:00Z",
  "context": {
    "tenant_id": "<uuid>",
    "legal_entity_id": "<uuid>",
    "market_id": "<uuid>"
  },
  "correlation_id": "<uuid>",
  "causation_id": "<uuid>",
  "schema": "...",
  "data": {}
}
```

---

# 56. Event schema ownership

Canonical event schemas SHALL be owned by:

```text
nabhold/shared
```

The ERP repository SHALL consume and implement those contracts.

It SHALL not maintain an incompatible private event definition.

---

# 57. Schema evolution

Breaking event schema changes SHALL require a new event version.

Example:

```text
erp.invoice.posted.v1
erp.invoice.posted.v2
```

Existing consumers SHALL not be silently broken.

---

# 58. Event payload discipline

Events SHOULD contain sufficient business facts for consumers to react without always calling ERP immediately.

However they SHALL avoid becoming uncontrolled replicas of ERP tables.

Sensitive financial or personal data SHALL be minimised.

---

# 59. Command versus event

Commands are imperative:

```text
PostSupplierInvoice
CompletePurchaseOrder
```

Events are past tense:

```text
SupplierInvoicePosted
PurchaseOrderCompleted
```

The distinction SHALL be preserved across contracts.

---

# 60. Correlation

Every externally initiated ERP operation SHALL carry or generate:

```text
correlation_id
```

The value SHALL propagate through:

```text
API
application service
ERP process
outbox
event
downstream consumer
```

---

# 61. Causation

Events SHOULD record:

```text
causation_id
```

where one command or event caused another event.

This enables distributed lineage.

---

# 62. Trace propagation

Where distributed tracing infrastructure exists:

```text
trace context
```

SHALL propagate through the ERP integration boundary.

Trace IDs are observability identifiers, not canonical business identifiers.

---

# 63. Database extensions

Baobab MAY add ERP-owned tables when necessary.

Examples:

```text
outbox
integration state
idempotency records
technical reconciliation state
```

Such tables SHALL have clear ownership and namespacing.

---

# 64. Custom table criteria

A new ERP database table SHALL require a reason such as:

- transactional co-location with ERP state;
- native ERP extension functionality;
- durable integration state;
- ERP-specific technical state.

The ERP database SHALL not become the dumping ground for canonical Control Plane data.

---

# 65. Canonical data prohibition

The following SHALL NOT be maintained as ERP-authoritative custom tables:

```text
canonical Tenant
canonical Market
Engine
EngineInstance registry
IsolationProfile registry
CapabilityBinding registry
platform-wide Mapping authority
```

Those belong to the Control Plane.

---

# 66. Cached canonical data

ERP MAY maintain bounded caches or local projections of canonical values needed for resilience/performance.

They SHALL be:

```text
derived
revocable
rebuildable
non-authoritative
```

---

# 67. Extension table naming

Baobab custom tables SHOULD use a consistent prefix or namespace clearly distinguishable from upstream tables.

Example conceptual prefix:

```text
BB_
```

The final naming convention SHALL be standardised across the repository.

---

# 68. Schema modification

Modifying upstream table structure SHALL be avoided.

Preferred:

```text
custom table
extension table
Application Dictionary extension
supported custom columns where appropriate
```

rather than invasive upstream schema changes.

---

# 69. Custom columns

Where a native iDempiere table legitimately requires an extension field, custom columns MAY be used according to supported iDempiere practices.

Such fields SHALL represent ERP-native requirements.

They SHALL not be used as a substitute for the Control Plane.

---

# 70. Canonical UUID storage

Where ERP needs to persist a canonical UUID for local correlation, it MAY do so.

However that column SHALL be treated as:

```text
external/canonical reference
```

not as replacement for iDempiere's own primary key.

---

# 71. UUID uniqueness

Where canonical UUIDs are stored locally:

- uniqueness scope SHALL be explicit;
- nullable migration states SHALL be defined;
- duplicate mapping SHALL fail validation where single-valued.

---

# 72. Application service transaction

Baobab application services SHALL explicitly define transaction boundaries.

Example:

```text
Create ERP document
      ↓
Validate
      ↓
Run native process
      ↓
Record canonical event
      ↓
Commit
```

Transactional behaviour SHALL not emerge accidentally from nested framework calls.

---

# 73. Idempotent commands

Externally retryable create/transition commands SHALL support idempotency.

An idempotency record SHOULD associate:

```text
tenant
operation
idempotency_key
request fingerprint
result
state
```

---

# 74. Idempotency scope

Idempotency SHALL be scoped at least by:

```text
tenant
operation
```

to avoid collisions between tenants.

---

# 75. Duplicate command

If the same idempotency key and equivalent request are repeated:

```text
return original result
```

SHALL normally apply.

If the key is reused with materially different content:

```text
IDEMPOTENCY_CONFLICT
```

SHALL be returned.

---

# 76. Native transaction integrity

Baobab SHALL use iDempiere transaction mechanisms rather than introducing independent JDBC transactions around native ERP operations in ways that bypass framework semantics.

---

# 77. Native validation preservation

The extension layer SHALL preserve:

```text
document validation
workflow
accounting checks
inventory checks
role/access controls
business rules
```

rather than reimplementing them outside iDempiere.

---

# 78. Financial posting

Posting/accounting SHALL remain native ERP responsibility.

The Baobab extension MAY initiate and observe posting.

It SHALL not implement a shadow accounting engine.

---

# 79. Error translation

Native errors SHALL be translated into stable Baobab error contracts.

Example:

```text
native:
"Period Closed"

canonical:
ERP_ACCOUNTING_PERIOD_CLOSED
```

Native diagnostic detail MAY be preserved internally.

---

# 80. Problem response

Baobab ERP APIs SHOULD expose a standard error form similar to:

```json
{
  "type": "...",
  "code": "ERP_ACCOUNTING_PERIOD_CLOSED",
  "title": "Accounting period is closed",
  "status": 409,
  "correlation_id": "<uuid>"
}
```

---

# 81. No exception leakage

Java stack traces, SQL, table names and unrestricted native exception details SHALL NOT be returned to external clients.

---

# 82. Security context

Every Baobab ERP application service SHALL require a resolved trusted Context.

Execution without tenant/client context SHALL be prohibited except for explicitly administrative operations.

---

# 83. Context SHALL be immutable per request

Once resolved, security-critical values such as:

```text
tenant
legal entity
engine instance
AD_Client
principal
```

SHALL not be arbitrarily mutable by downstream application code.

---

# 84. Thread/context safety

Where iDempiere uses thread-associated context, Baobab SHALL ensure:

```text
context initialized
operation executes
context cleared
```

for every request/worker execution.

Context leakage between tenants is a critical defect.

---

# 85. Worker context

Background jobs SHALL carry explicit canonical context.

They SHALL not rely on whichever tenant context happened to exist when a worker thread was reused.

---

# 86. Event publisher context

Outbox entries SHALL contain sufficient immutable context that publication does not depend on reconstructing tenant ownership from ambient thread state.

---

# 87. Tenant isolation tests

Extension tests SHALL include:

```text
Client A cannot read Client B
Client A cannot update Client B
background worker cannot leak previous Client context
outbox event has correct Tenant
reverse Mapping resolves correct Tenant
```

---

# 88. Plugin configuration

Baobab plugin configuration SHALL be externalised where appropriate.

Examples:

```text
Control Plane endpoint
event transport configuration
timeouts
retry policy
feature flags
observability endpoint
```

Secrets SHALL use secret references/injection.

---

# 89. No credentials in Application Dictionary

Long-lived secret credentials SHALL NOT be stored casually in ordinary Application Dictionary records.

Approved secret-management mechanisms SHALL be used.

---

# 90. Feature flags

Risky new integration behaviour MAY use feature flags.

Flags SHALL be:

- scoped;
- observable;
- documented;
- removable.

Permanent architectural branching through abandoned feature flags SHALL be avoided.

---

# 91. Plugin installation

Production extensions SHALL be packaged through reproducible plugin/feature artifacts.

Current iDempiere plugin guidance supports p2 repository-based installation and explicit bundle lifecycle management.

Baobab SHALL automate this through its delivery pipeline rather than manually copying arbitrary JAR files into production.

---

# 92. Feature project

Related bundles SHOULD be assembled into a Baobab ERP feature/distribution unit.

Conceptually:

```text
org.nabhold.baobab.erp.feature
```

which references required Baobab bundles and approved dependencies.

---

# 93. p2 repository

Release pipelines SHOULD publish a versioned p2 repository or equivalent supported distribution artifact for Baobab ERP extensions.

Each release SHALL be immutable.

---

# 94. Extension version

Baobab extension versions SHALL be independent from the iDempiere version.

Example:

```text
iDempiere:
    13.x

Baobab ERP Extension:
    1.4.0
```

Compatibility metadata SHALL state supported combinations.

---

# 95. Compatibility matrix

The repository SHALL maintain a matrix:

| Baobab ERP extension | iDempiere | Java | PostgreSQL | Status |
|---|---|---|---|---|
| 1.x | 13.x | approved runtime | 17 | supported |

Exact versions SHALL be pinned in release configuration.

---

# 96. No floating production versions

The following SHALL be prohibited:

```text
latest
master
main
unversioned plugin build
```

for production runtime dependencies.

---

# 97. Container image

Production ERP runtime images SHALL contain:

```text
approved iDempiere version
approved JVM
Baobab ERP feature/plugins
approved localisation plugins
required runtime dependencies
```

and nothing unnecessary.

---

# 98. Development image versus runtime image

`baobab-dev` remains a developer-tooling environment.

It SHALL NOT automatically become the ERP production runtime image.

Production images SHALL be purpose-built.

---

# 99. Immutable runtime

A production runtime image SHOULD be immutable.

Manual installation of new plugins directly into a running production container SHALL not be the normal deployment procedure.

---

# 100. Rebuild over repair

Production application nodes SHOULD normally be replaced from known images rather than manually repaired.

Persistent ERP state remains external.

---

# 101. CI pipeline

ERP extension CI SHALL include:

```text
compile
unit test
static analysis
dependency scan
license scan
package
integration tests
contract tests
container build
image scan
SBOM
```

---

# 102. SHA-pinned Actions

GitHub Actions used for `nabhold/baobab-erp` SHALL follow the organisation standard requiring full commit-SHA pinning.

Floating action tags SHALL not be accepted.

---

# 103. Reproducible build

Given the same:

```text
source commit
lock/config versions
upstream version
approved dependencies
```

the build SHOULD produce functionally equivalent artifacts.

---

# 104. Unit tests

Unit tests SHALL cover Baobab-owned logic independently from a full ERP runtime wherever practical.

Examples:

```text
mapping adapters
event translation
context validation
error translation
idempotency
```

---

# 105. ERP integration tests

Integration tests SHALL execute against a real supported iDempiere runtime.

Mocks SHALL not be considered sufficient for:

```text
document processing
accounting
tenant isolation
Application Dictionary behaviour
transactions
model validators
```

---

# 106. Contract tests

The ERP repository SHALL test compatibility with canonical contracts from `nabhold/shared`.

Examples:

```text
event schemas
context schema
API types
identifier conventions
error codes
```

---

# 107. Upgrade compatibility tests

Before upgrading iDempiere, automated tests SHALL validate:

```text
bundle resolution
Application Dictionary extensions
custom tables/columns
model validators
process invocation
REST adapters
outbox
tenant boundaries
financial regression
```

---

# 108. Upstream migration notes

Every upstream upgrade SHALL include review of iDempiere migration notes.

This is mandatory because upstream module boundaries and APIs can change between releases. Current migration documentation illustrates this with services and accounting code moving into separate bundles.

---

# 109. Upgrade sequence

Recommended upgrade lifecycle:

```text
new upstream version identified
        ↓
compatibility branch
        ↓
compile extensions
        ↓
migration-note review
        ↓
schema migration test
        ↓
integration suite
        ↓
financial regression
        ↓
security test
        ↓
staging deployment
        ↓
production rollout
```

---

# 110. Never upgrade production first

A new upstream release SHALL first be proven against:

```text
automated tests
representative database
extensions
localisations
integration contracts
```

---

# 111. Financial regression suite

The repository SHALL maintain representative end-to-end ERP scenarios.

Examples:

```text
purchase-to-pay
order-to-cash where applicable
goods receipt
supplier invoice
payment
posting
currency conversion
inventory accounting
period closing
```

Expected accounting outputs SHALL be tested.

---

# 112. Database migration ownership

Upstream iDempiere database migration remains governed by iDempiere-supported migration mechanisms.

Baobab extension migrations SHALL be independently versioned and ordered.

---

# 113. Extension migration versioning

Baobab extension schema SHALL have its own migration history.

Example:

```text
BB migration 000001
BB migration 000002
...
```

Exact implementation mechanism SHALL be defined in the repository specification.

---

# 114. No destructive automatic migration

Destructive schema changes SHALL require explicit review.

Production startup SHALL NOT casually drop or rewrite financially material data.

---

# 115. Backward-compatible deployment

Where practical, schema changes SHOULD support:

```text
expand
deploy
migrate
contract
```

rather than requiring instant destructive coupling between old and new runtime versions.

---

# 116. Observability

Every Baobab ERP request SHOULD record structured operational context such as:

```text
correlation_id
engine_instance_id
operation
outcome
duration
tenant pseudonymous/internal identifier where permitted
```

Sensitive business payloads SHALL not be logged by default.

---

# 117. Required metrics

At minimum:

```text
erp_requests_total
erp_request_duration
erp_request_failures_total

erp_outbox_pending
erp_outbox_publish_total
erp_outbox_publish_failures
erp_outbox_oldest_pending_seconds

erp_context_resolution_failures
erp_cross_tenant_denials
erp_mapping_failures

erp_document_process_failures
```

---

# 118. Health checks

The ERP Engine SHALL distinguish:

```text
liveness
readiness
dependency health
```

A process may be alive but unready because:

```text
database unavailable
critical plugin unresolved
Control Plane policy cache invalid
event outbox unavailable
```

---

# 119. Readiness semantics

An instance SHALL not be considered ready merely because the JVM accepts TCP connections.

Readiness SHOULD validate required operational dependencies.

---

# 120. OSGi health

Required Baobab bundles SHALL be verified active during readiness.

A partially resolved extension runtime SHALL not receive production traffic.

---

# 121. Audit logging

Security-sensitive operations SHALL produce audit records.

Examples:

```text
privileged operation
mapping override
administrative ERP access
context mismatch
cross-tenant denial
service identity change
```

Native ERP audit and Baobab platform audit SHALL complement each other.

---

# 122. Reconciliation

Because distributed engines operate asynchronously, reconciliation SHALL be first-class.

Examples:

```text
Medusa order acknowledged by ERP?
ERP invoice reflected downstream?
ERP event delivered?
canonical reference mapping complete?
```

---

# 123. Reconciliation state

Technical reconciliation state MAY be stored in ERP-owned extension tables when directly tied to ERP integration.

Platform-wide reconciliation orchestration MAY live outside ERP.

---

# 124. No direct Medusa callbacks inside native transaction

A Medusa acknowledgement SHALL not be required to commit an ERP financial transaction.

Use canonical events and reconciliation.

---

# 125. No direct Payload callbacks inside native transaction

The same applies to Payload.

ERP transaction success SHALL not depend on CMS availability.

---

# 126. Event consumer extensions

If ERP consumes canonical events, consumers SHALL:

```text
validate schema
validate Context
check idempotency
resolve canonical Mapping
execute application service
commit local transaction
record consumption result
```

---

# 127. Inbox pattern

For financially significant inbound events, Baobab SHOULD adopt an inbox/idempotency pattern analogous to the outbox.

Conceptually:

```text
event arrives
    ↓
deduplication
    ↓
local transaction
    ├── record consumed event
    └── ERP mutation
```

---

# 128. Consumer retry

Transient failures SHALL retry with bounded policy.

Permanent business failures SHALL not retry forever.

They SHALL be surfaced for reconciliation/operator handling.

---

# 129. Dead-letter handling

Dead-letter records SHALL preserve:

```text
event ID
event type
tenant context
failure reason
attempt history
correlation
```

Sensitive payload retention SHALL respect data policy.

---

# 130. No silent event discard

A financially relevant canonical event SHALL never be discarded because:

```text
deserialization failed
mapping missing
temporary ERP outage
```

The failure SHALL become observable and recoverable.

---

# 131. Canonical contract validation

Inbound events and commands SHALL be validated before native ERP mutation.

Invalid canonical payloads SHALL fail at the boundary.

---

# 132. ERP-native validation remains second line

Passing canonical validation does not imply the ERP operation is valid.

iDempiere's own business validations SHALL still execute.

Thus:

```text
canonical validity
        +
ERP validity
```

are both required.

---

# 133. Application services SHALL not expose PO objects

iDempiere persistent-object/model classes SHALL remain internal to the ERP implementation.

Public service signatures SHALL use Baobab-owned DTOs/interfaces.

---

# 134. Why PO isolation matters

If external contracts return native model objects:

```text
upstream schema
   ↓
becomes public API
```

which would make every upstream change a platform breaking change.

---

# 135. Persistence model boundary

Only the ERP native/application layers SHALL manipulate iDempiere persistence models.

HTTP controllers, event consumers and external adapters SHALL call application services.

---

# 136. Repository layout

A recommended repository structure is:

```text
baobab-erp/
│
├── extensions/
│   ├── org.nabhold.baobab.erp.contract/
│   ├── org.nabhold.baobab.erp.context/
│   ├── org.nabhold.baobab.erp.identity/
│   ├── org.nabhold.baobab.erp.application/
│   ├── org.nabhold.baobab.erp.integration/
│   ├── org.nabhold.baobab.erp.events/
│   ├── org.nabhold.baobab.erp.outbox/
│   ├── org.nabhold.baobab.erp.security/
│   └── org.nabhold.baobab.erp.observability/
│
├── features/
│   └── org.nabhold.baobab.erp.feature/
│
├── distribution/
│
├── migrations/
│
├── contracts/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── isolation/
│   └── financial/
│
├── docker/
├── scripts/
├── docs/
└── .github/
```

This is the preferred direction, not an obligation to create empty modules before they have useful ownership.

---

# 137. No architecture astronautics

Bundles SHALL be split because they own distinct responsibilities.

The project SHALL NOT create dozens of microscopic plugins merely to imitate theoretical modularity.

Cohesion comes first.

---

# 138. Package rules

Within each bundle:

```text
api
application
domain/adapters where useful
infrastructure
```

MAY be used.

Native iDempiere classes SHALL be contained toward the implementation side of the bundle.

---

# 139. API adapter ownership

If Baobab exposes an ERP HTTP API from within the iDempiere runtime, HTTP-specific classes SHALL be isolated from business application services.

The application layer SHALL remain callable from:

```text
HTTP
event consumer
administrative process
tests
```

without duplicating business logic.

---

# 140. Alternative sidecar

Some integration responsibilities MAY eventually run as a sidecar or separate service rather than OSGi bundle if doing so improves:

```text
security
operability
technology choice
scalability
upgrade independence
```

However ERP transaction hooks and transactional outbox creation MUST remain sufficiently close to ERP persistence to preserve atomicity.

---

# 141. Sidecar boundary

A sidecar MAY:

```text
publish outbox records
expose gateway-friendly API
perform Control Plane communication
```

but SHALL not recreate ERP business logic already inside iDempiere.

---

# 142. Java versus external service

Use Java/OSGi when the code must participate in:

```text
native transaction
iDempiere model lifecycle
Application Dictionary
native business process
```

Use external service technology when the code principally concerns:

```text
transport
gateway
protocol adaptation
cross-engine orchestration
```

and does not require native transaction participation.

---

# 143. Anti-corruption boundary remains regardless of deployment

Whether implemented:

```text
inside iDempiere
```

or:

```text
partly as adjacent service
```

the logical Baobab ERP boundary SHALL remain stable.

---

# 144. No cross-engine orchestration in validators

A model validator SHALL never implement:

```text
ERP changed
 → call Trade Engine
 → update CMS
 → call Control Plane
 → invoke AI engine
```

That would transform a local ERP hook into a distributed monolith.

---

# 145. Orchestration ownership

Multi-engine workflows SHOULD be coordinated through:

```text
canonical events
workflow/orchestration services
Control Plane where appropriate
```

not hidden inside ERP plugins.

---

# 146. Event choreography versus orchestration

Simple reactions MAY use choreography.

Example:

```text
erp.invoice.posted
      ↓
analytics updates projection
```

Complex workflows requiring compensation/state SHOULD use explicit orchestration.

ERP plugins SHALL not pretend asynchronous complexity does not exist.

---

# 147. Distributed transaction prohibition

XA/distributed ACID transactions across:

```text
ERP
Medusa
Payload
Control Plane
```

SHALL NOT be used as the default consistency model.

Use:

```text
local transactions
outbox
canonical events
idempotency
sagas
reconciliation
```

---

# 148. Data ownership invariant

Each engine owns its own persistence.

Therefore:

```text
iDempiere tables
```

SHALL not become shared platform tables.

Likewise ERP SHALL never manipulate Medusa or Payload tables.

---

# 149. Query integration

Where an external consumer requires ERP information:

```text
approved ERP query API
```

or:

```text
event-built projection
```

SHALL be used.

Direct SQL is not a platform integration contract.

---

# 150. Reporting exception

Approved reporting/ETL mechanisms MAY read ERP replicas or extracts under a separate architecture.

Such access SHALL not become transactional application coupling.

---

# 151. Extension licensing

All third-party iDempiere plugins SHALL undergo:

```text
license review
security review
maintenance assessment
compatibility review
```

before production adoption.

---

# 152. Plugin provenance

Production SHALL know:

```text
plugin name
version
source repository
commit
license
artifact digest
build provenance
```

for every non-core extension.

---

# 153. Abandoned plugin avoidance

A plugin SHALL not be selected merely because it exists.

Assess:

```text
supported iDempiere version
last maintenance
security posture
community/vendor support
source availability
testability
upgrade implications
```

---

# 154. Custom plugin ownership

Every Baobab plugin SHALL have:

```text
owning team
repository ownership
test suite
release version
documentation
```

No anonymous production JARs.

---

# 155. Architecture decision requirement

A new extension touching:

```text
accounting
security
tenant isolation
database structure
cross-engine integration
```

SHALL require architecture review.

---

# 156. Source compatibility

The extension SHALL compile against the supported upstream release without modifying upstream source.

If it cannot:

```text
upgrade blocker
```

must be recorded explicitly.

---

# 157. Runtime compatibility

Successful compilation is insufficient.

Bundles SHALL also be tested for:

```text
OSGi resolution
activation
service registration
runtime behaviour
```

---

# 158. Integration compatibility

Every release SHALL confirm compatibility with:

```text
baobab-cp contracts
nabhold/shared schemas
event transport
supported database
```

---

# 159. Security compatibility

Every release SHALL rerun:

```text
cross-client access tests
role tests
service-user tests
API authorization tests
context-leak tests
```

---

# 160. Core architectural invariants

```text
INV-ERP-EXT-001
Baobab SHALL NOT maintain a permanent private fork of iDempiere.

INV-ERP-EXT-002
Baobab-specific ERP behaviour SHALL use supported extension mechanisms.

INV-ERP-EXT-003
Upstream iDempiere SHALL never depend on Baobab code.

INV-ERP-EXT-004
Canonical platform concerns SHALL remain outside iDempiere authority.

INV-ERP-EXT-005
Native ERP models SHALL not cross the public engine boundary.

INV-ERP-EXT-006
Public APIs SHALL express business intent, not arbitrary table CRUD.

INV-ERP-EXT-007
Native REST SHALL not be the public Baobab ERP contract.

INV-ERP-EXT-008
Generic native REST SHALL not be directly exposed to the public Internet.

INV-ERP-EXT-009
Document lifecycle actions SHALL use native ERP processes.

INV-ERP-EXT-010
Baobab SHALL not mutate DocStatus-style fields to simulate business processing.

INV-ERP-EXT-011
Model validators SHALL not make blocking cross-engine network calls.

INV-ERP-EXT-012
Canonical events resulting from ERP transactions SHALL use a transactional outbox.

INV-ERP-EXT-013
Outbox insertion and ERP mutation SHALL share the local transaction when semantically coupled.

INV-ERP-EXT-014
Canonical events SHALL represent business facts rather than database changes.

INV-ERP-EXT-015
Event delivery SHALL assume at-least-once semantics.

INV-ERP-EXT-016
Event consumers SHALL be idempotent.

INV-ERP-EXT-017
ERP SHALL not own canonical Mapping authority.

INV-ERP-EXT-018
ERP SHALL not own canonical Tenant, Market, EngineInstance or IsolationProfile state.

INV-ERP-EXT-019
ERP SHALL not directly manipulate Medusa or Payload persistence.

INV-ERP-EXT-020
Cross-engine distributed ACID transactions are prohibited by default.

INV-ERP-EXT-021
Service integrations SHALL use least-privileged ERP identities.

INV-ERP-EXT-022
System-level ERP authority SHALL not be used for routine integrations.

INV-ERP-EXT-023
Baobab custom database extensions SHALL have explicit ownership.

INV-ERP-EXT-024
Custom ERP tables SHALL not become a second Control Plane.

INV-ERP-EXT-025
Production extension artifacts SHALL be reproducible and versioned.

INV-ERP-EXT-026
Production dependency versions SHALL be pinned.

INV-ERP-EXT-027
Every upstream upgrade SHALL pass extension compatibility tests.

INV-ERP-EXT-028
Financial regression testing SHALL precede production ERP upgrades.

INV-ERP-EXT-029
Production plugins SHALL have known provenance.

INV-ERP-EXT-030
Tenant Context SHALL never leak between requests or workers.
```

---

# 161. Initial implementation packages

The first production slice SHOULD contain only the modules required to establish the integration skeleton:

```text
erp.contract
erp.context
erp.identity
erp.application
erp.events
erp.outbox
erp.integration
erp.security
erp.observability
```

The initial implementation SHALL prove:

```text
Context resolution
      ↓
canonical-to-native Mapping
      ↓
native ERP operation
      ↓
transactional outbox
      ↓
canonical event publication
```

before broad ERP business functionality is added.

---

# 162. First vertical slice

The recommended first vertical slice is:

```text
Canonical command
    ↓
Create/resolve Business Partner
    ↓
Create purchase document
    ↓
Complete native ERP process
    ↓
Write outbox
    ↓
Commit
    ↓
Publish canonical event
```

This slice exercises nearly every architectural boundary without prematurely implementing the entire ERP domain.

---

# 163. Definition of done

ADR-ERP-004 SHALL be considered implemented when:

- [ ] iDempiere upstream source remains unmodified.
- [ ] Baobab extensions are separately packaged.
- [ ] OSGi bundle ownership boundaries are documented.
- [ ] A Baobab feature/distribution artifact exists.
- [ ] Bundle dependencies are explicit.
- [ ] Application Dictionary is preferred where appropriate.
- [ ] Model validators perform no blocking cross-engine calls.
- [ ] Business lifecycle operations use native iDempiere processes.
- [ ] Generic native REST is not publicly exposed.
- [ ] A Baobab business-intent API boundary exists.
- [ ] Canonical IDs are used externally.
- [ ] Native model objects remain internal.
- [ ] Control Plane Mapping resolution is integrated.
- [ ] Tenant Context is enforced per request.
- [ ] Worker Context is explicit.
- [ ] Transactional outbox exists.
- [ ] Outbox uses immutable event IDs.
- [ ] Event publisher supports retries.
- [ ] Consumers can deduplicate events.
- [ ] Canonical event schemas come from `nabhold/shared`.
- [ ] Correlation and causation identifiers propagate.
- [ ] Cross-engine direct database access does not exist.
- [ ] Service users follow least privilege.
- [ ] Production bundles/plugins have provenance metadata.
- [ ] CI verifies bundle resolution and activation.
- [ ] Tenant isolation integration tests exist.
- [ ] Financial regression tests exist.
- [ ] Upstream upgrade compatibility testing exists.
- [ ] Runtime images are immutable/reproducible.
- [ ] Production plugins are version-pinned.
- [ ] No canonical Control Plane registry is duplicated authoritatively inside ERP.

---

# 164. Final architectural model

```text
                   BAOBAB PLATFORM

      Control Plane             Shared Contracts
           │                          │
           └────────────┬─────────────┘
                        │
                        ▼
              Baobab ERP Boundary
                        │
       ┌────────────────┼────────────────┐
       │                │                │
    Context          Mapping          API/Event
       │                │                │
       └────────────────┼────────────────┘
                        ▼
                Application Services
                        │
          ┌─────────────┼──────────────┐
          │             │              │
     Processes      Validators      Outbox
          │             │              │
          └─────────────┼──────────────┘
                        ▼
                   iDempiere
                        │
                        ▼
                   PostgreSQL
```

The decisive architectural boundary is:

```text
Baobab Contract
      │
      ▼
Anti-Corruption Layer
      │
      ▼
Native ERP semantics
```

Never:

```text
Baobab ecosystem
      │
      ▼
generic iDempiere tables
```

---

# 165. Governing principle

The governing rule for all future iDempiere development SHALL be:

> **If a requirement changes how iDempiere performs ERP, implement it through a supported ERP extension. If it changes how Baobab understands tenants, markets, capabilities, topology or interoperability, keep it outside iDempiere and translate at the boundary.**

This keeps iDempiere powerful without allowing it to become the architecture of the entire Baobab Platform.

It also preserves the option that matters most in a long-lived enterprise system:

> **Baobab must be able to upgrade—or eventually replace—the ERP implementation without forcing every other engine and digital estate to understand iDempiere internals.**