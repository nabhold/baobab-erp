# ADR-ERP-007 — ERP Canonical Entity and External Reference Mapping Architecture

**Status:** Accepted  
**Decision class:** ERP / Identity / Canonical Mapping / Master Data / Integration  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`, `nabhold/baobab-trade`, future Baobab engines  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-006  
**Date:** 2026-09-02

---

# 1. Decision

Baobab SHALL maintain a canonical identity layer independent of iDempiere, MedusaJS, Payload CMS and every other engine.

Every business object that requires identity across engine boundaries SHALL be represented by a stable:

```text
CanonicalEntity
```

identified by a Baobab canonical UUID.

Engine-specific representations SHALL be associated with that canonical identity using:

```text
ExternalReference
Mapping
MappingScope
```

The relationship is:

```text
                 CanonicalEntity
                        │
              canonical UUID
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
       Mapping       Mapping       Mapping
          │             │             │
          ▼             ▼             ▼
      iDempiere       Medusa       Payload
          │             │             │
      native ID      native ID     native ID
```

No engine-native identifier SHALL become Baobab's universal business identity.

---

# 2. Governing principle

The fundamental identity rule is:

> **Business identity belongs to Baobab; engine identifiers identify representations of that business identity inside particular engine instances.**

Therefore:

```text
Canonical Product UUID
```

is not:

```text
M_Product_ID
```

and is not:

```text
Medusa product_id
```

even when all three currently refer to the same business concept.

---

# 3. Why this is necessary

Baobab is intentionally:

```text
polyrepo
polyglot
multi-engine
multi-tenant
multi-market
multi-region
replaceable
```

A product may simultaneously exist as:

```text
Canonical Product
       │
       ├── Medusa Product
       ├── iDempiere M_Product
       ├── Payload content representation
       ├── search document
       └── Intelligence feature/entity
```

None of those representations can safely become universal identity authority.

---

# 4. Canonical identity survives engines

The following SHALL NOT change canonical identity:

```text
iDempiere upgrade
Medusa upgrade
database migration
EngineInstance relocation
regional migration
tenant promotion to dedicated infrastructure
ERP replacement
commerce-engine replacement
record renumbering
native database restoration
```

Infrastructure and implementation may change.

Business identity remains.

---

# 5. CanonicalEntity

`CanonicalEntity` represents the platform-level identity of a meaningful entity requiring cross-context reference.

Conceptually:

```text
CanonicalEntity

id
entity_type
status
created_at
retired_at
metadata
```

The physical model remains governed by the Control Plane implementation contract.

---

# 6. CanonicalEntity is not a universal business database

The Control Plane SHALL NOT become the authoritative store for every attribute of every canonical entity.

For example:

```text
CanonicalEntity(Product)
```

does not imply the Control Plane owns:

```text
inventory quantity
product price
accounting cost
marketing description
commerce options
```

Canonical identity and domain state are different concerns.

---

# 7. Identity versus authority

Baobab SHALL distinguish:

```text
IDENTITY AUTHORITY
```

from:

```text
DOMAIN STATE AUTHORITY
```

Example:

```text
Canonical Product ID
        │
        └── Baobab canonical identity

Medusa
        │
        └── commerce representation

iDempiere
        │
        └── ERP/accounting representation

Payload
        │
        └── editorial representation
```

---

# 8. Canonical entity types

Initial canonical entity types SHOULD include where cross-engine identity is required:

```text
Party
Product
PurchaseOrder
SalesOrder
SupplierInvoice
CustomerInvoice
Payment
GoodsReceipt
Shipment
Warehouse
Location
AccountReference
```

Additional entity types SHALL be introduced only when canonical identity provides real cross-boundary value.

---

# 9. Do not canonicalise everything

An iDempiere record does not automatically require a `CanonicalEntity`.

Examples that may remain ERP-native:

```text
internal posting records
temporary process instances
workflow state
Application Dictionary configuration
technical accounting rows
internal cost detail records
```

Canonical identity exists for interoperability, not because a table exists.

---

# 10. ExternalReference

`ExternalReference` identifies an engine-specific representation.

Conceptually:

```text
ExternalReference

id
engine_id
engine_instance_id
namespace
external_entity_type
external_identifier
status
created_at
retired_at
```

Example:

```text
engine_instance:
    ERP-AF-SOUTH-01

namespace:
    idempiere

external_entity_type:
    C_BPartner

external_identifier:
    1000421
```

---

# 11. EngineInstance scope is mandatory

Native identifiers SHALL be interpreted within their EngineInstance.

This is invalid as a globally unique identity:

```text
C_BPartner_ID = 1000421
```

because another iDempiere database may contain:

```text
C_BPartner_ID = 1000421
```

for an unrelated entity.

Therefore uniqueness SHALL conceptually include:

```text
EngineInstance
+
namespace
+
external_entity_type
+
external_identifier
```

---

# 12. ExternalReference identity

An `ExternalReference` represents:

> This specific representation in this specific external system context.

It SHALL NOT mean:

> This is the canonical business entity itself.

---

# 13. Mapping

`Mapping` associates:

```text
CanonicalEntity
```

with:

```text
ExternalReference
```

under an explicit scope and effective period.

Conceptually:

```text
Mapping

id
canonical_entity_id
external_reference_id
mapping_scope_id
status
valid_from
valid_to
provenance
confidence
created_by
approved_by
created_at
```

---

# 14. Mapping is first-class

Mappings SHALL NOT be treated as incidental integration metadata.

They are critical platform infrastructure because they enable:

```text
routing
integration
migration
reconciliation
event attribution
audit
engine replacement
regional expansion
```

---

# 15. MappingScope

A Mapping SHALL explicitly identify where its equivalence applies.

Possible dimensions include:

```text
tenant
legal_entity
market
digital_estate
engine
engine_instance
capability
```

A mapping SHALL never silently imply global equivalence when it is actually contextual.

---

# 16. Most-specific valid mapping

Where multiple mappings exist, resolution SHALL select the most specific valid mapping permitted by the requested Context.

Resolution SHALL NOT arbitrarily choose the first database row.

---

# 17. Ambiguity

If multiple equally authoritative mappings are valid for a single-valued resolution:

```text
MAPPING_AMBIGUOUS
```

SHALL result.

The resolver SHALL fail closed.

---

# 18. Missing mapping

If no authoritative mapping exists:

```text
MAPPING_NOT_FOUND
```

SHALL result.

The resolver SHALL NOT guess from:

```text
names
email addresses
SKU similarity
document numbers
record proximity
```

during ordinary runtime processing.

---

# 19. Mapping authority

The Baobab Control Plane SHALL own authoritative mappings.

Therefore:

```text
baobab-cp
     │
     └── Mapping authority
