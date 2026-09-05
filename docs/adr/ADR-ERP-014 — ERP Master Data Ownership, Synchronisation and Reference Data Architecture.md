# ADR-ERP-014 — ERP Master Data Ownership, Synchronisation and Reference Data Architecture

**Status:** Accepted  
**Decision class:** ERP / Master Data / Reference Data / Synchronisation / Domain Ownership / Interoperability  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/baobab-trade`, Payload CMS engine, Baobab Intelligence Engine, Digital Estates, `nabhold/shared`  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-013  
**Date:** 2026-09-02

---

# 1. Decision

Baobab SHALL use an explicit, domain-owned master-data architecture rather than creating one universal database or declaring iDempiere the master of every enterprise entity.

For every cross-engine data concept, the architecture SHALL distinguish:

```text
Canonical Identity
        │
        ▼
Domain Authority
        │
        ▼
Engine Representation
        │
        ▼
Synchronization / Projection
```

The governing principle is:

> **Canonical identity establishes what a business thing is; domain authority establishes which bounded context is permitted to define particular facts about it.**

Therefore:

```text
Canonical identity != master data ownership

Master data ownership != storage location

Engine representation != canonical authority

Synchronization != shared ownership
```

---

# 2. Problem

Baobab contains several independently deployable engines that need overlapping knowledge about business entities.

Examples include:

```text
Party
Product
Product Variant
Supplier
Customer
Warehouse
Location
Price
Inventory
Tax Classification
Payment Terms
Unit of Measure
Currency
Country
Sales Channel
Business Document
```

The same conceptual business entity may appear in:

```text
iDempiere
MedusaJS
Payload CMS
Control Plane
Digital Estates
Intelligence Engine
```

without all these systems having equal authority over it.

---

# 3. Architectural risk

Without explicit ownership rules, Baobab would eventually experience:

```text
conflicting updates
circular synchronization
event ping-pong
duplicate master records
native-ID coupling
silent overwrite
ambiguous source of truth
incorrect financial posting
cross-tenant leakage
```

---

# 4. No universal master system

Baobab SHALL NOT designate one application as the universal master-data system for the entire platform.

Specifically:

```text
iDempiere != universal master
MedusaJS != universal master
Payload CMS != universal master
Control Plane != universal master
```

Each owns only the domains explicitly assigned to it.

---

# 5. Domain authority

Every important attribute family SHALL have an identified authority.

Authority SHALL be based on business semantics, not which application happens to contain a field.

---

# 6. CanonicalEntity

ADR-ERP-007 remains authoritative for canonical identity.

A `CanonicalEntity` SHALL answer:

> What business entity are these representations referring to?

It SHALL NOT automatically contain the complete authoritative master record.

---

# 7. ExternalReference

Each engine representation SHALL continue to use `ExternalReference`.

Example:

```text
CanonicalEntity: Product P-UUID

├── iDempiere
│   └── M_Product 1000372
│
├── Medusa
│   └── product_variant variant_01...
│
└── Payload
    └── content document ...
```

These representations MAY contain different subsets of information.

---

# 8. Mapping

`Mapping` SHALL establish representational equivalence under explicit `MappingScope`.

It SHALL NOT imply identical domain ownership.

---

# 9. Three data categories

Baobab SHALL classify interoperable data into at least:

```text
Master Data
Reference Data
Transactional Data
```

---

# 10. Master data

Master data represents relatively persistent business entities.

Examples:

```text
Party
Product
Warehouse
Location
Employee
Account
```

depending on bounded-context semantics.

---

# 11. Reference data

Reference data defines controlled classifications, codes or shared interpretation.

Examples:

```text
Currency
Country
Unit of Measure
Tax Category
Payment Term Type
Incoterm
Language
```

---

# 12. Transactional data

Transactional data represents business events/process state.

Examples:

```text
Order
Invoice
Payment
Goods Receipt
Shipment
Journal Entry
```

Transactional data SHALL NOT be misclassified as master data merely because it is long-lived.

---

# 13. Authority dimensions

Authority SHALL be definable at:

```text
entity level
attribute-family level
Context level
Market level
LegalEntity level
```

where necessary.

---

# 14. Attribute ownership

Different attributes of the same conceptual entity MAY have different authorities.

Example:

```text
Product

canonical identity
    → Baobab canonical layer

ERP accounting classification
    → iDempiere

commerce merchandising
    → Medusa

editorial description/media
    → Payload CMS
```

---

# 15. No last-writer-wins across domains

Baobab SHALL NOT use generic:

```text
last write wins
```

synchronization between engines for authoritative business data.

---

# 16. Party model

`Party` SHALL represent a canonical person or organisation participating in business relationships.

A Party MAY act as:

```text
customer
supplier
carrier
employee
partner
legal entity
other business counterparty
```

depending on Context.

---

# 17. Party is not C_BPartner

An iDempiere `C_BPartner` SHALL be treated as an ERP representation of a Party where semantically appropriate.

```text
Canonical Party
      │
      ▼
ExternalReference
      │
      ▼
