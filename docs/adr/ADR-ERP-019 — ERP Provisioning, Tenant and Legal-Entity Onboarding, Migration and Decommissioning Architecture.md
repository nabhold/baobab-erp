# ADR-ERP-019 — ERP Provisioning, Tenant and Legal-Entity Onboarding, Migration and Decommissioning Architecture

**Status:** Accepted  
**Decision class:** ERP / Provisioning / Tenant Lifecycle / Legal Entity / Migration / Cutover / Decommissioning  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`, `nabhold/infrastructure`, `nabhold/baobab-dev`, integration engines and authorised operational tooling  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-018  
**Date:** 2026-09-02

---

# 1. Decision

Baobab SHALL manage ERP onboarding, provisioning, migration, suspension and decommissioning as **explicit, governed lifecycle processes** coordinated through canonical Control Plane state.

Provisioning an ERP consumer SHALL NOT be reduced to creating an iDempiere `AD_Client`.

The lifecycle SHALL coordinate:

```text
Canonical organisation/tenant identity
        │
        ▼
Business and regulatory readiness
        │
        ▼
IsolationProfile
        │
        ▼
EngineInstance selection/provisioning
        │
        ▼
iDempiere Client / Organization structure
        │
        ▼
Accounting and localisation configuration
        │
        ▼
CapabilityBinding
        │
        ▼
Canonical mappings
        │
        ▼
Master/reference data
        │
        ▼
Integration validation
        │
        ▼
Financial validation
        │
        ▼
Production activation
```

The governing rule is:

> **ERP onboarding is the controlled establishment of an authoritative ERP operating boundary for a defined business Context; it is not merely database initialization.**

---

# 2. Lifecycle objectives

The architecture SHALL ensure that every ERP-enabled organisation can answer:

```text
Who is consuming ERP?
Which LegalEntity owns the books?
Which Market is being served?
Which EngineInstance is authoritative?
Which IsolationProfile applies?
Which iDempiere Client represents the boundary?
Which ERP Organizations operate inside it?
Which accounting configuration applies?
Which localisation applies?
Which canonical mappings are valid?
Which capabilities are enabled?
When did authority begin?
When did authority end?
```

---

# 3. Lifecycle entities

The lifecycle SHALL coordinate existing canonical concepts:

```text
Tenant
LegalEntity
Market
DigitalEstate
Engine
EngineInstance
Capability
CapabilityBinding
Context
IsolationProfile
CanonicalEntity
ExternalReference
Mapping
MappingScope
```

No parallel ERP-specific tenancy ontology SHALL be invented.

---

# 4. Tenant remains distinct from LegalEntity

The foundational rule remains:

```text
Tenant != LegalEntity
```

A LegalEntity is the normal/default business isolation boundary in many Baobab deployments, but tenancy represents the governed consuming boundary.

---

# 5. ERP provisioning target

An ERP provisioning request SHALL target an explicit business Context rather than simply:

```text
company_name = "Thamani"
```

---

# 6. Provisioning request

Conceptually:

```text
ERPProvisioningRequest
{
    tenant_id
    legal_entity_ids
    markets
    requested_capabilities
    isolation_profile
    residency_policy
    target_environment
    localisation_requirements
    requested_effective_date
}
```

This is conceptual lifecycle metadata; it does not require adding a new canonical CP entity without updating the parent Control Plane contract.

---

# 7. Provisioning is asynchronous

ERP provisioning SHALL normally be modelled as a long-running operation.

---

# 8. Why asynchronous

Provisioning may involve:

```text
infrastructure
database
iDempiere initialization
Client creation
Organizations
accounting schema
chart of accounts
currencies
tax
localisation
roles
service identities
mappings
integration tests
financial tests
```

It SHALL not be represented as one synchronous HTTP transaction.

---

# 9. Provisioning operation

A management-plane API MAY expose:

```text
POST /erp-provisioning-operations
```

returning:

```text
202 Accepted
```

with an operation identifier.

---

# 10. Lifecycle states

A provisioning lifecycle SHOULD support states such as:

```text
requested
assessing
approved
provisioning
configuring
migrating
validating
ready
activating
active
suspended
draining
decommissioning
retired
failed
```

---

# 11. State transition control

Lifecycle transitions SHALL be explicit and auditable.

---

# 12. Failed is not deleted

A failed provisioning operation SHALL retain sufficient evidence for:

```text
diagnosis
retry
cleanup
audit
```

---

# 13. Idempotent provisioning

Provisioning operations SHALL be idempotent.

Retrying:

```text
Provision Thamani ERP
```

SHALL NOT accidentally create:

```text
AD_Client Thamani #1
AD_Client Thamani #2
AD_Client Thamani #3
```

---

# 14. Stable operation identity

Provisioning requests SHOULD use durable operation/idempotency identifiers.

---

# 15. Desired state

Provisioning SHOULD operate from explicit desired state rather than imperative undocumented administrator steps.

Conceptually:

```text
desired ERP topology
        │
        ▼
current topology
        │
        ▼
difference
        │
        ▼
controlled convergence
```

---

# 16. Provisioning responsibility

Provisioning responsibilities SHALL be distributed.

### Control Plane

Owns:

```text
canonical Context
EngineInstance metadata
CapabilityBinding
IsolationProfile
Mapping
lifecycle state
```

### Infrastructure

Owns:

```text
runtime
network
database infrastructure
storage
secrets integration
observability
backup infrastructure
```

### ERP Engine

Owns:

```text
iDempiere Client
Organizations
ERP roles
ERP configuration
accounting
localisation
ERP validation
```

### Shared

Owns:

```text
contracts
schemas
workflow conventions
compatibility standards
```

---

# 17. No Control Plane business provisioning logic

The Control Plane SHALL coordinate topology and canonical lifecycle metadata.

It SHALL NOT become a remote SQL installer for iDempiere.

---

# 18. Provisioning service boundary

Detailed ERP provisioning MAY reside in:

```text
baobab-erp provisioning tooling
```

or a future dedicated lifecycle/orchestration capability.

---

# 19. Infrastructure provisioning

Infrastructure provisioning SHALL remain separate from ERP business configuration.

---

# 20. Infrastructure first

Where a dedicated EngineInstance is required:

```text
IsolationProfile
      │
      ▼
