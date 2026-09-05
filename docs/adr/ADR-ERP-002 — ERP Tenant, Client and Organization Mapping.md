# ADR-ERP-002 — ERP Tenant, Client and Organization Mapping

**Status:** Accepted  
**Decision class:** ERP / Tenancy / Canonical Mapping / Organisation Model  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`  
**Parent ADR:** ADR-ERP-001 — Implement iDempiere as an Isolated, Headless, Multi-Tenant Baobab ERP Engine  
**Date:** 2026-09-02

---

# 1. Decision

Baobab SHALL implement an explicit mapping layer between its canonical organisational and tenancy model and iDempiere’s native `AD_Client` / `AD_Org` hierarchy.

The following equivalences SHALL NOT be assumed globally:

```text
Baobab Tenant      = iDempiere AD_Client
Baobab LegalEntity = iDempiere AD_Org
Baobab Market      = iDempiere AD_Org
Baobab Context     = iDempiere login context
```

Instead, the Control Plane SHALL resolve the appropriate relationship at runtime through:

```text
CanonicalEntity
ExternalReference
Mapping
MappingScope
EngineInstance
CapabilityBinding
Context
IsolationProfile
```

The mapping SHALL be:

- explicit;
- temporal;
- auditable;
- scoped;
- independently versioned from iDempiere;
- capable of supporting shared and dedicated ERP instances;
- capable of supporting multi-market and multi-region legal entities;
- capable of surviving tenant migration between ERP instances;
- incapable of silently broadening security boundaries.

---

# 2. Why this ADR is required

iDempiere provides a native multi-tenant model.

Its documentation defines an iDempiere Tenant/Client as a company or legal entity and states that data cannot be shared between tenants. Organizations sit beneath a tenant and may represent units such as stores or departments, with data potentially shared among organizations.

iDempiere also describes an Organization as potentially being a legal entity or a sub-unit for which transactions and documents are processed.

Therefore iDempiere’s model is flexible, but that flexibility creates an architectural danger:

> A legal entity can plausibly appear either as an iDempiere Client or as an iDempiere Organization.

Baobab cannot allow individual deployments to make that choice informally.

The platform requires deterministic rules.

---

# 3. Baobab canonical concepts

This ADR uses the following canonical meanings.

## 3.1 Tenant

A `Tenant` is a Baobab isolation and consumption boundary.

It answers:

> Whose governed platform boundary is this?

A Tenant MAY correspond to:

- a legal entity;
- a group;
- another consuming organisation;
- a deliberately isolated business boundary.

A Tenant is not synonymous with LegalEntity.

---

# 4. LegalEntity

A `LegalEntity` represents a juridically recognised organisation.

Examples include:

```text
Nabhold Group Africa
Thamani
Zuribeans
future incorporated subsidiaries
external customer companies
```

A LegalEntity MAY be the default tenant boundary.

It does not automatically have to be one.

---

# 5. Organisation

`Organisation` represents structural units beneath or associated with a LegalEntity.

Baobab organisation structure may include:

```text
LegalEntity
    │
    ├── BusinessUnit
    │     ├── Function
    │     │     └── Team
    │     └── Function
    │
    └── BusinessUnit
```

Not every canonical Organisation requires an ERP representation.

This is critical.

The ERP SHALL model organisational structures only where they matter to ERP processing, accounting, inventory, operational reporting or authorisation.

---

# 6. Market

A `Market` represents a commercial or operating market.

Examples:

```text
South Africa
Uganda
Kenya
Rwanda
European Union market
regional export market
```

Market answers:

> In what commercial/regulatory market does this activity occur?

It SHALL NOT mean:

```text
legal entity
tenant
ERP organisation
cloud region
database
```

---

# 7. Engine

`Engine` describes the canonical Baobab capability provider.

For this ADR:

```text
Engine:
    Baobab ERP Engine

implementation:
    iDempiere
```

---

# 8. EngineInstance

An `EngineInstance` represents a deployed ERP runtime boundary.

Examples:

```text
ERP-AF-SOUTH-01
ERP-AF-EAST-01
ERP-THAMANI-01
```

One Engine can therefore have:

```text
1..N EngineInstances
```

---

# 9. CapabilityBinding

A `CapabilityBinding` associates a Baobab context with an EngineInstance that supplies a capability.

Conceptually:

```text
Tenant
LegalEntity
Market
Capability
       │
       ▼
CapabilityBinding
       │
       ▼
ERP EngineInstance
```

The binding therefore answers:

> Which actual ERP instance should satisfy this request?

---

# 10. IsolationProfile

An `IsolationProfile` defines the degree and mechanism of separation required.

Typical profiles include:

```text
shared_instance_dedicated_client
dedicated_instance
dedicated_regional_instance
regulated_instance
```

The IsolationProfile SHALL constrain permissible iDempiere mappings.

---

# 11. iDempiere Client semantics

Within iDempiere, `AD_Client` is the principal tenant boundary.

iDempiere documentation states that a Tenant is a company or legal entity and that data cannot be shared between tenants.

Therefore:

```text
different AD_Client_ID values
```

represent the strongest normal application-level data separation within one shared iDempiere installation.

---

# 12. iDempiere Organization semantics

`AD_Org` represents an organisational entity inside an iDempiere Client.

iDempiere describes organizations as units such as stores or departments and notes that data can be shared between organizations.

An Organization can also represent a legal entity or sub-unit for which documents and transactions are processed.

Therefore:

> `AD_Org` is an operational/accounting partition, not a universally safe hard-tenancy boundary.

---

# 13. Fundamental mapping rule

Where a Baobab boundary requires hard isolation from another tenant, that boundary SHALL NOT be represented solely through different `AD_Org` records under one shared `AD_Client`.

The minimum normal isolation SHALL be:

```text
Baobab Tenant A
       │
       ▼
AD_Client A


Baobab Tenant B
       │
       ▼
AD_Client B
```

or stronger:

```text
Baobab Tenant A
       │
       ▼
ERP EngineInstance A
       │
       ▼
AD_Client A
```

---

# 14. Preferred default mapping

Where one legal entity is also the Baobab Tenant boundary, the preferred default SHALL be:

```text
Baobab Tenant
      │
      └── LegalEntity
              │
              ▼
      CapabilityBinding
              │
              ▼
       EngineInstance
              │
              ▼
        AD_Client