```

while:

```text
baobab-erp
baobab-trade
Payload
```

may consume/cache those mappings.

---

# 20. Local mapping caches

Engines MAY maintain local mapping projections or caches for:

```text
performance
resilience
transaction processing
```

Such caches SHALL be:

```text
derived
bounded
rebuildable
invalidatable
non-authoritative
```

---

# 21. Mapping cache failure

Loss of an ERP mapping cache SHALL not destroy canonical identity.

The cache SHALL be reconstructable from authoritative Control Plane state.

---

# 22. Mapping lifecycle

Mappings SHALL support at least:

```text
pending
active
superseded
suspended
retired
invalid
```

---

# 23. Pending

`pending` means:

> A candidate mapping exists but is not yet authoritative.

It SHALL not normally be used for production transaction routing.

---

# 24. Active

`active` means:

> The mapping is currently authoritative within its scope and effective period.

---

# 25. Superseded

`superseded` means:

> Another mapping has replaced this mapping for future resolution.

Historical references remain valid.

---

# 26. Suspended

`suspended` means:

> Resolution is temporarily prohibited.

The record remains for audit/history.

---

# 27. Retired

`retired` means:

> The representation is no longer active for new processing.

Historical events and transactions may still reference it.

---

# 28. Invalid

`invalid` means:

> The mapping was determined to be erroneous and SHALL NOT be used.

Its existence remains auditable.

---

# 29. Temporal mapping

Mappings SHALL be temporal.

At minimum:

```text
valid_from
valid_to
```

SHALL define the effective interval.

---

# 30. Historical resolution

The resolver SHALL eventually support:

```text
resolve canonical entity
as of timestamp T
```

for audit, reconciliation and historical event interpretation.

---

# 31. Temporal uniqueness

Where the mapping relationship is single-valued, overlapping authoritative mapping intervals SHALL be prohibited.

PostgreSQL temporal exclusion constraints defined in the Control Plane physical model SHALL enforce this where applicable.

---

# 32. Mapping history is immutable in spirit

A migration SHALL normally:

```text
close old mapping
create new mapping
```

rather than overwrite history.

---

# 33. Provenance

Every authoritative mapping SHALL record provenance.

Recommended values include:

```text
provisioned
migrated
imported
manually-approved
reconciled
system-generated
```

---

# 34. Provenance metadata

Where appropriate, record:

```text
source
created_by
approved_by
reason
migration_id
reconciliation_id
```

---

# 35. Confidence

Mappings discovered through legacy reconciliation MAY carry confidence.

Example:

```text
candidate
probable
verified
authoritative
rejected
```

Only an approved authoritative state SHALL participate in normal transaction routing.

---

# 36. Fuzzy matching

Fuzzy matching MAY assist reconciliation.

It SHALL NOT silently establish canonical identity.

Example:

```text
"Acme Coffee Ltd"
```

matching:

```text
"ACME COFFEE LIMITED"
```

may produce:

```text
candidate mapping
```

not:

```text
automatic authoritative mapping
```

---

# 37. Natural keys

Natural keys MAY assist matching.

Examples:

```text
company registration number
tax identifier
GTIN
SKU
supplier reference
invoice number
```

But natural keys SHALL not universally replace canonical identity.

---

# 38. Why natural keys are insufficient

Natural keys can:

```text
change
be reused
be scoped to tenant
contain errors
differ by market
differ between systems
```

Canonical UUIDs provide stable technical identity independent of those changes.

---

# 39. Human-readable codes

Canonical entities MAY have human-readable codes.

Example:

```text
PROD-COFFEE-ARABICA-001
```

These are secondary identifiers.

The canonical UUID remains authoritative.

---

# 40. Party mapping

Canonical:

```text
Party
```

may map to:

```text
iDempiere:
    C_BPartner

Medusa:
    Customer
    Company
    Supplier representation where applicable

other systems:
    CRM Account
```

The exact representations depend on domain ownership.

---

# 41. Party is broader than Business Partner

The canonical `Party` abstraction MAY represent:

```text
person
organisation
legal entity
supplier
customer
partner
```

according to the canonical model.

`C_BPartner` is the ERP representation needed for iDempiere business operations.

They SHALL not be declared universally identical.

---

# 42. Party role

Supplier/customer/etc. roles SHALL not necessarily create different canonical Party identities.

One organisation can simultaneously be:

```text
supplier
customer
logistics partner
```

unless business requirements establish genuinely distinct identities.

---

# 43. ERP Business Partner creation

When ERP requires a `C_BPartner` representation for an existing canonical Party:

```text
Canonical Party
       │
       ▼
resolve Mapping
       │
   ┌───┴────┐
 exists    absent
   │         │
   ▼         ▼
 use      authorised provisioning
             │
             ▼
        C_BPartner
             │
             ▼
       ExternalReference
             │
             ▼
          Mapping