Infrastructure Provisioning
      │
      ▼
Database
      │
      ▼
ERP Runtime
      │
      ▼
ERP Configuration
```

---

# 21. Shared EngineInstance

Where policy permits shared infrastructure:

```text
Existing EngineInstance
      │
      ▼
New dedicated AD_Client
      │
      ▼
ERP configuration
```

MAY be used.

---

# 22. Shared instance does not mean shared tenant

Infrastructure sharing SHALL NOT collapse Tenant boundaries.

---

# 23. EngineInstance selection

EngineInstance selection SHALL consider:

```text
IsolationProfile
ResidencyPolicy
capacity
supported ERP release
localisation compatibility
jurisdiction
availability tier
maintenance constraints
```

---

# 24. Capacity alone is insufficient

The least-loaded EngineInstance SHALL not automatically be selected if policy or localisation makes it unsuitable.

---

# 25. Version compatibility

The target EngineInstance SHALL run a release compatible with all required:

```text
localisations
extensions
contracts
database requirements
```

---

# 26. Isolation escalation

If requirements cannot safely coexist on a shared EngineInstance, provisioning SHALL escalate to stronger isolation.

---

# 27. Initial topology

An economical initial topology MAY continue to use:

```text
ERP-AF-SOUTH-01
    │
    ├── NABHOLD AD_Client
    ├── THAMANI AD_Client
    └── ZURIBEANS AD_Client
```

provided the applicable isolation, residency, regulatory and operational requirements permit it.

---

# 28. Topology is not permanent

This topology SHALL remain migratable.

---

# 29. LegalEntity onboarding

Every ERP-enabled LegalEntity SHALL have explicit financial ownership configuration.

---

# 30. LegalEntity prerequisites

Before activation, required attributes MAY include:

```text
legal name
registration identifiers
jurisdiction
tax registrations
functional currency
fiscal calendar
accounting requirements
banking configuration
reporting obligations
```

subject to business requirements.

---

# 31. Tenant onboarding versus LegalEntity onboarding

These SHALL remain separate lifecycle concerns.

Example:

```text
Tenant: THAMANI
      │
      ├── LegalEntity ZA
      └── future LegalEntity UG
```

does not imply one accounting book or one ERP Organization.

---

# 32. ERP Client mapping

Default architecture:

```text
Tenant / governed isolation boundary
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

subject to ADR-ERP-002.

---

# 33. ERP Organization mapping

`AD_Org` SHALL represent the required ERP organisational structure inside the applicable Client.

It SHALL NOT automatically mean:

```text
Tenant
LegalEntity
Market
DigitalEstate
```

---

# 34. Organisation design

ERP Organization design SHALL be derived from actual accounting/operational requirements.

---

# 35. No org explosion

Baobab SHALL NOT create one `AD_Org` for every:

```text
website
sales channel
Market
team
warehouse
campaign
```

without ERP semantic justification.

---

# 36. Accounting bootstrap

Before financial activation, the LegalEntity SHALL have an approved accounting baseline.

---

# 37. Accounting baseline

At minimum where applicable:

```text
AccountingSchema
ChartOfAccounts
FunctionalCurrency
FiscalCalendar
AccountingPeriods
CostingConfiguration
TaxConfiguration
DocumentSequences
```

---

# 38. Financial approval

Finance SHALL approve materially significant accounting configuration before production activation.

---

# 39. Configuration template

Reusable configuration templates MAY accelerate onboarding.

---

# 40. Template is not automatic truth

A template SHALL NOT be blindly applied to every LegalEntity.

---

# 41. Template provenance

Templates SHOULD identify:

```text
version
jurisdiction
intended use
owner
approval
effective period
```

---

# 42. Localisation bootstrap

Applicable localisation SHALL be selected under ADR-ERP-009.

---

# 43. Localisation validation

Provisioning SHALL confirm:

```text
jurisdiction
ERP version
localisation version
tax configuration
document requirements
regulatory adapters
```

are compatible.

---

# 44. Market activation

ERP provisioning SHALL NOT automatically activate every Market associated with a Tenant.

---

# 45. Capability-specific Market readiness

A Market becomes available for ERP capabilities only after its required readiness gates pass.

---

# 46. Security bootstrap

Provisioning SHALL create only required:

```text
service identities
roles
permissions
administrative access
```

under ADR-ERP-010.

---

# 47. No default shared superuser

A new tenant SHALL NOT receive a shared universal integration superuser.

---

# 48. Secret bootstrap

Secrets SHALL be created through approved secret-management infrastructure.

---

# 49. No secrets in provisioning payload history

Long-lived credentials SHALL not be persisted in ordinary lifecycle/audit payloads.

---

# 50. Service identity mapping

Each integrating workload SHALL receive explicit ERP capability authorization.

---

# 51. Initial master data

Onboarding MAY require initial:

```text
Party
Product
Warehouse
UOM
PaymentTerm
PriceList
TaxCategory
```

representations.

Authority follows ADR-ERP-014.

---

# 52. Initial data source

Every imported master dataset SHALL identify its source and authority.

---

# 53. Staging

Bulk migration/import SHALL first enter a controlled staging process where appropriate.

---

# 54. Staging is not production authority

Staged records SHALL not become operational ERP truth merely because import succeeded technically.

---

# 55. Data-import lifecycle

Conceptually:

```text
Source
  │
  ▼
Extract
  │
  ▼
Staging
  │
  ▼
Validate
  │
  ▼
Normalize
  │
  ▼
Canonical Identity Resolution
  │
  ▼
Mapping
  │
  ▼
ERP Import
  │
  ▼
Reconciliation
  │
  ▼
Approval
```

---

# 56. Data provenance

Imported records SHALL retain sufficient provenance to determine their origin.

---

# 57. Migration source

A migration source MAY be:

```text
legacy ERP
spreadsheet
accounting package
CRM
commerce engine
manual master-data repository
```

---

# 58. Legacy source is untrusted

Legacy data SHALL be validated rather than assumed correct.

---

# 59. Canonical identity before import

Where an entity already has a Baobab canonical identity, migration SHALL reuse it.

---

# 60. No duplicate canonical identity

Migration SHALL NOT create a new canonical Party/Product merely because a new ERP representation is created.

---

# 61. Missing canonical identity