```

For such cases:

```text
Tenant       → AD_Client
LegalEntity  → principal business identity associated with that AD_Client
```

This is a mapping convention.

It is not an ontology equivalence.

---

# 15. Why LegalEntity does not automatically become AD_Org

Consider:

```text
Nabhold Group Africa
Thamani
Zuribeans
```

If all three require independent ERP isolation, this structure is inappropriate:

```text
AD_Client = Nabhold Ecosystem
    │
    ├── AD_Org = Nabhold
    ├── AD_Org = Thamani
    └── AD_Org = Zuribeans
```

because iDempiere permits various forms of intra-client sharing, and its data-access model explicitly distinguishes between tenant-level data and organization-level data.

Instead the normal pattern SHALL be:

```text
ERP EngineInstance
│
├── AD_Client = NABHOLD
│
├── AD_Client = THAMANI
│
└── AD_Client = ZURIBEANS
```

where shared infrastructure is permitted.

---

# 16. Concrete Nabhold example

The initial shared-instance topology MAY therefore be:

```text
               ERP-AF-SOUTH-01
                       │
      ┌────────────────┼────────────────┐
      │                │                │
      ▼                ▼                ▼
 AD_Client         AD_Client         AD_Client
 NABHOLD           THAMANI           ZURIBEANS
      │                │                │
      ▼                ▼                ▼
   AD_Org           AD_Org           AD_Org
 structures         structures       structures
```

This permits shared runtime infrastructure while preserving separate native iDempiere Client boundaries.

---

# 17. Nabhold itself may be an ERP tenant

Nabhold Group may consume ERP capabilities independently from subsidiaries.

Its canonical representation may therefore be:

```text
Tenant
    Nabhold

LegalEntity
    Nabhold Group Africa

Capability
    ERP

CapabilityBinding
    → ERP-AF-SOUTH-01

ExternalReference
    → AD_Client_ID <NABHOLD>
```

The fact that Nabhold also acts as a holding or platform-owning group does not disqualify it from being an ERP-consuming tenant.

Platform ownership and capability consumption are separate concerns.

---

# 18. Thamani example

Conceptually:

```text
Tenant:
    Thamani

LegalEntity:
    Thamani

Markets:
    South Africa
    Uganda
    future markets

ERP Binding:
    ERP-AF-SOUTH-01

iDempiere:
    AD_Client = THAMANI
```

Within the Client:

```text
THAMANI
│
├── AD_Org = *
├── AD_Org = South Africa Operations
├── AD_Org = Uganda Operations
└── future ERP organisations
```

Whether those market operations should actually be separate `AD_Org` records SHALL be determined by ERP operational/accounting requirements, not by the mere existence of Markets in Baobab.

---

# 19. Zuribeans example

Conceptually:

```text
Tenant:
    Zuribeans

LegalEntity:
    Zuribeans

Markets:
    South Africa
    future regional/export markets

CapabilityBinding:
    ERP → ERP-AF-SOUTH-01

ExternalReference:
    canonical tenant/legal entity
       → iDempiere AD_Client
```

Its ERP client remains independent from Thamani even if both reside in the same PostgreSQL-backed EngineInstance.

---

# 20. Organization "*" semantics

iDempiere supports tenant/client-level records through Organization `*`.

Its Tenant Share configuration explicitly distinguishes tenant-level shared data from organization-specific data, including Business Partners and Products.

Therefore Baobab SHALL treat:

```text
AD_Org_ID = 0 / "*"
```

as:

> shared within this iDempiere Client according to native rules.

It SHALL NOT mean:

```text
globally shared across Baobab
```

This distinction is mandatory.

---

# 21. Canonical sharing is different from ERP sharing

A canonical product could be visible across several Baobab contexts while each ERP Client maintains its own native product record.

Example:

```text
Canonical Product X
       │
       ├── ERP Client THAMANI
       │        M_Product 10045
       │
       └── ERP Client ZURIBEANS
                M_Product 20331
```

This SHALL be permitted.

Baobab canonical identity does not require physical ERP record sharing.

---

# 22. Mapping cardinality — Tenant to EngineInstance

A Tenant may consume ERP through:

```text
1..N EngineInstances
```

over its lifetime.

At any single effective Context, normally one binding SHALL be authoritative for a given ERP capability and scope.

Example over time:

```text
2026–2028
Tenant A → ERP-AF-SOUTH-01

2028 onward
Tenant A → ERP-TENANT-A-01
```

Historical mappings remain valid for reconciliation.

---

# 23. Mapping cardinality — Tenant to AD_Client

Within one EngineInstance:

```text
Tenant
    → normally exactly one AD_Client
```

for the applicable isolation scope.

Across multiple EngineInstances:

```text
Tenant
    → potentially multiple AD_Client representations
```

over time or by region.

Therefore the true mapping key SHALL include:

```text
tenant_id
engine_instance_id
external_identifier
validity period
```

not merely:

```text
tenant_id → AD_Client_ID
```

---

# 24. Mapping cardinality — LegalEntity to AD_Client

A LegalEntity MAY map to:

```text
0..N AD_Client representations
```

because:

- it may not consume ERP;
- it may operate across more than one isolated ERP instance;
- it may migrate;
- historical representations may coexist.

---

# 25. Mapping cardinality — LegalEntity to AD_Org

A LegalEntity MAY map to:

```text
0..N AD_Org
```

but only where an explicit organisational/accounting reason exists.

For example:

```text
Parent LegalEntity
       │
       ├── South Africa branch
       └── Uganda branch
```

might be represented differently depending on legal and accounting realities.

Baobab SHALL not prescribe `AD_Org` solely from the canonical hierarchy.

---

# 26. Mapping cardinality — Organisation to AD_Org

A canonical Organisation MAY map to:

```text
0..N AD_Org
```

and an `AD_Org` MAY map to:

```text
0..1 canonical Organisation
```

under ordinary active mappings.

Many canonical organisations may have no ERP representation.

Examples:

```text
Marketing Team
Software Architecture Team
Board Committee
Editorial Team
```

typically do not need their own `AD_Org`.

---

# 27. ERP-relevant organisation test

Before creating an `AD_Org`, at least one meaningful ERP requirement SHOULD exist.

Examples:

- separate accounting dimension;
- transaction ownership;
- warehouse responsibility;
- statutory reporting;
- operational reporting;
- separate document sequence;
- internal organisational costing;
- ERP security boundary;
- profit centre;
- location-specific ERP processing.

The question SHALL be:

> Does ERP need to transact, account, control or report separately for this unit?

not:

> Does this unit exist in the organisation chart?

---

# 28. Market-to-Organization mapping is optional

A Market SHALL NOT automatically create an `AD_Org`.

Example:

```text
Legal Entity = Thamani
Markets      = South Africa, Uganda
```

may legitimately map as:

### Pattern A

```text
AD_Client THAMANI
    └── AD_Org THAMANI
