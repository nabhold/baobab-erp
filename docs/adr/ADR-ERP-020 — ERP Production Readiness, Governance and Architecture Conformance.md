# ADR-ERP-020 — ERP Production Readiness, Governance and Architecture Conformance

**Status:** Accepted  
**Decision class:** ERP / Architecture Governance / Production Readiness / Conformance / Assurance  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`, `nabhold/infrastructure`, `nabhold/baobab-dev`, consuming Digital Estates, integrating Baobab Engines, CI/CD and production operations  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-019  
**Date:** 2026-09-02

---

# 1. Decision

The Baobab iDempiere ERP Engine SHALL be considered production-ready only when its implementation demonstrates measurable conformance with the complete ERP architecture established by ADR-ERP-001 through ADR-ERP-019.

Production readiness SHALL NOT be established merely because:

```text
iDempiere starts
PostgreSQL is reachable
containers are healthy
an invoice can be created
CI is green
a Digital Estate can call an endpoint
```

Production readiness is the demonstrated combination of:

```text
Architecture Conformance
        +
Functional Correctness
        +
Financial Integrity
        +
Tenant Isolation
        +
Security Assurance
        +
Contract Compatibility
        +
Operational Readiness
        +
Recoverability
        +
Migration Readiness
        +
Governance Evidence
```

The governing principle is:

> **Production readiness is a body of evidence, not a deployment status.**

---

# Part I — Architectural Authority

## 2. ADR hierarchy

ADR-ERP-001 through ADR-ERP-020 collectively form the normative architecture for the Baobab ERP Engine.

They SHALL be interpreted as a coherent architecture rather than twenty unrelated recommendations.

---

## 3. Normative hierarchy

Where implementation decisions are evaluated, authority SHALL follow:

```text
Organisation Standards
        │
        ▼
nabhold/shared Contracts
        │
        ▼
Baobab Platform Architecture
        │
        ▼
ERP ADR Series
        │
        ▼
ERP Implementation Contracts
        │
        ▼
Repository Implementation
        │
        ▼
Deployment Configuration
```

A lower layer SHALL NOT silently override a higher architectural contract.

---

## 4. Implementation convenience

Implementation convenience SHALL NOT override architectural invariants.

For example:

> “It is easier to query the iDempiere database directly.”

does not override the prohibition on cross-engine database coupling.

---

## 5. ADR conformance

Every material ERP architecture decision SHALL:

1. conform to the accepted ADRs;
2. explicitly amend/supersede an ADR; or
3. operate under an approved, time-bounded architecture exception.

There SHALL be no fourth category of undocumented divergence.

---

# Part II — Production Readiness Model

## 6. Readiness domains

Every production EngineInstance SHALL demonstrate readiness across at least:

```text
01 Architecture
02 Contracts
03 Tenancy
04 Canonical Identity
05 ERP Functionality
06 Financial Integrity
07 Localisation
08 Security
09 Integration
10 Events
11 Master Data
12 Documents
13 Observability
14 Reconciliation
15 Availability
16 Backup
17 Disaster Recovery
18 Release Management
19 Provisioning
20 Data / Analytics
21 Operations
22 Governance
```

---

## 7. Readiness is multidimensional

Passing one domain SHALL NOT compensate for failure in another.

For example:

```text
Excellent performance
        +
broken Tenant isolation
        =
NOT PRODUCTION READY
```

Similarly:

```text
Correct accounting
        +
untested backups
        =
NOT PRODUCTION READY
```

---

## 8. Readiness state

A production candidate SHOULD have a machine-readable readiness state such as:

```text
candidate
assessment
blocked
conditionally_ready
ready
active
suspended
```

---

## 9. `ready`

`ready` SHALL mean that all mandatory production gates have passed.

---

## 10. `conditionally_ready`

`conditionally_ready` MAY be used only where remaining exceptions:

```text
do not violate critical invariants
have approved owners
have explicit expiry
have compensating controls
```

---

## 11. No conditional security isolation

Cross-tenant isolation failures SHALL NOT qualify for conditional acceptance.

---

## 12. No conditional financial corruption

Known conditions capable of silently corrupting financial state SHALL NOT qualify for conditional acceptance.

---

# Part III — Conformance Levels

## 13. Conformance classifications

Each architectural requirement SHOULD be classified:

```text
MUST
SHOULD
MAY
PROHIBITED
```

---

## 14. MUST

Failure blocks production unless the governing ADR explicitly permits an exception.

---

## 15. SHOULD

Deviation requires documented rationale.

---

## 16. MAY

Implementation discretion applies within other constraints.

---

## 17. PROHIBITED

A prohibited pattern SHALL not be accepted through ordinary implementation review.

---

# Part IV — Architecture Conformance Matrix

## 18. Conformance matrix

The ERP repository SHALL maintain an architecture conformance matrix.

Conceptually:

```text
Requirement
ADR
Invariant
Implementation
Test
Evidence
Owner
Status
Exception
```

---

## 19. Example

```text
ADR-ERP-006
INV: transactional outbox required
Implementation:
  org.nabhold.baobab.erp.outbox

Test:
  outbox_transaction_test

Evidence:
  CI artifact / integration report

Status:
  PASS
```

---

## 20. Machine-readable conformance

Where practical, conformance metadata SHOULD be machine-readable.

For example:

```yaml
requirement: ERP-EVENT-OUTBOX
source: ADR-ERP-006
severity: mandatory

implementation:
  package: org.nabhold.baobab.erp.outbox

evidence:
  - test: integration/outbox_transaction_test

