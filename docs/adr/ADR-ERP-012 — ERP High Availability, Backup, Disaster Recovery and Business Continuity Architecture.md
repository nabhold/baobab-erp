# ADR-ERP-012 — ERP High Availability, Backup, Disaster Recovery and Business Continuity Architecture

**Status:** Accepted  
**Decision class:** ERP / Availability / Backup / Disaster Recovery / Business Continuity / Data Protection  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`, `nabhold/infrastructure`, PostgreSQL, event infrastructure, object storage, secrets/configuration and dependent ERP integrations  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-011  
**Date:** 2026-09-02

---

# 1. Decision

The Baobab ERP Engine SHALL implement high availability, backup, disaster recovery and business continuity as distinct but coordinated capabilities.

The architecture SHALL preserve the following through infrastructure or regional failure:

```text
ERP business state
financial integrity
canonical identity
tenant isolation
mapping integrity
event intent
audit history
reconciliation state
configuration
security boundaries
```

Recovery SHALL prioritise correctness over premature availability.

The governing rule is:

> **Baobab SHALL prefer a temporarily unavailable ERP over an available ERP whose authoritative financial state, tenant boundary or write authority is uncertain.**

---

# 2. Availability concepts

The architecture SHALL distinguish:

```text
High Availability
    resilience to ordinary component failure

Backup
    durable recoverable copies of state

Disaster Recovery
    restoration of service after material failure

Business Continuity
    ability for the enterprise to continue critical operations
    during disruption
```

None substitutes for another.

---

# 3. HA is not backup

Database replication SHALL NOT be treated as backup.

Replication can reproduce:

```text
accidental deletion
logical corruption
malicious mutation
application defects
```

to replicas.

Independent recoverable history is required.

---

# 4. Backup is not DR

A backup proves only that data was copied.

DR requires the ability to restore the entire required service safely.

---

# 5. DR is not business continuity

Restoring ERP infrastructure does not necessarily mean the business can immediately resume every process.

Continuity also includes:

```text
people
procedures
dependencies
external providers
communications
manual fallback
reconciliation
```

---

# 6. Recovery objectives

Every production `EngineInstance` SHALL have an assigned recovery tier defining at least:

```text
availability objective
RPO
RTO
backup policy
restore-testing policy
DR topology
failover authority
```

---

# 7. Recovery Point Objective

RPO answers:

> How much committed data loss can the business tolerate after a disaster?

RPO SHALL be explicitly defined.

---

# 8. Recovery Time Objective

RTO answers:

> How long may the ERP capability remain unavailable before recovery must be achieved?

RTO SHALL also be explicit.

---

# 9. RPO is not backup frequency

Backup frequency alone does not establish effective RPO.

The architecture must consider:

```text
WAL/archive continuity
replication
backup completeness
restore capability
corruption detection
```

---

# 10. RTO is not restart time

Container restart time does not establish ERP RTO.

RTO includes the time necessary to:

```text
detect
declare
restore/fail over
validate
reconcile
authorise write resumption
```

---

# 11. Recovery tier

Baobab SHOULD define standard recovery classes.

Conceptually:

```text
ERP-TIER-1
    critical financial operations

ERP-TIER-2
    important operational ERP

ERP-TIER-3
    lower-criticality/non-production workloads
```

Exact objectives SHALL be approved separately.

---

# 12. No invented universal RPO/RTO

This ADR SHALL NOT declare arbitrary values such as:

```text
RPO = 0
RTO = 5 minutes
```

for every Tenant.

Recovery objectives are business decisions constrained by cost and technology.

---

# 13. Recovery scope

Recovery policy MAY vary by:

```text
Tenant
LegalEntity
EngineInstance
IsolationProfile
jurisdiction
business criticality
```

---

# 14. Shared instance consequence

When several Tenants share an EngineInstance, the strongest applicable recovery requirement MAY determine the instance-level infrastructure design.

---

# 15. Dedicated instance

A dedicated EngineInstance permits recovery objectives to be tailored more closely to one Tenant or regulated workload.

---

# 16. IsolationProfile integration

`IsolationProfile` SHALL reference or constrain permitted:

```text
HA topology
backup location
backup encryption
DR region
recovery tier
```

---

# 17. EngineInstance authority

The Control Plane SHALL know which EngineInstance is authoritative for each capability binding.

Recovery SHALL never infer authority from infrastructure health alone.

---

# 18. One authoritative writer

For a given write capability and Context, exactly one EngineInstance SHALL be authoritative at a time.

---

# 19. Split-brain prohibition

Two geographically separated ERP databases SHALL NOT simultaneously accept authoritative writes for the same capability/Context unless a future architecture explicitly proves safe multi-writer semantics.

The initial architecture SHALL assume:

```text
single authoritative writer
```

---

# 20. Active-passive default

For regional DR, active-passive SHALL be preferred over active-active for ERP financial workloads.

---

# 21. Active-active rejection

Active-active multi-region iDempiere/PostgreSQL write architecture is NOT adopted by this ADR.

Reasons include:

```text
financial consistency
native ERP assumptions
sequence/state coordination
posting semantics
event ordering
operational complexity
split-brain risk
```

---

# 22. Stateless application HA

Where technically appropriate, ERP API/facade components MAY run multiple replicas.

These replicas SHALL share the same authoritative ERP state and Context rules.

---

# 23. Application replicas

Application replica count SHALL not alter business authority.

```text
ERP API Pod 1
ERP API Pod 2
ERP API Pod 3
```

remain one logical ERP capability.

---

# 24. Stateful ERP runtime

Any iDempiere runtime state that cannot safely be replicated as stateless application state SHALL be explicitly understood before horizontal scaling.

---

# 25. Scheduler coordination

Background jobs and ERP processes SHALL avoid duplicate execution when application instances are replicated.

---

# 26. Singleton workloads

Processes requiring singleton execution SHALL use an explicit coordination mechanism.

---

# 27. Database HA

Production PostgreSQL SHOULD support high availability appropriate to the assigned recovery tier.

---

# 28. Primary database

Only the authoritative PostgreSQL primary SHALL accept ordinary ERP writes.

---

# 29. Standby database

Standbys MAY support:

```text
failover
recovery
read workloads where proven safe
```

but SHALL not independently become authoritative writers.

---

# 30. Synchronous replication

Synchronous replication MAY reduce data-loss exposure.

It introduces availability and latency trade-offs.

Its use SHALL be determined by recovery tier.

---

# 31. Asynchronous replication

Asynchronous replication MAY provide regional DR with non-zero replication lag.

The corresponding RPO SHALL acknowledge that possibility.

---

# 32. Replication lag

Replication lag SHALL be observable.

---

# 33. Failover eligibility

A standby SHALL not be considered safely promotable merely because it is reachable.

Promotion SHALL consider:

```text
replication state
data freshness
primary fencing
recovery policy
operator/automation authority
```

---

# 34. Fencing

Before promoting a replacement writer, Baobab SHALL establish that the previous writer cannot continue accepting authoritative writes.

---

# 35. Network partition

Loss of connectivity to the primary SHALL NOT by itself prove the primary is dead.

---

# 36. Quorum and authority

Infrastructure mechanisms MAY help establish safe failover.

Canonical write authority SHALL still be reflected through controlled EngineInstance/CapabilityBinding state.

---

# 37. Failover sequence

Conceptually:

```text
Primary Failure Detected
          │
          ▼
