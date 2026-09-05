# ADR-ERP-001 — Implement iDempiere as an Isolated, Headless, Multi-Tenant Baobab ERP Engine

**Status:** Accepted  
**Decision class:** Platform / ERP / Integration / Tenancy / Regionalisation  
**Scope:** `nabhold/baobab-erp`  
**Engine:** Baobab ERP Engine  
**Underlying product:** iDempiere 13 “Orion” LTS  
**Control Plane:** `nabhold/baobab-cp` — Go  
**Canonical contracts:** `nabhold/shared`  
**Date:** 2026-09-02  
**Supersedes:** Any architecture in which ERPNext/Frappe is the Baobab ERP implementation  
**Related architecture:** Baobab Canonical Mapping Model; Baobab Control Plane Physical Data Model; Tenancy Architecture; Organisation Model; Engine/EngineInstance/Capability contracts; Event Contract; Environment Contract

---

# 1. Decision

Baobab SHALL implement ERP capabilities through **iDempiere as an independently deployable, headless Baobab ERP Engine**.

iDempiere SHALL remain an autonomous bounded system responsible for ERP transactional behaviour, accounting, procurement, inventory, warehousing, business partners, financial documents and other explicitly enabled ERP capabilities.

Baobab SHALL NOT:

- embed iDempiere inside the Control Plane;
- expose iDempiere database tables as Baobab platform APIs;
- permit other engines to read or write the iDempiere database;
- use iDempiere identifiers as Baobab canonical identifiers;
- equate a Baobab Tenant automatically with an iDempiere Client;
- equate a Legal Entity automatically with an iDempiere Organization;
- modify iDempiere upstream core to implement Baobab concerns;
- use iDempiere as the authoritative source for Baobab tenancy, markets, digital estates, engine topology or platform identity;
- make the ERP Engine synchronously dependent on MedusaJS, Payload CMS or any digital estate for its own transactional integrity.

The architecture SHALL instead follow the established Baobab principle:

> **Standardise contracts, not implementations.**

That principle was already established for the wider platform-of-engines architecture.

iDempiere SHALL therefore participate in Baobab through:

1. canonical identities;
2. explicit mapping;
3. bounded APIs;
4. commands;
5. canonical events;
6. transactional outbox processing;
7. asynchronous integrations;
8. declarative EngineInstance configuration;
9. Control Plane resolution;
10. strong isolation profiles;
11. independently versioned deployment;
12. explicit regional, market and currency configuration.

---

# 2. Architectural intent

The ERP Engine is not “the Baobab backend.”

It is one specialist engine behind the Baobab Platform Contract.

```text
                         BAOBAB PLATFORM

                      ┌─────────────────┐
                      │  Control Plane  │
                      │       Go        │
                      └────────┬────────┘
                               │
                  Context / Resolution / Policy
                               │
       ┌───────────────────────┼────────────────────────┐
       │                       │                        │
       ▼                       ▼                        ▼
┌───────────────┐      ┌───────────────┐       ┌───────────────┐
│   ERP Engine  │      │ Trade Engine  │       │ Content Engine│
│   iDempiere   │      │   MedusaJS    │       │    Payload    │
└───────┬───────┘      └───────┬───────┘       └───────┬───────┘
        │                       │                        │
        └───────────────────────┼────────────────────────┘
                                │
                         Canonical Events
                                │
                                ▼
                      Other platform consumers
```

The central architectural concern is not whether iDempiere “supports multi-tenancy.”

It does.

The critical concern is whether its tenancy semantics are the **same semantics Baobab requires**.

They are not necessarily the same.

iDempiere describes its Tenant/Client as a company or legal entity and treats data between tenants as non-shareable; an Organization is an organizational unit within that tenant for which data may be shared across organizations.

Baobab deliberately separates:

```text
Tenant
Legal Entity
Organisation Unit
Market
Digital Estate
Engine
Engine Instance
Capability
Context
Isolation Profile
```

Consequently, translation between Baobab and iDempiere SHALL always be explicit.

---

# 3. Version baseline

The initial production baseline SHALL target:

```text
iDempiere 13 "Orion" LTS
Java 17-compatible runtime
PostgreSQL 17
Linux container runtime
```

As of this ADR, iDempiere 13 is the current stable LTS release, while iDempiere 14 remains the development line. iDempiere officially documents PostgreSQL support and lists PostgreSQL 14 or newer among supported database platforms.

Production SHALL NOT automatically track:

```text
latest
master
nightly
development
14-dev
```

The upstream product version SHALL be explicitly pinned.

Baobab-specific plugins SHALL likewise be independently versioned.

Example:

```text
Baobab ERP Engine release
    1.0.0

contains:

    iDempiere:
        13.x pinned release

    Baobab integration plugins:
        1.0.0

    database contract:
        erp-schema-version-X

    canonical event contract:
        baobab.events/v1
```

---

# 4. Bounded-context ownership

## 4.1 iDempiere SHALL own

Subject to capability enablement, the ERP Engine may be authoritative for:

- general ledger;
- accounting facts;
- charts of accounts;
- accounting schemas;
- accounting periods;
- accounts receivable;
- accounts payable;
- invoices;
- payments;
- procurement;
- purchase orders;
- goods receipts;
- supplier operational records;
- inventory accounting;
- inventory movements;
- warehouses;
- stock balances used for ERP purposes;
- landed costs;
- costing;
- fixed assets;
- ERP-side business partners;
- ERP-side products/items;
- financial projects;
- tax configuration used for posting;
- payment terms;
- ERP document sequences;
- ERP approvals and workflows;
- financial reports;
- statutory ERP records where configured.

This ownership means operational authority within its bounded context.

It does **not** mean canonical platform ownership.

---

# 5. Canonical ownership remains outside iDempiere

The Baobab Control Plane and canonical contract layer SHALL remain authoritative for platform identity and topology.

Examples include:

```text
CanonicalEntity
ExternalReference
Mapping
MappingScope
Market
DigitalEstate
Engine
EngineInstance
Capability
CapabilityBinding
Context
IsolationProfile
Tenant
LegalEntity
```

Therefore:

```text
Baobab UUID
    ≠
iDempiere numeric primary key
```

and:

```text
AD_Client_ID
    ≠ universally equivalent to Tenant ID

AD_Org_ID
    ≠ universally equivalent to LegalEntity ID

C_BPartner_ID
    ≠ canonical BusinessPartner ID

M_Product_ID
    ≠ canonical Product ID
```

Native identifiers remain engine-local identifiers.

---

# 6. Canonical identity mapping

Every externally meaningful ERP entity SHALL be linkable to a Baobab canonical entity through the Control Plane mapping system.

Conceptually:

```text
CanonicalEntity
    id = UUID

        │
        └── ExternalReference
                engine_instance = ERP-ZA-01
                namespace       = idempiere
                entity_type     = business_partner
                external_id     = 1001234
```

The mapping relationship SHALL be capable of expressing:

```text
canonical_entity_id
engine_instance_id
external_namespace
external_entity_type
external_identifier
mapping_scope
market_id
legal_entity_id
valid_from
valid_to
status
provenance
```

Canonical UUIDs SHALL be carried in integration metadata where practical but SHALL NOT replace native iDempiere keys internally.

---

# 7. Tenant translation model

## 7.1 Fundamental rule

**Baobab Tenant is a platform concept.**

**iDempiere Client is an ERP isolation concept.**

The two MAY correspond 1:1 for a particular deployment.

They SHALL NOT be assumed to correspond universally.

---

# 8. Default mapping policy

For the initial operating model, the preferred mapping SHALL be:

```text
Baobab consuming tenant
        │
        ▼
ERP capability binding
        │
        ▼
EngineInstance
        │
        ▼
iDempiere AD_Client
```

When a Legal Entity is itself the effective tenancy boundary, this may appear operationally as:

```text
Thamani canonical LegalEntity
          │
          │ capability binding
          ▼
Baobab ERP Engine Instance
          │
          ▼
iDempiere Client: Thamani
```

Within that Client:

```text
AD_Org
├── Head Office
├── Cape Town Operation
├── Johannesburg Operation
├── Uganda Operation
├── Warehouse A
└── other ERP organisations
```

But this is a **deployment mapping decision**, not a universal ontology.

---

# 9. iDempiere Organization SHALL not define Baobab tenancy

iDempiere itself allows data sharing among Organizations within the same Client.

Therefore a Baobab hard security boundary SHALL NOT normally be implemented merely as two `AD_Org_ID` values belonging to one `AD_Client_ID`.

Example:

```text
Legal Entity A
Legal Entity B
```

if required to have strong isolation SHALL normally become:

```text
AD_Client_A
AD_Client_B
```

or separate EngineInstances where higher isolation is required.

They SHALL NOT casually become:

```text
AD_Client_SHARED
    ├── AD_Org_A
    └── AD_Org_B
```

because an iDempiere Organization is not equivalent to Baobab's strongest isolation boundary.

---

# 10. Isolation profiles

The Control Plane SHALL resolve an `IsolationProfile` before routing ERP traffic.

Supported profiles SHOULD include at least:

| Isolation profile | ERP topology |
|---|---|
| `shared_instance_shared_client` | Exceptional; logically separated only |
| `shared_instance_dedicated_client` | Shared runtime/database, separate iDempiere Client |
| `dedicated_instance` | Dedicated iDempiere runtime/database |
| `dedicated_regional_instance` | Dedicated runtime/database within a designated region |
| `regulated_instance` | Dedicated runtime/database with jurisdiction-specific controls |

The default production profile for unrelated legal entities SHALL be:

```text
shared_instance_dedicated_client
```

only where regulatory, confidentiality and workload requirements permit it.

For higher assurance:

```text
dedicated_instance
```

or:

```text
dedicated_regional_instance
```

SHALL be used.

---

# 11. Defense in depth for tenant isolation

iDempiere 13 includes cross-tenant safeguards that prohibit cross-tenant reads/writes by default in normal persistence operations. Its migration notes explicitly instruct plugin developers to constrain access to the active Client and warn against unsafe cross-tenant access.

Baobab SHALL use this protection as **defense in depth**.

It SHALL NOT rely on it as the sole tenancy mechanism.

Isolation SHALL be enforced at:

```text
1. Control Plane resolution
2. Capability binding
3. EngineInstance routing
4. Authentication
5. iDempiere Client
6. iDempiere Role
7. iDempiere Organization access
8. integration plugin
9. database boundary where required
10. infrastructure/network boundary
```

---

# 12. Prohibition on routine cross-client operations

Baobab custom plugins SHALL NOT use iDempiere cross-tenant override mechanisms during ordinary business processing.

Cross-client operations SHALL be exceptional administrative operations requiring:

- explicit technical justification;
- named use case;
- code review;
- security review;
- audit;
- test coverage;
- bounded execution scope.

No generic “super tenant” integration service SHALL iterate through all clients during normal transaction processing.

---

# 13. EngineInstance is the deployment routing boundary

Baobab SHALL route ERP interactions by `EngineInstance`, not by hard-coded hostname.

Example resolution:

```text
Context
  tenant        = <canonical UUID>
  legal_entity  = <canonical UUID>
  market        = ZA
  capability    = erp.accounting

                    │
                    ▼

Control Plane Resolver

                    │
                    ▼

CapabilityBinding

                    │
                    ▼

EngineInstance
  id             = <UUID>
  code           = erp-af-south-01
  region         = af-south
  isolation      = shared_instance_dedicated_client
  status         = active

                    │
                    ▼

ExternalReference

                    │
                    ▼

AD_Client_ID = <engine-local ID>
```

Digital estates SHALL not perform this mapping themselves.

---

# 14. Regional deployment strategy

A single global ERP database SHALL NOT be an immutable architectural requirement.

Baobab SHALL support multiple ERP EngineInstances.

Example:

```text
Baobab ERP Engine
│
├── ERP-AF-SOUTH-01
│     region: Southern Africa
│
├── ERP-AF-EAST-01
│     region: East Africa
│
├── ERP-EU-WEST-01
│     region: European operations
│
└── ERP-ME-01
      region: future Middle East operations
```

A new market SHALL not necessarily require a new instance.

A new instance SHALL be driven by:

- data residency;
- sovereignty;
- statutory obligations;
- latency;
- business continuity;
- tenant isolation;
- capacity;
- legal segregation;
- M&A requirements;
- operational autonomy;
- risk appetite.

---

# 15. Market is not deployment region

Baobab SHALL distinguish:

```text
Market
```

from:

```text
Infrastructure Region
```

Example:

```text
Market:
    Uganda

Infrastructure Region:
    AWS Africa (Cape Town)
```

or eventually:

```text
Market:
    Zambia

ERP EngineInstance:
    Southern Africa cluster
```

A `Market` describes where commerce/business takes place.

An `EngineInstance.region` describes where software/data is operated.

They SHALL never be conflated.

---

# 16. Legal Entity is not Market

A Legal Entity MAY operate in:

```text
1..N markets
```

A market MAY contain:

```text
1..N legal entities
```

Consequently the ERP configuration SHALL support:

```text
Legal Entity
     │
     ├── Market ZA
     ├── Market UG
     ├── Market KE
     └── future markets
```

without requiring the canonical LegalEntity itself to change identity.

---

# 17. Multi-currency architecture

Currency SHALL be treated as transactional context, not tenant identity.

The platform SHALL support:

```text
Legal entity functional currency
Accounting schema currency
Document currency
Price-list currency
Settlement currency
Reporting currency
Consolidation currency
```

as separate concepts where required.

iDempiere's Accounting Schema defines accounting rules including currency and calendar, while its Price Lists determine document currency and tax treatment.