status: conformant
```

---

## 21. Documentation alone

A README statement such as:

```text
"This system supports multi-tenancy."
```

is not sufficient conformance evidence.

---

# Part V — Architecture Fitness Functions

## 22. Fitness functions

Critical architectural invariants SHALL be enforced automatically wherever practical.

These automated checks are Architecture Fitness Functions.

---

## 23. Purpose

Fitness functions convert architecture from:

```text
documentation
```

into:

```text
continuously tested system properties
```

---

## 24. Categories

Fitness functions SHOULD cover:

```text
dependency boundaries
database boundaries
contract compatibility
tenant isolation
mapping integrity
security
event semantics
financial invariants
release provenance
container policy
configuration
```

---

## 25. Cross-engine database fitness function

CI SHALL detect prohibited dependencies or credentials enabling peer engines to connect directly to ERP PostgreSQL.

---

## 26. Native identifier fitness function

Public canonical contracts SHOULD be checked for accidental exposure of implementation-specific identifiers where prohibited.

---

## 27. Contract fitness function

OpenAPI and AsyncAPI implementations SHALL be validated against approved contracts.

---

## 28. Tenant fitness function

Automated integration tests SHALL attempt cross-tenant access.

Expected result:

```text
DENIED
```

---

## 29. Mapping fitness function

Tests SHALL verify:

```text
missing mapping -> fail closed
ambiguous mapping -> fail closed
wrong tenant mapping -> denied
expired mapping -> not current
```

---

## 30. Financial fitness functions

Tests SHOULD verify:

```text
balanced accounting
currency precision
closed-period protection
posting lifecycle
reversal semantics
tax calculations
costing behaviour
```

where applicable.

---

## 31. Event fitness functions

Tests SHALL verify:

```text
transaction + outbox atomicity
duplicate delivery safety
event schema compatibility
canonical subject identity
Context propagation
```

---

## 32. Release fitness functions

CI SHALL verify:

```text
immutable artifact
known source commit
approved dependencies
approved iDempiere baseline
SBOM generation
security scanning
contract compatibility
```

---

# Part VI — Repository Governance

## 33. ERP repository

`nabhold/baobab-erp` SHALL be independently buildable, testable, releasable and deployable.

---

## 34. Repository responsibilities

The repository SHALL contain or reference:

```text
ERP extensions
integration layer
application services
outbox/inbox
ERP-specific migrations
tests
release metadata
operational documentation
architecture documentation
```

---

## 35. Shared contracts

Organisation-wide schemas and standards SHALL remain in:

```text
nabhold/shared
```

rather than being privately redefined by ERP.

---

## 36. Infrastructure

Production infrastructure SHALL remain owned through:

```text
nabhold/infrastructure
```

rather than being hidden inside ERP application code.

---

## 37. Control Plane

Canonical topology, Context, CapabilityBinding, EngineInstance, Mapping and IsolationProfile authority remains with:

```text
nabhold/baobab-cp
```

---

## 38. Development environment

`nabhold/baobab-dev` SHALL provide development tooling.

It SHALL NOT become the production runtime image.

---

# Part VII — Source Governance

## 39. Protected branches

Production branches SHALL use repository protection appropriate to risk.

---

## 40. CODEOWNERS

Material ERP areas SHOULD have explicit code ownership.

---

## 41. Pull requests

Production changes SHALL pass through reviewed pull requests except controlled emergency procedures.

---

## 42. Direct production commits

Routine direct commits to protected production branches are prohibited.

---

## 43. Commit traceability

Production artifacts SHALL be traceable to source commits.

---

## 44. Release traceability

The relationship SHALL be reconstructable:

```text
Production EngineInstance
        │
        ▼
Baobab ERP Release
        │
        ▼
Container Digest
        │
        ▼
Source Commit
        │
        ▼
Pull Request
        │
        ▼
Approvals
```

---

# Part VIII — CI/CD Governance

## 45. CI gates

Required CI SHOULD include:

```text
format/lint
compile/build
unit tests
integration tests
contract tests
security tests
dependency scanning
container scanning
SBOM
architecture fitness functions
```

---

## 46. GitHub Actions

Third-party GitHub Actions SHALL be pinned according to Nabhold organisation policy, including full immutable commit SHAs where required.

---

## 47. Workflow permissions

CI workflows SHALL use least-privilege permissions.

---

## 48. Production environments

Production deployment environments SHOULD use protected approvals appropriate to risk.

---

## 49. Secret handling

CI secrets SHALL NOT be exposed to untrusted pull-request execution.

---

## 50. Artifact promotion

Production SHALL deploy approved immutable artifacts.

It SHALL not rebuild application source differently during production deployment.

---

# Part IX — Build Assurance

## 51. Reproducibility

ERP releases SHOULD be reproducible to the practical extent supported by the dependency ecosystem.

---

## 52. Build provenance

Each release SHALL record:

```text
repository
commit
build workflow
build time
artifact digest
ERP release
iDempiere version
extension versions
```

---

## 53. SBOM

Production releases SHALL produce a Software Bill of Materials.

---

## 54. Dependency inventory

The SBOM SHOULD cover:

```text
Java dependencies
iDempiere components
Baobab extensions
localisation extensions
third-party plugins
base runtime image
```

---

## 55. Unknown binary

Unidentified production binaries are prohibited.

---

## 56. Vulnerability findings

Security findings SHALL have:

```text
severity
owner
decision
remediation
or approved exception
```

---

# Part X — Contract Assurance

## 57. Contract sources

Canonical contracts SHALL be sourced from approved organisation contracts.

---

## 58. OpenAPI

ERP synchronous interfaces SHALL conform to the approved OpenAPI contract.

---

## 59. AsyncAPI

ERP canonical events SHALL conform to the approved AsyncAPI contracts.

---

## 60. Breaking changes

Breaking changes SHALL follow explicit versioning and compatibility policy.

---

## 61. Consumer compatibility

Critical consumers SHOULD participate in compatibility testing.

---

## 62. Contract implementation test

CI SHALL prove that implemented API/event behaviour matches declared contracts.

---

## 63. No undocumented production API

Material production integration endpoints SHALL NOT exist solely as undocumented implementation conveniences.

---

# Part XI — Tenant Isolation Gate

## 64. Tenant isolation is release-blocking

Tenant isolation SHALL be a mandatory production gate.

---

## 65. Isolation test matrix

Tests SHALL cover at least:

```text
Tenant A -> Tenant A resource = permitted when authorised

Tenant A -> Tenant B resource = denied