```

---

# 44. Mapping creation is not opportunistic

Ordinary application code SHALL NOT quietly create canonical mappings whenever lookup fails.

Mapping creation SHALL occur through explicitly authorised provisioning/synchronisation workflows.

---

# 45. Duplicate Party protection

Before creating an ERP Business Partner representation, the provisioning workflow SHOULD evaluate:

```text
existing mapping
authoritative identifiers
tenant scope
legal registration/tax reference where available
approved matching rules
```

to reduce duplicates.

---

# 46. Duplicate detection does not equal automatic merge

Potential duplicates SHALL become reconciliation candidates.

Automatic merging of financial counterparties is dangerous and SHALL require explicit rules/approval.

---

# 47. Product mapping

Canonical:

```text
Product
```

may map to:

```text
Medusa Product
iDempiere M_Product
Payload product-content representation
search index document
```

---

# 48. Product authority is contextual

Medusa may own:

```text
commerce presentation
variants
sales-channel configuration
commerce pricing behaviour
```

while ERP may own:

```text
accounting category
costing
inventory valuation
procurement representation
```

Canonical identity does not make the Control Plane owner of all Product attributes.

---

# 49. Product representation

Example:

```text
Canonical Product UUID
        │
        ├── Medusa
        │     product_id = prod_...
        │
        └── iDempiere
              M_Product_ID = 100134
```

Neither native ID is exported as universal identity.

---

# 50. SKU

SKU MAY be shared operationally across systems.

It SHALL NOT be assumed globally unique unless its scope is explicitly defined.

Conceptually:

```text
SKU uniqueness:
Tenant?
LegalEntity?
Brand?
Market?
Catalog?
```

must be known.

---

# 51. Product migration

If an ERP tenant migrates from:

```text
ERP-AF-SOUTH-01
```

to:

```text
ERP-THAMANI-01
```

the canonical Product UUID remains unchanged.

Mappings change:

```text
old:
Product UUID
    → ERP-AF-SOUTH-01 / M_Product 100134

new:
Product UUID
    → ERP-THAMANI-01 / M_Product 100021
```

---

# 52. Purchase order mapping

Canonical:

```text
PurchaseOrder
```

may map to:

```text
iDempiere C_Order
```

when iDempiere owns the ERP procurement representation.

Other systems MAY maintain their own representations.

---

# 53. Document number is not canonical identity

An ERP document number such as:

```text
PO-2026-00417
```

SHALL not be used as the canonical UUID.

Document numbers may be:

```text
tenant-scoped
sequence-scoped
legal-entity-scoped
reconfigured
duplicated across EngineInstances
```

---

# 54. Supplier invoice mapping

Canonical:

```text
SupplierInvoice
```

maps to:

```text
iDempiere C_Invoice
```

within the applicable ERP representation.

External supplier invoice numbers SHALL remain business attributes.

---

# 55. Invoice-number uniqueness

Supplier invoice numbers may only be meaningful with additional scope such as:

```text
supplier
legal entity
document type
jurisdiction
```

Therefore invoice number alone SHALL never be assumed to be a globally unique canonical identity.

---

# 56. Customer invoice mapping

Where ERP creates the authoritative financial invoice from a Trade transaction:

```text
Trade Order
      │
      ▼
ERP Customer Invoice
```

these are different canonical entity types.

They SHALL be related, not assigned the same canonical UUID.

---

# 57. Related does not mean identical

Example:

```text
SalesOrder UUID A
      │
      └── results in
              │
              ▼
CustomerInvoice UUID B
```

A mapping relates representations of the same entity.

A business relationship relates distinct entities.

The two SHALL not be confused.

---

# 58. Mapping versus relationship

This distinction is fundamental.

```text
MAPPING

Canonical Product
      ↕
M_Product
```

means:

> two representations of the same entity.

```text
RELATIONSHIP

PurchaseOrder
      │
      ▼
SupplierInvoice
```

means:

> two different entities with a business relationship.

---

# 59. Payment mapping

Canonical:

```text
Payment
```

may map to:

```text
iDempiere C_Payment
```

and possibly external payment-provider transactions.

However:

```text
ERP Payment
```

and:

```text
Payment Provider Transaction
```

are not automatically the same canonical entity.

The domain model SHALL decide whether they are:

```text
representations
```

or:

```text
related entities
```

---

# 60. Payment-provider identity

A gateway transaction ID SHALL normally be an ExternalReference or related transaction identifier.

It SHALL not become Baobab's universal Payment ID.

---

# 61. Goods receipt

Canonical:

```text
GoodsReceipt
```

may map to:

```text
iDempiere M_InOut
```

for the receiving transaction.

Supplier delivery-note number remains an attribute/external reference, not canonical identity.

---

# 62. Shipment

A customer shipment and supplier goods receipt SHALL remain semantically distinct even if iDempiere uses related native structures.

Canonicalisation SHALL preserve business meaning rather than blindly mirror table reuse.

---

# 63. Warehouse mapping

Canonical:

```text
Warehouse
```

may map to:

```text
iDempiere M_Warehouse
```

when the warehouse requires cross-engine identity.

---

# 64. Warehouse is not Organization

A Warehouse SHALL not be mapped to `AD_Org` merely because both participate in operational context.

These are different concepts.

---

# 65. Location mapping

Baobab SHALL distinguish where necessary:

```text
physical location
postal address
warehouse
business organisation
market
legal entity
```

iDempiere representations SHALL be mapped according to actual semantics.

---

# 66. Account references

Canonical financial account references MAY be introduced where another Baobab domain genuinely needs stable cross-engine reference to an ERP account.

However the entire chart of accounts SHALL not automatically become a platform-wide canonical entity set.

---

# 67. Accounting remains ERP-owned

General ledger account structure remains principally an ERP concern.

Canonical account identity SHALL be introduced only for explicit integration/reporting requirements.

---

# 68. Many representations

A single CanonicalEntity MAY have multiple ExternalReferences.

Example:

```text
Canonical Product P1
      │
      ├── Medusa ZA product
      ├── Medusa UG product
      ├── iDempiere South instance
      └── iDempiere East instance
```

provided scopes distinguish their applicability.

---

# 69. One external representation

An authoritative ExternalReference SHOULD normally map to at most one CanonicalEntity for a given effective scope.

Otherwise one native record would represent two canonical identities.

That is normally invalid.

---

# 70. Mapping cardinality

Conceptually:

```text
CanonicalEntity
    1
    │
    │
    N
Mapping
    N
    │
    │
    1