Confirm Failure / Assess
          │
          ▼
Fence Old Writer
          │
          ▼
Validate Standby
          │
          ▼
Promote Standby
          │
          ▼
Update Authoritative Routing
          │
          ▼
Validate ERP
          │
          ▼
Targeted Reconciliation
          │
          ▼
Resume Writes
```

---

# 38. Routing update

Failover SHALL update authoritative routing through the appropriate Control Plane/infrastructure mechanisms.

Consumers SHALL not hard-code the old ERP endpoint.

---

# 39. DNS is not business authority

DNS changes MAY participate in failover.

DNS alone SHALL not define canonical EngineInstance authority.

---

# 40. Load balancer is not business authority

A load balancer choosing a healthy backend SHALL not independently decide which database/region owns ERP writes.

---

# 41. Backup architecture

Production ERP SHALL have a documented backup policy covering:

```text
PostgreSQL
ERP configuration
custom extensions
integration state
outbox
inbox where applicable
audit state
attachments/documents where applicable
```

---

# 42. Database backup

PostgreSQL backup SHALL support recovery to a consistent database state.

---

# 43. Physical versus logical backup

Physical and logical backups serve different purposes.

Baobab MAY use both.

---

# 44. Physical backup

Physical backups are appropriate for whole-database recovery and point-in-time recovery strategies.

---

# 45. Logical backup

Logical exports MAY support:

```text
selective inspection
migration
portability
additional recovery options
```

but SHALL not automatically replace physical recovery architecture.

---

# 46. Point-in-time recovery

Production recovery SHOULD support point-in-time recovery where required by recovery tier.

---

# 47. WAL preservation

Where PITR is required, PostgreSQL WAL required for the recovery window SHALL be durably archived.

---

# 48. WAL continuity

Backup monitoring SHALL detect archive failures.

---

# 49. Backup chain

Recovery SHALL not depend on a backup chain whose required components have silently expired.

---

# 50. Backup retention

Retention SHALL be policy-driven.

It MAY include:

```text
short-term operational recovery
monthly retention
year-end retention
regulatory retention
```

according to requirements.

---

# 51. Backup immutability

Critical backup tiers SHOULD support protection against accidental or malicious deletion.

---

# 52. Backup encryption

Production backups SHALL be encrypted according to Baobab security policy.

---

# 53. Backup credentials

Backup infrastructure SHALL use dedicated least-privilege identities.

---

# 54. Backup separation

Backup credentials SHOULD not be identical to ordinary ERP runtime credentials.

---

# 55. Backup destination

Backup destinations SHALL comply with `ResidencyPolicy`.

---

# 56. Cross-border backup

Copying a backup into another country/region is a data transfer and SHALL be governed accordingly.

---

# 57. Multi-tenant backup

A backup of a shared EngineInstance may contain multiple Tenants.

It SHALL therefore receive protection appropriate to the combined sensitivity of that dataset.

---

# 58. Per-tenant restore limitation

A physical shared-database backup may not permit trivial single-Tenant restoration.

This operational consequence SHALL be considered when selecting isolation profiles.

---

# 59. Tenant-specific recovery

If contractual/regulatory requirements demand independent Tenant restoration, stronger isolation MAY be required.

---

# 60. Backup catalogue

Backups SHALL be catalogued with metadata such as:

```text
EngineInstance
environment
database identity
started_at
completed_at
backup type
recovery range
status
encryption state
location
```

---

# 61. Backup integrity

Backup completion SHALL include integrity checks appropriate to the backup technology.

---

# 62. Restore testing

Production backup policy SHALL include scheduled restore testing.

---

# 63. Restore testing principle

The governing rule is:

> **A backup is not operationally trusted until Baobab has demonstrated that it can be restored.**

---

# 64. Restore environment

Restore testing SHALL occur in an isolated environment.

---

# 65. Restored-data security

Restored production data SHALL retain production-equivalent protection unless sanitised.

---

# 66. Restore verification

Restore tests SHALL verify more than database startup.

At minimum, appropriate tests SHOULD verify:

```text
schema integrity
iDempiere startup
critical business entities
accounting data
mapping consistency
outbox state
tenant isolation
audit state
```

---

# 67. Trial balance validation

For financial recovery exercises, Finance SHOULD be able to validate critical ledger/trial-balance consistency where applicable.

---

# 68. Referential integrity

Recovery verification SHALL identify broken canonical/native mappings caused by inconsistent recovery points.

---

# 69. Application/database compatibility

Restored databases SHALL be paired with compatible ERP application and extension versions.

---

# 70. Artifact preservation

Baobab SHALL retain enough deployment provenance to recover compatible:

```text
iDempiere version
Baobab plugins
localisation plugins
configuration
container image
```

for supported recovery windows.

---

# 71. Infrastructure-as-code

Recoverable production infrastructure SHOULD be represented through version-controlled infrastructure definitions.

---

# 72. Configuration recovery

Configuration required to recreate an EngineInstance SHALL not exist only as undocumented manual server state.

---

# 73. Secrets recovery

DR SHALL include a controlled mechanism for restoring/accessing required secrets.

---

# 74. Secret separation

Secrets SHALL not simply be embedded in backups of application configuration.

---

# 75. Key recovery

Encryption-key recovery SHALL be part of DR planning.

An encrypted backup without recoverable keys is unusable.

---

# 76. Key protection

Recovery capability SHALL not justify insecure duplication of encryption keys.

---

# 77. Certificate recovery

Certificates and trust configuration required for ERP integrations SHALL have recovery procedures.

---

# 78. External dependencies

DR SHALL identify external dependencies including:

```text
identity provider
DNS
certificate authority
event broker
object storage
email provider
bank/payment integrations
regulatory services
Control Plane
```

---

# 79. Dependency degradation

ERP continuity SHALL define behaviour when an external dependency remains unavailable after ERP recovery.

---

# 80. Event broker outage

If the event broker is unavailable:

```text
ERP transaction
   ↓