Tenant A -> Tenant B canonical ID = denied

Tenant A -> Tenant B native ID = denied

Tenant A -> Tenant B mapping = denied

Tenant A -> Tenant B event subscription = denied

Tenant A -> Tenant B export = denied
```

---

## 66. Shared EngineInstance

Shared EngineInstances SHALL receive additional cross-client testing.

---

## 67. Background jobs

Tenant isolation tests SHALL include asynchronous/background processing.

---

## 68. Cache isolation

Tenant isolation SHALL be verified through caches.

---

## 69. Reconciliation isolation

Reconciliation tooling SHALL not expose other tenants' data.

---

## 70. Observability isolation

Operational tooling SHALL follow authorised visibility boundaries.

---

# Part XII — Canonical Identity Gate

## 71. Canonical identity

Cross-engine business entities SHALL use canonical identity according to ADR-ERP-007.

---

## 72. Mapping health

Before production activation, required mappings SHALL be:

```text
present
unique
valid
correctly scoped
temporally valid
```

---

## 73. Native ID leakage

Native IDs SHALL not become external platform identity.

---

## 74. Migration continuity

Migration tests SHALL prove canonical identity survives EngineInstance movement.

---

# Part XIII — Financial Readiness Gate

## 75. Financial readiness

Financial capability SHALL not be activated until Finance-approved validation is complete.

---

## 76. Accounting configuration

Verify:

```text
AccountingSchema
ChartOfAccounts
FunctionalCurrency
FiscalCalendar
AccountingPeriods
TaxConfiguration
CostingConfiguration
DocumentSequences
```

as applicable.

---

## 77. Golden accounting transaction

A controlled transaction SHALL prove:

```text
business document
      │
      ▼
ERP lifecycle
      │
      ▼
posting
      │
      ▼
ledger consequence
      │
      ▼
report/reconciliation
```

---

## 78. Balance

Posting tests SHALL prove required debit/credit balance.

---

## 79. Currency

Tests SHALL cover relevant:

```text
document currency
functional currency
settlement currency
FX
rounding
```

---

## 80. Period controls

Closed-period controls SHALL be tested.

---

## 81. Correction

Reversal/correction workflows SHALL be tested.

---

## 82. Direct financial SQL

Direct SQL mutation of financial state is prohibited as normal operational procedure.

---

## 83. Financial reconciliation

Relevant subledgers and integrations SHALL reconcile.

---

# Part XIV — Localisation Readiness Gate

## 84. Localisation approval

A Market/LegalEntity SHALL not use an uncertified localisation combination for production financial activity.

---

## 85. Compatibility

Validation SHALL include:

```text
iDempiere release
Baobab ERP release
localisation version
jurisdiction
tax
documents
regulatory integrations
```

---

## 86. Evidence

Regulatory/localisation evidence SHALL identify responsible reviewers.

---

## 87. Plugin installed != compliant

Technical installation SHALL not constitute regulatory certification.

---

# Part XV — Security Readiness Gate

## 88. Security gate

Security readiness SHALL be release-blocking for critical findings.

---

## 89. Required security evidence

At minimum:

```text
authentication tested
authorization tested
Tenant isolation tested
service identities reviewed
native ERP roles reviewed
secrets reviewed
network controls reviewed
database privileges reviewed
dependency/container scans reviewed
```

---

## 90. Privileged accounts

System-level ERP identities SHALL be inventoried.

---

## 91. Default credentials

Default production credentials are prohibited.

---

## 92. Shared credentials

Shared human administrator credentials are prohibited except explicitly controlled emergency mechanisms where unavoidable.

---

## 93. Break-glass

Break-glass access SHALL be tested periodically.

---

## 94. Secret rotation

Critical secret rotation procedures SHALL be demonstrated.

---

## 95. Database privileges

ERP application identities SHALL not operate as PostgreSQL superuser.

---

## 96. Penetration testing

Material Internet-facing or high-risk ERP integration surfaces SHOULD undergo appropriate security testing before production and periodically thereafter.

---

# Part XVI — Integration Readiness Gate

## 97. Integration paths

Each production integration SHALL identify:

```text
producer
consumer
contract
authentication
authorization
Context
failure behaviour
retry
idempotency
reconciliation
owner
```

---

## 98. Medusa integration

Trade/Medusa integration SHALL use approved APIs/events.

No database coupling.

---

## 99. Payload integration

Payload SHALL not acquire ERP authority through integration.

---

## 100. Digital Estates

Digital Estates SHALL receive only required ERP capabilities.

---

## 101. Control Plane outage

Critical integration behaviour during temporary CP unavailability SHALL be defined.

---

## 102. Broker outage

Broker outage behaviour SHALL be tested.

Committed ERP transactions SHALL remain recoverable through the outbox architecture.

---

# Part XVII — Event Readiness Gate

## 103. Event production

Canonical ERP events SHALL originate through approved event architecture.

---

## 104. Transactional outbox

The transactional outbox SHALL be demonstrated under failure.

---

## 105. Failure test

Test:

```text
ERP transaction commits
        │
        ▼
broker unavailable
        │
        ▼
event remains durable
        │
        ▼
broker recovers
        │
        ▼