ExternalReference
```

over lifecycle and scopes.

Constraints SHALL prevent contradictory active mappings.

---

# 71. One-to-many does not imply simultaneous equivalence

Multiple mappings may arise from:

```text
different EngineInstances
different markets
historical migrations
different capabilities
```

Their scopes and effective intervals determine which applies.

---

# 72. Split representation

Sometimes one canonical entity may legitimately require multiple native records in one engine.

This SHALL be treated as an explicit modelling exception.

Example possibilities:

```text
market-specific representation
legal-entity-specific representation
accounting-specific representation
```

The MappingScope SHALL explain why.

---

# 73. Merge

When two native records are determined to represent one canonical entity:

```text
Native A ─┐
          ├── CanonicalEntity X
Native B ─┘
```

the platform MAY preserve both ExternalReferences while identifying one as active/preferred and the other as retired/merged.

Historical references SHALL remain resolvable.

---

# 74. Canonical merge

If two CanonicalEntities are discovered to represent the same real entity, a controlled canonical merge workflow SHALL be required.

It SHALL NOT simply delete one UUID.

---

# 75. Canonical merge requirements

The merge SHALL preserve:

```text
surviving canonical ID
retired canonical ID
redirect/alias relationship
all ExternalReferences
audit trail
reason
approver
effective time
```

---

# 76. Historical IDs

Historical canonical IDs SHALL remain resolvable after merge.

Consumers processing archived events SHALL not encounter dangling identity.

---

# 77. Split

A previously single canonical entity MAY occasionally require splitting.

This is materially more complex than merge.

It SHALL require explicit governance because historical mappings may no longer be unambiguous.

---

# 78. Legal entity restructuring

A merger, acquisition, divestiture or incorporation SHALL NOT be represented by casually changing mappings.

Canonical legal/business identity changes SHALL follow explicit organisational lifecycle rules.

---

# 79. Engine migration

When an entity representation moves between EngineInstances:

```text
CanonicalEntity remains stable
```

while:

```text
ExternalReference changes
Mapping changes
```

This is a central reason for canonical identity.

---

# 80. Migration sequence

Recommended:

```text
existing canonical entity
       │
       ▼
existing source Mapping
       │
       ▼
create target native representation
       │
       ▼
create target ExternalReference
       │
       ▼
create pending target Mapping
       │
       ▼
reconcile source/target
       │
       ▼
activate target Mapping
       │
       ▼
close source Mapping
```

---

# 81. No identity recreation during migration

Migration SHALL NOT create a new canonical UUID merely because a new native record was created.

---

# 82. Source mapping retention

Old mappings SHALL remain historically queryable after migration.

---

# 83. Capability binding versus entity mapping

These solve different problems.

```text
CapabilityBinding
```

answers:

> Which EngineInstance handles this capability for this Context?

```text
Mapping
```

answers:

> Which native representation corresponds to this CanonicalEntity there?

---

# 84. Resolver order

Correct:

```text
Context
   │
   ▼
CapabilityBinding
   │
   ▼
EngineInstance
   │
   ▼
Mapping
   │
   ▼
ExternalReference
```

Not:

```text
Canonical entity
   │
   ▼
find arbitrary native record anywhere
```

---

# 85. Resolver API

The Control Plane SHOULD expose resolution operations conceptually equivalent to:

```text
resolveCanonicalToExternal()

resolveExternalToCanonical()
```

under explicit Context and scope.

---

# 86. Canonical-to-external request

Conceptually:

```json
{
  "canonical_entity_id": "<uuid>",
  "engine_instance_id": "<uuid>",
  "entity_type": "Product",
  "context": {
    "tenant_id": "<uuid>",
    "legal_entity_id": "<uuid>",
    "market_id": "<uuid>"
  },
  "effective_at": "2026-09-02T00:00:00Z"
}
```

---

# 87. Resolution response

Conceptually:

```json
{
  "canonical_entity_id": "<uuid>",
  "external_reference": {
    "engine_instance_id": "<uuid>",
    "namespace": "idempiere",
    "external_entity_type": "M_Product",
    "external_identifier": "100134"
  },
  "mapping_id": "<uuid>",
  "status": "active"
}
```

---

# 88. Reverse resolution

When ERP emits an event from a native object:

```text
M_Product_ID
```

the extension SHALL reverse-resolve:

```text
EngineInstance
+
M_Product_ID
        │
        ▼
Canonical Product
```

before emitting a canonical event.

---

# 89. Unresolved outbound event

If reverse mapping is required but absent:

```text
canonical event SHALL NOT guess
```

The event SHALL enter:

```text
reconciliation/quarantine
```

unless the contract explicitly supports an unresolved representation.

---

# 90. Mapping-before-event invariant

For canonical events whose subject requires canonical identity:

```text
authoritative Mapping
```

SHALL exist before publication.

---

# 91. Provisioning order

For a new ERP representation:

```text
canonical entity
      ↓
native record
      ↓
ExternalReference
      ↓
Mapping
      ↓