commit
   ↓
outbox retained
```

SHALL remain the normal correctness model.

---

# 81. Broker DR

Event infrastructure SHALL have its own recovery policy.

ERP database recovery SHALL not assume event broker history is perfectly preserved.

---

# 82. Outbox recovery

The transactional outbox SHALL be part of ERP database recovery.

---

# 83. Unpublished events

Unpublished outbox entries restored from backup SHALL remain eligible for publication.

---

# 84. Published events

Published-state recovery SHALL avoid blindly reclassifying all historical events as unpublished.

---

# 85. Publication uncertainty

If recovery cannot establish whether a particular event reached the broker, Baobab SHALL prefer safe duplicate delivery over silent loss.

Consumers SHALL be idempotent.

---

# 86. Exactly-once recovery rejected

Recovery SHALL not depend on global exactly-once delivery guarantees.

---

# 87. Consumer inbox recovery

Where an ERP-side consumer uses a durable inbox/deduplication store, that state SHALL be included in recovery planning.

---

# 88. Lost inbox consequence

Losing deduplication state can cause historical events to appear new.

Therefore replay/recovery must remain idempotent at the business layer.

---

# 89. Audit recovery

Required audit records SHALL be included in recovery architecture.

---

# 90. Audit consistency

Financial records SHALL not be restored to a point materially later than their mandatory audit evidence without controlled remediation.

---

# 91. Reconciliation state

Reconciliation state MAY be restored.

However, prior `matched` status SHALL not automatically prove correctness after recovery.

---

# 92. Post-recovery reconciliation

After significant restore or failover, critical reconciliation SHALL rerun.

---

# 93. Recovery checkpoint

Before reopening writes, Baobab SHOULD establish a recovery checkpoint recording:

```text
recovery event
restored point
authoritative EngineInstance
data-loss assessment
validation result
reconciliation result
approver
```

---

# 94. Disaster declaration

A disaster SHALL be explicitly declared according to operational governance when invoking full DR procedures.

---

# 95. Failover authority

The authority to trigger ERP disaster failover SHALL be restricted.

---

# 96. Automated failover

Automated failover MAY be used where the architecture can safely prove:

```text
failure
fencing
replication state
promotion
routing
```

without ambiguity.

---

# 97. Regional disaster

A regional disaster MAY require:

```text
secondary region activation
database promotion/restore
application deployment
secret activation
network activation
routing changes
```

---

# 98. Region versus Market

As established previously:

```text
DeploymentRegion != Market
```

Failing over from one infrastructure region to another SHALL NOT change the business Market.

---

# 99. Region versus LegalEntity

Infrastructure failover SHALL NOT change LegalEntity ownership.

---

# 100. Region versus Tenant

Infrastructure failover SHALL NOT change Tenant identity.

---

# 101. Canonical identity continuity

All canonical UUIDs SHALL survive disaster recovery unchanged.

---

# 102. Native identity continuity

Native iDempiere IDs SHOULD remain unchanged in normal database-level recovery.

---

# 103. ExternalReference continuity

ExternalReferences SHALL remain valid after infrastructure failover when native records remain the same representations.

---

# 104. Mapping continuity

A pure infrastructure failover SHALL not create new business mappings merely because the database runs in another region.

---

# 105. EngineInstance identity

Whether regional failover preserves or changes `EngineInstance` identity SHALL depend on the deployment model.

This SHALL be explicit.

---

# 106. Replica promotion model

If standby infrastructure represents the same logical EngineInstance, promotion MAY preserve `EngineInstance` identity.

---

# 107. Replacement-instance model

If DR provisions a separately governed EngineInstance, CapabilityBinding SHALL be changed explicitly.

---

# 108. No ambiguity

The two models SHALL NOT be mixed implicitly.

---

# 109. Recovery mode

ERP SHOULD support an operational recovery mode.

Possible states:

```text
normal
read_only
recovery_validation
draining
unavailable
```

---

# 110. Read-only recovery

Where safe, ERP MAY become read-only during recovery validation.

---

# 111. Read-only limitations

Read-only mode SHALL not permit business operations that appear harmless but generate:

```text
workflow state
audit mutation
session-dependent changes
posting
outbox records
```

unless specifically supported.

---

# 112. Write resumption

Writes SHALL resume only after:

```text
authoritative writer established
critical dependencies verified
security verified
mapping integrity checked
recovery validation passed
```

according to recovery tier.

---

# 113. Financial validation

For material disasters, financial validation MAY be required before write resumption.

---

# 114. Data-loss assessment

If RPO results in known or possible data loss, Baobab SHALL identify the affected time interval.

---

# 115. Lost transaction recovery

Potentially lost transactions SHALL be recovered through:

```text
source-system reconciliation
event history
external provider records
operator review
business correction
```

rather than guessing.

---

# 116. Re-entry

Business transactions lost because of disaster MAY need controlled re-entry.

---

# 117. Re-entry idempotency

Re-entered external operations SHALL use canonical IDs/idempotency controls where available to avoid duplication.

---

# 118. Payment recovery

Payment recovery SHALL be especially conservative.

External payment-provider state SHALL be reconciled before repeating payment-related actions.

---

# 119. Payment retry risk

An uncertain payment outcome SHALL NOT be retried blindly.

---

# 120. Bank reconciliation after DR

Bank/payment reconciliation SHOULD be prioritised after financial recovery.

---

# 121. Accounting periods

Recovery SHALL preserve accounting-period status.

---

# 122. No automatic period reopening

DR SHALL not automatically reopen accounting periods.

---

# 123. Posting continuity

Transactions occurring after the recovery point but absent from restored ERP state SHALL not be silently backdated without finance policy.

---

# 124. Financial corrections

Corrections SHALL follow ADR-ERP-008 posting/reversal principles.

---

# 125. Business continuity

Baobab SHALL define continuity strategies for critical ERP processes.

---

# 126. Process criticality

Business processes SHALL be classified by recovery importance.

Examples:

```text
supplier payments
customer invoicing
goods receipt
inventory movements
procurement
period close
financial reporting
```

---

# 127. Not every process requires same RTO

Period-end finance may have different continuity requirements from routine master-data administration.

---

# 128. Manual fallback

Where business risk warrants it, continuity plans MAY define temporary manual procedures.

---

# 129. Manual fallback records

Manual fallback SHALL preserve enough evidence for later controlled ERP entry.

---

# 130. Shadow spreadsheet prohibition

Business continuity SHALL not accidentally create an indefinite ungoverned spreadsheet ERP.

---

# 131. Reconciliation after manual operation

Transactions executed outside ERP during disruption SHALL be reconciled after service restoration.

---

# 132. Sequence preservation

Manual continuity procedures SHOULD capture:

```text
business reference
time
amount/quantity
currency
party
approver
supporting evidence
```

where applicable.

---

# 133. Digital Estate continuity

Digital Estates MAY continue selected operations while ERP is unavailable only where business rules explicitly permit eventual ERP reconciliation.

---

# 134. Commerce continuity

Medusa SHALL NOT assume ERP availability for every customer interaction.

However, operations requiring authoritative ERP confirmation SHALL fail or defer according to capability policy.

---

# 135. Deferred integration

Where permitted:

```text
Commerce operation
       │
       ▼