Where required canonical identity does not exist, onboarding SHALL use the approved canonical-entity provisioning workflow.

---

# 62. ExternalReference creation

Native iDempiere identifiers SHALL be recorded as scoped `ExternalReference`s after successful provisioning.

---

# 63. Mapping creation

Mappings SHALL be:

```text
explicit
scoped
temporal
auditable
idempotent
```

---

# 64. Mapping activation

A mapping SHOULD not become authoritative until the corresponding native representation has been validated.

---

# 65. CapabilityBinding activation

CapabilityBinding SHALL not become active until the target ERP capability passes readiness checks.

---

# 66. Binding before mapping distinction

Recall:

```text
CapabilityBinding = WHERE capability is served

Mapping = WHICH native representation corresponds
```

Both are required.

---

# 67. Provisioning ordering

A typical sequence is:

```text
Context
   │
   ▼
Isolation Decision
   │
   ▼
EngineInstance
   │
   ▼
Native ERP Boundary
   │
   ▼
Configuration
   │
   ▼
Mappings
   │
   ▼
Validation
   │
   ▼
CapabilityBinding Activation
```

---

# 68. No early production routing

Production traffic SHALL NOT be routed merely because the ERP container is running.

---

# 69. Readiness gates

Production readiness SHALL include:

```text
technical
security
financial
integration
mapping
localisation
operational
recovery
```

validation.

---

# 70. Technical validation

Includes:

```text
runtime health
database health
required extensions
schema compatibility
configuration baseline
```

---

# 71. Security validation

Includes:

```text
tenant isolation
service identities
least privilege
secret configuration
network controls
administrative access
```

---

# 72. Financial validation

Includes appropriate verification of:

```text
accounting schema
chart of accounts
currency
periods
tax
costing
posting
```

---

# 73. Integration validation

Includes:

```text
API
events
outbox
inbox
mapping resolution
Trade integration where applicable
```

---

# 74. Operational validation

Includes:

```text
logging
metrics
tracing
alerts
runbooks
backup
restore evidence
reconciliation
```

---

# 75. Golden transaction

Every newly provisioned ERP boundary SHOULD execute controlled golden transactions before activation.

---

# 76. Example golden procurement transaction

```text
Supplier
   │
   ▼
Purchase Order
   │
   ▼
Goods Receipt
   │
   ▼
Supplier Invoice
   │
   ▼
Posting
   │
   ▼
Accounting Validation
```

---

# 77. Example golden sales transaction

Where commerce applies:

```text
Commerce Order
      │
      ▼
ERP Sales Order
      │
      ▼
Shipment
      │
      ▼
Customer Invoice
      │
      ▼
Payment
      │
      ▼
Allocation
```

---

# 78. Activation approval

Production activation SHALL be a distinct governed transition.

---

# 79. Activation authority

Activation SHOULD require appropriate approvals based on risk.

---

# 80. Activation event

Control Plane MAY publish:

```text
erp.capability-binding.activated.v1
```

or the approved canonical equivalent.

---

# 81. Activation time

The effective activation time SHALL be recorded.

---

# 82. Authority begins explicitly

Baobab SHALL be able to answer:

> At what time did this EngineInstance become authoritative for this ERP capability and Context?

---

# 83. Cutover

Migration cutover SHALL establish exactly one authoritative write path.

---

# 84. Cutover phases

A typical migration MAY use:

```text
discover
prepare
initial-copy
synchronize
validate
freeze
final-delta
cutover
verify
stabilize
retire-old
```

---

# 85. Discovery

Discovery SHALL identify:

```text
source system
entities
volumes
customisations
integrations
financial periods
open transactions
data quality
external references
attachments
```

---

# 86. Migration classification

Data SHALL be classified as:

```text
Master Data
Open Transactional Data
Historical Transactional Data
Financial Balances
Configuration
Documents/Evidence
Integration State
```

---

# 87. Migration policy by class

Not every class requires the same migration technique.

---

# 88. Historical data

Historical data MAY be:

```text
fully migrated
summarised
archived read-only
retained in legacy system
```

according to business/legal requirements.

---

# 89. Historical migration decision

The migration strategy SHALL explicitly document which option applies.

---

# 90. Open transactions

Open operational/financial transactions require special treatment.

Examples:

```text
open purchase orders
unreceived goods
unpaid supplier invoices
open customer invoices
unallocated payments
inventory
```

---

# 91. Opening balances

Opening balances SHALL follow Finance-approved accounting migration methodology.

---

# 92. No fabricated transaction history

Baobab SHALL NOT invent fake historical transactions merely to force an opening balance.

---

# 93. Balance migration

Migration SHALL distinguish:

```text
transaction history
opening balances
open-item detail
```

---

# 94. Trial balance reconciliation

Financial cutover SHALL reconcile:

```text
source closing trial balance
↔
target opening position
```

for applicable scope.

---

# 95. Subledger reconciliation

Where relevant:

```text
AR
AP
inventory
bank
fixed assets
```

SHALL reconcile to migrated/opening ledger state.

---

# 96. Inventory cutover

Inventory migration SHALL define:

```text
quantity
warehouse
lot/serial where applicable
valuation
costing
cutover time
```

---

# 97. In-flight transactions

Migration SHALL explicitly address transactions crossing cutover.

---

# 98. Freeze window

A write freeze MAY be used where required for deterministic cutover.

---

# 99. Freeze is scoped

Freeze SHOULD affect only the capabilities requiring it.

---

# 100. Dual-write prohibition

Uncontrolled:

```text
Legacy ERP
     +
New ERP
```

simultaneous authoritative writes are prohibited.

---

# 101. Controlled parallel run

Parallel validation MAY be used.

It SHALL NOT imply two authoritative ledgers.

---

# 102. Shadow mode

A new ERP MAY consume replicated inputs in shadow mode before cutover.

Its outputs SHALL not be authoritative until activation.

---

# 103. Authority marker

Control Plane CapabilityBinding SHALL identify the authoritative target.

---

# 104. Migration mapping

During migration:

```text
CanonicalEntity
      │
      ├── old ExternalReference
      └── new ExternalReference
```

may coexist temporally.

---

# 105. Temporal mapping

Old mapping:

```text
valid_to = cutover
```

New mapping:

```text
valid_from = cutover
```

subject to exact transaction-time policy.