event published
```

---

## 106. Duplicate test

Consumers SHALL tolerate duplicate delivery.

---

## 107. Ordering

Any ordering assumptions SHALL be explicit and scoped.

---

## 108. DLQ

Dead-letter/quarantine handling SHALL be operational.

---

## 109. Replay

Replay SHALL be controlled and auditable.

---

# Part XVIII — Master Data Readiness Gate

## 110. Authority matrix

Production SHALL have an approved source-of-record matrix for critical master/reference data.

---

## 111. No universal master assumption

The Control Plane SHALL not become a universal master-data database.

---

## 112. Product authority

ERP, Medusa and Payload product responsibilities SHALL remain explicit.

---

## 113. Party authority

Identity, commerce profile and ERP financial counterparty responsibilities SHALL remain explicit.

---

## 114. Inventory semantics

Financial inventory and commerce availability SHALL not be silently collapsed.

---

## 115. Price semantics

Commerce pricing, procurement cost and accounting valuation SHALL remain distinguishable.

---

## 116. Master-data reconciliation

Critical synchronized representations SHALL have reconciliation.

---

# Part XIX — Operational Readiness Gate

## 117. Production ownership

Every production EngineInstance SHALL have an operational owner.

---

## 118. Support ownership

Escalation paths SHALL identify:

```text
platform
ERP
database
security
finance
integration
infrastructure
```

owners.

---

## 119. Runbooks

Required runbooks SHALL exist before production activation.

---

## 120. Minimum runbooks

At minimum:

```text
ERP unavailable
database unavailable
outbox backlog
event consumer failure
mapping failure
financial posting failure
tenant-isolation incident
backup failure
restore
EngineInstance failover
certificate expiry
localisation failure
migration/cutover
security incident
```

---

## 121. On-call

Production support arrangements SHALL match the agreed service level.

---

## 122. Alert ownership

Every critical alert SHALL have an owner.

---

## 123. Unowned alert

An alert with no operational response path is not a production control.

---

# Part XX — Observability Gate

## 124. Structured logging

Production ERP services SHALL emit structured logs.

---

## 125. Correlation

Correlation SHALL work across:

```text
gateway
ERP API
application service
iDempiere
outbox
event publisher
consumer
```

where applicable.

---

## 126. Metrics

Minimum operational metrics SHALL include:

```text
request rate
latency
error rate
resource saturation
database health
outbox backlog
event publication failures
background process failures
mapping failures
```

---

## 127. Business-operational metrics

Where appropriate:

```text
unposted documents
failed posting
stuck workflows
reconciliation mismatches
```

SHOULD be observable.

---

## 128. Sensitive telemetry

Sensitive financial/customer data SHALL not become uncontrolled telemetry.

---

# Part XXI — Reconciliation Gate

## 129. Reconciliation is mandatory

Critical independently persisted representations SHALL have reconciliation.

---

## 130. Initial required reconciliations

At minimum as applicable:

```text
Canonical Mapping ↔ ERP representation

Medusa Order ↔ ERP Order/Invoice

Goods Receipt ↔ Supplier Invoice

Payment Provider ↔ ERP Payment

ERP Subledger ↔ General Ledger

ERP Financial Data Product ↔ ERP Ledger
```

---

## 131. Mismatch ownership

Every reconciliation mismatch class SHALL have an owner.

---

## 132. Silent mismatch

Silent persistent mismatch is prohibited.

---

## 133. Correction

Correction SHALL respect domain authority.

---

# Part XXII — Backup Gate

## 134. Backup existence

A backup policy SHALL exist.

---

## 135. Backup success

Recent successful backup SHALL be observable.

---

## 136. Backup integrity

Backup integrity SHALL be checked.

---

## 137. Encryption

Production backups SHALL be encrypted according to policy.

---

## 138. Residency

Backup location SHALL comply with ResidencyPolicy.

---

## 139. Shared instance

Shared-instance backup classification SHALL reflect all contained tenants.

---

# Part XXIII — Restore Gate

## 140. Restore test

Production readiness SHALL require successful restore testing.

---

## 141. Restore evidence

Evidence SHALL demonstrate recovery of:

```text
ERP database
ERP configuration
Baobab extensions
outbox/inbox
required documents
canonical integration compatibility
```

---

## 142. Restore verification

Restore completion SHALL include:

```text
tenant isolation
mapping integrity
financial state
event state
security
```

verification.

---

## 143. Backup without restore

> A backup that has never been successfully restored is not sufficient production evidence.

---

# Part XXIV — Disaster Recovery Gate

## 144. Recovery objectives

Applicable RPO and RTO SHALL be explicitly approved.

---

## 145. No invented objectives

Engineering SHALL not invent financial/business recovery objectives without business approval.

---

## 146. Failover

Failover procedures SHALL preserve one authoritative writer.

---

## 147. Fencing

Old writers SHALL be fenced before promotion of a replacement writer.

---

## 148. DR exercise

Critical EngineInstances SHALL undergo periodic recovery exercises.

---

## 149. Reconciliation after DR

Post-failover/recovery reconciliation SHALL be mandatory.

---

# Part XXV — Performance and Capacity Gate

## 150. Performance

Production readiness SHALL include representative load testing.

---

## 151. Workloads

Tests SHOULD reflect:

```text
API traffic
ERP users
background jobs
posting
event publication
integration bursts
period-end workloads
```

---

## 152. Capacity

EngineInstance capacity SHALL account for all hosted Clients.

---

## 153. Noisy neighbour

Shared EngineInstances SHALL evaluate noisy-neighbour risk.

---

## 154. Scaling limit

Operational thresholds SHOULD indicate when stronger isolation or capacity expansion is required.

---

## 155. Analytics isolation

Analytical workloads SHALL not be allowed to destabilize transactional ERP.

---

# Part XXVI — Release Gate

## 156. Production release

Every production deployment SHALL use an approved Baobab ERP Release.

---

## 157. Release manifest

The release SHALL identify:

```text
iDempiere baseline
Baobab extensions
localisations
third-party extensions
database compatibility
shared contract compatibility
container digest
```

---

## 158. No `latest`

Production SHALL not depend on floating `latest` artifacts.

---

## 159. Preflight

Deployment SHALL execute appropriate preflight checks.

---

## 160. Recovery point

Risky deployments SHALL have a verified recovery point.

---

## 161. Migration state

Database migrations SHALL be known before deployment.

---

## 162. Rollback strategy

Rollback/roll-forward strategy SHALL be explicit.

---

## 163. Deployment success

Deployment success SHALL not be declared merely because Kubernetes/Docker reports healthy containers.

---

## 164. Post-deployment validation

Required validation SHALL include:

```text
health
database
security
business operations
events
mappings
financial behaviour
reconciliation
```

as applicable.

---

# Part XXVII — Provisioning Gate

## 165. New Tenant/LegalEntity

A newly provisioned ERP Context SHALL pass ADR-ERP-019 readiness before activation.

---

## 166. Provisioning evidence

Required evidence includes:

```text
Context
IsolationProfile
EngineInstance
AD_Client mapping
AD_Org design
accounting
localisation
service identities
mappings
CapabilityBinding
golden transactions
reconciliation
```

---

## 167. Activation

CapabilityBinding SHALL remain inactive until mandatory gates pass.

---

# Part XXVIII — Migration Gate

## 168. Migration

Every production migration SHALL have:

```text
scope
source
target
cutover plan
mapping plan
event plan
financial plan
reconciliation
rollback/roll-forward plan
approvals
```

---

## 169. Single authority

Exactly one authoritative write path SHALL exist after cutover.

---

## 170. Post-cutover gate

Migration SHALL not be considered complete until reconciliation passes or approved exceptions are recorded.

---

# Part XXIX — Analytics and Intelligence Gate

## 171. Analytics

Analytics SHALL consume governed ERP-derived data.

---

## 172. Production database

General analytics SHALL not execute directly against ERP primary PostgreSQL.

---

## 173. Intelligence Engine

The Intelligence Engine SHALL not have unrestricted ERP database authority.

---

## 174. AI mutation

AI-driven ERP mutation SHALL use governed business APIs.

---

## 175. Prediction

AI predictions SHALL remain distinguishable from ERP facts.

---

## 176. AI data access

Tenant, LegalEntity, classification and residency controls SHALL continue into AI/analytical systems.

---

# Part XXX — Production Evidence Package

## 177. Evidence package

Every initial production launch SHALL assemble a Production Readiness Evidence Package.

---

## 178. Package contents

At minimum:

```text
Architecture Conformance Matrix