Baobab SHALL use these native capabilities rather than creating a parallel ERP currency subsystem.

---

# 18. Currency canonicalisation

Currency identifiers crossing platform boundaries SHALL use canonical ISO 4217 codes.

Example:

```json
{
  "currency": "ZAR"
}
```

not:

```json
{
  "currency_id": 100
}
```

An iDempiere internal currency ID SHALL remain engine-local.

Canonical mappings MAY maintain an ExternalReference when required.

---

# 19. Exchange rates

The ERP Engine SHALL own exchange rates used for statutory and accounting posting within the ERP context.

External market-data engines MAY provide currency-rate observations.

However:

```text
market FX observation
        ≠
automatically authoritative accounting conversion rate
```

A controlled process SHALL determine whether an external FX observation becomes an ERP accounting conversion rate.

This avoids silently changing posted financial results because an intelligence or market-data feed changed.

---

# 20. Accounting date semantics

Canonical financial events SHALL distinguish at minimum:

```text
occurred_at
document_date
accounting_date
posted_at
event_created_at
```

iDempiere uses Accounting Date for general-ledger posting and currency conversion.

Therefore Baobab SHALL never assume:

```text
event timestamp == accounting date
```

---

# 21. Time zones

Time zone SHALL form part of resolved Context.

The model SHALL distinguish:

```text
user time zone
market time zone
legal entity time zone
engine instance time zone
accounting date
UTC event timestamp
```

All canonical event timestamps SHALL use ISO 8601 timestamps with explicit UTC offsets, preferably UTC for event transport.

Business dates SHALL retain their domain semantics.

iDempiere Client configuration supports a tenant-level time zone.

---

# 22. Country localisation

Country localisation SHALL be treated as a deployable ERP capability, not a fork of iDempiere.

Localisation may include:

- tax rules;
- statutory reports;
- electronic invoicing;
- fiscal numbering;
- withholding;
- language;
- geography;
- statutory account structures;
- payment conventions.

iDempiere's ecosystem explicitly supports localisation extensions for countries and regions.

Baobab SHALL package such functionality through plugins and configuration.

---

# 23. No core forks for localisation

Baobab SHALL NOT maintain a permanent private fork of iDempiere core merely to support regional requirements.

The hierarchy SHALL be:

```text
upstream iDempiere
       │
       ├── configuration
       ├── application dictionary configuration
       ├── Baobab OSGi plugins
       ├── approved localisation plugins
       └── Baobab integration plugins
```

The iDempiere developer guidance itself recommends extensions/plugins instead of modifying core, specifically because direct core/schema modifications damage upgradeability.

---

# 24. Headless operating model

Baobab SHALL treat iDempiere primarily as a **headless ERP engine**.

Its WebUI MAY remain available for:

- finance administration;
- ERP configuration;
- accounting operations;
- advanced back-office workflows;
- audit/reconciliation;
- authorised ERP specialists.

It SHALL NOT become the customer-facing presentation layer.

Public and subsidiary experiences SHALL live in Digital Estates.

```text
Customer
   │
   ▼
Digital Estate
   │
   ├── MedusaJS
   ├── Payload CMS
   └── Baobab APIs
             │
             ▼
        ERP capability
             │
             ▼
          iDempiere
```

---

# 25. Integration surface

External consumers SHALL communicate through Baobab-defined service contracts.

The supported hierarchy SHALL be:

```text
Canonical Baobab API
        │
        ▼
ERP Adapter / Integration Plugin
        │
        ▼
iDempiere application services
```

Direct generic access to the complete iDempiere REST surface SHALL NOT be considered the Baobab ERP public contract.

---

# 26. API gateway requirement

The native iDempiere REST interface SHALL remain an internal integration surface.

It SHALL NOT be directly Internet exposed.

iDempiere's own security guidance warns that its REST facilities are powerful and recommends placing an API gateway between REST services and external consumers.

The production route SHALL therefore resemble:

```text
Consumer
   │
   ▼
Baobab Gateway
   │
   ▼
Authentication / Context
   │
   ▼
ERP Facade / Integration API
   │
   ▼
iDempiere
```

---

# 27. API design

Canonical ERP APIs SHOULD model business capabilities rather than database tables.

Good:

```text
POST /erp/v1/supplier-invoices
POST /erp/v1/purchase-orders
POST /erp/v1/payments
POST /erp/v1/goods-receipts
GET  /erp/v1/inventory-positions
```

Discouraged:

```text
POST /api/C_Invoice
POST /api/C_Order
PUT  /api/M_Product/1000421
```

The Baobab boundary SHALL expose intent, not iDempiere internals.

---

# 28. Commands and queries

Write operations SHALL be modelled as commands.

Examples:

```text
CreateSupplier
CreatePurchaseOrder
AcknowledgeGoodsReceipt
CreateSupplierInvoice
PostInvoice
RegisterPayment
CreateInventoryAdjustment
```

Queries SHALL be explicit read models.

Examples:

```text
GetSupplier
GetPurchaseOrder
GetInvoice
GetStockPosition
GetAccountBalance
```

This preserves the ability to replace or substantially change the ERP implementation without breaking Baobab consumers.

---

# 29. Events

ERP integration SHALL be event driven wherever immediate synchronous coupling is unnecessary.

Canonical ERP events SHALL use past-tense business facts.

Examples:

```text
erp.supplier.created.v1
erp.supplier.updated.v1

erp.purchase-order.created.v1
erp.purchase-order.approved.v1
erp.purchase-order.completed.v1

erp.goods-receipt.completed.v1

erp.supplier-invoice.completed.v1
erp.supplier-invoice.posted.v1

erp.customer-invoice.completed.v1
erp.customer-invoice.posted.v1

erp.payment.completed.v1

erp.inventory-adjusted.v1

erp.accounting-period.closed.v1
```

Events SHALL describe facts that have happened.

They SHALL NOT be disguised RPC instructions.

Bad:

```text
erp.create_invoice
```

Good:

```text
erp.invoice.created.v1
```

---

# 30. Canonical event envelope

Every Baobab ERP event SHALL conform to the organisation-wide event envelope.

Minimum conceptual fields:

```json
{
  "specversion": "1.0",
  "id": "<uuid>",
  "type": "erp.supplier-invoice.posted.v1",
  "source": "baobab://engine-instance/<uuid>",
  "subject": "canonical-entity/<uuid>",
  "time": "2026-09-02T03:00:00Z",

  "tenant_id": "<uuid>",
  "legal_entity_id": "<uuid>",
  "market_id": "<uuid>",
  "engine_id": "<uuid>",
  "engine_instance_id": "<uuid>",

  "correlation_id": "<uuid>",
  "causation_id": "<uuid>",
  "trace_id": "...",

  "schema": "baobab://contracts/events/erp/.../v1",

  "data": {}
}
```

Not every Context dimension is necessarily applicable to every event.

Fields SHALL nevertheless follow the canonical contract rather than engine-native conventions.