canonical event publication enabled
```

---

# 92. Race conditions

Concurrent representation creation SHALL be protected.

Two workers SHALL not independently create:

```text
two C_BPartner records
```

for the same canonical Party because they simultaneously observed a missing mapping.

---

# 93. Creation lock

Provisioning SHALL use an appropriate uniqueness/serialization mechanism.

Possible mechanisms include:

```text
Control Plane reservation
database uniqueness
idempotency key
distributed coordination
```

The exact mechanism belongs to implementation design.

---

# 94. Idempotent provisioning

Provisioning request:

```text
ensure ERP representation for Product X
```

SHOULD be idempotent.

Repeated calls return the existing authoritative representation.

---

# 95. Reconciliation

Baobab SHALL provide mapping reconciliation.

It SHALL detect:

```text
canonical entity without expected representation
native representation without canonical mapping
duplicate active mapping
mapping to missing native record
mapping to wrong tenant
mapping to wrong EngineInstance
expired mapping still used
```

---

# 96. Orphan native record

A native ERP record without canonical mapping is not necessarily erroneous.

Some records are intentionally ERP-local.

Reconciliation SHALL first determine whether that entity type requires canonical identity.

---

# 97. Orphan canonical entity

Likewise, a CanonicalEntity need not have representation in every engine.

Example:

```text
Product
```

may exist canonically and in Medusa before ERP provisioning becomes necessary.

---

# 98. Representation requirement

Whether a canonical entity requires ERP representation depends on:

```text
CapabilityBinding
business process
tenant
legal entity
market
entity lifecycle
```

not merely its existence.

---

# 99. Mapping audit

Every mapping lifecycle transition SHALL be auditable.

At minimum:

```text
who
what
when
previous state
new state
reason
source
correlation
```

---

# 100. Canonical mapping events

The Control Plane SHOULD emit events such as:

```text
mapping.created.v1
mapping.activated.v1
mapping.superseded.v1
mapping.suspended.v1
mapping.retired.v1
mapping.invalidated.v1
```

These are Control Plane events, not ERP domain events.

---

# 101. Cache invalidation

ERP MAY consume mapping lifecycle events to invalidate local mapping caches.

---

# 102. Security

Mapping resolution is security-sensitive.

An incorrect mapping can cause:

```text
cross-tenant access
financial misposting
data leakage
wrong legal entity attribution
wrong market processing
```

Therefore Mapping is part of the security boundary.

---

# 103. Caller cannot submit mapping override

Ordinary consumers SHALL NOT provide:

```text
mapping_id
M_Product_ID
C_BPartner_ID
C_Invoice_ID
```

to override server-side resolution.

---

# 104. Administrative override

Exceptional mapping override SHALL require:

```text
privileged role
reason
audit
approval where required
```

and SHALL not be available through ordinary business APIs.

---

# 105. Tenant verification

Every ERP ExternalReference resolution SHALL verify consistency with the resolved native `AD_Client`.

A Product mapping resolving into another tenant's Client SHALL fail.

---

# 106. Organization verification

Where MappingScope requires organisation-specific representation, native `AD_Org` compatibility SHALL also be validated.

---

# 107. EngineInstance verification

A mapping for:

```text
ERP-AF-SOUTH-01
```

SHALL not be used against:

```text
ERP-AF-EAST-01
```

even if the numeric native identifier happens to exist there.

---

# 108. Mapping errors

Stable errors SHALL include:

```text
MAPPING_NOT_FOUND
MAPPING_AMBIGUOUS
MAPPING_EXPIRED
MAPPING_SUSPENDED
MAPPING_INVALID
MAPPING_SCOPE_MISMATCH
MAPPING_ENGINE_INSTANCE_MISMATCH
MAPPING_TENANT_MISMATCH
MAPPING_ENTITY_TYPE_MISMATCH
```

---

# 109. Error translation

ERP API errors MAY prefix these according to the ERP API taxonomy:

```text
ERP_MAPPING_NOT_FOUND
ERP_MAPPING_AMBIGUOUS
```

while preserving common canonical error semantics.

---

# 110. Cross-engine references

An ERP event SHALL refer to canonical Trade entities where necessary.

Example:

```json
{
  "source_order_id": "<canonical-sales-order-uuid>"
}
```

not:

```json
{
  "medusa_order_id": "order_01..."
}
```

unless the native reference is explicitly diagnostic metadata.

---

# 111. Medusa does not map directly to iDempiere

Avoid:

```text
Medusa Product ID
       │
       ▼
iDempiere M_Product_ID
```

as the authoritative relationship.

Preferred:

```text
Medusa Product
       │
       ▼
Canonical Product
       │
       ▼
iDempiere M_Product
```

---

# 112. Why hub mapping wins

With direct pairwise mappings, N engines produce approximately:

```text
N × (N - 1)
```

possible directional integration relationships.

Canonical hub identity reduces conceptual mapping to:

```text
each representation
       ↕
canonical identity
```

This becomes increasingly valuable as Baobab adds engines.

---

# 113. Payload relationship

Payload may maintain editorial representation of a Product.

Its document ID remains a Payload ExternalReference.

It SHALL not become the canonical Product ID.

---

# 114. Intelligence Engine

The Intelligence Engine SHOULD consume canonical entity identifiers.

Model features, embeddings and analytical records MAY maintain their own references.

They SHALL map to canonical identity rather than becoming authoritative identity.

---

# 115. Search indexes

Search index document IDs MAY use canonical UUIDs where appropriate.

However a search index remains a projection.

Loss/rebuild of the index SHALL not alter canonical identity.

---

# 116. Analytics

Analytical warehouses SHOULD preserve canonical IDs alongside source provenance.

This permits cross-engine joins without treating source database IDs as universal keys.

---

# 117. Data lineage

Mappings SHALL permit lineage such as:

```text
Canonical Product
      │
      ├── source representation: Medusa
      ├── ERP representation: iDempiere
      └── analytical representation: warehouse
```

without confusing ownership.

---

# 118. Import/export scenarios

External supplier/customer identifiers MAY be represented as ExternalReferences when durable interoperability requires them.

Examples:

```text
supplier product code
customs system identifier
external logistics reference
marketplace listing ID
```

They SHALL be explicitly namespaced.

---

# 119. Namespace

External references SHALL have a namespace identifying the external identity domain.

Examples:

```text
idempiere
medusa
payload
supplier:<supplier-id>
customs:<jurisdiction>
marketplace:<provider>
```

Namespace conventions SHALL be governed centrally.

---

# 120. External identifier opacity

Baobab SHALL treat external identifiers as opaque strings unless a specific adapter understands their syntax.

The Control Plane SHALL not infer semantics merely because an identifier looks numeric.

---

# 121. Case sensitivity

Identifier normalization SHALL be namespace-specific.

The platform SHALL not globally lowercase or uppercase every external identifier.

Some external identity domains may be case-sensitive.

---

# 122. Leading zeros

External identifiers SHALL normally be stored as strings.

This preserves values such as:

```text
00012345
```

that would be damaged by numeric coercion.

---

# 123. Identifier length

Canonical contracts SHALL define reasonable maximum external identifier lengths to protect storage and APIs.

They SHALL remain sufficiently flexible for external systems.

---

# 124. No secrets in ExternalReference

ExternalReference SHALL contain identity, not authentication material.

Do not store:

```text
API key
password
token
secret
```

as an external identifier.

---

# 125. Soft deletion

Canonical mappings and references involved in financial history SHALL normally be retired rather than physically deleted.

---

# 126. GDPR/POPIA-style erasure considerations

Identity metadata SHALL minimise personal data.

Where privacy law requires erasure or anonymisation of attributes, canonical technical identity MAY need to remain for financial/audit integrity where lawful retention applies.

Privacy implementation SHALL be governed separately.

---

# 127. Data residency

Canonical mappings SHOULD contain minimal data required for identity resolution.

This reduces cross-region exposure.

Sensitive domain attributes remain with the authoritative engine.

---

# 128. Regional mapping

The same CanonicalEntity MAY have different native representations in different regional EngineInstances.

Example:

```text
Canonical Product P