durable local state
       │
       ▼
ERP unavailable
       │
       ▼
integration pending
       │
       ▼
ERP restored
       │
       ▼
idempotent ERP command
       │
       ▼
reconciliation
```

---

# 136. No distributed transaction requirement

Business continuity SHALL retain the local-transaction + outbox/event + reconciliation model.

---

# 137. Control Plane outage

Temporary Control Plane outage SHALL have explicitly defined behaviour.

---

# 138. Context cache

ERP MAY use bounded cached Control Plane-derived Context/routing information where security policy permits.

---

# 139. Security-sensitive suspension

A known revoked/suspended Tenant or capability SHALL not remain indefinitely usable because of stale cache.

---

# 140. Cache expiry

Control Plane-derived authorization/routing caches SHALL have bounded lifetime.

---

# 141. CP recovery

Control Plane recovery is independently governed.

ERP recovery SHALL not reconstruct canonical mappings from guesses if CP data is unavailable.

---

# 142. Mapping backup

Control Plane mappings SHALL have their own backup/recovery architecture.

---

# 143. Cross-system recovery consistency

Because ERP and Control Plane databases are separate, restoring them to different points MAY create mapping inconsistencies.

---

# 144. Mapping reconciliation after recovery

Cross-system recovery SHALL therefore reconcile:

```text
CanonicalEntity
ExternalReference
Mapping
CapabilityBinding
EngineInstance
native ERP record
```

---

# 145. Recovery ordering

Where multiple platform components require recovery, runbooks SHALL define dependency ordering.

Conceptually:

```text
Infrastructure
     ↓
Identity / Secrets
     ↓
Control Plane essentials
     ↓
ERP database
     ↓
ERP runtime
     ↓
Event infrastructure
     ↓
Integrations
     ↓
Reconciliation
     ↓