```

with markets represented through other ERP dimensions.

Or:

### Pattern B

```text
AD_Client THAMANI
    ├── AD_Org SOUTH_AFRICA
    └── AD_Org UGANDA
```

if accounting/operational requirements justify this.

The choice SHALL be documented in configuration or a subordinate market-localisation decision.

---

# 29. Market SHALL remain canonical

Even when an `AD_Org` corresponds closely to a market operation:

```text
Market Uganda
       ≠
AD_Org Uganda Operations
```

The relationship SHALL still be expressed as a Mapping.

This protects against future reorganisation.

---

# 30. Infrastructure Region SHALL never map directly to AD_Org

Example:

```text
AWS af-south-1
```

is an infrastructure concern.

It SHALL not produce:

```text
AD_Org = af-south-1
```

Deployment region is represented through EngineInstance metadata.

---

# 31. MappingScope

Every Mapping SHALL have an explicit `MappingScope`.

Relevant scopes SHOULD include:

```text
global
tenant
legal_entity
market
digital_estate
engine
engine_instance
capability
```

ERP mappings will usually be:

```text
engine_instance
```

or narrower.

---

# 32. Example mapping

Conceptually:

```json
{
  "canonical_entity": "<tenant-uuid>",
  "external_reference": {
    "engine": "baobab-erp",
    "engine_instance": "<erp-instance-uuid>",
    "namespace": "idempiere",
    "external_type": "AD_Client",
    "external_id": "1000000"
  },
  "scope": {
    "type": "engine_instance",
    "id": "<erp-instance-uuid>"
  },
  "valid_from": "2026-09-02T00:00:00Z",
  "valid_to": null,
  "status": "active"
}
```

---

# 33. Native iDempiere IDs SHALL never cross as canonical IDs

The following is prohibited:

```json
{
  "tenant_id": 1000000
}
```

where that number is actually `AD_Client_ID`.

Correct:

```json
{
  "tenant_id": "019...",
  "erp_reference": {
    "namespace": "idempiere",
    "type": "AD_Client",
    "id": "1000000"
  }
}
```

---

# 34. Mapping resolution direction

Resolution SHALL support both:

```text
canonical → native
```

and:

```text
native → canonical
```

where authorised.

Examples:

### Command path

```text
Canonical Tenant UUID
      ↓
Mapping Resolver
      ↓
AD_Client_ID
```

### Event path

```text
AD_Client_ID
      ↓
Reverse Mapping
      ↓
Canonical Tenant UUID
```

---

# 35. No blind trust of native identifiers

An inbound request SHALL never be authorised merely because it supplies:

```text
AD_Client_ID = X
```

Instead:

```text
authenticated principal
       ↓
Baobab Context
       ↓
CapabilityBinding
       ↓
EngineInstance
       ↓
Mapping resolution
       ↓
AD_Client_ID
```

The server determines the Client.

The caller does not.

---

# 36. Context model

Every ERP operation SHALL execute within a resolved Baobab Context.

Minimum relevant dimensions:

```text
tenant_id
legal_entity_id
market_id
capability_id
engine_id
engine_instance_id
isolation_profile_id
principal_id
```

Additional dimensions may include:

```text
digital_estate_id
organisation_id
currency
locale
timezone
jurisdiction
```

---

# 37. Context resolution pipeline

The canonical pipeline SHALL resemble:

```text
Incoming Request
       │
       ▼
Authenticate Principal
       │
       ▼
Resolve Tenant
       │
       ▼
Resolve LegalEntity
       │
       ▼
Resolve Market
       │
       ▼
Resolve Capability
       │
       ▼
Resolve CapabilityBinding
       │
       ▼
Resolve EngineInstance
       │
       ▼
Validate IsolationProfile
       │
       ▼
Resolve Mapping
       │
       ▼
Derive AD_Client / AD_Org
       │
       ▼
Execute ERP Operation
```

A request SHALL fail closed if a required step cannot be resolved unambiguously.

---

# 38. AD_Org resolution

`AD_Org` SHALL normally be resolved from context or business document rules.

It SHALL not be casually defaulted from user input.

Potential sources include:

```text
canonical organisation mapping
warehouse
market operation
legal entity configuration
document type policy
ERP business rule
```

---

# 39. Ambiguity SHALL fail

If the resolver finds:

```text
Tenant A
    →
AD_Client 100
AD_Client 200
```

both active for the same EngineInstance/scope/time, without a distinguishing Context dimension, the operation SHALL fail.

The platform SHALL not choose arbitrarily.

Suggested error:

```text
ERP_MAPPING_AMBIGUOUS
```

---

# 40. Missing mapping SHALL fail explicitly

A missing mapping SHALL produce a stable platform error such as:

```text
ERP_MAPPING_NOT_FOUND
```

It SHALL NOT silently create a new iDempiere Client or Organization during ordinary API execution.

Provisioning is a lifecycle operation.

---

# 41. Mapping creation authority

Mapping creation SHALL be limited to authorised control-plane or provisioning workflows.

Ordinary business services SHALL not create mappings opportunistically.

This prevents accidental duplicate ERP identities.

---

# 42. Mapping lifecycle

Mappings SHALL support at least:

```text
pending
active
superseded
suspended
retired
invalid
```

Suggested progression:

```text
pending
   ↓
active
   ↓
superseded
   ↓
retired
```

A mapping with financial history SHALL normally be retired, not physically deleted.

---

# 43. Temporal validity

Mappings SHALL include:

```text
valid_from
valid_to
```

because identity relationships may change.

Example:

```text
Tenant Thamani

2026-09-02 → 2028-12-31
    ERP-AF-SOUTH-01 / AD_Client 1000000

2029-01-01 →
    ERP-THAMANI-01 / AD_Client 1000000