Release Manifest

SBOM

Security Assessment

Tenant Isolation Results

Financial Validation

Localisation Approval

Contract Compatibility Results

Integration Results

Event/Outbox Results

Mapping Validation

Reconciliation Results

Performance Results

Backup Evidence

Restore Evidence

DR Plan / Exercise Evidence

Operational Runbooks

Monitoring / Alert Inventory

Provisioning Evidence

Migration Evidence where applicable

Known Exceptions

Approvals
```

---

## 179. Evidence storage

Evidence SHALL be retained in an auditable controlled location.

---

## 180. Evidence freshness

Evidence SHALL correspond to the actual production candidate or an explicitly equivalent artifact/configuration.

---

## 181. Stale evidence

A penetration test against a materially different release SHALL not automatically certify the current release.

---

# Part XXXI — Production Readiness Review

## 182. Review

Before initial production activation, a formal readiness review SHALL occur.

---

## 183. Participants

Depending on scope:

```text
ERP Engineering
Platform Architecture
Infrastructure
Security
Finance
Operations
Integration owners
Business owner
Compliance/Legal where applicable
```

---

## 184. Approval

Approval SHALL be explicit.

---

## 185. No meeting-as-control

Holding a readiness meeting does not itself establish readiness.

Evidence establishes readiness.

---

# Part XXXII — Architecture Exceptions

## 186. Exception mechanism

Baobab SHALL maintain a formal architecture exception mechanism.

---

## 187. Exception record

Every exception SHALL contain:

```text
Exception ID
Requirement
ADR
Reason
Risk
Scope
Compensating Control
Owner
Approver
Created
Expiry
Remediation Plan
```

---

## 188. Time bounded

Architecture exceptions SHOULD be time bounded.

---

## 189. Permanent deviation

A permanent intentional deviation SHOULD result in:

```text
ADR amendment
or
new superseding ADR
```

rather than an immortal exception.

---

## 190. Expiry

Expired exceptions SHALL become non-conformant until:

```text
remediated
renewed
or architecture changed
```

---

## 191. Exception review

Exceptions SHALL be periodically reviewed.

---

# Part XXXIII — Non-Waivable Controls

## 192. Non-waivable category

Some controls SHALL be designated non-waivable through ordinary project approval.

---

## 193. Initial non-waivable controls

At minimum:

```text
No uncontrolled cross-tenant access

No uncontrolled dual authoritative ERP writers

No ordinary peer-engine direct ERP database access

No production default credentials

No uncontrolled financial-state SQL mutation

No untracked production release artifact

No silent failure of required financial posting

No canonical identity reassignment through engine migration

No production routing to an unvalidated EngineInstance