---

# 31. Transactional outbox

Events SHALL NOT be published directly as an uncontrolled side effect of business methods.

A transactional-outbox mechanism SHALL ensure that:

```text
ERP transaction committed
        │
        AND
        │
canonical event recorded
```

form one durable transactional outcome.

Conceptually:

```text
BEGIN

iDempiere business transaction
        │
        ├── domain state changes
        └── outbox record

COMMIT

        │
        ▼

Outbox Publisher
        │
        ▼

Event Transport
```

This prevents:

```text
database commit succeeds
event publication fails
```

from silently producing inconsistent cross-engine state.

---

# 32. Event interception mechanism

Baobab ERP extensions SHOULD use native iDempiere extension mechanisms such as OSGi services and model lifecycle interfaces where appropriate.

iDempiere's OSGi architecture explicitly exposes interfaces including `IModelValidator`, which is invoked on model persistence events.

However, low-level model events SHALL NOT automatically become canonical platform events.

For example:

```text
C_Invoice row changed
```

does not necessarily equal:

```text
erp.invoice.posted.v1
```

Canonical events SHALL reflect business semantics.

---

# 33. Delivery semantics

The initial event guarantee SHALL be:

```text
at-least-once delivery
```

not impossible-to-guarantee distributed exactly-once semantics.

Consumers SHALL therefore be idempotent.

Every event SHALL have an immutable globally unique event ID.

Consumer processing SHOULD maintain:

```text
consumer
event_id
processed_at
result
```

or equivalent deduplication state.

---

# 34. Event ordering

Baobab SHALL NOT promise universal ordering across all ERP events.

Ordering guarantees, when required, SHALL exist only within explicitly defined aggregates or partitions.

Potential ordering key:

```text
canonical_entity_id
```

or:

```text
document canonical ID
```

Consumers SHALL not rely on total global ordering.

---

# 35. Integration with MedusaJS

The ERP Engine and Trade Engine SHALL remain peers.

Neither SHALL become a subordinate database of the other.

```text
MedusaJS
    │
    ├── API
    └── Events
          │
          ▼
   Baobab Integration
          │
          ▼
      iDempiere
```

and:

```text
iDempiere
    │
    └── Events
          │
          ▼
   Baobab Integration
          │
          ▼
      MedusaJS
```

No:

```text
Medusa → SELECT * FROM idempiere...
```

No:

```text
iDempiere → UPDATE medusa_product...
```

---

# 36. Product ownership boundary

The platform SHALL distinguish the meanings of “product.”

Conceptually:

```text
Canonical Product
       │
       ├── Medusa Product
       │      commerce representation
       │
       └── iDempiere M_Product
              ERP representation
```

Neither representation universally replaces the canonical identity.

Medusa MAY own:

- merchandising;
- storefront availability;
- channel assortment;
- commerce presentation;
- commerce pricing workflows.

iDempiere MAY own:

- inventory accounting;
- procurement representation;
- costing;
- financial posting configuration;
- ERP item configuration.

Mappings SHALL explicitly reconcile them.

---

# 37. Business Partner ownership

Similarly:

```text
Canonical Party / Organisation
        │
        ├── Medusa Customer
        └── iDempiere Business Partner
```

An iDempiere `C_BPartner_ID` is not the platform identity of the organisation.

This is especially important because a party may simultaneously be:

```text
customer
supplier
employee
agent
affiliate
```

depending on context.

---

# 38. Payload CMS boundary

Payload CMS SHALL own content.

iDempiere SHALL not become:

- product-copy CMS;
- website-content repository;
- editorial workflow engine;
- page composer;
- media catalogue for digital publishing.

ERP may maintain factual operational attributes required for ERP processing.

Payload maintains editorial content.

Canonical mappings may connect both representations.

---

# 39. Data sovereignty

Data classification and residency SHALL be resolved before provisioning an ERP EngineInstance.

Required context SHOULD include:

```text
jurisdiction
deployment region
residency policy
retention policy
classification
backup region
disaster-recovery region
```

A tenant SHALL not be moved between ERP EngineInstances merely for operational convenience if that migration violates residency or statutory obligations.

---

# 40. Database architecture

Every production EngineInstance SHALL have an explicitly assigned ERP database.

The database is private to the ERP Engine.

```text
ERP EngineInstance
       │
       ▼
Private PostgreSQL
```

Other engines SHALL have no runtime credentials for it.

Database credentials SHALL be scoped only to required ERP services and administrative roles.

---

# 41. Shared database prohibition

The following topology is prohibited:

```text
                  Shared PostgreSQL Schema
                   /        |         \
               Medusa   iDempiere   Payload
```

The approved topology is:

```text
Medusa
   │
   ▼
Medusa DB

iDempiere
   │
   ▼
ERP DB

Payload
   │
   ▼
Payload DB
```

Even if all three happen to use PostgreSQL, database technology commonality SHALL not become database coupling.

---

# 42. Database access

Production application credentials SHALL follow least privilege.

Administrative credentials SHALL not be embedded in containers.

Credentials SHALL be:

- injected at runtime;
- stored in approved secret management;
- rotatable;
- separately scoped by environment;
- separately scoped by EngineInstance;
- auditable.

---

# 43. Extension architecture

All Baobab-specific iDempiere code SHALL be implemented through isolated OSGi plugins wherever technically practical.

Suggested logical bundles:

```text
org.nabhold.baobab.erp.contract
org.nabhold.baobab.erp.identity
org.nabhold.baobab.erp.context
org.nabhold.baobab.erp.integration
org.nabhold.baobab.erp.events
org.nabhold.baobab.erp.outbox
org.nabhold.baobab.erp.observability
```

These names are indicative; package boundaries may be refined during implementation.

The principle is mandatory:

> Baobab customisation SHALL remain outside upstream core.

iDempiere's OSGi architecture is specifically designed to allow independently deployable plugins without modifying the upstream codebase.

---

# 44. Upstream-core policy

Changes SHALL be classified as:

```text
A. configuration
B. Baobab plugin
C. localisation plugin
D. upstream contribution
E. prohibited private core patch
```

Category E SHALL require an explicit exception ADR.

If functionality is generally useful to iDempiere, contribution upstream SHOULD be preferred over long-lived private core divergence.

---

# 45. Authentication

External application users SHALL authenticate through Baobab-approved identity infrastructure.

A digital-estate user's identity SHALL not necessarily imply an interactive iDempiere account.

Machine-to-machine integration SHALL use workload identities/service credentials appropriate to the security architecture.

The ERP integration layer SHALL translate authenticated platform identity into the ERP authorization context required for the operation.

---

# 46. Authorization

Authorization SHALL be defense in depth:

```text
Platform Identity
       │
       ▼
Tenant membership
       │
       ▼
Capability authorization
       │
       ▼
Context resolution
       │
       ▼
EngineInstance policy
       │
       ▼
ERP service identity / role
       │
       ▼
iDempiere authorization
```