C_BPartner
```

---

# 18. Party roles

Supplier and Customer SHALL normally be roles or contextual classifications of Party rather than necessarily different canonical identities.

---

# 19. Party authority

ERP MAY be authoritative for:

```text
payment terms
credit controls
accounting-related business-partner settings
supplier accounting status
customer accounting status
```

where those concepts belong to ERP.

---

# 20. Commerce party authority

Medusa or another commerce identity/customer subsystem MAY be authoritative for:

```text
commerce customer account
buyer organisation membership
commerce channel-specific profile
commerce checkout preferences
```

---

# 21. Content authority

Payload CMS SHALL NOT become authoritative for financial Party attributes.

---

# 22. Contact information

Contact-data ownership SHALL be explicitly defined.

One engine SHALL NOT silently overwrite another engine's verified contact information without policy.

---

# 23. Legal identifiers

Identifiers such as:

```text
company registration number
tax registration number
VAT number
customs registration
```

SHALL be typed, jurisdiction-scoped and governed.

They SHALL NOT replace canonical UUID identity.

---

# 24. Duplicate Party detection

Duplicate detection MAY use:

```text
registration identifiers
tax identifiers
name
address
email
telephone
```

as evidence.

It SHALL NOT silently merge identities.

---

# 25. Party merge

Canonical Party merge SHALL follow ADR-ERP-007.

Merge SHALL preserve:

```text
historical canonical IDs
external mappings
audit
redirect/alias information
```

---

# 26. Product model

`Product` SHALL represent a canonical commercial/business item family where canonical identity is needed.

---

# 27. Product versus variant

Baobab SHALL distinguish:

```text
Product
Product Variant / SKU representation
```

where commerce semantics require it.

The exact canonicalization depth SHALL be intentional.

---

# 28. SKU

SKU SHALL NOT automatically be global canonical identity.

SKU uniqueness SHALL be explicitly scoped.

Possible scope:

```text
Tenant
LegalEntity
catalogue
Market
commerce channel
```

---

# 29. ERP product

iDempiere `M_Product` SHALL be an ERP-native representation.

ERP MAY own attributes such as:

```text
accounting category
costing method
inventory treatment
valuation configuration
procurement configuration
tax accounting classification
```

---

# 30. Commerce product

Medusa SHALL own commerce-specific representation such as:

```text
sellability
commerce variants
sales-channel availability
commerce pricing relationships
checkout-related attributes
```

subject to final Trade Engine ADRs.

---

# 31. CMS product content

Payload MAY own:

```text
marketing title
editorial description
rich content
campaign copy
media
SEO metadata
```

It SHALL NOT become the accounting Product authority.

---

# 32. Product synchronization

Product projections SHALL therefore be directional.

Example:

```text
Canonical Product Identity
          │
          ├─────────────┐
          ▼             ▼
     iDempiere       Medusa
 accounting state   commerce state
          │             │
          └──────┬──────┘
                 ▼
             Payload
          content enrichment