No deliberate bypass of required financial reconciliation
```

---

# Part XXXIV — Technical Debt

## 194. Technical debt

Technical debt SHALL be distinguished from architecture violation.

---

## 195. Example technical debt

```text
manual reconciliation step
limited dashboard
slow provisioning automation
```

may be technical debt.

---

## 196. Example architecture violation

```text
Medusa directly reads C_Invoice tables
```

is an architectural violation.

It SHALL not be normalized by labelling it technical debt.

---

# Part XXXV — Conformance Drift

## 197. Continuous conformance

Production readiness is not permanent.

---

## 198. Drift sources

Conformance may degrade because of:

```text
new release
configuration change
plugin
localisation update
infrastructure change
new Market
new Tenant
new integration
security vulnerability
regulatory change
```

---

## 199. Continuous controls

Fitness functions SHALL run continuously through CI/CD and scheduled operational checks where appropriate.

---

## 200. Periodic reassessment

Production systems SHALL undergo periodic architecture/security/operational reassessment.

---

# Part XXXVI — Architecture Review Triggers

## 201. Mandatory review triggers

Architecture reassessment SHOULD occur before:

```text
new country/jurisdiction
new high-risk localisation
new EngineInstance isolation model
active-active ERP
new payment architecture
new ledger/consolidation architecture
new major iDempiere version
major custom ERP module
new cross-tenant analytics
autonomous AI financial action
ERP replacement
```

---

## 202. No accidental architecture

Major architectural changes SHALL not emerge solely through incremental pull requests without architecture review.

---

# Part XXXVII — Ownership Model

## 203. Architecture ownership

Baobab Platform Architecture owns cross-platform architectural integrity.

---

## 204. ERP ownership

ERP Engineering owns ERP implementation correctness.

---

## 205. Finance ownership

Finance owns approval of accounting policy/configuration and financial correctness requirements.

---

## 206. Security ownership

Security owns applicable security assurance policy and risk acceptance.

---

## 207. Infrastructure ownership

Infrastructure owns production runtime/platform infrastructure.

---

## 208. Control Plane ownership

Control Plane owns canonical topology and resolution semantics.

---

## 209. Shared ownership

`nabhold/shared` owns organisation-level machine-readable contracts and standards.

---

## 210. Business ownership

Business owners determine operational requirements and acceptable business service levels.

---

## 211. Shared responsibility

No team may claim:

```text
"that is someone else's problem"
```

for an invariant spanning multiple components.

The invariant SHALL have an end-to-end owner.

---

# Part XXXVIII — Architecture Maturity

## 212. Maturity model

Baobab ERP MAY assess maturity through five levels.

### Level 0 — Experimental

```text
developer environment
manual configuration
no production assurance
```

### Level 1 — Repeatable

```text
containerized
source controlled
basic CI
repeatable startup
```

### Level 2 — Governed

```text
contracts
tenant isolation
release process
security controls
backup
observability
```

### Level 3 — Production Grade

```text
financial assurance
reconciliation
tested recovery
automated conformance
controlled provisioning
operational runbooks
```

### Level 4 — Enterprise Resilient

```text
fleet governance
automated drift detection
regular DR exercises
mature SLOs
multi-region capability
continuous compliance evidence
```

---

## 213. Initial target

Initial production Baobab ERP SHALL achieve at least:

```text
Level 3 — Production Grade
```

for capabilities exposed to real business operations.

---

# Part XXXIX — Production Certification

## 214. Certification unit

Production readiness SHALL be evaluated at an appropriate scope.

It SHALL NOT automatically certify every future EngineInstance.

---

## 215. Certification dimensions

Certification may depend on:

```text
Baobab ERP Release
EngineInstance
IsolationProfile
LocalisationProfile
LegalEntity
Capability
Market
```

---

## 216. Example

Certification:

```text
ERP Release: 1.x
EngineInstance: ERP-AF-SOUTH-01
Tenant: THAMANI
LegalEntity: Thamani ZA
Market: ZA
Capabilities:
  accounting
  procurement
  inventory
```

does NOT automatically certify:

```text
future Uganda LegalEntity
+
new localisation
+
different EngineInstance
```

---

## 217. Reuse of evidence

Evidence MAY be reused where applicability is demonstrable.

---

## 218. Delta assessment

Future onboarding SHOULD assess only changed/risk-relevant areas where previous evidence remains valid.

---

# Part XL — Initial Production Certification

## 219. Initial organisations

Initial ERP certification SHALL treat:

```text
NABHOLD
THAMANI
ZURIBEANS
```

as independently governed consuming Contexts.

---

## 220. Independent activation

One organisation's readiness SHALL not force another into production.

---

## 221. Example

```text
NABHOLD       READY
THAMANI       READY
ZURIBEANS     BLOCKED
```

is a valid platform state.

---

## 222. Shared instance implication

If all three share one EngineInstance, an infrastructure defect affecting that instance may affect all three.

This is an accepted consequence only while compatible with their approved IsolationProfiles.

---

## 223. Financial independence

Each independently governed LegalEntity SHALL have separately validated financial configuration.

---

# Part XLI — Architecture Invariants

## 224. Capstone invariants

The following consolidate the ERP ADR series.

```text
INV-ERP-CAP-001
iDempiere is an isolated headless Baobab ERP Engine.

INV-ERP-CAP-002
The ERP Engine does not own Baobab tenancy.

INV-ERP-CAP-003
Tenant and LegalEntity remain distinct concepts.

INV-ERP-CAP-004
LegalEntity is the normal/default tenant boundary, not a synonym for Tenant.

INV-ERP-CAP-005
AD_Client is an ERP representation, not canonical Tenant identity.

INV-ERP-CAP-006
AD_Org is not canonical organisation identity.

INV-ERP-CAP-007
EngineInstance is first-class canonical topology.

INV-ERP-CAP-008
IsolationProfile governs deployment isolation requirements.

INV-ERP-CAP-009
Market and DeploymentRegion remain distinct.

INV-ERP-CAP-010
Jurisdiction and DeploymentRegion remain distinct.

INV-ERP-CAP-011
CapabilityBinding determines where a capability is served.

INV-ERP-CAP-012
Mapping determines which native representation corresponds to canonical identity.

INV-ERP-CAP-013
CapabilityBinding and Mapping are never collapsed.

INV-ERP-CAP-014
Canonical identity survives engine migration.

INV-ERP-CAP-015
Native engine IDs never become global business identity.

INV-ERP-CAP-016
Cross-engine database coupling is prohibited.

INV-ERP-CAP-017
ERP integrations use approved APIs/events.

INV-ERP-CAP-018
Canonical APIs express business semantics rather than iDempiere table semantics.

INV-ERP-CAP-019
Canonical events express business facts rather than database row changes.

INV-ERP-CAP-020
Canonical ERP events use transactional outbox publication.

INV-ERP-CAP-021
At-least-once delivery is assumed.

INV-ERP-CAP-022
Consumers are idempotent.

INV-ERP-CAP-023
Global exactly-once delivery is not assumed.

INV-ERP-CAP-024
ERP owns authoritative ERP transactional state.

INV-ERP-CAP-025
ERP owns authoritative accounting state.

INV-ERP-CAP-026
Medusa does not become a shadow ledger.

INV-ERP-CAP-027
Payload does not become ERP master authority.

INV-ERP-CAP-028
Control Plane does not become a universal master-data database.

INV-ERP-CAP-029
Canonical identity and domain-data authority remain distinct.

INV-ERP-CAP-030
Master-data synchronization propagates authority rather than creating dual authority.

INV-ERP-CAP-031
Financial amounts preserve decimal semantics.