---

# 106. No mapping overwrite

The old mapping SHALL NOT simply be overwritten.

---

# 107. Historical resolution

Historical events SHALL remain resolvable to the representation authoritative at their effective time.

---

# 108. Cutover timestamp

Cutover time SHALL be explicitly recorded.

---

# 109. Time synchronization

Systems participating in cutover SHALL have reliable time synchronization.

---

# 110. Event cutover

Event consumers SHALL understand the authoritative producer transition.

---

# 111. Old outbox

Pending legitimate events from the old system SHALL be handled deliberately.

---

# 112. No event loss

Migration SHALL not discard committed but unpublished business facts.

---

# 113. Duplicate events

Cutover MAY produce duplicate delivery.

Consumers SHALL remain idempotent.

---

# 114. Event boundary

A migration runbook SHALL define:

```text
last accepted old-system event
first authoritative new-system event
```

where relevant.

---

# 115. Integration cutover

Consumers SHALL not need to change native ERP identifiers.

They continue using canonical contracts.

---

# 116. API routing cutover

CapabilityBinding changes SHALL redirect canonical ERP requests.

---

# 117. Cache invalidation

Routing and mapping caches SHALL be invalidated/updated as part of cutover.

---

# 118. DNS alone insufficient

Changing DNS does not constitute business-authority migration.

---

# 119. Validation after cutover

Immediately after cutover, Baobab SHALL validate:

```text
authoritative routing
tenant isolation
mappings
financial balances
open transactions
events
payments
inventory
documents
integrations
```

as applicable.

---

# 120. Stabilisation period

Migration SHOULD have an explicit stabilization period.

---

# 121. Stabilisation monitoring

During stabilization, enhanced monitoring SHOULD cover:

```text
integration failures
financial mismatches
mapping errors
event backlog
user errors
performance
reconciliation
```

---

# 122. Rollback decision

Rollback criteria SHALL be defined before cutover.

---

# 123. Rollback is not always possible

After new authoritative business writes occur, simple infrastructure rollback may be unsafe.

---

# 124. Business-state rollback

If rollback is required after new transactions, migration SHALL address those transactions explicitly.

---

# 125. No database restore as casual rollback

Restoring the old ERP database while ignoring new committed transactions is prohibited.

---

# 126. Roll-forward preference

Where safe, roll-forward correction SHOULD be preferred after authoritative production activity has begun.

---

# 127. Shared-to-dedicated migration

Baobab SHALL support:

```text
Shared EngineInstance
        │
        ▼
Dedicated EngineInstance
```

without changing canonical business identity.

---

# 128. Trigger examples

Isolation escalation MAY be triggered by:

```text
regulation
residency
performance
scale
localisation conflict
upgrade independence
security
business criticality
```

---

# 129. Shared-to-dedicated sequence

Conceptually:

```text
Provision dedicated target
        │
        ▼
Restore/migrate tenant ERP state
        │
        ▼
Validate
        │
        ▼
Freeze source tenant
        │
        ▼
Final synchronization
        │
        ▼
Switch CapabilityBinding
        │
        ▼
Activate new mappings
        │
        ▼
Validate/reconcile
        │
        ▼
Retire source representation
```

---

# 130. Tenant extraction challenge

Extracting one AD_Client from a shared database SHALL be treated as a controlled data migration, not assumed trivial.

---

# 131. Database-level separation advantage

Where future independent recovery/migration is critical, dedicated EngineInstance/database isolation MAY be preferable.

---

# 132. Market expansion

Adding a Market SHALL not necessarily create a new ERP tenant.

---

# 133. Market expansion decision

Evaluate:

```text
existing LegalEntity?
new LegalEntity?
new jurisdiction?
new currency?
new tax regime?
new residency requirement?
new localisation?
new isolation requirement?
```

---

# 134. New LegalEntity

A new LegalEntity MAY require:

```text
new accounting books
new tax registrations
new ERP organizational structure
new AD_Client
or
dedicated EngineInstance
```

depending on isolation/accounting architecture.

---

# 135. No automatic topology inference

Market expansion SHALL pass through lifecycle assessment rather than topology heuristics.

---

# 136. Capability expansion

An existing tenant MAY add:

```text
procurement
inventory
accounting
payments
```

at different times.

---

# 137. Capability activation

Each new capability SHALL have its own readiness and binding lifecycle where required.

---

# 138. Suspension

Baobab SHALL support suspension without immediate deletion.

---

# 139. Suspension reasons

Examples:

```text
security incident
regulatory restriction
contract suspension
non-payment
maintenance
migration
data-integrity incident
```

---

# 140. Suspension scope

Suspension MAY apply to:

```text
Tenant
LegalEntity
Market
Capability
EngineInstance
```

depending on incident/policy.

---

# 141. Suspension semantics

Suspension SHALL explicitly define whether it blocks:

```text
new writes
all writes
reads
background processing
events
settlement
regulatory reporting
```

---

# 142. Financial continuity

A suspended Market may still require:

```text
payment settlement
invoice correction
statutory reporting
period close
```

for prior activity.

Therefore suspension SHALL not be implemented as indiscriminate database shutdown by default.

---

# 143. Security emergency

Security suspension MAY override ordinary business continuity where required.

---

# 144. Drain

Before migration/maintenance/decommissioning, a capability MAY enter:

```text
draining
```

state.

---

# 145. Draining

Draining SHOULD:

```text
reject/redirect new work
allow approved in-flight work
process durable queues
publish committed outbox events
```

according to policy.

---

# 146. Decommissioning

Decommissioning SHALL be a governed lifecycle, not:

```text
docker rm
```

---

# 147. Decommission prerequisites

Before decommissioning, verify:

```text
business termination approval
financial closure
open transactions
reconciliation
data export
records retention
legal holds
regulatory obligations
event backlog
mappings
credentials
```

---

# 148. Financial closure

Finance SHALL confirm required:

```text
period close
open AR/AP treatment
bank reconciliation
inventory disposition
tax/statutory obligations
```

before final retirement where applicable.

---

# 149. Open transactions

Open transactions SHALL be:

```text
completed
cancelled
transferred
migrated
```

under approved business rules.

---

# 150. Data export

A tenant/legal entity SHALL receive required export/transfer before destruction where contract/law/policy requires.