├── ERP-AF-SOUTH-01
│      M_Product 1001
│
└── ERP-AF-EAST-01
       M_Product 2407
```

MappingScope and CapabilityBinding determine which applies.

---

# 129. Market-specific representation

A market-specific representation MAY be appropriate where:

```text
regulation
local catalog
local accounting
local taxation
local unit conventions
```

require distinct native records.

This SHALL be explicit rather than inferred from geography.

---

# 130. Canonical identity across markets

Different market representations do not automatically imply different canonical Products.

The decision depends on whether they represent the same underlying business entity/product concept.

---

# 131. Product variants

Canonical modelling SHALL explicitly determine whether:

```text
Product
Variant
SKU
```

are separate canonical entity types.

This ADR does not force Medusa's exact product/variant ontology onto Baobab.

---

# 132. ERP product structure

Likewise, iDempiere's `M_Product` representation SHALL not dictate Baobab's entire canonical product ontology.

The Anti-Corruption Layer translates between them.

---

# 133. Event mapping resolution

Before ERP publishes:

```text
erp.supplier-invoice.posted.v1
```

it SHALL resolve:

```text
C_Invoice
     ↓
Canonical SupplierInvoice

C_BPartner
     ↓
Canonical Party

M_Product
     ↓
Canonical Product
```

for fields required by the canonical contract.

---

# 134. Partial mapping

If optional event data lacks mapping, the event contract MAY omit that optional reference.

Required subject identity SHALL never be guessed.

---

# 135. Mapping dependency

An event processor MAY enter:

```text
waiting_for_mapping
```

when a required mapping is expected to become available shortly.

This SHALL be observable and bounded.

---

# 136. Mapping reconciliation priority

Financially material unresolved mappings SHALL have higher operational priority than low-risk content mappings.

---

# 137. Mapping service availability

Because mapping resolution participates in transaction processing, ERP MAY use validated bounded local caches.

The architecture SHALL avoid requiring a remote Control Plane round trip for every line of every financial document.

---

# 138. Cache key

Mapping caches SHALL include sufficient scope.

Conceptually:

```text
canonical_entity_id
engine_instance_id
mapping_scope
effective_time/current-generation
```

A cache keyed only by canonical UUID may return the wrong regional/native representation.

---

# 139. Cache invalidation

Mappings SHALL be invalidated upon:

```text
supersession
suspension
retirement
isolation change
EngineInstance migration
```

where relevant.

---

# 140. Security-sensitive invalidation

Security-sensitive invalidation SHALL take precedence over cache availability.

A suspended mapping SHALL not remain usable merely because a stale cache exists.

---

# 141. Bulk resolution

The Control Plane SHOULD support efficient bulk mapping resolution.

Example:

```text
resolve 100 product canonical IDs
for ERP-AF-SOUTH-01
```

rather than requiring 100 sequential network calls.

---

# 142. Batch semantics

Bulk resolution SHALL return per-entity resolution status.

One missing mapping SHALL not make ambiguity invisible.

---

# 143. Mapping API authorization

Only authorised engines/services SHALL query mappings.

Mapping information can reveal platform topology and external identifiers.

---

# 144. Least disclosure

Consumers SHALL receive only the mappings they require.

A Digital Estate does not need a dump of all ERP native identifiers.

---

# 145. Mapping export

Administrative export of mapping data SHALL be controlled and audited.

---

# 146. Disaster recovery

Control Plane backups SHALL include canonical identity, ExternalReference and Mapping history.

Loss of this data could make independently healthy engines unable to correlate business state.

---

# 147. Mapping DR priority

Canonical identity/mapping data SHALL be treated as critical platform metadata.

Recovery requirements SHALL reflect that.

---

# 148. Restore validation

A Control Plane restore SHALL verify:

```text
canonical entity counts
external-reference integrity
mapping temporal constraints
active mapping uniqueness
EngineInstance references
```

before returning to authoritative service.

---

# 149. ERP restore

If ERP is restored to an earlier point in time, mappings SHALL be reconciled against the restored native state before normal event publication resumes.

---

# 150. Mapping drift

Baobab SHALL detect drift such as:

```text
Mapping points to deleted native record

Mapping says active
but native record belongs another Client