```

This diagram describes conceptual relationships, not universal event flow.

---

# 33. Product lifecycle

Creation of a Product representation in one system SHALL NOT automatically imply all engines require an immediate representation.

Representations SHALL be provisioned when required by capability.

---

# 34. Lazy representation

Baobab MAY create an engine representation only when a relevant capability requires it.

---

# 35. Pre-provisioning

Baobab MAY pre-provision representations when operationally useful.

Both SHALL use explicit idempotent workflows.

---

# 36. Warehouse

Warehouse identity SHALL be explicitly modelled where cross-engine identity is necessary.

---

# 37. Warehouse is not AD_Org

As established earlier:

```text
Warehouse != LegalEntity
Warehouse != AD_Org
Warehouse != Market
```

although relationships may exist.

---

# 38. ERP warehouse

iDempiere `M_Warehouse` SHALL normally be authoritative for ERP warehouse/inventory accounting configuration.

---

# 39. Commerce stock location

A Medusa stock location MAY correspond to an ERP warehouse or a different logistical representation.

Equivalence SHALL require explicit mapping.

---

# 40. Location

Baobab SHALL distinguish:

```text
physical location
postal address
warehouse
legal address
delivery address
billing address
Market
DeploymentRegion
```

---

# 41. Location identity

A location SHALL only receive canonical identity when cross-engine identity or governance requires it.

---

# 42. Inventory

Inventory quantity is NOT ordinary master data.

It is operational state.

---

# 43. Inventory authority

Baobab SHALL explicitly distinguish:

```text
ERP financial inventory
commerce availability
warehouse operational quantity
reservation state
```

---

# 44. ERP inventory

iDempiere SHALL own inventory state where it is authoritative for:

```text
stock accounting
inventory valuation
goods movements
warehouse financial consequence
```

---

# 45. Commerce availability

Medusa MAY own commerce reservations and computed sellable availability.

---

# 46. Availability is derived

`available_to_sell` MAY be derived from multiple facts.

It SHALL NOT automatically equal an ERP on-hand quantity.

---

# 47. Inventory synchronization

Inventory integration SHALL use explicit events/APIs rather than shared tables.

---

# 48. Inventory conflict

Conflicting inventory state SHALL trigger reconciliation rather than blind overwrite.

---

# 49. Price

Price SHALL NOT be treated as one universal scalar attribute of Product.

---

# 50. Price dimensions

Price MAY depend on:

```text
Market
currency
customer group
quantity
channel
contract
effective date
tax treatment
```

---

# 51. Commerce pricing

Medusa MAY own customer-facing commercial pricing.

---

# 52. ERP pricing

iDempiere MAY own:

```text
procurement price
accounting valuation
cost
price lists used by ERP processes
```

depending on configured business process.

---

# 53. Price synchronization

Price flows SHALL be defined capability by capability.

No universal bidirectional Price synchronization SHALL exist.

---

# 54. Cost

Cost SHALL remain ERP/accounting-owned where it affects:

```text
inventory valuation
COGS
landed cost
financial statements
```

---

# 55. Content

Product content SHALL normally remain Payload-owned.

ERP SHALL not become the rich-content management system.

---

# 56. Tax classification

Tax classification SHALL be authoritative in the domain responsible for legal accounting/tax consequences.

For ERP-controlled transactions, this normally means ERP/localisation configuration.

---

# 57. Commerce tax projection

Commerce MAY consume tax-relevant classifications or calculation outputs.

It SHALL not silently redefine ERP tax accounting.

---

# 58. Unit of Measure

UOM SHALL be governed reference data.

---

# 59. UOM identity

UOM codes SHALL have explicit semantics and conversion rules.

---

# 60. UOM conversion

Conversions SHALL distinguish:

```text
exact conversion
business conversion
packaging conversion
```

where relevant.

---

# 61. UOM ambiguity

Systems SHALL NOT infer that identically named units necessarily have identical semantics.

---

# 62. Currency

Currency SHALL be governed reference data.

---

# 63. Currency code

ISO-style currency code may be used as interoperable reference where appropriate.

Canonical platform semantics SHALL still preserve explicit reference authority.

---

# 64. Exchange rate

Exchange Rate is temporal business/reference data, not static Currency reference data.

ADR-ERP-008 remains authoritative.

---

# 65. Country

Country SHALL be reference data.

---

# 66. Country is not Market

```text
Country != Market
```

A Market MAY span or subdivide jurisdictional geography.

---

# 67. Language and locale

Language and locale SHALL remain distinct from Country and Market.

---

# 68. Payment terms

Payment Terms MAY be ERP-owned master/reference configuration where they govern receivables/payables.

---

# 69. Incoterms

Incoterms SHALL be governed reference data.

Contract-specific application remains transactional/business context.

---

# 70. Commodity/customs classifications

Commodity codes and customs classifications SHALL be jurisdiction/effective-date aware.

They SHALL not be canonical Product identity.

---

# 71. Reference-data authority

Every reference-data family SHALL have an identified authority.

---

# 72. Reference-data catalogue

Baobab SHOULD maintain a governed reference-data catalogue containing:

```text
reference type
namespace
code
meaning
authority
effective dates
status
```

where cross-engine standardisation requires it.

---

# 73. Shared repo boundary

`nabhold/shared` MAY define schemas/enumerations/contracts for organisation-wide reference data.

It SHALL NOT necessarily own the runtime business administration of every reference value.

---

# 74. Control Plane boundary

The Control Plane MAY own platform reference data such as:

```text
Engine type
Capability definition
Isolation classification
Market identity
Digital Estate identity
```

It SHALL NOT become ERP master-data administration.

---

# 75. ERP boundary

iDempiere SHALL own ERP-specific master/reference data required to execute ERP semantics.

---

# 76. Sync model

Baobab SHALL use explicit synchronization patterns rather than generic database replication.

Approved patterns include:

```text
API command
domain event
integration event
projection
scheduled reconciliation
controlled import
```

---

# 77. Direct database synchronization

Direct cross-engine database synchronization is prohibited.

---

# 78. CDC

CDC MAY support operational infrastructure or specialised internal projections.

Raw CDC SHALL NOT automatically become canonical master-data integration.

---

# 79. Directionality

Every synchronization flow SHALL have an explicit direction.

Example:

```text
ERP → Trade
```

does not imply:

```text
Trade → ERP
```

for the same attributes.

---

# 80. Ownership matrix

Every significant synchronized entity SHOULD have an ownership matrix.

Example:

| Entity / attribute | Authority | Consumer |
|---|---|---|
| Product canonical ID | Canonical layer | all |
| Product accounting class | ERP | ERP/authorised consumers |
| Product cost | ERP | authorised consumers |
| Commerce sellability | Trade | Digital Estates |
| Marketing copy | Payload | Digital Estates |
| Inventory valuation | ERP | Finance |
| Commerce reservation | Trade | Commerce |
| Tax accounting config | ERP | ERP integrations |

---

# 81. Authority matrix is normative

The ownership matrix SHALL form part of the interoperability contract.

---

# 82. Synchronization contract

A synchronization contract SHALL define at least:

```text
source authority
target
entity type
attributes
trigger
delivery mechanism
idempotency
ordering requirements
failure behaviour
reconciliation
```

---

# 83. Projection

A target MAY store a projection of authoritative data for:

```text
performance
availability
query convenience
local workflow
```

---

# 84. Projection is derivative

A projection SHALL NOT automatically gain authority because it persists data locally.

---

# 85. Projection metadata

Critical projections SHOULD retain:

```text
canonical_entity_id
source authority
source version/sequence where available
observed_at
```

---

# 86. Projection update

Projection updates SHALL be idempotent.

---

# 87. Projection deletion

When an authoritative entity is retired, consumer behaviour SHALL be defined.

Possible actions include:

```text
disable
archive
remove from discovery
retain historical reference
```

---

# 88. Hard delete

Financially referenced master data SHOULD normally not be hard-deleted.

---

# 89. Retirement

Master entities SHOULD support lifecycle states such as:

```text
active
suspended
retired
```

where appropriate.

---

# 90. Retirement is not identity deletion

A retired entity remains historically identifiable.

---

# 91. Referential history

Historical invoices SHALL continue to resolve their Party/Product references even if the master entity is now retired.

---

# 92. Effective dating

Reference/master data that changes legally or financially over time SHALL support effective dating where required.

---

# 93. Historical truth

New master/reference values SHALL not silently reinterpret historical financial documents.

---

# 94. Versioning

Important master-data projections MAY use a source version/sequence.

---

# 95. Version semantics

Source version SHALL represent domain state progression.

It SHALL remain distinct from:

```text
schema version
event version
application version
```

---

# 96. Out-of-order updates

Consumers SHALL define behaviour for out-of-order master-data updates.

---

# 97. Stale projection

A lower source version SHALL NOT overwrite a known higher version unless explicit replay semantics require it.

---

# 98. Event ordering

Where master-data state requires ordering, ordering SHOULD be entity-scoped rather than global.

---

# 99. Event schema

Master-data integration events SHALL follow ADR-ERP-006 event-contract rules.

---

# 100. Event minimalism

Events SHALL contain enough state to integrate safely without copying unrestricted master records.

---

# 101. Sensitive master data

Sensitive attributes SHALL be excluded from broad events.

Examples:

```text
banking details
personal identifiers
credit information
confidential commercial terms
```

---

# 102. Restricted attributes

Restricted attributes SHALL use narrow APIs/events and explicit authorization.

---

# 103. Supplier bank account

Supplier bank information SHALL receive particularly strong controls.

---

# 104. Bank-account authority

ERP MAY hold supplier payment details when required for payment processes.

Access SHALL follow ADR-ERP-010 security controls.

---

# 105. Bank changes

Changes to supplier bank details SHOULD be strongly audited and MAY require enhanced approval.

---

# 106. Credit limits

ERP SHALL normally own credit limits where they govern financial exposure.

Commerce MAY consume an approved projection/result.

---

# 107. Credit evaluation

Commerce SHALL not silently redefine ERP financial credit policy.

---

# 108. Supplier status

Supplier procurement/accounting eligibility SHOULD be ERP-owned where ERP governs procurement.

---

# 109. Vendor onboarding

Vendor onboarding MAY span multiple systems.

The workflow SHALL not imply shared authority.

Example:

```text
Onboarding workflow
       │
       ├── documents → Payload/records capability
       ├── compliance approval → governed service
       └── ERP supplier representation → iDempiere