INV-ERP-CAP-032
Currency roles remain explicit.

INV-ERP-CAP-033
Accounting dates remain distinct from system/event times.

INV-ERP-CAP-034
Posted financial history is corrected through accounting workflows, not silent mutation.

INV-ERP-CAP-035
Market does not define accounting books.

INV-ERP-CAP-036
Market does not define data residency.

INV-ERP-CAP-037
Localisation does not require an iDempiere core fork.

INV-ERP-CAP-038
Plugin installation does not constitute regulatory compliance.

INV-ERP-CAP-039
Security Context is resolved server-side.

INV-ERP-CAP-040
Caller-supplied native Client/Org IDs do not establish authorization.

INV-ERP-CAP-041
Cross-tenant access fails closed.

INV-ERP-CAP-042
Group ownership does not automatically authorize subsidiary access.

INV-ERP-CAP-043
ERP PostgreSQL remains private.

INV-ERP-CAP-044
Production service identities use least privilege.

INV-ERP-CAP-045
Secrets are not stored in source code.

INV-ERP-CAP-046
Observability, audit and reconciliation remain distinct controls.

INV-ERP-CAP-047
Critical independently persisted business representations are reconcilable.

INV-ERP-CAP-048
Reconciliation respects domain authority.

INV-ERP-CAP-049
One authoritative ERP writer exists for a capability and Context.

INV-ERP-CAP-050
Split-brain financial authority is prohibited.

INV-ERP-CAP-051
Backup and replication remain distinct controls.

INV-ERP-CAP-052
Recovery is not complete until correctness is validated.

INV-ERP-CAP-053
ERP releases are immutable and identifiable.

INV-ERP-CAP-054
Production does not consume floating `latest` releases.

INV-ERP-CAP-055
Production runtime images are purpose-built.

INV-ERP-CAP-056
baobab-dev is not the production runtime.

INV-ERP-CAP-057
ERP upgrades validate localisations and integrations.

INV-ERP-CAP-058
ERP provisioning is a governed lifecycle.

INV-ERP-CAP-059
AD_Client creation alone does not constitute onboarding.

INV-ERP-CAP-060
Production CapabilityBinding activates only after readiness validation.

INV-ERP-CAP-061
Migration preserves canonical identity.

INV-ERP-CAP-062
Migration has one authoritative cutover path.

INV-ERP-CAP-063
Uncontrolled dual-write migration is prohibited.

INV-ERP-CAP-064
Decommissioning preserves required historical evidence.

INV-ERP-CAP-065
Runtime lifetime is not financial-record lifetime.

INV-ERP-CAP-066
Analytics does not acquire ERP authority.

INV-ERP-CAP-067
The ERP primary database is not the enterprise warehouse.

INV-ERP-CAP-068
AI does not receive unrestricted ERP database authority.

INV-ERP-CAP-069
AI predictions remain distinguishable from business facts.

INV-ERP-CAP-070
AI mutations enter ERP through governed business capabilities.

INV-ERP-CAP-071
Production readiness requires evidence.

INV-ERP-CAP-072
Critical architectural invariants are continuously tested where practical.

INV-ERP-CAP-073
Architecture exceptions are explicit and governed.

INV-ERP-CAP-074
Known cross-tenant leakage cannot be conditionally accepted.

INV-ERP-CAP-075
Known silent financial corruption cannot be conditionally accepted.

INV-ERP-CAP-076
Every production artifact is traceable to approved source.

INV-ERP-CAP-077
Every production EngineInstance has operational ownership.

INV-ERP-CAP-078
Every critical alert has an operational response path.

INV-ERP-CAP-079
Every critical reconciliation mismatch has ownership.

INV-ERP-CAP-080
A backup is not trusted until restore has been demonstrated.

INV-ERP-CAP-081
Disaster recovery preserves one authoritative writer.

INV-ERP-CAP-082
Post-recovery reconciliation is mandatory.

INV-ERP-CAP-083
Shared infrastructure never implies shared authority.

INV-ERP-CAP-084
Nabhold, Thamani and Zuribeans remain independently governable ERP consumers.

INV-ERP-CAP-085
Future organisations can be onboarded without redesigning ERP tenancy.

INV-ERP-CAP-086
Future Markets can be added without redefining canonical identity.

INV-ERP-CAP-087
Future EngineInstances can be introduced without changing consumer contracts.

INV-ERP-CAP-088
Future ERP replacement can preserve canonical identity and platform contracts.

INV-ERP-CAP-089
Implementation convenience never silently overrides accepted architecture.

INV-ERP-CAP-090
Production readiness remains a continuously maintained state, not a one-time milestone.
```

---

# Part XLII — Final Production Gate

## 225. Gate equation

The final production decision SHALL conceptually evaluate:

```text
ARCHITECTURE
      ∩
SECURITY
      ∩
TENANT ISOLATION
      ∩
FINANCIAL CORRECTNESS
      ∩
CONTRACT COMPATIBILITY
      ∩
LOCALISATION
      ∩
INTEGRATION
      ∩
RECONCILIATION
      ∩
OPERABILITY
      ∩
RECOVERABILITY
      ∩
GOVERNANCE
      =