---

# 151. Export integrity

Exports SHALL follow ADR-ERP-017 and ADR-ERP-018 as applicable.

---

# 152. Evidence preservation

Documents subject to retention SHALL remain preserved after runtime decommissioning.

---

# 153. Runtime lifetime != record lifetime

```text
EngineInstance lifetime
      !=
financial record retention lifetime
```

---

# 154. Legal hold

Decommissioning SHALL respect all active legal holds.

---

# 155. Archived ERP

Some circumstances MAY require a read-only historical ERP instance.

---

# 156. Read-only archive

A read-only archive SHALL be explicitly classified and secured.

It SHALL not accidentally resume authoritative writes.

---

# 157. Preferred long-term approach

Where practical, required historical records SHOULD be retained through governed archival/evidence mechanisms rather than indefinitely operating unsupported legacy software.

---

# 158. Native identifier history

ExternalReferences MAY remain retained after EngineInstance retirement for historical interpretation.

---

# 159. Mapping retirement

Mappings SHALL move to appropriate historical/retired state rather than disappear.

---

# 160. Canonical identity survives retirement

Retiring ERP representation SHALL not delete the canonical business entity.

---

# 161. CapabilityBinding retirement

The retired binding SHALL preserve its historical validity interval.

---

# 162. No routing to retired instance

Current resolver requests SHALL not route to retired EngineInstances.

---

# 163. Historical resolver

Historical resolution MAY still identify which EngineInstance was authoritative at a prior time.

---

# 164. Credentials

All tenant/instance-specific credentials SHALL be revoked during retirement.

---

# 165. Service accounts

Native ERP service accounts SHALL be disabled/revoked.

---

# 166. Certificates

Certificates and integration credentials SHALL be revoked/expired according to policy.

---

# 167. Network access

Retired runtime endpoints SHALL be removed from production routing.

---

# 168. Secrets

Secrets SHALL be destroyed according to policy after retention/recovery requirements permit.

---

# 169. Infrastructure

Infrastructure destruction SHALL occur only after data/evidence obligations are satisfied.

---

# 170. Database destruction

Database destruction SHALL be deliberate, authorised and auditable where required.

---

# 171. Backup destruction

Backup retention SHALL be handled separately.

---

# 172. No orphan backups

Retiring a tenant SHALL not leave forgotten backups indefinitely outside governance.

---

# 173. Object storage

ERP-related documents SHALL follow their own retention/disposition lifecycle.

---

# 174. Analytical copies

Analytical/warehouse copies SHALL participate in offboarding and retention workflows.

---

# 175. Vector/AI copies

Embeddings, features and AI-derived datasets containing tenant information SHALL also participate where applicable.

---

# 176. Event retention

Historical events SHALL follow event-retention policy.

---

# 177. DLQ cleanup

Dead-letter/quarantine data SHALL not become an unmanaged indefinite retention path.

---

# 178. Observability cleanup

Logs/traces/audit remain subject to their own retention policies.

---

# 179. Decommission completion

A decommission operation SHALL produce evidence that:

```text
authority ended
routing ended
credentials revoked
required records retained
eligible data destroyed
mappings retired
reconciliation completed
```

---

# 180. Decommission event

Canonical events MAY include:

```text
engine-instance.retired.v1
capability-binding.retired.v1
```

or approved equivalents.

---

# 181. Tenant offboarding does not imply canonical deletion

Canonical organisational history MAY remain where required for referential/audit integrity.

---

# 182. Privacy erasure

Privacy erasure SHALL be treated separately from business decommissioning.

---

# 183. Anonymisation

Where financial retention prevents full deletion, applicable personal data MAY require minimisation/anonymisation according to law/policy.

---

# 184. Divestiture

Divestiture is a special lifecycle.

---

# 185. Divestiture principle

A subsidiary leaving Nabhold SHALL not require its historical canonical identities to be rewritten merely because corporate ownership changed.

---

# 186. Ownership history

Corporate relationships SHALL be temporally represented.

---

# 187. Data transfer

Divestiture SHALL determine:

```text
what data transfers
what remains
what is duplicated
what must be destroyed
what is legally retained
```

---

# 188. Independent continuation

A divested LegalEntity MAY migrate to its own dedicated EngineInstance while retaining canonical identity continuity where contractually appropriate.

---

# 189. Merger

Merger of LegalEntities SHALL NOT automatically merge:

```text
Tenant
AD_Client
ledger
canonical Party identities
```

without explicit migration/accounting decisions.

---

# 190. Acquisition

Acquired businesses SHOULD first be onboarded through controlled boundary integration.

---

# 191. No forced immediate harmonisation

An acquired ERP need not immediately be merged into Baobab iDempiere.

A staged migration MAY preserve operational continuity.

---

# 192. ERP replacement

Future replacement of iDempiere SHALL use the same lifecycle principles.

---

# 193. Engine abstraction payoff

Because canonical identity and CapabilityBinding are independent:

```text
iDempiere
     │
     ▼
Future ERP
```

can occur without redefining every Digital Estate contract.

---

# 194. Migration rehearsal

High-risk migrations SHALL be rehearsed.

---

# 195. Production-like data volumes

Rehearsal SHOULD include representative data volumes and timing.

---

# 196. Cutover duration

Cutover plans SHALL estimate:

```text
freeze duration
migration duration
validation duration
rollback decision point
```

---

# 197. Performance validation

New EngineInstance capacity SHALL be validated before migration.

---

# 198. Backup before migration

A verified recovery point SHALL exist before destructive migration/cutover steps.

---

# 199. Backup is not migration strategy

Backup provides recovery.

It does not replace migration design.

---

# 200. Reconciliation before cutover

Pre-cutover reconciliation establishes the source baseline.

---

# 201. Reconciliation after cutover

Post-cutover reconciliation proves convergence.

---

# 202. Sign-off

Migration SHALL require explicit business/technical sign-off appropriate to risk.

---

# 203. Migration audit record

A migration record SHOULD capture:

```text
source
target
scope
cutover time
release versions
mapping changes
approvals
reconciliation results
exceptions
rollback decision
```

---

# 204. Automation

Provisioning and migration SHOULD be automated wherever repeatability improves safety.

---

# 205. Automation is not autonomy

Automation SHALL execute governed decisions.