```

---

# 110. Customer onboarding

Customer identity/account creation MAY originate in commerce.

ERP representation SHALL be provisioned when required by ERP capability.

---

# 111. No premature ERP record

Browsing or newsletter signup SHALL NOT automatically require `C_BPartner`.

---

# 112. B2B customers

For B2B commerce, customer organisations may require canonical Party identity and controlled ERP mapping.

---

# 113. Person versus organisation

Canonical Party SHALL distinguish person and organisation where required.

---

# 114. Buyer membership

A user's membership in a buyer organisation is not equivalent to Party identity.

---

# 115. User identity versus Party

```text
Authentication User != Party
```

although explicit relationships may exist.

---

# 116. Employee

An employee may be represented as:

```text
Human identity
Party/person
ERP employee/business partner
```

These identities SHALL not be collapsed blindly.

---

# 117. Organisational master data

LegalEntity and organisational structure SHALL remain canonical platform concepts according to the wider Baobab organisation/tenancy architecture.

---

# 118. ERP organisation representation

`AD_Org` SHALL remain the ERP representation required for ERP processes.

It SHALL not become canonical organisation identity.

---

# 119. Organisation synchronization

Changes to canonical organisational structure SHALL be provisioned into ERP only where ERP semantics require corresponding organisation changes.

---

# 120. Organisational rename

A LegalEntity rename SHALL not create a new canonical identity.

---

# 121. Incorporation/restructure

A genuinely new legal entity MAY require a new canonical entity and potentially a new ERP representation.

Business/legal semantics determine identity continuity.

---

# 122. Tenant movement

Moving an organisation between Tenant boundaries SHALL not silently mutate master-data identity.

---

# 123. MappingScope

Master-data resolution SHALL use `MappingScope`.

This is essential where the same canonical entity has multiple engine representations.

---

# 124. Market-specific representation

A Product MAY have multiple representations across Markets where implementation requires it.

Canonical identity may remain shared where semantically appropriate.

---

# 125. Market-specific attributes

Market-specific attributes SHALL not automatically overwrite global attributes.

---

# 126. Scope precedence

Where mappings/projections are scoped:

```text
Tenant
LegalEntity
Market
DigitalEstate
EngineInstance
```

resolution SHALL follow the explicit specificity rules established by the mapping architecture.

---

# 127. Ambiguity

Ambiguous master-data mapping SHALL fail closed.

---

# 128. Runtime fuzzy matching prohibited

Production business execution SHALL NOT use fuzzy matching to choose authoritative master records.

---

# 129. Fuzzy matching use

Fuzzy matching MAY generate candidates for human reconciliation.

---

# 130. Master-data creation flow

Cross-engine entity creation SHOULD be explicit.

Example:

```text
Need ERP Product
      │
      ▼
Resolve Canonical Product
      │
      ├── exists
      │      │
      │      ▼
      │   resolve ERP mapping
      │
      └── missing
             │
             ▼
       canonical creation process
             │
             ▼
        ERP provisioning
```

Exact creation authority depends on domain.

---

# 131. Idempotent provisioning

Provisioning SHALL be idempotent.

---

# 132. Duplicate prevention

Concurrent representation creation SHALL use constraints/idempotency mechanisms to prevent duplicates.

---

# 133. Native natural key

A native unique key MAY participate in duplicate detection.

It SHALL not replace canonical mapping.

---

# 134. Bulk imports

Bulk master-data imports SHALL use controlled ingestion.

---

# 135. Import Context

Every import SHALL be scoped to:

```text
Tenant
LegalEntity where applicable
authority
entity type
```

---

# 136. Import validation

Imports SHALL validate:

```text
schema
required references
duplicate keys
currency/UOM
authorization
mapping conflicts
```

---

# 137. Import dry run

High-risk master-data imports SHOULD support validation/dry-run before mutation.

---

# 138. Import audit

Material imports SHALL be auditable.

---

# 139. Import source

Imported data SHALL retain provenance where relevant.

---

# 140. Import is not authority transfer

Importing data from a spreadsheet does not make that spreadsheet the continuing authority.

---

# 141. Data quality

Baobab SHOULD define data-quality rules for critical master entities.

---

# 142. Data-quality dimensions

Possible dimensions:

```text
completeness
uniqueness
validity
consistency
timeliness
referential integrity
```

---

# 143. Data-quality failure

A data-quality failure SHALL be distinguished from infrastructure failure.

---

# 144. Blocking quality rules

Some quality failures SHALL block transactions.

Example:

```text
supplier missing required tax registration
```

where legally required.

---

# 145. Non-blocking quality rules

Other quality issues MAY create warnings/reconciliation tasks.

---

# 146. Master-data reconciliation

Critical master data SHALL be reconcilable.

---

# 147. Reconciliation examples

```text
Canonical Party ↔ C_BPartner

Canonical Product ↔ M_Product

ERP Warehouse ↔ approved stock-location mapping