```

Even if the native numeric ID coincidentally remains the same, EngineInstance distinguishes the identities.

---

# 44. Temporal overlap prohibition

For any canonical entity, engine instance, external type and mapping scope, two authoritative active mappings SHALL NOT overlap unless the mapping model explicitly allows multiplicity.

For single-valued mappings, Control Plane persistence SHOULD enforce this through PostgreSQL temporal exclusion constraints.

---

# 45. ExternalReference identity

An external ERP reference SHALL be uniquely identified by at least:

```text
engine_instance_id
namespace
external_entity_type
external_identifier
```

Because:

```text
AD_Client_ID 1000000
```

could legitimately exist in two separate iDempiere databases.

Therefore this is incorrect:

```text
idempiere:AD_Client:1000000
```

as a globally unique identifier.

This is correct:

```text
ERP-AF-SOUTH-01:
    idempiere:
        AD_Client:
            1000000
```

---

# 46. System Client

iDempiere's System-level Client SHALL NOT be mapped to an ordinary Baobab tenant.

System-level iDempiere configuration is platform/engine administration.

It belongs to:

```text
EngineInstance administration
```

not:

```text
Tenant business context
```

No digital estate or tenant business workload SHALL operate as System Client.

---

# 47. System Organization

Likewise, system-level or special wildcard organisations SHALL not be assigned arbitrary canonical organisational meaning.

`*` remains a native iDempiere sharing mechanism within its Client.

It is not a canonical Baobab organisation.

---

# 48. Business Partner data sharing

iDempiere allows Business Partner records to be defined at Tenant/Client level or Organization level depending on sharing rules.

Therefore a Baobab canonical BusinessPartner may map differently depending on tenant configuration.

Example:

```text
Canonical Supplier S
       │
       ▼
AD_Client THAMANI
       │
       └── C_BPartner
             AD_Org = *
```

or:

```text
AD_Org = Uganda Operations
```

if deliberately organisation-specific.

That native sharing decision SHALL not redefine the canonical supplier identity.

---

# 49. Product sharing

The same rule applies to ERP products.

iDempiere Client Share can control whether Products are tenant-shared or organization-specific.

Baobab SHALL preserve the distinction:

```text
Canonical Product identity
       ≠
iDempiere Product sharing policy
```

---

# 50. Role mapping

Baobab Roles SHALL NOT automatically map 1:1 to iDempiere `AD_Role`.

Instead:

```text
Baobab Principal
       │
       ▼
Platform authorization
       │
       ▼
ERP capability permission
       │
       ▼
ERP integration identity / role
```

Interactive back-office ERP users MAY additionally have native iDempiere roles.

---

# 51. Organization access

iDempiere supports role/user organization access controls, including user organization access records.

These SHALL be used as defense in depth for native ERP users.

However:

> Native iDempiere Organization access does not replace Baobab tenant and capability authorization.

---

# 52. Integration identities

Machine integrations SHALL preferably use service identities scoped to:

```text
EngineInstance
Client
capability
required operation
```

They SHALL not use unrestricted System-level administrative identities.

---

# 53. Tenant-wide ERP service

Where a service identity needs to operate across Organizations inside one Client, that authority MAY be granted deliberately.

It SHALL still be constrained to that Client.

Cross-client service identities SHALL be exceptional.

---

# 54. Multiple legal entities inside one Baobab Tenant

Baobab permits a Tenant boundary wider than one LegalEntity.

For example:

```text
Tenant = Group X
    │
    ├── LegalEntity A
    └── LegalEntity B
```

This does NOT imply both legal entities should automatically become `AD_Org` under one Client.

The IsolationProfile and accounting/legal requirements determine the ERP representation.

---

# 55. Multi-legal-entity strategy A — separate Clients

Preferred where entities require strong separation:

```text
Baobab Tenant Group X
     │
     ├── LegalEntity A
     │       └── AD_Client A
     │
     └── LegalEntity B
             └── AD_Client B
```

Both may still belong to one canonical Baobab Tenant.

This demonstrates why:

```text
Tenant != AD_Client
```

is necessary.

One Tenant can map to multiple ERP Clients when its internal legal entities require separate ERP boundaries.

---

# 56. Multi-legal-entity strategy B — shared Client

This MAY be permitted only after an explicit architecture/accounting decision:

```text
AD_Client Group X
    │
    ├── AD_Org Legal Entity A
    └── AD_Org Legal Entity B
```

This is appropriate only if:

- inter-organization sharing is acceptable;
- accounting architecture supports it;
- regulatory separation permits it;
- access risks are accepted;
- future divestiture implications are understood.

It SHALL NOT be the default.

---

# 57. Shared Client exception requirements

Using multiple LegalEntities as `AD_Org` under a shared `AD_Client` SHALL require documented evidence addressing:

```text
legal separation
financial reporting
tax
data confidentiality
user access
shared master data
intercompany processing
future separation
localisation
audit
```

The Control Plane SHALL explicitly record this topology.

---

# 58. Group consolidation

Holding-company consolidation SHALL not by itself justify collapsing subsidiaries into one AD_Client.

Financial consolidation may be implemented through appropriate ERP/accounting/reporting mechanisms while preserving entity separation.

The architecture SHALL prioritise isolation correctness over cosmetic convenience.

---

# 59. Branches

A branch that is not an independent legal entity MAY reasonably map to an iDempiere Organization.

Example:

```text
LegalEntity
    Thamani

Organisation
    Uganda Branch

           │
           ▼

AD_Client
    THAMANI

AD_Org
    UGANDA_BRANCH
```

provided accounting and operating requirements support that representation.

---

# 60. Departments

Departments SHALL normally not receive separate AD_Org records unless ERP requirements demand it.

Examples:

```text
Marketing
HR
Software Engineering
Legal
```

may instead be represented through:

- accounting dimensions;
- projects;
- activity;
- cost centres;
- other suitable ERP structures.

Avoid exploding the AD_Org hierarchy merely to copy an HR organogram.

---

# 61. Warehouses

Warehouse identity SHALL remain distinct from Organization identity.

An iDempiere Warehouse may be associated with an Organization, but:

```text
Warehouse != AD_Org
```

canonically.

Baobab SHALL model warehouse/location mapping separately.

---

# 62. DigitalEstate SHALL not map to AD_Client

A DigitalEstate such as a public or customer-facing web estate is a presentation/application context.

It SHALL not normally create an ERP Client.

Example:

```text
Zuribeans Digital Estate
          │
          ▼