It SHALL not invent:

```text
LegalEntity
accounting schema
tax configuration
retention
```

without authority.

---

# 206. Human approval

Human approval SHALL remain where business/legal/financial judgement is required.

---

# 207. Infrastructure-as-code

Infrastructure provisioning SHOULD be reproducible from version-controlled definitions.

---

# 208. ERP configuration-as-code

Appropriate technical/configuration baselines SHOULD be reproducible according to ADR-ERP-013.

---

# 209. Business data is not IaC

Customers, invoices and payments SHALL not be managed as Terraform-style infrastructure resources.

---

# 210. Drift

Provisioned state SHALL be monitored for material drift.

---

# 211. Drift categories

Examples:

```text
infrastructure drift
security drift
ERP technical configuration drift
financial configuration drift
mapping drift
localisation drift
```

---

# 212. Auto-remediation

Only low-risk unambiguous drift SHOULD be automatically remediated.

---

# 213. Financial drift

Financial configuration drift SHALL normally require controlled review.

---

# 214. Provisioning observability

Provisioning SHALL expose:

```text
operation state
current stage
duration
failure reason
retry status
target EngineInstance
```

without exposing secrets.

---

# 215. Migration observability

Migration dashboards SHOULD expose:

```text
records planned
records migrated
records rejected
mapping failures
reconciliation differences
event backlog
cutover status
```

---

# 216. Cardinality

Per-record migration identifiers SHALL not become uncontrolled metric labels.

---

# 217. Logs

Lifecycle logs SHALL preserve correlation/operation identifiers.

---

# 218. Audit

Administrative lifecycle changes SHALL be audited under ADR-ERP-011.

---

# 219. Security

Only authorised management-plane principals SHALL initiate:

```text
provision
activate
suspend
migrate
decommission
```

operations.

---

# 220. Separation of duties

High-risk lifecycle actions SHOULD support separation of:

```text
requester
approver
executor
validator
```

where warranted.

---

# 221. Break-glass

Emergency lifecycle operations SHALL follow ADR-ERP-010.

---

# 222. API separation

Provisioning APIs SHALL remain separate from normal ERP business APIs.

---

# 223. Management-plane endpoint examples

Conceptually:

```text
POST /management/erp/provisioning-operations

GET /management/erp/provisioning-operations/{id}

POST /management/erp/engine-instances/{id}/drain

POST /management/erp/migrations

POST /management/erp/capability-bindings/{id}/activate

POST /management/erp/capability-bindings/{id}/suspend

POST /management/erp/decommissioning-operations
```

Final resources belong to the Control Plane/API contract design.

---

# 224. Business APIs remain separate

Ordinary commerce consumers SHALL not call provisioning endpoints.

---

# 225. Canonical lifecycle events

Potential canonical events include:

```text
erp.provisioning.requested.v1
erp.provisioning.completed.v1
erp.provisioning.failed.v1

engine-instance.ready.v1
engine-instance.draining.v1
engine-instance.retired.v1

capability-binding.activated.v1
capability-binding.suspended.v1
capability-binding.retired.v1

erp.migration.started.v1
erp.migration.cutover-completed.v1
erp.migration.completed.v1
erp.migration.failed.v1
```

Final ownership/naming SHALL be governed through `nabhold/shared`.

---

# 226. Events do not authorize lifecycle

Receiving:

```text
erp.migration.started
```

does not itself authorize a migration.

Authorization occurs before the management command.

---

# 227. Event replay

Replaying lifecycle events SHALL NOT accidentally reprovision infrastructure.

---

# 228. Command/event distinction

Lifecycle commands and lifecycle facts SHALL remain distinct.

---

# 229. Nabhold onboarding

Nabhold Group MAY consume ERP capabilities itself.

Therefore Nabhold SHALL be onboarded as a valid ERP-consuming Context where business need exists.

---

# 230. Group ownership does not exempt onboarding

Nabhold SHALL not receive special implicit System Client access merely because it owns the platform.

---

# 231. Thamani onboarding

Thamani SHALL be onboarded as an independently governed business Context.

Its:

```text
commerce
ERP
accounting
Market
financial data
```

SHALL remain explicitly scoped.

---

# 232. Zuribeans onboarding

Zuribeans SHALL likewise be independently onboarded.

No assumption SHALL be made that Thamani and Zuribeans share:

```text
customers
products
books
tax
bank accounts
pricing
inventory
```

merely because they belong to Nabhold.

---

# 233. Shared suppliers

If multiple group entities transact with the same supplier, each ERP boundary MAY maintain its own BPartner representation.

---

# 234. Shared real-world identity

A common canonical Party MAY be used only where canonical identity governance determines they represent the same real-world Party and sharing is permitted.

---

# 235. Data confidentiality

Canonical identity correlation SHALL not automatically expose one subsidiary's commercial relationship to another.

---

# 236. Future countries

Expansion into:

```text
South Africa
Uganda
Kenya
Tanzania
EU markets
```

or elsewhere SHALL use the same lifecycle architecture.

No country-specific provisioning architecture SHALL be hard-coded into the platform.

---

# 237. Provisioning profile

Reusable onboarding profiles MAY exist for combinations such as:

```text
ZA Trading LegalEntity
UG Trading LegalEntity
B2C Retail
B2B Import/Wholesale
Group Holding
```

but they remain templates requiring validation.

---

# 238. Market template is not legal advice

A technical template SHALL never be interpreted as automatic regulatory approval.

---

# 239. Onboarding evidence

Each production onboarding SHOULD retain evidence of:

```text
business approval
financial approval
security validation
localisation validation
migration reconciliation
technical validation
production activation
```

---

# 240. Architecture invariants