Currency reference ↔ native ERP currency
```

---

# 148. Reconciliation detects

At minimum:

```text
missing representation
missing mapping
duplicate active mapping
orphaned mapping
wrong Tenant
wrong EngineInstance
wrong native entity type
unexpected authoritative divergence
```

---

# 149. Reconciliation does not automatically repair

As established in ADR-ERP-011, repair depends on known authority.

---

# 150. Master-data conflicts

A conflict SHALL be classified.

Suggested classes:

```text
mapping conflict
ownership conflict
stale projection
invalid reference
duplicate entity
attribute divergence
```

---

# 151. Conflict resolution

Resolution SHALL identify:

```text
authority
correct value
affected representations
historical impact
required corrective action
```

---

# 152. Ownership conflict

If two engines both claim authority for the same attribute, this is an architecture defect.

It SHALL NOT be solved by timestamp comparison.

---

# 153. Synchronization loop prevention

A projected update SHALL carry enough provenance to prevent:

```text
ERP
 ↓
Trade
 ↓
ERP
 ↓
Trade
```

ping-pong.

---

# 154. Event provenance

Integration messages SHOULD identify authoritative source/domain.

---

# 155. Consumer-generated event

A consumer updating its projection SHALL NOT republish that change as if it were a new authoritative business fact.

---

# 156. Canonical event ownership

Only the domain authority SHALL publish canonical authoritative events for the attributes it owns.

---

# 157. Change notification

A projection owner MAY publish technical projection-state events where operationally needed.

These SHALL not masquerade as authoritative domain changes.

---

# 158. Sync latency

Synchronization requirements SHALL define acceptable latency.

---

# 159. Strong consistency

Cross-engine strong consistency SHALL only be required where business semantics truly demand synchronous validation.

---

# 160. Eventual consistency

Most projections SHALL tolerate bounded eventual consistency.

---

# 161. Synchronous validation

An operation MAY synchronously query the authority when stale projection risk is unacceptable.

---

# 162. Cache

Caching authoritative master data SHALL follow the same projection rules.

---

# 163. Cache invalidation

Relevant authority events SHOULD invalidate/update caches.

---

# 164. Security revocation exception

Security-critical revocation SHALL not rely solely on eventual master-data propagation.

ADR-ERP-010 remains authoritative.

---

# 165. Degraded authority

When a master-data authority is unavailable, consuming services SHALL follow explicit degradation policy.

---

# 166. No blind fallback authority

A consumer SHALL NOT promote its stale projection to authority merely because the source is unavailable.

---

# 167. Read from cache

Stale read MAY be permitted where:

```text
risk acceptable
age known
operation read-only
```

---

# 168. Financial writes

Financially sensitive writes SHOULD fail/defer if required master authority cannot be reliably established.

---

# 169. Synchronization outage

A synchronization outage SHALL create observable backlog/error state.

---

# 170. Recovery

After synchronization recovery:

```text
resume events
       │
       ▼
process backlog
       │
       ▼
reconcile
```

---

# 171. Migration

During ERP migration, canonical identity SHALL remain stable.

---

# 172. Native representation migration

An old `ExternalReference` MAY be superseded by a new ERP representation.

---

# 173. Projection migration

Consumers SHALL not require canonical identity changes simply because the ERP representation changes.

---

# 174. ERP replacement

Future replacement of iDempiere SHALL preserve canonical master identity.

This ADR intentionally prevents platform master data from becoming locked to iDempiere identifiers.

---

# 175. Multi-ERP possibility

Baobab MAY eventually operate multiple ERP engine types or versions.

Canonical identity and authority contracts SHALL remain valid.

---

# 176. Data export

Master-data export SHALL clearly identify:

```text
canonical identifiers
authority
as-of timestamp
Context
```

where appropriate.

---

# 177. Analytics

Analytics MAY combine master data from multiple engines.

---

# 178. Analytics authority

An analytical warehouse/lake SHALL NOT become transactional master authority merely because it has the most complete joined dataset.

---

# 179. Intelligence Engine

The Intelligence Engine MAY enrich or infer attributes.

---

# 180. AI-derived attributes

AI-generated enrichment SHALL be marked as:

```text
derived
inferred
confidence-bearing
```

and SHALL NOT silently replace authoritative ERP/master data.

---

# 181. AI correction

AI MAY propose master-data corrections.

Changes SHALL pass through ordinary governed domain APIs/workflows.

---

# 182. AI entity matching

AI MAY assist duplicate detection/entity resolution.

It SHALL produce candidates rather than silently merging canonical identities.

---

# 183. Provenance

Derived/enriched attributes SHOULD retain provenance.

---

# 184. Privacy

Master-data synchronization SHALL minimise personal data distribution.

---

# 185. Need-to-know

An engine SHALL not receive every Party attribute merely because it references the same Party.

---

# 186. Data classification

Synchronization contracts SHALL consider classification such as:

```text
public
internal
confidential
restricted
```

according to the wider Baobab information-classification model.

---

# 187. Residency

Master-data copies SHALL obey `ResidencyPolicy`.

---

# 188. Cross-region projection

Creating a projection in another region is data replication and SHALL be policy-governed.

---

# 189. Deletion/privacy requests

Privacy deletion/correction SHALL account for:

```text
canonical identity
authoritative source
projections
audit
legal retention
financial records
```

---

# 190. Financial retention

Financial/legal retention MAY override ordinary erasure of certain transaction-linked attributes.

---

# 191. Pseudonymisation

Where legally appropriate, historical records MAY use pseudonymisation rather than destroying required financial evidence.

---

# 192. Master-data API

Master-data APIs SHALL be domain-oriented.

---

# 193. Native CRUD rejection

Baobab SHALL NOT expose generic:

```text
POST /M_Product
POST /C_BPartner
```

as canonical platform APIs.

---

# 194. Canonical endpoint examples

Possible ERP capability endpoints:

```text
/erp/v1/business-partners
/erp/v1/products
/erp/v1/warehouses
```

where those APIs are appropriate.

---

# 195. Command semantics

Creation/update APIs SHALL express domain intent.

---

# 196. Patch restrictions

Generic arbitrary PATCH SHALL be avoided for financially sensitive master-data fields.

---

# 197. Field authorization

Different attributes MAY require different authorization.

Example:

```text
supplier display name
```

and:

```text
supplier bank details
```

SHALL not automatically share the same privilege.

---

# 198. Optimistic concurrency

Master-data mutation SHOULD support optimistic concurrency where concurrent updates matter.

---

# 199. Change reason

Sensitive master-data changes MAY require change reason/audit evidence.

---

# 200. Approval

High-risk changes MAY require approval workflows.

Examples:

```text
bank account
credit limit
tax registration
financial account mapping
```

---

# 201. Master-data event families

Potential canonical events include:

```text
party.created.v1
party.updated.v1
party.retired.v1