Normal operations
```

Exact ordering MAY vary.

---

# 146. Observability recovery

Critical monitoring SHALL recover early enough to observe the recovery itself.

---

# 147. Audit of DR

Every material DR invocation SHALL be audited.

---

# 148. DR audit fields

At minimum:

```text
incident
trigger
decision maker
old writer
new writer
recovery point
promotion time
routing change
write-resumption time
validation outcome
```

---

# 149. Recovery telemetry

Recovery operations SHOULD have a common correlation/incident identifier.

---

# 150. DR runbooks

Production SHALL maintain runbooks for at least:

```text
application-instance failure
database-primary failure
database corruption
accidental deletion
regional outage
event-broker outage
object-storage failure
Control Plane outage
credential/key failure
failed deployment
ransomware/security event
```

---

# 151. Database corruption

Logical corruption MAY require PITR rather than standby promotion.

---

# 152. Accidental deletion

If destructive business data is deleted, blindly failing over to a replica may reproduce the deletion.

PITR/reconciliation may be required.

---

# 153. Application defect

A defective release that corrupts data SHALL be treated as a data-recovery incident, not merely a deployment rollback.

---

# 154. Security incident

Security-driven recovery MAY require restoring from a known-clean point.

---

# 155. Compromised credentials

Restoring data SHALL not restore trust in compromised credentials.

Credentials SHALL be rotated/revoked independently.

---

# 156. Ransomware scenario

Backup architecture SHOULD provide sufficient isolation/immutability to survive compromise of ordinary runtime credentials.

---

# 157. Clean-room recovery

Severe security incidents MAY require recovery into isolated clean infrastructure before production reactivation.

---

# 158. Forensic preservation

Security incidents MAY require preservation of evidence before destructive recovery operations.

---

# 159. Backup monitoring

Baobab SHALL alert on:

```text
backup failure
WAL archive failure
backup age threshold
retention failure
integrity failure
```

according to recovery tier.

---

# 160. DR readiness monitoring

Baobab SHOULD monitor:

```text
standby health
replication lag
DR configuration drift
certificate expiry
backup availability
```

---

# 161. Recovery dashboard

Operations SHOULD have a recovery posture dashboard showing:

```text
EngineInstance
recovery tier
last successful backup
last verified restore
replication health
RPO posture
DR readiness
```

---

# 162. Restore-test age

The time since the last successful restore test SHOULD be observable.

---

# 163. DR exercise

Critical ERP deployments SHALL periodically exercise disaster recovery.

---

# 164. Tabletop exercise

Not every exercise needs production failover.

Baobab MAY use:

```text
tabletop exercises
isolated restore exercises
regional failover simulations
```

according to risk.

---

# 165. Full failover test

Critical deployments SHOULD periodically test actual failover mechanics where feasible.

---

# 166. Test success

A DR test SHALL not be considered successful merely because the secondary application starts.

---

# 167. DR test acceptance

Acceptance SHOULD verify:

```text
RTO achieved
RPO understood
ERP accessible
financial state consistent
tenant isolation intact
events functioning
mappings valid
security intact
reconciliation passed
```

---

# 168. Recovery evidence

Every formal recovery exercise SHOULD produce evidence suitable for audit/review.

---

# 169. Improvement actions

DR exercise findings SHALL produce tracked corrective actions.

---

# 170. Capacity

DR capacity SHALL be sufficient for the intended recovery mode.

---

# 171. Reduced-capacity DR

A lower-capacity DR environment MAY be acceptable if the business continuity plan explicitly permits degraded service.

---

# 172. Degraded service

Recovery mode MAY prioritise critical capabilities.

Example:

```text
payments / invoicing
    before
bulk reporting
```

according to business policy.

---

# 173. Capability prioritisation

CapabilityBinding and gateway policy MAY help temporarily restrict non-critical operations during recovery.

---

# 174. Recovery traffic control

Rate limiting MAY protect a recovering ERP from a backlog surge.

---

# 175. Thundering herd

After recovery, thousands of queued integrations SHALL not overwhelm ERP simultaneously.

---

# 176. Controlled backlog release

Pending workloads SHOULD be resumed progressively where necessary.

---

# 177. Event backlog

Event consumers SHALL be designed to catch up without overwhelming ERP or downstream services.

---

# 178. Backpressure

Integration infrastructure SHOULD support backpressure appropriate to its transport.

---

# 179. Recovery order by dependency

Financially causal operations SHOULD be recovered in appropriate order.

For example:

```text
master/reference mappings
        ↓
business documents
        ↓
payments/settlements
        ↓