A valid JWT alone SHALL never imply authorization to perform arbitrary ERP operations.

---

# 47. Advanced iDempiere roles

Advanced iDempiere roles SHALL be treated as privileged administrative access.

The iDempiere project itself notes the broad power available through advanced roles.

Such access SHALL therefore be:

- limited;
- named;
- MFA-protected where supported by the identity architecture;
- logged;
- periodically reviewed;
- prohibited for ordinary integration workloads.

---

# 48. Correlation and trace context

All synchronous and asynchronous calls SHALL propagate:

```text
request_id
correlation_id
causation_id
trace_id
tenant_id
legal_entity_id
engine_instance_id
```

as applicable.

An ERP transaction originating from Medusa should therefore be traceable:

```text
customer action
   ↓
digital estate request
   ↓
trade command
   ↓
trade event
   ↓
ERP command
   ↓
iDempiere document
   ↓
ERP event
```

without relying on human interpretation of logs.

---

# 49. Audit

Three audit domains SHALL remain distinct.

## ERP audit

iDempiere-native document and accounting history.

## Platform audit

Who invoked which Baobab operation in which Context.

## Integration audit

Which message or command crossed which system boundary and with what result.

These SHALL complement one another.

They SHALL not be collapsed into one generic log file.

---

# 50. Observability

Every EngineInstance SHALL expose observable signals sufficient for production operation.

Minimum classes:

```text
health
readiness
availability
latency
request rate
error rate
database health
JVM health
queue/outbox depth
event publication failures
integration retries
authentication failures
tenant-resolution failures
posting failures
background-process status
```

OSGi/JVM/iDempiere runtime metrics SHALL be complemented by Baobab integration metrics.

---

# 51. Logging

Structured logs SHALL be preferred.

Log records SHOULD include:

```text
timestamp
severity
service
engine_instance_id
environment
tenant_id
legal_entity_id
correlation_id
trace_id
operation
outcome
error_code
```

Sensitive accounting, customer, authentication or payment data SHALL not be indiscriminately logged.

---

# 52. Health checks

Health SHALL distinguish:

```text
liveness
readiness
dependency health
business-process health
```

For example:

```text
JVM alive
```

does not mean:

```text
ERP is ready to receive transactions
```

if its database or essential plugin is unavailable.

---

# 53. Failure isolation

Failure of one ERP EngineInstance SHALL not require failure of every Baobab ERP tenant.

Regional and dedicated instances SHALL therefore provide natural blast-radius containment.

Similarly:

```text
ERP unavailable
```

SHALL not automatically make:

```text
Payload CMS unavailable
```

or:

```text
Medusa storefront browsing unavailable
```

where those functions can operate independently.

---

# 54. Synchronous versus asynchronous coupling

Use synchronous integration when an immediate authoritative answer is required.

Examples:

```text
validate supplier state
retrieve ERP document status
perform explicitly requested ERP command
```

Use asynchronous integration for propagation and eventual consistency.

Examples:

```text
supplier updated
invoice posted
stock accounting changed
payment completed
```

The default between engines SHALL favour asynchronous propagation.

---

# 55. ERP unavailability

Upstream systems SHALL define explicit behaviour for ERP outages.

For operations that do not require immediate ERP commitment:

```text
accept locally
persist intent
queue integration
retry
reconcile
```

may be permitted.

For operations that require ERP authority:

```text
fail safely
```

shall be preferred over pretending that the ERP transaction succeeded.

---

# 56. Retry policy

Retries SHALL be:

- bounded;
- observable;
- idempotent;
- exponentially backed off;
- aware of retryable versus permanent errors.

A malformed supplier invoice SHALL not be retried forever.

A temporary network timeout may be retried.

---

# 57. Dead-letter handling

Messages that cannot be automatically processed SHALL enter a controlled failure state.

The platform SHALL record:

```text
message/event ID
original payload reference
error classification
attempt count
first failure
last failure
tenant/context
engine instance
resolution status
```

Operational tooling SHALL support replay after remediation.

---

# 58. Idempotency

All externally invokable financial commands SHALL support idempotency wherever duplicate execution could produce duplicate ERP documents.

Example:

```text
Idempotency-Key:
    4c1...
```

The same command retried because of a timeout SHALL not accidentally produce:

```text
Invoice 1
Invoice 2
Invoice 3
```

---

# 59. Optimistic consistency

Distributed engines SHALL not attempt distributed ACID transactions.

Baobab SHALL NOT implement:

```text
BEGIN distributed transaction

Medusa DB
iDempiere DB
Payload DB

COMMIT
```

Cross-engine consistency SHALL use:

- local transactions;
- outbox;
- canonical events;
- idempotency;
- reconciliation;
- compensating actions where necessary.

---

# 60. Reconciliation

Event-driven architecture SHALL be complemented by reconciliation.

Critical mappings SHOULD support scheduled comparison such as:

```text
Medusa order financial status
          ↔
ERP invoice/payment status

Medusa fulfillment quantity
          ↔
ERP receipt/issue state

Canonical supplier
          ↔
ERP business partner
```

Events provide immediacy.

Reconciliation provides assurance.

Both are required for enterprise-grade integration.

---

# 61. Accounting remains authoritative

No other Baobab engine SHALL recreate ERP accounting calculations merely for convenience.

Examples prohibited outside ERP authority:

- duplicate general ledger;
- duplicate statutory posting engine;
- duplicate AP ledger;
- duplicate AR ledger;
- duplicate accounting-period control.

Other engines may maintain derived read models.

They SHALL not become competing books of record.

---

# 62. Reporting

Operational ERP reporting MAY be provided directly by iDempiere for authorised back-office users.

Cross-engine business intelligence SHOULD consume:

```text
canonical events
approved extracts
analytical projections
```

rather than issuing unrestricted analytical queries against production ERP tables.

Operational ERP and analytical workloads SHOULD remain separable.

---

# 63. Data warehouse boundary

Future analytics infrastructure SHALL not become part of the transactional ERP database.

Future pattern:

```text
iDempiere
     │
     ├── canonical events
     └── controlled CDC/export
              │
              ▼
       Analytical Platform
```

not:

```text
BI users
   │
   ▼
production Fact_Acct
```

with unrestricted access.

---

# 64. Backup and restore

Each EngineInstance SHALL define:

```text
RPO
RTO
backup frequency
retention
encryption
off-site storage
restore procedure
restore verification
```

according to its IsolationProfile and business criticality.

Backup existence SHALL not be treated as proof of recoverability.

Restoration SHALL be routinely tested.

---

# 65. Point-in-time recovery

Where PostgreSQL infrastructure permits, production ERP instances SHOULD support point-in-time recovery.

Financial transaction systems SHALL normally receive stronger durability and recovery requirements than non-critical content services.

---

# 66. Disaster recovery

Multi-region disaster recovery SHALL be introduced according to business requirements rather than imposed indiscriminately.