CapabilityBinding
          │
          ▼
Zuribeans Tenant
          │
          ▼
ERP Client
```

Not:

```text
Zuribeans website
      =
AD_Client
```

---

# 63. Multiple DigitalEstates

One Tenant may have multiple estates:

```text
corporate website
B2B portal
B2C portal
mobile app
partner portal
```

All can legitimately resolve to the same ERP Client while having distinct capability policies.

---

# 64. DigitalEstate context

DigitalEstate MAY form part of MappingScope or CapabilityBinding when access differs by channel.

For example:

```text
B2B Portal
    → ERP purchase-order query capability

Public Website
    → no direct ERP capability
```

This is a capability concern, not native iDempiere tenancy.

---

# 65. Market-specific binding

A LegalEntity may resolve to different ERP instances by Market.

Example:

```text
LegalEntity Thamani
│
├── Market ZA
│      → ERP-AF-SOUTH-01
│
└── Market UG
       → ERP-AF-EAST-01
```

The same canonical LegalEntity can therefore have different native ERP representations.

---

# 66. Example multi-region mapping

```text
Canonical LegalEntity:
    Thamani
          │
          ├─────────────────────────┐
          │                         │
    Market ZA                   Market UG
          │                         │
          ▼                         ▼
ERP-AF-SOUTH-01              ERP-AF-EAST-01
          │                         │
          ▼                         ▼
AD_Client 1000000             AD_Client 1000000
```

The identical numeric IDs cause no collision because the EngineInstance is part of identity.

---

# 67. Regional split does not create new canonical identity

When Thamani expands from South Africa into Uganda:

```text
Thamani
```

remains the same canonical LegalEntity unless a new legal company is incorporated.

A new Market or EngineInstance SHALL not cause a new LegalEntity UUID.

---

# 68. Incorporation does create a possible new LegalEntity

If the Uganda operation later becomes:

```text
Thamani Uganda Ltd
```

then Baobab may create a new LegalEntity.

Its ERP representation may become:

```text
new AD_Client
```

or another approved structure.

The canonical model therefore supports business evolution without conflating geography with legal identity.

---

# 69. Tenant inheritance rules

Canonical hierarchy SHALL NOT imply automatic ERP authorization inheritance.

Example:

```text
Tenant Group
    └── LegalEntity Subsidiary
```

does not automatically mean Group users can access subsidiary ERP data.

Access inheritance SHALL be policy-driven.

---

# 70. Organization inheritance rules

A parent canonical Organisation SHALL not automatically inherit all child `AD_Org` permissions.

iDempiere's own role and organisation-access mechanisms SHALL remain independently configured as defense in depth.

---

# 71. Mapping inheritance

Mappings SHALL not be inferred merely from hierarchy unless the Mapping type explicitly declares an inheritance rule.

Default:

```text
inheritance = none
```

This avoids accidental privilege and routing expansion.

---

# 72. Capability inheritance

Capabilities MAY inherit according to Control Plane policy, but such inheritance SHALL be explicit.

Example:

```text
Tenant-level ERP capability enabled
```

does not necessarily enable every child LegalEntity if different isolation or licensing requirements apply.

---

# 73. IsolationProfile precedence

Where mappings and isolation policy conflict:

```text
IsolationProfile wins.
```

Example:

```text
Existing mapping:
LegalEntity B → AD_Org B

New policy:
LegalEntity B requires dedicated-client isolation
```

The platform SHALL migrate the representation rather than retain the unsafe mapping for convenience.

---

# 74. Mapping policy precedence

Resolution precedence SHOULD be:

```text
most-specific valid MappingScope
        ↓
less-specific valid scope
        ↓
default binding
```

For example:

```text
LegalEntity + Market + Capability
```

wins over:

```text
Tenant + Capability
```

if both are valid and intentionally defined.

---

# 75. No implicit fallback across tenants

If a mapping cannot be found for Tenant A, the resolver SHALL never fall back to:

```text
default Client
another tenant
System
*
```

The operation fails closed.

---

# 76. Provisioning Client creation

Creation of a new iDempiere Client SHALL occur only through ERP provisioning.

Provisioning SHALL:

1. validate canonical Tenant/LegalEntity;
2. resolve IsolationProfile;
3. select EngineInstance;
4. ensure no conflicting mapping exists;
5. create/configure AD_Client;
6. initialise accounting and required reference data;
7. create required AD_Org structures;
8. create service roles;
9. record ExternalReference;
10. activate Mapping;
11. run isolation tests;
12. activate CapabilityBinding.

---

# 77. Client creation is not atomic from the business perspective

Provisioning an iDempiere tenant requires multiple configuration steps.

Therefore the Control Plane SHALL treat provisioning as a workflow/saga with lifecycle state.

Example:

```text
requested
   ↓
instance_allocated
   ↓
client_created
   ↓
client_configured
   ↓
mappings_created
   ↓
validated
   ↓
active
```

Failures SHALL be recoverable.

---

# 78. Organization provisioning

Creating an AD_Org SHALL likewise be controlled.

Required inputs SHOULD include:

```text
canonical organisation/legal entity
ERP Client
purpose
accounting implications
market
location
effective date
```

No general API SHALL permit arbitrary tenant users to proliferate organizations.

---

# 79. Migration between EngineInstances

Migration SHALL preserve canonical identity.

Example:

```text
Before

Tenant UUID T
    → ERP-AF-SOUTH-01
    → AD_Client 1000000
```

After:

```text
Tenant UUID T
    → ERP-THAMANI-01
    → AD_Client 1000000
```

The canonical Tenant remains `T`.

The first Mapping becomes historical.

The second becomes active.

---

# 80. Engine migration lifecycle

Suggested lifecycle:

```text
migration_planned
      ↓
target_provisioned
      ↓
data_migrated
      ↓
reconciled
      ↓
writes_frozen
      ↓
final_delta_migrated
      ↓
binding_switched
      ↓
source_draining
      ↓
source_retired
```

No consumer should need to change canonical IDs.

---

# 81. Historical events after migration

An old event SHALL retain:

```text
engine_instance_id
```

from the source instance.

Reverse mapping therefore remains possible after migration.

Historical ExternalReferences SHALL not be deleted.

---

# 82. Divestiture

If a subsidiary is divested, the architecture SHALL support extracting its ERP boundary.

Where it already owns a dedicated AD_Client:

```text
shared EngineInstance
       ↓