derived analytics
```

where applicable.

---

# 180. Infrastructure portability

Baobab SHALL avoid making canonical ERP recovery semantics depend on AWS-specific resource identifiers.

---

# 181. AWS implementation

AWS MAY provide production mechanisms for:

```text
compute
managed PostgreSQL
object storage
backup
KMS
regional networking
```

but these remain implementation choices below canonical contracts.

---

# 182. Cloud resource identity

An AWS:

```text
ARN
RDS identifier
availability zone
region code
```

SHALL not become canonical business identity.

---

# 183. Future cloud migration

Moving an EngineInstance to another infrastructure provider SHALL not change:

```text
Tenant
LegalEntity
CanonicalEntity
Market
```

identity.

---

# 184. Infrastructure recovery contract

`nabhold/infrastructure` SHALL own implementation-level DR infrastructure definitions.

---

# 185. ERP recovery contract

`nabhold/baobab-erp` SHALL own ERP-specific recovery validation and application runbooks.

---

# 186. Shared recovery contract

`nabhold/shared` SHOULD define organisation-wide recovery metadata/contracts where cross-repository consistency is required.

---

# 187. Control Plane responsibility

`nabhold/baobab-cp` SHALL own canonical:

```text
EngineInstance
CapabilityBinding
IsolationProfile
```

state affecting authoritative routing.

---

# 188. Finance responsibility

Finance/business owners SHALL approve:

```text
financial recovery acceptance
manual corrections
period implications
material reconciliation exceptions
```

where applicable.

---

# 189. Security responsibility

Security SHALL participate where recovery follows:

```text
credential compromise
data exfiltration
malicious mutation
ransomware
```

---

# 190. Recovery responsibility matrix

Every production EngineInstance SHALL identify accountable roles for:

```text
incident declaration
database recovery
application recovery
routing change
security validation
financial validation
write resumption
business communication
```

---

# 191. No single-person undocumented recovery

Critical recovery SHALL not depend solely on knowledge held by one engineer.

---

# 192. Documentation

Recovery procedures SHALL be version-controlled.

---

# 193. Runbook drift

DR runbooks SHALL be reviewed when infrastructure architecture materially changes.

---

# 194. Migration versus DR

Planned migration and disaster recovery are distinct.

---

# 195. Planned migration

Migration permits controlled:

```text
pre-copy
validation
draining
cutover
rollback
```

---

# 196. Disaster recovery

DR may begin with:

```text
primary unavailable
data freshness uncertain
external dependencies degraded
```

and therefore requires stronger validation.

---

# 197. Tenant migration

Moving a Tenant from a shared to dedicated EngineInstance SHALL follow a controlled migration procedure, not DR.

---

# 198. Migration preservation

Tenant migration SHALL preserve canonical identity.

---

# 199. Migration mapping

Where native ERP records are copied with stable native identity, mappings MAY be migrated accordingly.

Where native IDs change, temporal mappings SHALL be superseded according to ADR-ERP-007.

---

# 200. Migration cutover

Exactly one authoritative write binding SHALL exist at cutover.

---

# 201. Migration reconciliation

Migration SHALL include reconciliation before and after cutover.

---

# 202. Migration rollback

Rollback SHALL define how transactions created after cutover are handled.

A database snapshot alone is not a safe rollback plan once new business writes have occurred.

---

# 203. Engine upgrade recovery

ERP upgrades SHALL include backup and recovery procedures.

---

# 204. Pre-upgrade backup

Material ERP/database upgrades SHALL create or verify an appropriate recovery point before migration.

---

# 205. Schema migration

Irreversible schema migration SHALL be identified before deployment.

---

# 206. Upgrade rollback

Rollback compatibility SHALL be tested where claimed.

---

# 207. Recovery after failed migration

If an upgrade fails after database mutation, recovery MAY require restoring the pre-upgrade recovery point rather than simply redeploying the old container.

---

# 208. Versioned configuration

ERP configuration/localisation versions SHALL be associated with the deployment version used at recovery.

---

# 209. Backup privacy

Retention requirements SHALL account for the fact that deleted or corrected personal information may remain in backups for defined periods.

---

# 210. Backup access requests

Operational restore mechanisms SHALL not be casually used as general-purpose historical data browsing.

---

# 211. Backup deletion

Backup expiry/deletion SHALL follow controlled retention policy.

---

# 212. Legal hold

Where legally required, normal retention expiry MAY be suspended through an explicit legal-hold mechanism.

---

# 213. Data destruction

At the end of required retention, backup destruction SHOULD be verifiable according to infrastructure capabilities and policy.

---

# 214. Recovery security invariant

A recovered system SHALL meet the same security architecture as the primary production system.

---

# 215. No emergency security downgrade

DR SHALL NOT justify:

```text
public database access
shared administrator passwords
disabled MFA
disabled tenant authorization
disabled TLS
unrestricted event access
```

---

# 216. Temporary exception

If an emergency exception is unavoidable, it SHALL be:

```text
explicit
time-bound
risk-accepted
audited
removed after recovery
```

---

# 217. Tenant communication

Material incidents affecting a Tenant SHOULD support controlled communication workflows.

---

# 218. Communication accuracy

Operational teams SHALL distinguish:

```text
service unavailable
service degraded
possible data loss
confirmed data loss
financial inconsistency under investigation
```

rather than making unsupported assurances.

---

# 219. Recovery completion

Recovery SHALL not be declared complete until both:

```text
technical service
```

and required:

```text
business integrity controls
```

have passed.

---

# 220. Recovery state machine

Conceptually:

```text
NORMAL
   │
   ▼
INCIDENT
   │
   ▼
RECOVERY_INITIATED
   │
   ▼
WRITER_FENCED
   │
   ▼
STATE_RESTORED
   │
   ▼
VALIDATING
   │
   ▼
RECONCILING
   │
   ├── failure → REMEDIATION
   │
   ▼
WRITE_AUTHORISED
   │
   ▼
SERVICE_RESTORED
   │
   ▼
POST_RECOVERY_REVIEW
   │
   ▼
NORMAL
```

---

# 221. Recovery events

Operational events MAY include:

```text
erp.recovery.started.v1
erp.recovery.validation-completed.v1
erp.failover.completed.v1
erp.recovery.completed.v1
```

These SHALL be operational/control events rather than business financial events.

---

# 222. Financial events during recovery

Business events SHALL continue to represent committed business facts.

They SHALL not be rewritten merely because recovery occurred.

---

# 223. Recovery metadata

Replayed/recovered event processing MAY carry operational metadata indicating recovery context without changing original business-event identity.

---

# 224. Recovery testing matrix

At minimum, production qualification SHOULD test:

```text
application pod failure

database primary failure

standby promotion

backup restoration

PITR

broker outage

outbox recovery

duplicate event delivery

Control Plane temporary outage

mapping recovery

credential rotation

regional failover simulation

post-recovery reconciliation
```

---

# 225. Financial recovery tests

Tests SHOULD include:

```text
posted supplier invoice before failure

payment committed immediately before failure

open accounting period

closed accounting period

multi-currency transaction

pending outbox event

duplicate inbound event
```

---

# 226. Tenant isolation recovery test

A shared-instance restore SHALL verify:

```text
Tenant A cannot access Tenant B
Tenant B cannot access Tenant A
```

after recovery.

---

# 227. Mapping recovery test

Recovery SHALL verify that:

```text
canonical UUID
    ↓
Mapping
    ↓
ExternalReference
    ↓
native ERP record
```

remains correct.

---

# 228. Outbox recovery test

A committed-but-unpublished ERP event SHALL survive database recovery and eventually publish.

---

# 229. Duplicate recovery test

If publication status is uncertain, duplicate delivery SHALL not produce duplicate financial effects.

---

# 230. Split-brain test

DR exercises SHOULD prove that the old writer cannot continue accepting authoritative traffic after promotion.

---

# 231. Recovery acceptance criteria

A recovery SHALL be accepted only when required controls show:

```text
authoritative writer known
database consistent
application compatible
security intact
tenant isolation intact
mappings valid
critical events recoverable
critical reconciliations passed
```

---

# 232. Non-negotiable invariants

```text
INV-ERP-DR-001
High availability is not backup.

INV-ERP-DR-002
Backup is not disaster recovery.

INV-ERP-DR-003
Disaster recovery is not business continuity.

INV-ERP-DR-004
Every production EngineInstance has explicit recovery objectives.

INV-ERP-DR-005
RPO and RTO are business-approved rather than invented universally.

INV-ERP-DR-006
Exactly one authoritative writer exists for a write capability/Context.