```text
INV-ERP-LCM-001
ERP onboarding is an explicit governed lifecycle.

INV-ERP-LCM-002
Provisioning an AD_Client alone does not constitute ERP onboarding.

INV-ERP-LCM-003
Tenant and LegalEntity remain distinct.

INV-ERP-LCM-004
Provisioning targets explicit business Context.

INV-ERP-LCM-005
Provisioning is idempotent.

INV-ERP-LCM-006
Provisioning is normally asynchronous.

INV-ERP-LCM-007
Failed provisioning retains diagnostic/audit evidence.

INV-ERP-LCM-008
Control Plane does not become an iDempiere SQL installer.

INV-ERP-LCM-009
Infrastructure provisioning and ERP business configuration remain distinct.

INV-ERP-LCM-010
EngineInstance selection respects IsolationProfile.

INV-ERP-LCM-011
EngineInstance selection respects ResidencyPolicy.

INV-ERP-LCM-012
Localisation compatibility is validated before placement.

INV-ERP-LCM-013
Shared infrastructure does not imply shared tenant authority.

INV-ERP-LCM-014
AD_Org is not automatically Tenant, LegalEntity, Market or DigitalEstate.

INV-ERP-LCM-015
Accounting configuration follows actual LegalEntity requirements.

INV-ERP-LCM-016
Configuration templates do not automatically establish financial truth.

INV-ERP-LCM-017
Localisation is validated before production activation.

INV-ERP-LCM-018
Security identities are least privilege.

INV-ERP-LCM-019
Provisioning does not create shared universal superusers.

INV-ERP-LCM-020
Secrets are not persisted in ordinary provisioning records.

INV-ERP-LCM-021
Imported master data retains provenance.

INV-ERP-LCM-022
Staging data is not production authority.

INV-ERP-LCM-023
Existing canonical identities are reused during migration.

INV-ERP-LCM-024
New engine representations do not create duplicate canonical identities.

INV-ERP-LCM-025
ExternalReferences are EngineInstance-scoped.

INV-ERP-LCM-026
Mappings are explicit and temporal.

INV-ERP-LCM-027
CapabilityBinding and Mapping remain distinct.

INV-ERP-LCM-028
Production routing begins only after readiness validation.

INV-ERP-LCM-029
Container health alone does not establish ERP readiness.

INV-ERP-LCM-030
Financial validation precedes financial production use.

INV-ERP-LCM-031
Golden transactions are executed before initial activation where applicable.

INV-ERP-LCM-032
Authority activation has an explicit effective time.

INV-ERP-LCM-033
Exactly one authoritative write path exists at cutover.

INV-ERP-LCM-034
Uncontrolled dual-write migration is prohibited.

INV-ERP-LCM-035
Shadow/parallel systems are not authoritative before activation.

INV-ERP-LCM-036
Historical mappings are never overwritten during migration.

INV-ERP-LCM-037
Canonical identity survives EngineInstance migration.

INV-ERP-LCM-038
Committed unpublished events are not discarded during migration.

INV-ERP-LCM-039
Consumers remain idempotent across cutover.

INV-ERP-LCM-040
DNS changes alone do not define business authority.

INV-ERP-LCM-041
Post-cutover reconciliation is mandatory.

INV-ERP-LCM-042
Rollback criteria are defined before cutover.

INV-ERP-LCM-043
Database restore is not a casual business rollback after new writes.

INV-ERP-LCM-044
Shared-to-dedicated migration preserves canonical identity.

INV-ERP-LCM-045
Market expansion does not automatically create a new tenant.

INV-ERP-LCM-046
New LegalEntity onboarding evaluates accounting and isolation independently.

INV-ERP-LCM-047
Capability activation may occur independently.

INV-ERP-LCM-048
Suspension is explicit and scoped.

INV-ERP-LCM-049
Suspension does not automatically destroy historical data.

INV-ERP-LCM-050
Draining preserves committed integration work according to policy.

INV-ERP-LCM-051
Decommissioning is a governed lifecycle.

INV-ERP-LCM-052
Runtime lifetime is independent of financial-record retention.

INV-ERP-LCM-053
Legal holds survive runtime decommissioning.

INV-ERP-LCM-054
Retired mappings remain historically resolvable where required.

INV-ERP-LCM-055
Canonical identity survives ERP representation retirement.

INV-ERP-LCM-056
Retired EngineInstances cannot receive current authoritative routing.

INV-ERP-LCM-057
Credentials are revoked during retirement.

INV-ERP-LCM-058
Backups participate in retention/decommission policy.

INV-ERP-LCM-059
Analytical and AI-derived copies participate in offboarding governance.

INV-ERP-LCM-060
Decommission completion produces auditable evidence.

INV-ERP-LCM-061
Privacy erasure and business decommissioning remain distinct.

INV-ERP-LCM-062
Divestiture does not rewrite historical canonical identity.

INV-ERP-LCM-063
Acquisitions need not be forcibly migrated on day one.

INV-ERP-LCM-064
Migration rehearsals are required for high-risk cutovers.

INV-ERP-LCM-065
Verified recovery points precede destructive migration.

INV-ERP-LCM-066
Pre- and post-cutover reconciliation are distinct controls.

INV-ERP-LCM-067
Automation executes policy but does not invent accounting/legal decisions.

INV-ERP-LCM-068
Business data is not infrastructure-as-code.

INV-ERP-LCM-069
Financial configuration drift is governed.

INV-ERP-LCM-070
Lifecycle management APIs are management-plane capabilities.

INV-ERP-LCM-071
Lifecycle events do not themselves authorize lifecycle actions.

INV-ERP-LCM-072
Replayed lifecycle events cannot reprovision resources accidentally.

INV-ERP-LCM-073
Nabhold receives no implicit ERP superuser authority.

INV-ERP-LCM-074
Thamani and Zuribeans remain independently governed ERP consumers.

INV-ERP-LCM-075
Group ownership does not collapse subsidiary ERP boundaries.
```

---

# 241. Initial onboarding sequence

The first production onboarding SHALL follow:

```text
                    ORGANISATION
                         │
                         ▼
                 Canonical Context
                         │
                         ▼
                  ERP Assessment
            ┌────────────┼────────────┐
            ▼            ▼            ▼
        Financial     Security    Localisation
        Readiness     Review       Review
            └────────────┼────────────┘
                         ▼
                  IsolationProfile
                         │
                         ▼
                  EngineInstance
                         │
                         ▼
                     AD_Client
                         │
                         ▼
                    ERP AD_Org(s)
                         │
                         ▼
              Accounting Configuration
                         │
                         ▼
               Master Data / Mappings
                         │
                         ▼
                 Integration Setup
                         │
                         ▼
                Golden Transactions
                         │
                         ▼
                   Reconciliation
                         │
                         ▼
                CapabilityBinding
                         │
                         ▼
                     ACTIVE
```

---

# 242. Recommended initial rollout order