product.created.v1
product.updated.v1
product.retired.v1

warehouse.activated.v1
warehouse.retired.v1
```

Only where canonical/domain ownership justifies them.

---

# 202. ERP representation events

ERP MAY emit more specifically:

```text
erp.business-partner.activated.v1
erp.product.accounting-configured.v1
```

where these are ERP-owned facts.

---

# 203. Avoid over-eventing

Every changed descriptive field does not require a globally published event.

---

# 204. Change sets

Events MAY identify changed attribute groups instead of shipping the entire entity.

---

# 205. Master-data contract schema

Cross-engine master-data schemas SHALL live in `nabhold/shared` where they are organisation-wide contracts.

---

# 206. ERP-native models remain private

`M_Product`, `C_BPartner`, etc. SHALL not become shared canonical schemas.

---

# 207. Contract evolution

Master-data contract changes SHALL follow compatibility/versioning rules.

---

# 208. Consumer tolerance

Consumers SHOULD ignore additive fields they do not understand when contract rules allow.

---

# 209. Required-field change

Making a previously optional field mandatory across repositories may be a breaking contract change.

---

# 210. Deployment independence

Master-data contract evolution SHALL preserve independent repository deployment where practical.

---

# 211. No synchronous fan-out creation

Creating a canonical Product SHALL not require a distributed transaction that synchronously creates representations in every engine.

---

# 212. Provisioning workflow

Representation provisioning MAY be asynchronous.

---

# 213. Provisioning status

Where required, provisioning SHALL expose statuses such as:

```text
pending
provisioning
active
failed
retired
```

---

# 214. Provisioning failure

Failure in one engine SHALL not delete canonical identity established elsewhere.

---

# 215. Retry

Provisioning retries SHALL be idempotent.

---

# 216. Partial representation

Baobab SHALL tolerate a canonical entity having representations in only the engines required by its active capabilities.

---

# 217. Completeness is contextual

A Party does not need a Payload, Medusa and ERP representation merely to be considered valid.

---

# 218. Digital Estate

Digital Estates SHOULD consume master data through approved engine APIs/projections.

They SHALL not become authoritative merely because they provide an editing UI.

---

# 219. Editing UI

If a Digital Estate offers a master-data administration interface, commands SHALL route to the actual domain authority.

---

# 220. Control Plane administration

Control Plane UI/API SHALL administer canonical platform metadata.

It SHALL not become a generic ERP Product/Supplier editor.

---

# 221. Multi-market business partner

The same Party MAY operate in multiple Markets.

Market participation SHALL not automatically create distinct canonical Party identities.

---

# 222. Market-specific tax representation

The same Party MAY have jurisdiction-specific registrations.

These SHALL be contextual attributes/related records.

---

# 223. Multi-legal-entity supplier

A supplier may transact with several independent Nabhold LegalEntities.

Each LegalEntity MAY require an ERP `C_BPartner` representation in its own Client.

---

# 224. Representation plurality

Therefore:

```text
1 Canonical Party
       │
       ├── ERP Client A → C_BPartner A
       ├── ERP Client B → C_BPartner B
       └── Trade → Supplier representation
```

can be correct.

---

# 225. No cross-client native sharing

The existence of one canonical Party SHALL not justify cross-client native database references.

---

# 226. Product plurality

Similarly:

```text
1 Canonical Product

→ ERP representation for LegalEntity A
→ ERP representation for LegalEntity B
→ Trade representation
→ CMS content representation
```

may coexist.

---

# 227. Independent commercial configuration

Each representation MAY legitimately have different:

```text
price
tax
cost
availability
description
status
```

according to domain/Context.

---

# 228. Same identity does not mean same state

This is a fundamental invariant:

> **Two representations may refer to the same canonical entity without having identical data.**

---

# 229. Same state does not prove same identity

Conversely, two records with matching names/SKUs do not automatically represent the same canonical entity.

---

# 230. Data stewardship

Critical master-data domains SHOULD have an identified business steward.

---

# 231. Steward

A steward is responsible for:

```text
definition
quality
ownership clarification
conflict resolution
governance
```

not necessarily technical storage.

---

# 232. Technical owner

Each authoritative service SHALL have a technical owner.

---

# 233. Steward versus owner

Business stewardship and technical ownership SHALL be distinguished.

---

# 234. Master-data governance registry

Baobab SHOULD maintain a registry documenting:

```text
entity
attribute group
authority
steward
technical owner
consumers
synchronization mechanism
classification
```

---

# 235. Architecture review

Introducing a new cross-engine master-data domain SHALL require ownership determination before integration.

---

# 236. No owner, no synchronization

If no authority can be identified, the architecture is incomplete.

Synchronization SHALL not proceed by arbitrarily choosing a source.

---

# 237. Initial authority matrix

The initial ERP-related authority position SHALL be:

| Domain | Primary authority |
|---|---|
| Canonical identity | Baobab canonical layer / Control Plane governance |
| Tenant / Context | Control Plane |
| LegalEntity canonical identity | Canonical organisation model |
| ERP business partner accounting attributes | iDempiere |
| ERP Product accounting/cost configuration | iDempiere |
| ERP warehouse/accounting inventory | iDempiere |
| Financial inventory valuation | iDempiere |
| Commerce reservations | Medusa |
| Commerce sellability | Medusa |
| Customer-facing commerce pricing | Medusa, unless capability contract says otherwise |
| Accounting cost | iDempiere |
| Accounting/tax configuration | iDempiere |
| Rich editorial content | Payload CMS |
| Engine topology | Control Plane |
| Mapping metadata | Control Plane |

This matrix SHALL evolve only through explicit architecture decisions.

---

# 238. Initial implementation slice

The first production-grade implementation SHOULD prove master-data architecture using:

```text
Party
Product
Warehouse
Currency
UnitOfMeasure
```

before broadening to additional domains.

---

# 239. Party implementation proof

The Party slice SHALL demonstrate:

```text
Canonical Party
      │
      ▼