INV-ERP-DR-007
Regional DR does not introduce uncontrolled active-active ERP writes.

INV-ERP-DR-008
The old writer is fenced before replacement writer authority is granted.

INV-ERP-DR-009
Infrastructure health alone does not determine canonical write authority.

INV-ERP-DR-010
Replication does not replace independent backups.

INV-ERP-DR-011
Critical production backups are encrypted.

INV-ERP-DR-012
Backup location obeys ResidencyPolicy.

INV-ERP-DR-013
Shared-instance backups are treated as multi-tenant sensitive datasets.

INV-ERP-DR-014
Backups are periodically restore-tested.

INV-ERP-DR-015
Recovery verifies business integrity, not merely database startup.

INV-ERP-DR-016
Compatible application/configuration artifacts remain recoverable.

INV-ERP-DR-017
Encryption-key recovery is part of DR.

INV-ERP-DR-018
Outbox state is protected with ERP transactional state.

INV-ERP-DR-019
Unpublished committed event intent survives recovery.

INV-ERP-DR-020
Recovery tolerates uncertain publication through idempotent duplicate delivery.

INV-ERP-DR-021
Required audit history participates in recovery.

INV-ERP-DR-022
Material recovery triggers reconciliation.

INV-ERP-DR-023
Deployment-region change does not change Market.

INV-ERP-DR-024
Deployment-region change does not change Tenant.

INV-ERP-DR-025
Deployment-region change does not change LegalEntity.

INV-ERP-DR-026
Canonical entity identity survives recovery.

INV-ERP-DR-027
Infrastructure failover does not arbitrarily create new mappings.

INV-ERP-DR-028
Write resumption occurs only after authoritative routing is established.

INV-ERP-DR-029
Uncertain payments are reconciled before retry.

INV-ERP-DR-030
DR does not automatically reopen accounting periods.

INV-ERP-DR-031
Lost transactions are reconstructed from evidence rather than guessed.

INV-ERP-DR-032
Manual continuity transactions are subsequently reconciled.

INV-ERP-DR-033
Control Plane recovery never reconstructs canonical mappings by guesswork.

INV-ERP-DR-034
Cross-system restore-point differences trigger mapping reconciliation.

INV-ERP-DR-035
Recovery actions are auditable.

INV-ERP-DR-036
Recovery infrastructure preserves production security controls.

INV-ERP-DR-037
Backup success without restore testing is insufficient evidence of recoverability.

INV-ERP-DR-038
Failover testing verifies tenant isolation.

INV-ERP-DR-039
Failover testing verifies event recovery.

INV-ERP-DR-040
Failover testing verifies mapping integrity.

INV-ERP-DR-041
Application rollback does not reverse business transactions.

INV-ERP-DR-042
Queue/outbox deletion is never an ordinary recovery technique.

INV-ERP-DR-043
Tenant migration is distinct from disaster recovery.

INV-ERP-DR-044
Tenant migration preserves canonical identity.

INV-ERP-DR-045
Migration cutover has exactly one authoritative writer.

INV-ERP-DR-046
Emergency recovery does not silently weaken authorization.

INV-ERP-DR-047
A recovered service is not considered healthy until required business validation succeeds.

INV-ERP-DR-048
DR procedures are version-controlled and exercised.

INV-ERP-DR-049
Critical recovery knowledge is not dependent upon one individual.

INV-ERP-DR-050
Correctness takes precedence over premature write availability.
```

---

# 233. Reference recovery topology

```text
                         CONTROL PLANE
                              │
                       authoritative
                    CapabilityBinding
                              │
                              ▼
                   ┌───────────────────┐
                   │ PRIMARY REGION    │
                   │                   │
Consumers ────────►│ ERP Application   │
                   │        │          │
                   │        ▼          │
                   │ PostgreSQL Primary│
                   └────────┬──────────┘
                            │
                     replication
                            │
                            ▼
                   ┌───────────────────┐
                   │ DR REGION         │
                   │                   │
                   │ ERP Application   │
                   │   standby/off     │
                   │        │          │
                   │        ▼          │
                   │ PostgreSQL Standby│
                   └───────────────────┘

                            │
                            │ WAL / Backup
                            ▼
                   ┌───────────────────┐
                   │ Protected Backup  │
                   │ Storage           │
                   └───────────────────┘
```

The DR region SHALL not become writable merely because it exists.

---

# 234. Database-loss scenario

```text
Primary database failure
        │
        ▼
Detect
        │
        ▼
Can primary recover within objective?
      │             │
     YES            NO
      │             │
      ▼             ▼
recover local     invoke failover
                    │
                    ▼
                fence primary
                    │
                    ▼
              validate standby
                    │
                    ▼
                  promote
                    │
                    ▼
               route writes
                    │
                    ▼
               ERP validation
                    │
                    ▼
              reconciliation
                    │
                    ▼
               resume normal
```

---

# 235. Logical-corruption scenario

Replication alone is insufficient:

```text
Bad operation
     │
     ▼
Primary corrupted
     │
     ▼
Replication
     │
     ▼
Standby corrupted too
```

Recovery MAY instead require:

```text
identify safe recovery point
        │
        ▼
PITR into isolated environment
        │
        ▼
validate
        │
        ▼
determine affected transactions
        │
        ▼
reconcile
        │
        ▼
controlled production restoration
```

---

# 236. Regional-disaster scenario

```text
Primary Region Unavailable
           │
           ▼
Declare Disaster
           │
           ▼
Establish Old Writer Fenced
           │
           ▼
Determine DR Data Freshness
           │
           ▼
Within accepted RPO?
       │          │
      YES         NO/UNKNOWN
       │          │
       ▼          ▼
    promote     assess business
      DR         consequences
       │          │
       └────┬─────┘
            ▼
       Restore Services
            │
            ▼
        Validate Context
            │
            ▼
      Validate Mappings
            │
            ▼
      Financial Controls
            │
            ▼
       Reconciliation
            │
            ▼
      Authorise Writes