PRODUCTION READY
```

This is an intersection, not an average.

---

# Part XLIII — Definition of Done

## 226. ERP architecture programme

The iDempiere architecture programme defined by ADR-ERP-001 through ADR-ERP-020 is considered implementation-ready when:

- [ ] all twenty ADRs are Accepted;
- [ ] ADRs are stored using the organisation ADR naming convention;
- [ ] cross-ADR terminology is normalized;
- [ ] normative MUST/SHOULD/MAY requirements are identifiable;
- [ ] architecture invariants are catalogued;
- [ ] invariants map to implementation contracts;
- [ ] critical invariants map to automated fitness functions;
- [ ] architecture conformance matrix exists;
- [ ] Control Plane contracts align with ERP architecture;
- [ ] `nabhold/shared` contracts align with ERP architecture;
- [ ] `nabhold/infrastructure` responsibilities align with ERP architecture;
- [ ] `nabhold/baobab-erp` implementation boundaries align;
- [ ] iDempiere extension packages follow ADR-ERP-004;
- [ ] REST contracts follow ADR-ERP-005;
- [ ] event contracts follow ADR-ERP-006;
- [ ] canonical mappings follow ADR-ERP-007;
- [ ] financial architecture follows ADR-ERP-008;
- [ ] localisation follows ADR-ERP-009;
- [ ] security follows ADR-ERP-010;
- [ ] observability/reconciliation follows ADR-ERP-011;
- [ ] HA/backup/DR follows ADR-ERP-012;
- [ ] releases/upgrades follow ADR-ERP-013;
- [ ] master-data ownership follows ADR-ERP-014;
- [ ] cross-engine workflows follow ADR-ERP-015;
- [ ] document/evidence architecture follows ADR-ERP-016/017 as defined by the series;
- [ ] analytics/intelligence follows ADR-ERP-018;
- [ ] provisioning/migration follows ADR-ERP-019;
- [ ] production readiness is enforced by this ADR;
- [ ] initial tenant-isolation tests pass;
- [ ] initial financial golden transactions pass;
- [ ] initial event/outbox tests pass;
- [ ] initial mapping tests pass;
- [ ] initial reconciliation tests pass;
- [ ] initial backup/restore test passes;
- [ ] initial production release is reproducible and traceable;
- [ ] initial Production Readiness Evidence Package is approved.

---

# 227. The completed Baobab ERP architecture

The resulting architecture is:

```text
                         BAOBAB PLATFORM
                               │
                    ┌──────────┴──────────┐
                    │                     │
              CONTROL PLANE          SHARED CONTRACTS
                    │                     │
                    └──────────┬──────────┘
                               │
                      Canonical Context
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
          NABHOLD           THAMANI          ZURIBEANS
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                        CapabilityBinding
                               │
                               ▼
                       ERP EngineInstance
                               │
                  ┌────────────┼────────────┐
                  │            │            │
                  ▼            ▼            ▼
              AD_Client    AD_Client    AD_Client
              NABHOLD      THAMANI      ZURIBEANS
                  │            │            │
                  └────────────┼────────────┘
                               │
                           iDempiere
                               │
          ┌────────────────────┼─────────────────────┐
          │                    │                     │
          ▼                    ▼                     ▼
     ERP Business         Accounting           Integration
       State                State                Outbox
          │                    │                     │
          └────────────────────┼─────────────────────┘
                               │
                               ▼
                        Canonical Events
                               │
             ┌─────────────────┼──────────────────┐
             ▼                 ▼                  ▼
           Trade          Intelligence        Analytics
          Medusa             Engine            Platform
```

with independent Digital Estates operating above the platform capabilities rather than becoming extensions of the ERP runtime.

---

# 228. Final separation of concerns

The architecture can ultimately be reduced to the following distinctions:

```text
CONTROL PLANE
    owns:
        identity
        Context
        topology
        capability routing
        isolation policy
        canonical mappings

ERP
    owns:
        operational ERP state
        accounting
        procurement
        financial inventory
        ERP workflows

MEDUSA
    owns:
        commerce state
        buying journeys
        commerce orchestration

PAYLOAD
    owns:
        content
        editorial composition

DIGITAL ESTATES
    own:
        customer experience
        brand
        presentation
        estate-specific journeys

INTELLIGENCE
    owns:
        analysis
        models
        predictions
        recommendations

SHARED
    owns:
        organisational contracts
        schemas
        interoperability standards

INFRASTRUCTURE
    owns:
        runtime infrastructure
        networking
        databases as infrastructure
        deployment
        observability infrastructure
        recovery infrastructure
```

No component receives authority merely because it can technically access another.

---

# 229. Final architectural test

For every future ERP design decision, the architecture team SHOULD be able to ask:

```text
WHO owns this fact?

WHO owns this identity?

WHO owns this policy?

WHICH Context applies?

WHICH capability is being requested?

WHICH EngineInstance is authoritative?

WHICH mapping resolves the representation?

WHICH isolation boundary applies?

WHICH contract governs the interaction?

HOW is failure recovered?

HOW is divergence reconciled?

HOW is the decision audited?

WHAT evidence proves this is production safe?
```

If these questions cannot be answered, the implementation is not sufficiently defined for production.

---

# 230. Final governing statement

> **Baobab SHALL treat iDempiere as an authoritative enterprise capability within the platform, not as the platform itself.**

The ERP Engine therefore remains independently deployable, independently upgradeable and independently replaceable while participating in a stable canonical architecture governed by the Baobab Control Plane and organisation-wide contracts.

The final invariant of the entire ERP ADR series is:

> **Business identity SHALL outlive engine topology; business authority SHALL remain explicit; financial truth SHALL remain accountable; integration SHALL remain contractual; and production readiness SHALL always be provable.**

---

# 231. Status of the ERP ADR series

```text
ADR-ERP-001  ACCEPTED
ADR-ERP-002  ACCEPTED
ADR-ERP-003  ACCEPTED
ADR-ERP-004  ACCEPTED
ADR-ERP-005  ACCEPTED
ADR-ERP-006  ACCEPTED
ADR-ERP-007  ACCEPTED
ADR-ERP-008  ACCEPTED
ADR-ERP-009  ACCEPTED
ADR-ERP-010  ACCEPTED
ADR-ERP-011  ACCEPTED
ADR-ERP-012  ACCEPTED
ADR-ERP-013  ACCEPTED
ADR-ERP-014  ACCEPTED
ADR-ERP-015  ACCEPTED
ADR-ERP-016  ACCEPTED
ADR-ERP-017  ACCEPTED
ADR-ERP-018  ACCEPTED
ADR-ERP-019  ACCEPTED
ADR-ERP-020  ACCEPTED

                 ─────────────────────
                  ERP ADR SERIES CLOSED
                 ─────────────────────
```

**The Baobab iDempiere ERP architecture is now defined at ADR level.**