native representation changed identity unexpectedly
```

---

# 151. Mapping health

Control Plane SHOULD expose mapping health/status sufficient for operations.

Example:

```text
healthy
unresolved
ambiguous
stale
broken
reconciling
```

This operational status SHALL not necessarily replace lifecycle status.

---

# 152. Metrics

Recommended metrics:

```text
mapping_resolution_total
mapping_resolution_failure_total
mapping_not_found_total
mapping_ambiguous_total
mapping_scope_mismatch_total
mapping_cache_hit_total
mapping_cache_miss_total
mapping_reconciliation_backlog
mapping_drift_detected_total
```

---

# 153. Metric cardinality

Canonical entity IDs SHALL not be metric labels.

Detailed IDs belong in controlled logs/traces.

---

# 154. Audit query

Baobab SHALL eventually be able to answer:

> Which iDempiere record represented canonical supplier X for Thamani in the Uganda market at time T?

and:

> Which canonical entity did `C_BPartner_ID=10042` in `ERP-AF-SOUTH-01` represent on 1 June 2026?

These are first-class mapping requirements.

---

# 155. Ownership query

Baobab SHALL also be able to answer:

> Which engine owns the authoritative state for this attribute or operation?

Canonical identity alone SHALL not be mistaken for domain authority.

---

# 156. Rejected alternative — use iDempiere IDs globally

**Rejected.**

They are engine-instance-specific implementation identifiers.

---

# 157. Rejected alternative — use Medusa IDs globally

**Rejected.**

Commerce implementation identity cannot govern ERP, CMS and future engines.

---

# 158. Rejected alternative — direct Medusa-to-iDempiere mapping only

**Rejected.**

It creates pairwise coupling and does not scale to additional engines.

---

# 159. Rejected alternative — use SKU as canonical Product identity

**Rejected as universal rule.**

SKU scope and lifecycle are business-specific.

---

# 160. Rejected alternative — use email as canonical Party identity

**Rejected.**

Email is mutable, potentially shared, personal and unsuitable as universal identity.

---

# 161. Rejected alternative — use document number as canonical document identity

**Rejected.**

Document sequences are scoped and configurable.

---

# 162. Rejected alternative — create mapping automatically whenever lookup fails

**Rejected.**

It creates silent identity corruption.

---

# 163. Rejected alternative — delete old mappings after migration

**Rejected.**

Historical audit and event interpretation require them.

---

# 164. Rejected alternative — store canonical domain state in Mapping

**Rejected.**

Mapping relates identity; it does not replace domain storage.

---

# 165. Rejected alternative — Control Plane as master-data ERP

**Rejected.**

The Control Plane owns canonical identity and routing metadata, not ERP operational state.

---

# 166. Rejected alternative — every ERP row gets canonical UUID

**Rejected.**

Canonical identity is introduced where interoperability requires it.

---

# 167. Rejected alternative — mapping by name at runtime

**Rejected.**

Names are attributes, not reliable identity.

---

# 168. Rejected alternative — canonical UUID changes during engine migration

**Rejected.**

That would defeat the purpose of canonical identity.

---

# 169. Non-negotiable invariants

```text
INV-ERP-MAP-001
CanonicalEntity identity is independent of iDempiere.

INV-ERP-MAP-002
CanonicalEntity identity is independent of Medusa.

INV-ERP-MAP-003
Native IDs never become universal Baobab IDs.

INV-ERP-MAP-004
ExternalReference identifies an engine-specific representation.

INV-ERP-MAP-005
Every ExternalReference is scoped to its external identity domain.

INV-ERP-MAP-006
iDempiere native identifiers are scoped by EngineInstance.

INV-ERP-MAP-007
Mappings are first-class Control Plane resources.

INV-ERP-MAP-008
The Control Plane is authoritative for canonical mappings.

INV-ERP-MAP-009
Engine mapping caches are non-authoritative.

INV-ERP-MAP-010
Mapping resolution is Context-aware.

INV-ERP-MAP-011
Missing mappings are never guessed during ordinary transaction processing.

INV-ERP-MAP-012
Ambiguous mappings fail closed.

INV-ERP-MAP-013
Authoritative mappings are temporal.

INV-ERP-MAP-014
Historical mappings required for financial history are retained.

INV-ERP-MAP-015
Canonical UUIDs survive EngineInstance migration.

INV-ERP-MAP-016
Mapping creation is an explicit authorised operation.

INV-ERP-MAP-017
Fuzzy matching cannot directly create authoritative identity.

INV-ERP-MAP-018
Natural keys do not replace canonical UUIDs.

INV-ERP-MAP-019
Mapping and business relationship are distinct concepts.

INV-ERP-MAP-020
Distinct business documents receive distinct canonical identities.

INV-ERP-MAP-021
Canonical identity does not imply canonical domain-state ownership.

INV-ERP-MAP-022
Product identity does not make Control Plane the product catalog.

INV-ERP-MAP-023
Party identity does not make Control Plane the CRM or ERP.

INV-ERP-MAP-024
Mapping scope prevents accidental global equivalence.

INV-ERP-MAP-025
External identifiers are treated as opaque strings unless namespace rules specify otherwise.

INV-ERP-MAP-026
Mapping resolution verifies tenant compatibility.

INV-ERP-MAP-027
Mapping resolution verifies EngineInstance compatibility.

INV-ERP-MAP-028
Caller-supplied native IDs cannot override canonical resolution.

INV-ERP-MAP-029
Canonical events use canonical subjects.

INV-ERP-MAP-030
Required outbound event mappings exist before publication.

INV-ERP-MAP-031
Old mappings remain historically resolvable after migration.

INV-ERP-MAP-032
Canonical merge preserves retired identity history.

INV-ERP-MAP-033
One native representation cannot silently become authoritative for two unrelated canonical entities.

INV-ERP-MAP-034
Mapping data is critical Control Plane metadata and participates in DR.

INV-ERP-MAP-035
Mappings SHALL be auditable.

INV-ERP-MAP-036
Mapping caches SHALL support security-sensitive invalidation.

INV-ERP-MAP-037
Digital Estates cannot query unrestricted native mapping inventories.

INV-ERP-MAP-038
Cross-engine identity flows through canonical identity, not pairwise native IDs.

INV-ERP-MAP-039
Canonical identity survives replacement of an engine implementation.

INV-ERP-MAP-040
Canonicalisation SHALL preserve domain meaning rather than merely mirror source tables.
```

---

# 170. Initial mapping matrix

The initial ERP implementation SHOULD establish the following mappings:

| Canonical entity | iDempiere representation | Typical other representation |
|---|---|---|
| Party | `C_BPartner` | Medusa customer/company where applicable |
| Product | `M_Product` | Medusa Product/Variant representation |
| PurchaseOrder | `C_Order` | External procurement reference where applicable |
| SalesOrder | `C_Order` where ERP representation exists | Medusa Order |
| SupplierInvoice | `C_Invoice` | Supplier document reference |
| CustomerInvoice | `C_Invoice` | Commerce/account document projection |
| Payment | `C_Payment` | Payment-provider transaction where related |
| GoodsReceipt | `M_InOut` | Supplier delivery reference |
| Shipment | `M_InOut` where appropriate | Commerce fulfilment representation |
| Warehouse | `M_Warehouse` | Commerce inventory location where semantically equivalent |

The table describes potential representations.

It SHALL NOT be interpreted as automatic one-to-one equivalence.

---

# 171. Initial implementation vertical slice

The first implementation SHOULD prove Product and Party identity before broader document mapping.

```text
Canonical Party
      │
      ▼