dedicated EngineInstance
```

is considerably easier than untangling transactions from a shared AD_Client.

This is another reason dedicated Clients are the preferred legal-entity isolation boundary.

---

# 83. Acquisition

An acquired business MAY initially receive:

```text
dedicated ERP Client
```

even within a shared EngineInstance.

Its data does not need to be merged into Nabhold's Client merely because ownership has changed.

Corporate control and ERP tenant boundaries are separate decisions.

---

# 84. Suspension

Suspending a Baobab Tenant SHALL NOT automatically delete or deactivate its ERP Client.

Suspension may instead:

```text
disable CapabilityBinding
deny new platform requests
retain ERP records
retain mapping
retain auditability
```

Financial retention rules may require the data for years.

---

# 85. Retirement

Retiring a Tenant or LegalEntity SHALL preserve:

```text
canonical identity
historical mappings
audit records
financial records
event lineage
```

according to retention policy.

Hard deletion SHALL be exceptional.

---

# 86. Name changes

Names are attributes.

Identifiers are identities.

If:

```text
Thamani Global
```

becomes:

```text
Thamani Trading
```

canonical IDs SHALL remain unchanged if the legal entity remains the same.

The same principle applies to iDempiere Search Keys and names.

---

# 87. Legal identity changes

A genuine juridical transformation SHALL be evaluated separately.

Examples:

```text
new registration
merger
legal conversion
successor entity
```

may require a new canonical LegalEntity.

This SHALL be a governance decision, not inferred from ERP master-data edits.

---

# 88. ExternalReference immutability

Once used historically:

```text
engine_instance
external_type
external_id
```

SHOULD remain immutable.

Corrections should normally create a replacement/superseding Mapping rather than rewriting historical identity lineage.

---

# 89. Mapping provenance

Every mapping SHALL record provenance such as:

```text
provisioned
migrated
imported
manually-approved
reconciled
system-generated
```

and preferably:

```text
created_by
approved_by
source
reason
```

This becomes important during audits and migrations.

---

# 90. Mapping confidence

Where automated matching is ever used for legacy migration, candidates SHALL NOT become authoritative solely because of fuzzy matching.

Potential states:

```text
candidate
verified
authoritative
rejected
```

Financial identity mappings require deterministic approval.

---

# 91. Canonical identifiers

Baobab SHALL use globally unique opaque identifiers—according to the canonical Control Plane UUID strategy—for:

```text
Tenant
LegalEntity
Organisation
Market
Engine
EngineInstance
Mapping
ExternalReference
CapabilityBinding
Context
```

Human-readable codes may coexist.

They SHALL not be identity authority.

---

# 92. Human-readable codes

Examples:

```text
tenant code:
    THAMANI

engine instance:
    ERP-AF-SOUTH-01

market:
    ZA
```

are useful operational identifiers.

They SHALL be unique within their declared namespace but SHALL remain secondary to canonical UUID identity.

---

# 93. Search Keys

iDempiere Search Keys MAY deliberately align with Baobab-readable codes where useful.

Example:

```text
AD_Client search key:
    THAMANI
```

This improves operability.

It SHALL not constitute canonical identity mapping.

---

# 94. Tenant/Client mapping table

Conceptually, the Control Plane should be capable of representing:

| Canonical concept | Engine | Instance | Native concept | Native key | Effective |
|---|---|---|---|---|---|
| Tenant Thamani | ERP | ERP-AF-SOUTH-01 | AD_Client | 1000000 | active |
| Tenant Zuribeans | ERP | ERP-AF-SOUTH-01 | AD_Client | 1000001 | active |
| Tenant Nabhold | ERP | ERP-AF-SOUTH-01 | AD_Client | 1000002 | active |

The IDs above are illustrative only.

---

# 95. Organisation mapping table

Similarly:

| Canonical concept | ERP Client | Native concept | Native key |
|---|---|---|---|
| Thamani South Africa Operations | THAMANI | AD_Org | X |
| Thamani Uganda Operations | THAMANI | AD_Org | Y |

But only if these organisations genuinely require ERP representation.

---

# 96. Runtime invariant

Every ERP transaction SHALL satisfy:

```text
resolved canonical context
        ∧
valid CapabilityBinding
        ∧
active EngineInstance
        ∧
compatible IsolationProfile
        ∧
active canonical/native Mapping
        ∧
authorized operation
```

before business execution.

---

# 97. Client injection invariant

The application integration layer SHALL derive Client identity.

Caller-supplied `AD_Client_ID` SHALL never override the resolved mapping.

---

# 98. Organization injection invariant

Where AD_Org can be derived authoritatively from Context and document rules, caller-supplied native `AD_Org_ID` SHALL not override it.

Where users select an Organization, selection SHALL be from an authorised canonical/native set.

---

# 99. Transaction validation

Immediately before executing a write, ERP integration SHOULD verify:

```text
record AD_Client_ID
    ==
resolved Client
```

where applicable.

For updates:

```text
existing record belongs to current Client
```

MUST be confirmed.

---

# 100. Event validation

Before publishing an ERP event:

```text
native AD_Client
        ↓
reverse mapping
        ↓
canonical tenant
```

MUST succeed for externally visible tenant-scoped events.

An event whose canonical ownership cannot be resolved SHALL be quarantined rather than emitted with guessed ownership.

---

# 101. Event Context

ERP events SHOULD carry applicable:

```text
tenant_id
legal_entity_id
organisation_id
market_id
engine_instance_id
```

but canonical Context must be reconstructed from authoritative mappings, not simply translated from whatever native fields happen to exist.

---

# 102. Cross-client transactions

Ordinary business documents SHALL remain Client-local.

Any genuine intercompany process across separate Clients SHALL be represented as coordinated business operations, not a cross-tenant database transaction.

Conceptually:

```text
Company A
   ↓
sale / receivable
   ↓
canonical intercompany relationship
   ↓
Company B
   ↓
purchase / payable
```

This preserves independent books and isolation.

---

# 103. Intercompany mappings

Canonical relationships MAY connect:

```text
LegalEntity A
        ↔
LegalEntity B
```

while each entity has its own iDempiere Business Partner representation of the other.

For example:

```text
Canonical LegalEntity Thamani
       │
       └── ERP Client Zuribeans
              C_BPartner THAMANI