An EngineInstance MAY define:

```text
primary_region
recovery_region
recovery_mode
rpo
rto
```

The Control Plane SHALL know the lifecycle state of the active EngineInstance.

---

# 67. EngineInstance lifecycle

An ERP EngineInstance SHALL progress through explicit lifecycle states.

Suggested model:

```text
provisioning
      ↓
configured
      ↓
validating
      ↓
active
      ↓
draining
      ↓
suspended
      ↓
retired
```

Additional failure states may include:

```text
degraded
failed
quarantined
```

Traffic SHALL only be routed to an instance in an acceptable serving state.

---

# 68. Tenant onboarding lifecycle

ERP tenant/client onboarding SHALL be orchestrated.

Conceptually:

```text
Canonical tenant/legal entity exists
        ↓
ERP capability requested
        ↓
IsolationProfile resolved
        ↓
EngineInstance selected/provisioned
        ↓
AD_Client created/configured
        ↓
Organizations configured
        ↓
Accounting schema configured
        ↓
Currency/calendar configured
        ↓
Roles configured
        ↓
Mappings created
        ↓
Contract validation
        ↓
Smoke tests
        ↓
CapabilityBinding activated
```

No tenant SHALL be considered ERP-enabled merely because an `AD_Client` row exists.

---

# 69. Market onboarding

Entering a new market SHALL trigger explicit assessment of:

- localisation;
- taxation;
- currency;
- statutory reporting;
- invoicing;
- electronic fiscal requirements;
- data residency;
- time zone;
- language;
- chart-of-accounts implications;
- banking;
- payment conventions;
- warehouse/geographic model.

Market enablement SHALL therefore be a governed capability lifecycle.

---

# 70. Configuration as code

Platform-level configuration SHOULD be represented declaratively where practical.

Examples:

```text
engine version
plugin versions
deployment region
resource limits
feature activation
secret references
monitoring configuration
network policy
```

Financial master data SHALL not blindly be treated as infrastructure configuration.

ERP master-data governance remains a business concern.

---

# 71. Environment separation

At minimum:

```text
development
test
staging
production
```

SHALL remain separate environments.

Production financial data SHALL not be copied casually into development.

Sanitisation/anonymisation SHALL be required where production-derived datasets are used in non-production systems.

---

# 72. Containerisation

The Baobab ERP Engine SHALL be container deployable.

The runtime image SHALL:

- contain only required runtime components;
- run as a non-root user;
- be reproducibly built;
- be immutable;
- be vulnerability scanned;
- be digest-addressable;
- have pinned dependencies;
- not contain development credentials;
- not contain database backups;
- not use mutable application source mounts in production.

The upstream iDempiere project currently recommends its Docker deployment path for simplified installation.

---

# 73. Development environment

Development SHALL use the approved `nabhold/baobab-dev` profile appropriate to Java/iDempiere development, while runtime packaging remains engine-specific.

The development image is the engineering toolbox.

The ERP runtime image is the production machine.

They SHALL not be conflated.

---

# 74. CI/CD

The `nabhold/baobab-erp` pipeline SHALL include at minimum:

```text
compile
unit tests
plugin tests
contract tests
integration tests
migration validation
static analysis
dependency scan
secret scan
container build
container scan
SBOM generation
signature/attestation
deployment validation
```

GitHub Actions SHALL remain SHA-pinned according to Nabhold organisation standards.

---

# 75. Supply-chain provenance

Production artifacts SHALL be traceable to:

```text
Git commit
workflow
iDempiere upstream version
Baobab plugin versions
container digest
SBOM
build provenance
configuration release
```

The production ERP Engine SHALL not be deployed from an unversioned workstation build.

---

# 76. Upgrade policy

iDempiere SHALL be treated as an upstream dependency.

Upgrade procedure SHALL include:

```text
upstream release assessment
security assessment
plugin compatibility
database migration review
contract compatibility testing
regional localisation testing
accounting regression testing
integration testing
performance testing
staging soak
backup verification
production rollout
rollback strategy
```

Because Baobab avoids modifying upstream core, upgrades should remain materially safer than maintaining a deep fork.

---

# 77. Contract compatibility

Baobab APIs and canonical events SHALL be versioned independently from iDempiere.

Therefore upgrading:

```text
iDempiere 13.x → future LTS
```

SHALL NOT automatically imply:

```text
Baobab ERP API v1 → v2
```

The adapter layer absorbs engine-specific changes where semantics remain unchanged.

---

# 78. Schema evolution

Canonical events SHALL follow additive evolution where possible.

Existing event fields SHALL not silently change meaning.

Breaking changes SHALL require a new event version.

Example:

```text
erp.invoice.posted.v1
erp.invoice.posted.v2
```

During migration the producer MAY temporarily publish both when justified.

---

# 79. API error contract

Native iDempiere exceptions SHALL not leak directly to platform consumers.

Errors SHALL map into the Baobab error model.

Example:

```json
{
  "type": "https://contracts.nabhold/.../erp/document-period-closed",
  "title": "Accounting period is closed",
  "status": 409,
  "code": "ERP_PERIOD_CLOSED",
  "correlation_id": "...",
  "context": {}
}
```

No consumer should need to parse a Java stack trace or an iDempiere database constraint message.

---

# 80. Security boundaries

Production networking SHALL enforce:

```text
Internet
   │
   ▼
Gateway
   │
   ▼
Baobab integration interface
   │
   ▼
ERP Engine
   │
   ▼
ERP database
```

The database SHALL not be Internet reachable.

The native administrative interface SHALL receive stronger network and identity restrictions than ordinary platform APIs.

---

# 81. Secrets

Secrets SHALL never be:

- committed to Git;
- stored in canonical event payloads;
- copied into logs;
- embedded in Dockerfiles;
- embedded in frontend bundles;
- passed through Payload content;
- stored in Medusa product metadata.

Secret references MAY be represented in configuration.

Secret values SHALL remain in the secret-management boundary.

---

# 82. PII and financial data

Events SHALL carry only data necessary for their consumers.

A canonical event SHALL not become a convenient replica of an entire ERP row/document.

Minimise:

```text
personal information
bank information
tax identifiers
account details
financially sensitive fields
```

unless the business contract explicitly requires them.

---

# 83. Change-data-capture policy

Raw database CDC MAY eventually be used for analytics or operational replication.

It SHALL NOT replace semantic canonical events for platform integration.

Difference:

```text
CDC:
    row X changed

Canonical event:
    supplier invoice was posted
```

Baobab requires the latter for stable business integration.

---

# 84. Performance scaling

The architecture SHALL permit independent ERP scaling.

Scaling decisions may include:

- JVM resources;
- database capacity;
- connection pools;
- asynchronous workers;
- separate EngineInstances;
- geographic partitioning;
- tenant migration;
- dedicated-instance promotion.

Medusa or Payload scaling SHALL not require iDempiere to scale identically.

---

# 85. No premature global distribution