The architecture SHALL permit onboarding each organisation independently.

A sensible rollout sequence is:

```text
1. NABHOLD
      │
      └── where the holding company actually requires ERP capability

2. THAMANI
      │
      └── commerce / inventory / accounting integration

3. ZURIBEANS
      │
      └── independently governed B2B ERP requirements
```

The order is operational rather than architectural; none becomes dependent on another's ERP tenancy.

---

# 243. Per-organisation onboarding package

Each onboarding SHALL produce an explicit package containing at minimum:

```text
Context definition
LegalEntity definition
Market scope
IsolationProfile
EngineInstance assignment
AD_Client mapping
AD_Org design
Accounting configuration
Localisation profile
Service identities
CapabilityBindings
Canonical mappings
Integration configuration
Readiness evidence
Recovery evidence
Operational ownership
```

---

# 244. Migration control record

Every material ERP migration SHOULD have:

```text
Migration ID
Source
Target
Scope
Canonical Context
Planned Cutover
Actual Cutover
Source Release
Target Release
Data Classes
Mapping Changes
Reconciliation Results
Approvals
Exceptions
Final Outcome
```

---

# 245. Decommission control record

Every retirement SHOULD capture:

```text
Retirement ID
Context
EngineInstance
Capabilities
Authority End Time
Final Reconciliation
Financial Closure
Record Retention
Legal Holds
Exports
Credential Revocation
Infrastructure Disposition
Approvals
```

---

# 246. Definition of done

ADR-ERP-019 is implemented when:

- [ ] ERP provisioning is represented as a lifecycle.
- [ ] provisioning operations are idempotent.
- [ ] provisioning operations are auditable.
- [ ] Tenant and LegalEntity remain distinct.
- [ ] IsolationProfile drives placement decisions.
- [ ] ResidencyPolicy is evaluated.
- [ ] localisation compatibility is evaluated.
- [ ] EngineInstance capacity/compatibility is evaluated.
- [ ] shared and dedicated deployment paths exist.
- [ ] AD_Client creation is automated or reproducibly governed.
- [ ] AD_Org design is explicit.
- [ ] accounting bootstrap is governed.
- [ ] financial approval gates exist.
- [ ] localisation bootstrap exists.
- [ ] least-privilege service identities are provisioned.
- [ ] secret provisioning is integrated.
- [ ] master-data bootstrap is governed.
- [ ] migration staging exists.
- [ ] canonical identity is preserved during imports.
- [ ] ExternalReferences are created idempotently.
- [ ] temporal mappings are supported.
- [ ] CapabilityBindings remain inactive until validation.
- [ ] technical readiness checks exist.
- [ ] security readiness checks exist.
- [ ] financial readiness checks exist.
- [ ] integration readiness checks exist.
- [ ] operational readiness checks exist.
- [ ] golden procurement transaction exists.
- [ ] golden sales transaction exists where applicable.
- [ ] production activation is explicit.
- [ ] activation time is recorded.
- [ ] migration lifecycle exists.
- [ ] data-class migration policies exist.
- [ ] open-transaction migration strategy exists.
- [ ] opening-balance methodology is Finance-approved.
- [ ] financial reconciliation exists.
- [ ] inventory cutover is defined.
- [ ] uncontrolled dual-write is prevented.
- [ ] cutover has one authoritative writer.
- [ ] event cutover is controlled.
- [ ] mapping cutover is temporal.
- [ ] post-cutover reconciliation exists.
- [ ] stabilization monitoring exists.
- [ ] rollback criteria exist.
- [ ] shared-to-dedicated migration is supported.
- [ ] Market expansion uses readiness assessment.
- [ ] suspension semantics exist.
- [ ] draining exists.
- [ ] decommissioning workflow exists.
- [ ] record retention survives runtime retirement.
- [ ] legal hold survives retirement.
- [ ] credentials are revoked.
- [ ] historical mappings are retained.
- [ ] retired bindings cannot route current traffic.
- [ ] backup disposition is governed.
- [ ] analytical copies participate in offboarding.
- [ ] AI/vector copies participate where applicable.
- [ ] divestiture workflow is supportable.
- [ ] lifecycle management APIs are separated from business APIs.
- [ ] lifecycle events are defined.
- [ ] migration rehearsal is available.
- [ ] provisioning/migration telemetry exists.
- [ ] Nabhold can be independently onboarded as an ERP consumer.
- [ ] Thamani can be independently onboarded.
- [ ] Zuribeans can be independently onboarded.

---

# 247. Final lifecycle model

```text
                         REQUEST
                            │
                            ▼
                         ASSESS
                            │
                            ▼
                         APPROVE
                            │
                            ▼
                        PROVISION
                            │
                            ▼
                        CONFIGURE
                            │
                            ▼
                         MIGRATE
                            │
                            ▼
                        VALIDATE
                            │
                            ▼
                         ACTIVATE
                            │
                            ▼
                          ACTIVE
                            │
          ┌─────────────────┼──────────────────┐
          │                 │                  │
          ▼                 ▼                  ▼
       EXPAND            SUSPEND            MIGRATE
          │                 │                  │
          └─────────────────┼──────────────────┘
                            │
                            ▼
                          DRAIN
                            │
                            ▼
                      DECOMMISSION
                            │
                            ▼
                         RETIRED
                            │
             ┌──────────────┼───────────────┐
             ▼              ▼               ▼
         Records         Evidence        Historical
         Retained        Retained        Mappings
```

---

# 248. Definitive architectural statements

> **Provisioning establishes authority; migration transfers authority; suspension constrains authority; decommissioning terminates authority. None of these operations is merely infrastructure management.**

> **Canonical identity SHALL survive every change in ERP topology.**

> **A Tenant, LegalEntity or Market does not become ERP-ready because an `AD_Client`, database or container exists. ERP readiness exists only when topology, isolation, accounting, localisation, security, mappings, integration, recovery and operational controls have been validated together.**

And most importantly:

> **At every instant in the lifecycle, Baobab SHALL be able to determine exactly which ERP representation and EngineInstance is authoritative for a given capability and business Context.**

That invariant is what makes migration between shared and dedicated infrastructure, expansion into new markets, divestiture, future ERP replacement and independent scaling of Nabhold operating companies possible without changing their canonical business identities.