ExternalReference
      │
      ▼
Mapping
      │
      ▼
ERP C_BPartner
```

including:

```text
creation
resolution
update
retirement
reconciliation
```

---

# 240. Product implementation proof

Product SHALL demonstrate at least:

```text
Canonical Product
     │
     ├── ERP M_Product
     │
     └── Trade representation
```

with explicit attribute ownership.

---

# 241. Warehouse proof

Warehouse SHALL demonstrate that:

```text
ERP Warehouse
```

is not automatically:

```text
Market
AD_Org
LegalEntity
```

---

# 242. Failure example

Suppose Medusa changes:

```text
product title
```

and ERP changes:

```text
costing method
```

Both changes may be valid because they belong to different authority domains.

No conflict exists.

---

# 243. Real ownership conflict example

Suppose both Medusa and ERP attempt to authoritatively modify:

```text
financial inventory valuation
```

That is not a synchronization conflict.

It is an architecture ownership defect.

---

# 244. Duplicate supplier example

Suppose:

```text
ERP Client A:
    C_BPartner 1001 = ACME Coffee Ltd

ERP Client B:
    C_BPartner 7754 = ACME Coffee Ltd
```

These MAY legitimately map to:

```text
one Canonical Party UUID
```

because native ERP Client representations are independently scoped.

---

# 245. Duplicate detection example

If two records appear within the same Client:

```text
ACME Coffee Ltd
ACME COFFEE LIMITED
```

Baobab MAY flag them as candidate duplicates.

It SHALL NOT merge them without governed resolution.

---

# 246. Product migration example

Suppose ERP migrates from:

```text
EngineInstance A
```

to:

```text
EngineInstance B
```

and `M_Product` IDs change.

Baobab SHALL preserve:

```text
Canonical Product UUID
```

and supersede the external representation mapping.

---

# 247. Reference-data synchronization

Stable reference-data synchronization SHOULD favour:

```text
versioned seed
governed API
reference-data event
```

according to volatility.

---

# 248. Static-looking reference data

Even apparently stable values such as:

```text
currency
country
tax code
```

SHALL not be assumed eternally immutable.

Effective-date/version requirements may apply.

---

# 249. Local extension

Jurisdiction-specific reference data MAY extend common reference data without polluting global enums.

---

# 250. Hard-coded country logic

Business code SHALL NOT contain widespread constructs like:

```text
if country == "ZA":
...
elif country == "UG":
...
```

where policy/configuration/reference data should determine behaviour.

---

# 251. Validation location

Validation belonging to a domain SHALL execute at its authority boundary.

---

# 252. Duplicate validation layers

Consumers MAY perform early validation for UX.

The authoritative service SHALL still validate before mutation.

---

# 253. Master-data command flow

```text
Consumer
    │
    ▼
Authenticated Context
    │
    ▼
Domain API
    │
    ▼
Authority Validation
    │
    ▼
Canonical Mapping
    │
    ▼
Native Mutation
    │
    ▼
Local Transaction
    │
    ▼
Outbox
    │
    ▼
Canonical/Integration Event
    │
    ▼
Projections
    │
    ▼
Reconciliation
```

---

# 254. Read flow

```text
Consumer
    │
    ├── authoritative read required
    │          │
    │          ▼
    │      domain authority
    │
    └── projection acceptable
               │
               ▼
          local projection
```

The API contract SHALL establish which semantics apply.

---

# 255. Master-data invariants

```text
INV-ERP-MD-001
No engine is the universal master for all Baobab data.

INV-ERP-MD-002
Canonical identity and domain authority are separate concepts.

INV-ERP-MD-003
ExternalReference represents an engine-native identity.

INV-ERP-MD-004
Mapping does not imply identical attribute ownership.

INV-ERP-MD-005
Authority is determined by domain semantics, not field location.

INV-ERP-MD-006
Cross-engine last-writer-wins is prohibited for authoritative data.

INV-ERP-MD-007
Party is not equivalent to C_BPartner.

INV-ERP-MD-008
Product is not equivalent to M_Product.

INV-ERP-MD-009
Warehouse is not equivalent to AD_Org.

INV-ERP-MD-010
SKU is not inherently global canonical identity.

INV-ERP-MD-011
Inventory quantity is operational state, not ordinary master data.

INV-ERP-MD-012
Commerce availability is not automatically ERP on-hand inventory.

INV-ERP-MD-013
Financial inventory valuation remains ERP/accounting-owned.

INV-ERP-MD-014
Price is Context-sensitive and not one universal Product attribute.

INV-ERP-MD-015
Cost remains ERP/accounting-owned when financially material.

INV-ERP-MD-016
Rich editorial content is not ERP master authority.

INV-ERP-MD-017
Reference data has explicit authority.

INV-ERP-MD-018
Country is not Market.

INV-ERP-MD-019
Language is not Market.

INV-ERP-MD-020
Cross-engine database synchronization is prohibited.

INV-ERP-MD-021
Every synchronization flow has explicit direction.

INV-ERP-MD-022
A projection does not become authoritative through persistence.

INV-ERP-MD-023
Master-data projections are idempotently updated.