Baobab SHALL be **multi-region capable**, not necessarily multi-region active-active on day one.

The architecture must avoid design choices preventing regional expansion.

It does not need to incur the operating cost of that expansion before demand exists.

---

# 86. Tenant promotion

A tenant originally operating inside a shared ERP EngineInstance SHALL be migratable to a dedicated instance.

Example:

```text
Before:

ERP-AF-SOUTH-01
    ├── Nabhold
    ├── Thamani
    └── Zuribeans
```

Later:

```text
ERP-AF-SOUTH-01
    ├── Nabhold
    └── Thamani

ERP-ZURIBEANS-01
    └── Zuribeans
```

Canonical entity IDs SHALL remain stable.

Only ExternalReferences, CapabilityBindings and EngineInstance mappings change.

That is one of the primary reasons canonical identity MUST not be an iDempiere ID.

---

# 87. Mergers, acquisitions and divestitures

The architecture SHALL also permit:

```text
tenant split
tenant merge
legal-entity transfer
market transfer
engine-instance migration
```

without changing historical canonical identity unnecessarily.

The Mapping model SHALL be temporal so historical transactions can still be resolved according to the configuration effective at the time.

---

# 88. Historical mapping

Mappings SHALL support validity periods.

Example:

```text
Canonical supplier X

2026-01-01 → 2028-03-31
    ERP-AF-01 / C_BPartner 100033

2028-04-01 →
    ERP-AF-02 / C_BPartner 200918
```

Deleting the old mapping would corrupt historical traceability.

---

# 89. Test strategy

Testing SHALL include at least six layers:

### Unit

Baobab plugin/domain logic.

### Engine integration

iDempiere API/plugin behaviour.

### Contract

Canonical commands, responses and events.

### Cross-engine

Medusa ↔ ERP and other integrations.

### Tenant isolation

Attempts to cross tenant/client boundaries.

### Regionalisation

Currencies, dates, taxes, localisations and market-specific configuration.

Financial integrations SHALL additionally have accounting reconciliation tests.

---

# 90. Isolation tests

Automated tests SHALL attempt prohibited operations such as:

```text
Tenant A reads Tenant B invoice
Tenant A updates Tenant B supplier
Context A routed to Instance B
invalid Client mapping
invalid Organization mapping
cross-market configuration leakage
```

A multi-tenant architecture is not validated merely because the happy path works.

---

# 91. Contract tests

`nabhold/shared` SHALL provide machine-readable contracts consumed by ERP CI.

The ERP repository SHALL fail CI where it becomes incompatible with required organisational contracts.

This SHALL include as applicable:

```text
JSON Schema
OpenAPI
AsyncAPI
event envelope
canonical enums
error model
context headers
version policy
```

---

# 92. Financial regression testing

A representative accounting test suite SHALL verify outcomes such as:

```text
purchase order
goods receipt
supplier invoice
payment
currency conversion
inventory costing
posting
period close
reversal
credit note
```

after every material engine or plugin upgrade.

Passing HTTP contract tests alone is insufficient for an ERP engine.

---

# 93. Data migration

Migration into iDempiere SHALL preserve:

```text
source identity
canonical identity
destination identity
migration batch
provenance
reconciliation result
```

Historical records SHALL not lose their source-system lineage.

Any migration from ERPNext SHALL therefore be handled as a controlled data-migration programme rather than direct table conversion.

---

# 94. Rejected alternative — Use one AD_Client for the entire Nabhold ecosystem

**Rejected.**

Why:

iDempiere Organizations share a Client boundary.

This would risk turning legal entities and tenants into mere organisational partitions when Baobab requires stronger, configurable isolation.

It would also make future divestiture and dedicated-instance migration unnecessarily difficult.

---

# 95. Rejected alternative — One iDempiere installation per legal entity universally

**Rejected as universal policy.**

It provides excellent isolation but imposes needless operational duplication for every small tenant.

Baobab instead uses `IsolationProfile`.

Dedicated instances remain available when justified.

---

# 96. Rejected alternative — Make AD_Client_ID the canonical Baobab tenant identifier

**Rejected.**

It would couple canonical identity to one ERP implementation and make instance migration, ERP replacement and multi-engine mapping structurally difficult.

---

# 97. Rejected alternative — Make Legal Entity equal AD_Org

**Rejected as a universal mapping.**

It may occasionally be appropriate.

It cannot define the general architecture because an iDempiere Organization exists below its Client isolation boundary.

---

# 98. Rejected alternative — Share the ERP database with Medusa or Payload

**Rejected.**

It would create:

- schema coupling;
- security coupling;
- release coupling;
- failure coupling;
- upgrade coupling;
- vendor lock-in.

---

# 99. Rejected alternative — Direct database integration

**Rejected.**

No external Baobab system shall make iDempiere tables its integration contract.

---

# 100. Rejected alternative — Modify iDempiere core extensively

**Rejected.**

Baobab SHALL use configuration, OSGi plugins and upstream contributions.

This is consistent with iDempiere's own extension architecture and substantially improves upgradeability.

---

# 101. Rejected alternative — Expose native generic REST directly to digital estates

**Rejected.**

It exposes too much implementation detail and weakens the canonical Baobab contract.

The iDempiere security guidance itself recommends an API gateway for REST exposure.

---

# 102. Rejected alternative — Distributed transactions across engines

**Rejected.**

Baobab SHALL use local transactions, events, idempotency and reconciliation.

---

# 103. Rejected alternative — Duplicate accounting in Medusa

**Rejected.**

Commerce and ERP have different bounded contexts.

Medusa may expose commerce totals and payment state.

iDempiere remains the accounting authority where the ERP capability is bound.

---

# 104. Rejected alternative — One global ERP region forever

**Rejected.**

Baobab is designed for multiple markets and jurisdictions.

Deployment topology must be capable of following sovereignty, latency and regulatory needs.

---

# 105. Consequences — positive

This decision provides:

### Engine replaceability

The platform is not permanently bound to native iDempiere IDs or tables.

### Tenant portability

A tenant can move between EngineInstances.

### Regional expansion

New jurisdictions do not require redesigning canonical identity.

### Strong isolation

Isolation can graduate from shared Client boundaries to dedicated infrastructure.

### Upgradeability

Baobab plugins remain outside upstream iDempiere core.

### Event-driven interoperability

Medusa, Payload, Intelligence and future engines remain independently deployable.

### Accounting integrity

ERP accounting remains inside a specialised ERP system.

### Technology autonomy

The Go Control Plane does not need to reproduce ERP internals.

---

# 106. Consequences — costs

The design deliberately incurs:

- mapping infrastructure;
- an ERP adapter/integration layer;
- event infrastructure;
- outbox maintenance;
- reconciliation logic;
- more sophisticated observability;
- multiple identifier domains;
- explicit tenant provisioning;
- operational management of EngineInstances.

These are not accidental complexities.