C_BPartner

Canonical Product
      │
      ▼
M_Product
```

Then:

```text
Canonical PurchaseOrder
      │
      ▼
C_Order
```

followed by:

```text
Canonical SupplierInvoice
      │
      ▼
C_Invoice
```

This sequence exercises both master-data and transactional mapping.

---

# 172. Example complete identity flow

```text
                  BAOBAB CONTROL PLANE

                    Canonical Product
                     UUID = P-123
                           │
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        ExternalReference         ExternalReference
              │                         │
        Medusa Product              iDempiere
         prod_abc123              M_Product 10042
              │                         │
              └────────────┬────────────┘
                           │
                         Mapping
                           │
                    scoped / temporal
```

Neither engine knows the other's native identifier.

Both know—or can resolve—the canonical identity.

---

# 173. Migration example

Before migration:

```text
Product P-123
    │
    ▼
ERP-AF-SOUTH-01
M_Product 10042
```

After migration:

```text
Product P-123
    │
    ▼
ERP-THAMANI-01
M_Product 821
```

History:

```text
P-123
 │
 ├── Mapping A
 │     ERP-AF-SOUTH-01
 │     M_Product 10042
 │     valid_until = T
 │
 └── Mapping B
       ERP-THAMANI-01
       M_Product 821
       valid_from = T
```

No consumer changes Product ID.

---

# 174. Multi-market example

Canonical Product:

```text
P-COFFEE-001
```

may have:

```text
South Africa
    ↓
ERP-AF-SOUTH-01
M_Product 10042

Uganda
    ↓
ERP-AF-EAST-01
M_Product 731
```

The resolver uses:

```text
Tenant
LegalEntity
Market
CapabilityBinding
EngineInstance
MappingScope
```

to select the correct representation.

---

# 175. Definition of done

ADR-ERP-007 SHALL be considered implemented when:

- [ ] `CanonicalEntity` is authoritative outside ERP.
- [ ] `ExternalReference` model exists.
- [ ] `Mapping` model exists.
- [ ] `MappingScope` is enforced.
- [ ] External-reference uniqueness includes EngineInstance where required.
- [ ] Mapping lifecycle states are implemented.
- [ ] Mapping effective periods are implemented.
- [ ] Temporal overlap constraints exist.
- [ ] Mapping provenance is recorded.
- [ ] Canonical-to-native resolver exists.
- [ ] Native-to-canonical resolver exists.
- [ ] Resolver fails closed on ambiguity.
- [ ] Resolver fails closed on missing required mapping.
- [ ] Tenant compatibility is verified.
- [ ] EngineInstance compatibility is verified.
- [ ] Mapping caches are explicitly non-authoritative.
- [ ] Cache invalidation exists.
- [ ] Bulk resolution is supported or planned.
- [ ] Party ↔ `C_BPartner` mapping is implemented.
- [ ] Product ↔ `M_Product` mapping is implemented.
- [ ] PurchaseOrder ↔ `C_Order` mapping is implemented for the first procurement slice.
- [ ] SupplierInvoice ↔ `C_Invoice` mapping is implemented.
- [ ] Event publication performs required reverse mapping.
- [ ] Missing outbound mappings enter reconciliation rather than being guessed.
- [ ] Mapping reconciliation exists.
- [ ] Duplicate mapping detection exists.
- [ ] Migration preserves canonical IDs.
- [ ] Historical mappings survive migration.
- [ ] Mapping lifecycle changes are audited.
- [ ] Mapping lifecycle events are emitted by the Control Plane.
- [ ] Engine consumers cannot submit arbitrary native IDs as identity overrides.
- [ ] Contract tests cover mapping semantics.
- [ ] Cross-tenant mapping tests exist.
- [ ] Multi-EngineInstance mapping tests exist.
- [ ] Multi-market mapping tests exist.
- [ ] DR procedures include canonical identity and mapping data.

---

# 176. Final architectural model

```text
                     CANONICAL WORLD

                      CanonicalEntity
                            │
                      Canonical UUID
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
            Mapping       Mapping       Mapping
              │             │             │
              ▼             ▼             ▼
          iDempiere       Medusa        Payload
              │             │             │
              ▼             ▼             ▼
          Native ID      Native ID      Native ID


                    DOMAIN AUTHORITY

        ERP                  Trade               Content
         │                     │                    │
         ▼                     ▼                    ▼
   accounting state       commerce state       content state


                    CONTROL PLANE

                          │
                          ▼
                 canonical identity
                 external references
                     mappings
                 mapping scopes
                 engine instances
               capability bindings
```

---

# 177. Governing statement

The architecture SHALL preserve the distinction:

```text
IDENTITY
     ≠
REPRESENTATION
     ≠
DOMAIN AUTHORITY
```

A canonical entity answers:

> **What business thing is this?**

An ExternalReference answers:

> **What does this particular system call its representation of that thing?**

A Mapping answers:

> **Under what scope and during what period do these identities correspond?**

A CapabilityBinding answers:

> **Which EngineInstance should handle this capability in this Context?**

And the authoritative engine answers:

> **What is currently true about this entity inside my domain?**

Those questions SHALL remain separate.

The definitive rule is therefore:

> **Baobab canonical identity must outlive every engine representation that carries it.**

That rule is what allows Thamani, Nabhold, Zuribeans and future legal entities to expand into additional markets, move between regional ERP instances, replace individual engines, reorganise their businesses and preserve years of transactional history without rewriting the identity of the enterprise each time the underlying technology changes.