```

---

# 237. Recovery after uncertain payment

```text
Payment request initiated
        │
        ▼
External provider processes
        │
        X
ERP region fails before
final state confirmed
        │
        ▼
ERP restored
        │
        ▼
DO NOT blindly retry
        │
        ▼
Query/reconcile provider
        │
    ┌───┴────┐
    ▼        ▼
Settled    Not settled
    │        │
    ▼        ▼
record/     governed
reconcile   retry
```

This pattern is mandatory for financially irreversible external operations.

---

# 238. Shared-instance recovery consequence

Suppose:

```text
ERP-AF-SOUTH-01

├── NABHOLD AD_Client
├── THAMANI AD_Client
└── ZURIBEANS AD_Client
```

A database-level restore affects all three.

Therefore:

> **Shared runtime economics create shared recovery blast radius even when logical tenant isolation remains strong.**

This is an explicit architectural trade-off.

A Tenant requiring independently scheduled:

```text
restore
failover
RPO
RTO
maintenance
```

may therefore require a dedicated EngineInstance.

---

# 239. Business continuity decision matrix

Conceptually:

| Capability | ERP unavailable | Continuity approach |
|---|---|---|
| Customer browsing | Usually continue | No ERP write required |
| Commerce cart | Usually continue | Commerce-local state |
| Commerce checkout | Policy-dependent | Queue/defer ERP handoff where safe |
| Purchase-order creation | Policy-dependent | Controlled deferred capture |
| Goods receipt | Operationally sensitive | Manual/deferred procedure if approved |
| Supplier invoice posting | Financially sensitive | Prefer controlled outage/defer |
| Payment execution | Highly sensitive | No blind fallback/retry |
| Reporting | Degraded/read-only possible | Cached/previous reporting where labelled |
| Period close | Critical financial control | Defer until ERP/reconciliation healthy |

This matrix is illustrative; LegalEntity-specific continuity policies SHALL be explicitly approved.

---

# 240. Recovery hierarchy

Baobab SHALL use the following hierarchy when deciding how aggressively to restore service:

```text
1. Protect people and legal obligations

2. Protect financial/data integrity

3. Prevent split-brain

4. Preserve tenant isolation

5. Preserve canonical identity

6. Preserve audit/event intent

7. Establish authoritative state

8. Reconcile

9. Restore critical business capabilities

10. Restore non-critical capabilities
```

---

# 241. Definition of done

ADR-ERP-012 SHALL be considered implemented when:

- [ ] Every production EngineInstance has a recovery tier.
- [ ] RPO is documented.
- [ ] RTO is documented.
- [ ] HA topology is documented.
- [ ] DR topology is documented.
- [ ] authoritative writer semantics are implemented.
- [ ] split-brain prevention exists.
- [ ] failover fencing exists.
- [ ] database replication health is monitored.
- [ ] replication lag is monitored.
- [ ] PostgreSQL backup exists.
- [ ] PITR exists where required.
- [ ] WAL archival is monitored where required.
- [ ] backup encryption exists.
- [ ] backup ResidencyPolicy is enforced.
- [ ] backup retention is defined.
- [ ] backup catalogue exists.
- [ ] restore testing is scheduled.
- [ ] restore tests validate ERP functionality.
- [ ] restore tests validate tenant isolation.
- [ ] restore tests validate mappings.
- [ ] restore tests validate financial state.
- [ ] compatible deployment artifacts are retained.
- [ ] infrastructure configuration is reproducible.
- [ ] secrets recovery is documented.
- [ ] encryption-key recovery is documented.
- [ ] external dependencies are documented.
- [ ] outbox participates in recovery.
- [ ] inbox/deduplication recovery is addressed.
- [ ] audit recovery is addressed.
- [ ] post-recovery reconciliation exists.
- [ ] regional failover procedure exists.
- [ ] Control Plane routing update procedure exists.
- [ ] write-resumption approval exists.
- [ ] uncertain-payment procedure exists.
- [ ] business continuity procedures exist for critical capabilities.
- [ ] manual fallback is governed where allowed.
- [ ] deferred integrations are idempotent.
- [ ] Control Plane outage behaviour is documented.
- [ ] cross-system recovery reconciliation exists.
- [ ] DR actions are audited.
- [ ] recovery dashboards/alerts exist.
- [ ] DR runbooks are version-controlled.
- [ ] DR exercises occur periodically.
- [ ] split-brain testing exists.
- [ ] regional recovery testing exists where required.
- [ ] post-failover event recovery is tested.
- [ ] post-failover tenant isolation is tested.
- [ ] recovery acceptance criteria are documented.
- [ ] responsible recovery roles are documented.

---

# 242. Final architectural position

Baobab ERP SHALL not optimise disaster recovery around the simplistic objective:

```text
"bring the server back online"
```

The real objective is:

```text
Recover the correct
authoritative
secure
tenant-isolated
financially coherent
auditable
event-consistent
ERP state
```

and only then safely resume business operations.

The complete recovery chain is therefore:

```text
Failure
   │
   ▼
Detect
   │
   ▼
Contain
   │
   ▼
Fence
   │
   ▼
Determine Authoritative State
   │
   ▼
Restore / Promote
   │
   ▼
Validate Security
   │
   ▼
Validate Tenant Isolation
   │
   ▼
Validate Canonical Mappings
   │
   ▼
Validate Financial State
   │
   ▼
Recover Event Intent
   │
   ▼
Reconcile
   │
   ▼
Authorise Writes
   │
   ▼
Resume Critical Capabilities
   │
   ▼
Drain Backlogs
   │
   ▼
Reconcile Again
   │
   ▼
Return to Normal Operations
```

The definitive rule is:

> **Recovery is complete only when Baobab knows which state is authoritative, can prove the tenant and financial boundaries remain intact, and can reconcile the recovered ERP with the rest of the platform.**

Availability without that proof is not recovery.

It is uncertainty with an endpoint.