They are the price of maintaining decoupling, replacement ability, regional flexibility and strong tenant isolation.

For an enterprise platform intended to span legal entities and markets, those costs are justified.

---

# 107. Non-negotiable invariants

The following SHALL be treated as architectural invariants.

```text
INV-ERP-001
Every external ERP entity is identified canonically outside iDempiere.

INV-ERP-002
No iDempiere native ID is a Baobab global identifier.

INV-ERP-003
No engine reads or writes the ERP database directly.

INV-ERP-004
Baobab Tenant is not implicitly AD_Client.

INV-ERP-005
Legal Entity is not implicitly AD_Org.

INV-ERP-006
Every ERP request executes inside resolved Baobab Context.

INV-ERP-007
Every ERP request resolves an EngineInstance before execution.

INV-ERP-008
Tenant security cannot rely solely on application-supplied IDs.

INV-ERP-009
Cross-client access is forbidden during normal operation.

INV-ERP-010
Baobab customisation does not patch upstream core without an exception ADR.

INV-ERP-011
Canonical integration uses APIs and/or events.

INV-ERP-012
Canonical events are semantic business facts, not row-change notifications.

INV-ERP-013
Event consumers are idempotent.

INV-ERP-014
Transactional state and event publication are protected through outbox/reconciliation patterns.

INV-ERP-015
Every production EngineInstance has an explicit IsolationProfile.

INV-ERP-016
Market, Legal Entity, Tenant and deployment Region remain distinct concepts.

INV-ERP-017
Currencies cross boundaries using canonical ISO currency codes.

INV-ERP-018
ERP accounting authority is not duplicated in another Baobab engine.

INV-ERP-019
Production iDempiere REST is not exposed directly to the public Internet.

INV-ERP-020
Engine upgrades cannot silently redefine Baobab contracts.
```

---

# 108. Required implementation artefacts

Acceptance of this ADR SHALL result in subordinate implementation artefacts.

## ADR-ERP-002

**ERP Tenant, Client and Organization Mapping**

Define precise mappings among:

```text
Tenant
LegalEntity
Organisation
Market
AD_Client
AD_Org
```

including Nabhold, Thamani and Zuribeans examples.

## ADR-ERP-003

**ERP EngineInstance Isolation and Regional Deployment**

Define:

```text
shared
dedicated
regional
regulated
migration
failover
```

topologies.

## ADR-ERP-004

**Baobab iDempiere Extension Architecture**

Define the OSGi bundle/package structure and prohibitions on core modification.

## ADR-ERP-005

**ERP Integration API**

Define inbound command and query contracts.

## ADR-ERP-006

**ERP Canonical Event Architecture**

Define event catalogue, schemas, outbox, retry, ordering and idempotency.

## ADR-ERP-007

**ERP Canonical Entity Mapping**

Define mappings for:

```text
Product
BusinessPartner
Supplier
Customer
Warehouse
Order
Invoice
Payment
Currency
Tax
Account
```

## ADR-ERP-008

**ERP Financial and Currency Architecture**

Define:

```text
functional currency
transaction currency
accounting currency
reporting currency
conversion rate authority
accounting date
```

## ADR-ERP-009

**ERP Market Localisation Architecture**

Define country plugins, taxation, statutory reporting and localisation governance.

## ADR-ERP-010

**ERP Security Architecture**

Define identities, roles, credentials, network boundary and administrative access.

## ADR-ERP-011

**ERP Observability and Audit**

Define logs, metrics, traces, audit, SLOs and alerting.

## ADR-ERP-012

**ERP Business Continuity**

Define RPO/RTO, PITR, backups, restore, DR and regional failover.

## ADR-ERP-013

**ERP Release and Upgrade Architecture**

Define upstream LTS policy, plugin compatibility, migrations and rollback.

---

# 109. Acceptance criteria

ADR-ERP-001 SHALL be considered implemented only when all of the following are demonstrably true:

- [ ] `nabhold/baobab-erp` builds an iDempiere 13-based runtime reproducibly.
- [ ] No Baobab-specific requirement depends on permanent modification of upstream core.
- [ ] PostgreSQL is private to the ERP Engine.
- [ ] Engine registration exists in the Control Plane.
- [ ] At least one EngineInstance can be registered.
- [ ] An IsolationProfile can govern that EngineInstance.
- [ ] A canonical tenant/legal entity can be mapped to an iDempiere Client without sharing canonical/native IDs.
- [ ] Canonical mappings are held outside iDempiere as defined by the Control Plane contract.
- [ ] Context resolution occurs before ERP routing.
- [ ] Cross-tenant isolation tests pass.
- [ ] A canonical ERP command can be executed without exposing native table CRUD as the external contract.
- [ ] At least one ERP business event is emitted through the canonical event envelope.
- [ ] The event path is retryable and idempotent.
- [ ] Correlation IDs survive an end-to-end request/event round trip.
- [ ] Medusa can interact with ERP only through approved APIs/events.
- [ ] Payload remains independent of the ERP database.
- [ ] Native iDempiere REST is not directly Internet exposed.
- [ ] Container and dependency scans pass required organisational gates.
- [ ] Contract compatibility tests run in CI.
- [ ] Backup restoration is tested.
- [ ] ERP LTS upgrade procedure is documented.
- [ ] Architecture documentation clearly distinguishes Tenant, Client, Organization, LegalEntity, Market and EngineInstance.

---

# 110. Final architectural statement

The Baobab ERP Engine SHALL therefore be understood as:

> **An independently deployable, strongly isolated, region-capable and event-driven ERP capability powered by iDempiere, governed by Baobab canonical identity and Control Plane context, integrated exclusively through explicit contracts, and free to retain its native ERP data model without imposing that model upon the wider platform.**

Its governing relationship is:

```text
              BAOBAB CANONICAL MODEL
                        │
                        │ identity / mappings
                        ▼
                BAOBAB CONTROL PLANE
                        │
                        │ Context
                        │ CapabilityBinding
                        │ IsolationProfile
                        ▼
                    ERP ENGINE
                    iDempiere
                        │
       ┌────────────────┼────────────────┐
       │                │                │
       ▼                ▼                ▼
    Client A          Client B       Dedicated/
    Tenant A          Tenant B       Regional Instance
       │                │
       ▼                ▼
 Organizations      Organizations
       │                │
       └────────────────┘
                ERP domain model
                        │
                        ▼
                Transactional Outbox
                        │
                        ▼
                 Canonical Events
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Medusa         Payload     Intelligence/
                                     Analytics
```

The central principle is deliberately stronger than “use iDempiere for ERP”:

> **iDempiere is authoritative inside the ERP bounded context; Baobab remains authoritative over platform identity, context, topology, isolation and interoperability.**

That distinction is what allows Nabhold, Thamani, Zuribeans and future independent organisations to operate across different markets, currencies, jurisdictions and deployment regions without turning one ERP installation—or one vendor's data model—into the architecture of the entire Baobab Platform.