INV-ERP-MD-024
Retirement does not erase historical identity.

INV-ERP-MD-025
Historical financial records remain resolvable after master retirement.

INV-ERP-MD-026
Effective-dated master/reference changes preserve history.

INV-ERP-MD-027
Consumers do not overwrite newer source versions with stale updates.

INV-ERP-MD-028
Sensitive attributes are not broadly propagated through events.

INV-ERP-MD-029
Bulk imports execute inside explicit Context.

INV-ERP-MD-030
Spreadsheet import does not confer continuing domain authority.

INV-ERP-MD-031
Critical master data is reconcilable.

INV-ERP-MD-032
Authority conflict is an architectural defect, not a timestamp conflict.

INV-ERP-MD-033
Projection changes do not create event ping-pong.

INV-ERP-MD-034
Only domain authorities emit authoritative domain changes.

INV-ERP-MD-035
A consumer never becomes authority merely because the source is unavailable.

INV-ERP-MD-036
ERP migration preserves canonical master identity.

INV-ERP-MD-037
Analytics stores are not transactional master authorities.

INV-ERP-MD-038
AI-derived attributes do not silently replace authoritative master data.

INV-ERP-MD-039
AI entity matching proposes candidates; it does not silently merge identities.

INV-ERP-MD-040
Master-data distribution obeys data classification and ResidencyPolicy.

INV-ERP-MD-041
Native ERP models are not organisation-wide canonical schemas.

INV-ERP-MD-042
Cross-engine entity creation does not require distributed ACID.

INV-ERP-MD-043
Representation provisioning is idempotent.

INV-ERP-MD-044
Canonical entities need only the representations required by active capabilities.

INV-ERP-MD-045
Editing UI ownership does not imply data ownership.

INV-ERP-MD-046
One canonical Party may have multiple Client-scoped ERP representations.

INV-ERP-MD-047
One canonical Product may have multiple Context-scoped representations.

INV-ERP-MD-048
Same canonical identity does not require identical representation state.

INV-ERP-MD-049
Matching native attributes do not prove canonical identity.

INV-ERP-MD-050
Every critical master-data domain has explicit authority.

INV-ERP-MD-051
Every critical master-data domain has business stewardship.

INV-ERP-MD-052
No owner means synchronization architecture is incomplete.

INV-ERP-MD-053
Master-data mutation remains subject to tenant authorization.

INV-ERP-MD-054
Native identifiers never substitute for canonical authorization.

INV-ERP-MD-055
Critical master-data changes are auditable.

INV-ERP-MD-056
Financial master-data changes may require separation of duties.

INV-ERP-MD-057
Recovery and migration preserve canonical identity.

INV-ERP-MD-058
Synchronization outages are observable and reconcilable.

INV-ERP-MD-059
Direct database repair is not normal master-data conflict resolution.

INV-ERP-MD-060
Domain authority must remain explicit throughout the entity lifecycle.
```

---

# 256. Definition of done

ADR-ERP-014 SHALL be considered implemented when:

- [ ] Canonical identity and domain authority are represented separately.
- [ ] A master-data authority registry exists.
- [ ] Attribute-level ownership can be documented.
- [ ] Party ownership is defined.
- [ ] Product ownership is defined.
- [ ] Warehouse ownership is defined.
- [ ] Inventory authority boundaries are defined.
- [ ] Price authority boundaries are defined.
- [ ] Cost authority is defined.
- [ ] Content authority is defined.
- [ ] Tax-classification authority is defined.
- [ ] Currency/UOM/reference-data authority is defined.
- [ ] Cross-engine synchronization contracts exist.
- [ ] Direct cross-engine DB synchronization is prohibited.
- [ ] Projections are explicitly marked derivative.
- [ ] Projection updates are idempotent.
- [ ] Master-data lifecycle includes retirement.
- [ ] Historical references remain resolvable.
- [ ] Effective-dated data preserves history.
- [ ] Version/out-of-order handling is defined.
- [ ] Sensitive attributes have restricted propagation.
- [ ] Bulk-import governance exists.
- [ ] Master-data quality rules exist.
- [ ] Master-data reconciliation exists.
- [ ] Mapping reconciliation exists.
- [ ] Conflict classifications exist.
- [ ] Event-loop prevention exists.
- [ ] Sync-latency expectations are defined.
- [ ] Authority-unavailable behaviour is defined.
- [ ] ERP migration preserves canonical identity.
- [ ] Analytics/AI remain derivative consumers.
- [ ] Privacy/residency apply to projections.
- [ ] Master-data APIs are domain-oriented.
- [ ] High-risk master-data changes support stronger approval.
- [ ] Critical authority events are defined.
- [ ] Master-data schemas live in the appropriate shared contracts.
- [ ] Provisioning is idempotent.
- [ ] Party/Product/Warehouse vertical slices are tested.
- [ ] Business stewardship is assigned.
- [ ] Technical ownership is assigned.

---

# 257. Final architectural position

Baobab SHALL reject this model:

```text
             "Master Data"

                 │
                 ▼

            ONE DATABASE
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      ERP      Trade     CMS
```

It SHALL instead implement:

```text
                  CANONICAL IDENTITY
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
        ERP DOMAIN   TRADE DOMAIN  CONTENT DOMAIN
            │            │            │
       authoritative authoritative authoritative
       ERP facts      commerce facts content facts
            │            │            │
            └────────────┼────────────┘
                         │
                         ▼
                  CONTRACTED EVENTS
                     / APIs
                         │
                         ▼
                    PROJECTIONS
                         │
                         ▼
                  RECONCILIATION
```

The decisive rule is:

> **A business entity may have one canonical identity, several engine representations, and several domain authorities over different parts of its state.**

And:

> **Synchronization propagates authoritative facts; it does not manufacture authority.**

This allows Baobab to remain genuinely polyglot and polyrepo while still behaving as one coherent enterprise platform.