```

The party's canonical identity remains singular even though native records are tenant-local.

---

# 104. Reporting hierarchy

iDempiere supports reporting hierarchies for accounting dimensions including Organization.

Baobab SHOULD use native reporting capabilities where appropriate rather than forcing the canonical organisation tree to equal the ERP reporting tree.

The two hierarchies may legitimately differ.

---

# 105. Why the hierarchies may differ

Canonical organisational hierarchy answers:

> How is the enterprise structurally organised?

ERP reporting hierarchy answers:

> How should ERP/accounting data be grouped for this reporting purpose?

Those are different questions.

Therefore:

```text
Canonical hierarchy
        ≠
ERP reporting hierarchy
```

by default.

---

# 106. Security rationale

iDempiere's role-data-access model contains both Tenant and Organization dimensions, reinforcing that these are distinct levels of access control.

Baobab SHALL therefore never reduce security to a single organization identifier.

Strong isolation requires Client-aware enforcement.

---

# 107. Multi-tenant test matrix

Every release SHALL test at least:

```text
Tenant A / Client A
Tenant B / Client B
```

with attempts to:

- read another Client's records;
- update another Client's records;
- guess another Client's IDs;
- invoke another Client through API parameters;
- publish misattributed events;
- resolve mappings with wrong EngineInstance;
- cross organization boundaries without permission;
- exploit wildcard Organization semantics.

All SHALL fail according to policy.

---

# 108. Shared-data test matrix

Tests SHALL verify both:

```text
tenant-shared records
```

and:

```text
organization-specific records
```

because iDempiere explicitly supports this distinction for classes such as Business Partner and Product.

---

# 109. Migration tests

Tenant relocation tests SHALL confirm that:

```text
canonical UUID remains stable
new ExternalReference resolves
old ExternalReference remains historical
new CapabilityBinding routes correctly
historical events remain traceable
old instance cannot receive new writes after cutover
```

---

# 110. Failure modes

The resolver SHALL explicitly recognise:

```text
MAPPING_NOT_FOUND
MAPPING_AMBIGUOUS
MAPPING_EXPIRED
MAPPING_SUSPENDED
ENGINE_INSTANCE_UNAVAILABLE
CAPABILITY_NOT_BOUND
ISOLATION_POLICY_VIOLATION
CLIENT_CONTEXT_MISMATCH
ORG_CONTEXT_MISMATCH
```

These SHALL become stable platform error contracts.

---

# 111. Observability

Mapping resolution SHALL expose metrics such as:

```text
erp_mapping_resolution_total
erp_mapping_resolution_failure_total
erp_mapping_ambiguous_total
erp_context_mismatch_total
erp_cross_tenant_denied_total
erp_engine_binding_failure_total
```

No sensitive native identifiers should be unnecessarily exposed as high-cardinality metric labels.

---

# 112. Audit

Mapping changes SHALL be audit events.

Examples:

```text
mapping.created
mapping.activated
mapping.superseded
mapping.suspended
mapping.retired

capability-binding.activated
capability-binding.reassigned

engine-instance.migration.started
engine-instance.migration.completed
```

The audit record SHALL identify who or what authorized the change.

---

# 113. Control Plane responsibility

`baobab-cp` SHALL own:

```text
canonical identities
mapping records
mapping scopes
engine instances
isolation profiles
capability bindings
context resolution
mapping lifecycle
routing decisions
```

---

# 114. ERP Engine responsibility

`baobab-erp` SHALL own:

```text
native AD_Client
native AD_Org
native ERP configuration
native roles
native transactional data
validation that resolved native context is respected
```

It SHALL consume resolved context.

It SHALL not redefine the canonical model.

---

# 115. Shared repository responsibility

`nabhold/shared` SHALL own machine-readable contracts such as:

```text
canonical entity schemas
context schema
mapping schema
event schemas
error contracts
identifier formats
enumerations
API conventions
```

The source-of-truth principle established previously remains: canonical organisation standards belong in shared contracts rather than being duplicated inside individual engines.

---

# 116. ERP repository SHALL not duplicate canonical truth

It MAY cache mappings where required for performance or resilience.

Such cache is:

```text
derived
```

not:

```text
authoritative
```

Control Plane remains the mapping authority.

---

# 117. Resolver caching

Mapping results MAY be cached if:

- cache keys include Context-relevant scope;
- expiry is bounded;
- mapping updates invalidate appropriately;
- stale entries cannot bypass suspension or isolation changes.

Security-sensitive changes SHOULD invalidate immediately.

---

# 118. Control Plane outage

ERP operations SHALL have an explicit policy for Control Plane unavailability.

Possible future pattern:

```text
validated signed Context token
        +
bounded mapping cache
```

may permit limited continued operation.

However, stale state SHALL never permit a tenant to gain broader access than its last validated policy.

Fail-safe semantics are mandatory.

---

# 119. Signed Context

Future Context tokens MAY carry immutable resolved claims such as:

```text
tenant
legal_entity
market
engine_instance
capability
expiry
```

but the token SHALL be cryptographically verifiable and short lived.

Raw caller headers SHALL not become trustworthy Context merely because they use canonical names.

---

# 120. Rejected alternative — Tenant equals Client universally

**Rejected.**

A Baobab Tenant may contain several legal entities, may use multiple regional ERP instances or may migrate over time.

---

# 121. Rejected alternative — LegalEntity equals Organization universally

**Rejected.**

Some legal entities require full iDempiere Client isolation.

iDempiere Organizations can share data within their Client.

---

# 122. Rejected alternative — Every Organisation becomes AD_Org

**Rejected.**

It would replicate the company organogram into ERP irrespective of ERP relevance and create unnecessary complexity.

---

# 123. Rejected alternative — Every Market becomes AD_Org

**Rejected.**

Market and ERP organisational structures answer different architectural questions.

---

# 124. Rejected alternative — EngineInstance equals Tenant

**Rejected.**

One EngineInstance may host multiple isolated Clients.

One Tenant may also move across or deliberately use multiple EngineInstances.

---

# 125. Rejected alternative — Native IDs embedded in canonical entities

**Rejected.**

This would prevent transparent engine migration and introduce collisions between instances.

---

# 126. Rejected alternative — Mapping stored only in iDempiere

**Rejected.**

That would allow the engine being mapped to become the authority for the platform relationship.

The canonical mapping belongs to the Control Plane.

---

# 127. Rejected alternative — Mapping stored only in Medusa/Payload integrations

**Rejected.**

Each engine would develop its own inconsistent translation table.

Canonical mapping is an organisation-wide platform concern.

---

# 128. Rejected alternative — Shared AD_Client for all Nabhold companies by default

**Rejected.**

It weakens independent legal-entity isolation and makes future divestiture or dedicated-instance migration more difficult.

---

# 129. Rejected alternative — Dedicated iDempiere installation for every entity from day one

**Rejected as mandatory policy.**

It imposes significant operational duplication without always adding material protection over dedicated `AD_Client` boundaries in a properly secured shared instance.

The IsolationProfile determines when dedicated infrastructure is justified.

---

# 130. Non-negotiable invariants

```text
INV-ERP-MAP-001
A Baobab Tenant is never globally defined as an AD_Client.

INV-ERP-MAP-002
A LegalEntity is never globally defined as an AD_Org.

INV-ERP-MAP-003
A Market is never globally defined as an AD_Org.

INV-ERP-MAP-004
An infrastructure Region never defines an AD_Org.

INV-ERP-MAP-005
All native ERP identity is scoped by EngineInstance.

INV-ERP-MAP-006
Canonical UUIDs remain stable across ERP migrations.

INV-ERP-MAP-007
Mappings are temporal.

INV-ERP-MAP-008
Historical financial mappings are retained.

INV-ERP-MAP-009
Caller-supplied AD_Client_ID cannot override resolved Context.

INV-ERP-MAP-010
Caller-supplied AD_Org_ID cannot bypass authorised context.

INV-ERP-MAP-011
Missing mappings fail closed.

INV-ERP-MAP-012
Ambiguous authoritative mappings fail closed.

INV-ERP-MAP-013
Hard-isolated Baobab tenants cannot be represented merely by different AD_Org values in one Client.

INV-ERP-MAP-014
Control Plane owns canonical mapping authority.

INV-ERP-MAP-015
iDempiere owns the native client and organisation records.

INV-ERP-MAP-016
No ordinary business transaction creates a canonical/native mapping opportunistically.

INV-ERP-MAP-017
System Client is never mapped to an ordinary Baobab tenant.

INV-ERP-MAP-018
Organization * means iDempiere Client-level sharing, not Baobab-global sharing.

INV-ERP-MAP-019
Canonical organisational hierarchy and ERP organisational hierarchy may differ.

INV-ERP-MAP-020
IsolationProfile overrides convenient but unsafe mappings.
```

---

# 131. Default Nabhold implementation policy

Until explicitly superseded, the initial Baobab ERP topology SHALL therefore assume:

```text
                        BAOBAB

                           │
                   ERP Engine capability
                           │
                           ▼
                  ERP-AF-SOUTH-01
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   AD_Client          AD_Client        AD_Client
     NABHOLD            THAMANI          ZURIBEANS
          │                │                │
          ▼                ▼                ▼
      AD_Org(s)        AD_Org(s)        AD_Org(s)
     as required      as required      as required
```

Each client remains isolated from the others.

Future scale or regulatory requirements may promote one of them to:

```text
dedicated EngineInstance
```

without changing its Baobab canonical identity.

---

# 132. Illustrative future promotion

Initial:

```text
ERP-AF-SOUTH-01
│
├── NABHOLD
├── THAMANI
└── ZURIBEANS
```

Later:

```text
ERP-AF-SOUTH-01
│
├── NABHOLD
└── THAMANI


ERP-ZURIBEANS-AF-01
│
└── ZURIBEANS
```

The canonical model remains:

```text
Tenant Zuribeans
LegalEntity Zuribeans
```

unchanged.

Only:

```text
CapabilityBinding
Mapping
ExternalReference
EngineInstance
```

change.

That is exactly the decoupling this ADR is intended to guarantee.

---

# 133. Acceptance criteria

ADR-ERP-002 SHALL be considered implemented when:

- [ ] Canonical Tenant IDs are independent of `AD_Client_ID`.
- [ ] Canonical LegalEntity IDs are independent of `AD_Org_ID`.
- [ ] ExternalReferences include EngineInstance identity.
- [ ] Mapping records support validity periods.
- [ ] Active mapping overlaps are constrained where mappings are single-valued.
- [ ] Mapping resolution supports canonical-to-native lookup.
- [ ] Reverse native-to-canonical resolution is supported for events.
- [ ] Missing mappings fail closed.
- [ ] Ambiguous mappings fail closed.
- [ ] The caller cannot inject arbitrary `AD_Client_ID`.
- [ ] The caller cannot use `AD_Org_ID` to cross authorised scope.
- [ ] System Client cannot be routed as a business tenant.
- [ ] `AD_Org = *` is never interpreted as globally shared Baobab data.
- [ ] Nabhold, Thamani and Zuribeans can occupy separate Clients in the same EngineInstance.
- [ ] A tenant can be migrated to another EngineInstance without changing canonical identity.
- [ ] Historical mappings remain queryable.
- [ ] Isolation tests cover at least two independent Clients.
- [ ] Organisation mapping requires an ERP-relevance rationale.
- [ ] Market mappings are not automatically converted into organizations.
- [ ] Mapping changes emit audit records.
- [ ] `baobab-cp` remains authoritative for canonical mappings.

---

# 134. Final decision statement

The definitive relationship between Baobab and iDempiere is therefore:

```text
            BAOBAB CANONICAL WORLD

Tenant
LegalEntity
Organisation
Market
DigitalEstate
Capability
Context
IsolationProfile
EngineInstance

                 │
                 │ explicit, scoped,
                 │ temporal mappings
                 ▼

              iDEMPIERE WORLD

AD_Client
AD_Org
AD_Role
C_BPartner
M_Product
Warehouse
Accounting Schema
Documents
Transactions
```

The bridge is deliberate.

It is never implicit.

The most important rule is:

> **Baobab describes the enterprise. iDempiere describes the ERP representation required to operate that enterprise.**

The two models cooperate, but neither is permitted to silently redefine the other.

This preserves tenant isolation today while retaining enough architectural freedom for independent legal entities, cross-border expansion, regional deployments, incorporation, acquisitions, divestitures, dedicated-instance promotion and eventual replacement of the ERP implementation itself.