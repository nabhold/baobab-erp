# ADR-ERP-011 — ERP Observability, Audit, Reconciliation and Operational Control Architecture

**Status:** Accepted  
**Decision class:** ERP / Observability / Audit / Reconciliation / Operations / Reliability  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`, `nabhold/infrastructure`, event infrastructure, operational tooling and authorised consumers  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-010  
**Date:** 2026-09-02

---

# 1. Decision

The Baobab ERP Engine SHALL implement observability, audit, reconciliation and operational control as first-class architectural capabilities.

They SHALL NOT be treated as deployment-time additions.

The production operating model SHALL distinguish:

```text
Observability
    What is the system doing?

Audit
    Who or what changed business/security state?

Reconciliation
    Do independently maintained representations agree?

Operational Control
    Can operators safely diagnose, contain and recover the system?
```

These capabilities overlap.

They SHALL NOT be conflated.

---

# 2. Governing principle

The governing rule is:

> **A financial system is not production-grade merely because transactions succeed; Baobab must be able to prove what happened, detect when representations diverge, identify the responsible Context, and recover safely.**

For every materially important ERP operation Baobab SHOULD eventually be able to answer:

```text
What happened?

When did it happen?

Which canonical entity was affected?

Which Tenant was involved?

Which LegalEntity was involved?

Which Market was involved?

Which EngineInstance processed it?

Which principal or workload initiated it?

Which request caused it?

Which event resulted from it?

Was the event delivered?

Did downstream systems process it?

Did the corresponding systems reconcile?

Were retries involved?

Did an operator intervene?
```

---

# 3. Four operational planes

The architecture SHALL distinguish four related operational planes.

```text
┌─────────────────────────────────────┐
│           Observability             │
│ logs • metrics • traces • health    │
├─────────────────────────────────────┤
│               Audit                 │
│ business • security • admin         │
├─────────────────────────────────────┤
│          Reconciliation             │
│ compare • detect • classify • fix   │
├─────────────────────────────────────┤
│       Operational Control           │
│ alert • diagnose • contain • recover│
└─────────────────────────────────────┘
```

---

# 4. Observability is not audit

Application logs SHALL NOT be treated as the authoritative audit ledger.

Logs may be:

```text
sampled
aggregated
rotated
redacted
reformatted
```

Audit records have different integrity and retention requirements.

---

# 5. Audit is not reconciliation

An audit trail can prove that an invoice was posted.

It does not prove that:

```text
Trade
ERP
payment provider
warehouse
analytics
```

all agree about the resulting business state.

That is reconciliation.

---

# 6. Reconciliation is not monitoring

Monitoring can report:

```text
all services healthy
```

while business data is inconsistent.

Reconciliation therefore remains a separate control mechanism.

---

# 7. Operational telemetry model

Baobab SHALL use the standard telemetry categories:

```text
Logs
Metrics
Traces
```

with supporting:

```text
Health
Readiness
Operational Events
Audit
```

---

# 8. Structured logging

Production ERP components SHALL emit structured logs.

Preferred conceptual structure:

```json
{
  "timestamp": "2026-09-02T15:20:31.431Z",
  "severity": "INFO",
  "service": "baobab-erp-api",
  "engine": "erp",
  "engine_instance_id": "<uuid>",
  "tenant_id": "<uuid>",
  "legal_entity_id": "<uuid>",
  "market_id": "<uuid>",
  "correlation_id": "<uuid>",
  "trace_id": "<trace-id>",
  "operation": "supplier_invoice.post",
  "canonical_entity_id": "<uuid>",
  "outcome": "success"
}
```

Fields SHALL be omitted where not applicable.

---

# 9. Machine-readable logs

Production components SHALL NOT rely primarily on free-form human log strings.

This:

```text
Invoice posted successfully for customer
```

is insufficient operational telemetry.

Structured dimensions are required.

---

# 10. Log levels

Baobab SHALL standardise semantic log levels.

At minimum:

```text
TRACE
DEBUG
INFO
WARN
ERROR
```

where supported.

---

# 11. TRACE and DEBUG

Verbose diagnostic logging SHALL normally be disabled or restricted in production.

It SHALL NOT expose sensitive ERP data when enabled.

---

# 12. INFO

`INFO` SHOULD represent meaningful normal operational milestones.

It SHALL not produce one arbitrary log entry for every internal method invocation.

---

# 13. WARN

`WARN` SHOULD represent recoverable or unusual conditions requiring potential attention.

---

# 14. ERROR

`ERROR` SHALL represent failed operations or conditions requiring investigation.

Expected client validation failures SHALL not automatically become infrastructure errors.

---

# 15. Log correlation

Every externally initiated ERP operation SHALL receive or generate a `correlation_id`.

---

# 16. Correlation propagation

Correlation SHALL propagate across:

```text
API Gateway
   ↓
ERP API
   ↓
ERP Application Service
   ↓
iDempiere extension
   ↓
Outbox
   ↓
Canonical Event
   ↓
Consumer
```

where technically possible.

---

# 17. Correlation versus trace

`correlation_id` and `trace_id` SHALL remain conceptually distinct.

```text
correlation_id
    business/application workflow correlation

trace_id
    distributed execution trace
```

They MAY coincide in implementations where deliberately designed, but SHALL not be assumed equivalent.

---

# 18. Causation

Canonical events SHALL retain `causation_id` according to ADR-ERP-006.

This permits reconstruction such as:

```text
API command
   ↓ caused
ERP transaction
   ↓ caused
ERP event
   ↓ caused
Trade projection update
```

---

# 19. Trace propagation

Baobab SHOULD adopt W3C-compatible distributed tracing conventions through its observability stack.

Trace context SHOULD propagate across supported synchronous service boundaries.

---

# 20. Asynchronous traces

Trace relationships SHOULD continue across event publication/consumption where supported.

The absence of one continuous synchronous span SHALL not destroy correlation.

---

# 21. Trace sampling

Tracing MAY be sampled for ordinary operations.

Security, audit and reconciliation correctness SHALL NOT depend upon trace sampling.

---

# 22. Metrics

Metrics SHALL represent aggregate operational behaviour.

They SHALL not be used as a substitute for transaction-level audit.

---

# 23. Metric naming

Metric names SHOULD use stable technical semantics.

Examples:

```text
erp_api_requests_total

erp_api_request_duration_seconds

erp_outbox_pending

erp_outbox_publish_total

erp_outbox_publish_failures_total

erp_inbox_processing_total

erp_reconciliation_runs_total

erp_reconciliation_mismatches_total

erp_background_jobs_pending

erp_mapping_resolution_failures_total
```

Exact naming SHALL be standardised in `nabhold/shared` or the observability contract.

---

# 24. Metric cardinality

Metric labels SHALL avoid uncontrolled high cardinality.

The following SHOULD generally NOT become metric labels:

```text
invoice UUID
order UUID
customer ID
supplier ID
email address
document number
correlation ID
trace ID
```

These belong in logs/traces/audit.

---

# 25. Tenant metric cardinality

Tenant identifiers MAY be inappropriate metric labels once tenant count becomes large.

Baobab SHALL consciously decide where tenant-level metrics are operationally justified.

---

# 26. Sensitive metrics

Metrics SHALL not expose:

```text
tax identifiers
bank account numbers
customer names
supplier names
invoice descriptions
personal data
```

as labels.

---

# 27. Golden operational signals

ERP infrastructure SHOULD monitor at least:

```text
traffic
latency
errors
saturation
```

for exposed services.

---

# 28. Business-operational signals

ERP SHALL additionally monitor business-processing indicators such as:

```text
unposted documents
stuck workflows
failed background processes
outbox backlog
inbox failures
mapping failures
reconciliation mismatches
regulatory submission failures
```

---

# 29. Health endpoints

ERP services SHALL expose appropriate health information.

At minimum the architecture SHALL distinguish:

```text
liveness
readiness
```

---

# 30. Liveness

Liveness answers:

> Is this process alive enough that restarting it may be appropriate if it fails?

It SHALL NOT perform expensive dependency checks.

---

# 31. Readiness

Readiness answers:

> Can this instance safely receive new workload?

Readiness MAY depend upon critical runtime dependencies.

---

# 32. Startup health

Where orchestration requires it, startup health MAY be separate from liveness/readiness.

---

# 33. Dependency health

Dependency failure SHALL not automatically imply that the ERP process itself should be repeatedly restarted.

Example:

```text
event broker unavailable
```

may make event publishing degraded while local ERP transaction processing remains valid because the transactional outbox persists events.

---

# 34. Degraded state

Baobab SHOULD represent:

```text
healthy
degraded
unavailable
```

where useful rather than reducing every condition to binary health.

---

# 35. Business readiness

Infrastructure readiness SHALL NOT be confused with business readiness.

An ERP pod can be healthy while:

```text
accounting period is closed
Market is suspended
CapabilityBinding is inactive
localisation is uncertified
```

Those are business/control conditions.

---

# 36. Service Level Indicators

Production ERP capabilities SHALL define measurable Service Level Indicators where business criticality warrants them.

Possible SLIs include:

```text
API availability
API latency
successful command rate
event publication delay
reconciliation completion
background-process delay
```

---

# 37. Service Level Objectives

SLOs SHALL be defined by capability and criticality rather than applying one arbitrary platform-wide percentage.

---

# 38. Availability SLO

Availability SHOULD measure whether an authorised request can obtain the expected service.

It SHALL not count deliberate policy rejection as infrastructure failure.

---

# 39. Latency SLO

Latency SHALL be measured at defined boundaries.

Example:

```text
gateway → ERP API response
```

rather than mixing API latency with asynchronous downstream settlement time.

---

# 40. Asynchronous SLO

Asynchronous capabilities MAY define:

```text
event committed → event published
event published → consumer processed
```

as separate indicators.

---

# 41. Error budget

Where mature SRE practices are adopted, SLOs MAY be associated with error budgets.

Error budgets SHALL inform operational decisions rather than becoming accounting theatre.

---

# 42. SLO ownership

Every production SLO SHALL have:

```text
owner
measurement definition
data source
review cadence
```

---

# 43. Availability target does not define DR

SLO, RTO and RPO are distinct.

```text
SLO = expected service quality

RTO = acceptable recovery time

RPO = acceptable recoverable data-loss window
```

---

# 44. ERP audit architecture

Baobab SHALL distinguish:

```text
Business Audit
Security Audit
Administrative Audit
Integration Audit
```

---

# 45. Business audit

Business audit records significant ERP business actions.

Examples:

```text
purchase order completed
goods receipt completed
supplier invoice posted
payment completed
journal posted
accounting period opened
accounting period closed
```

---

# 46. Security audit

Security audit records security-sensitive actions.

Examples:

```text
authentication
authorization denial
role change
credential revocation
break-glass use
privileged access
```

---

# 47. Administrative audit

Administrative audit records changes such as:

```text
localisation configuration
ERP role configuration
EngineInstance configuration
mapping administration
financial configuration
integration configuration
```

where applicable.

---

# 48. Integration audit

Integration audit records significant interoperability activity such as:

```text
command received
external reference resolved
mapping created
event emitted
regulatory submission made
reconciliation correction approved
```

---

# 49. Audit identity

Audit records SHALL identify both:

```text
human principal
```

and:

```text
executing workload
```

where one acts through another.

---

# 50. Audit Context

Tenant-sensitive audit records SHALL retain applicable historical:

```text
Tenant
LegalEntity
Market
EngineInstance
canonical entity
```

Context.

---

# 51. Historical Context

Audit records SHALL retain the Context that applied when the action occurred.

They SHALL not dynamically reinterpret history using today's organisation mappings.

---

# 52. Audit time

Audit SHALL distinguish relevant timestamps.

Examples:

```text
occurred_at
recorded_at
effective_at
```

where semantics require them.

---

# 53. Audit immutability

Historical audit records SHALL not be casually mutable.

Corrections SHOULD append new records rather than rewrite history.

---

# 54. Audit deletion

Audit retention SHALL follow:

```text
legal
financial
security
privacy
operational
```

requirements.

A user deleting their account SHALL not automatically erase legally required financial audit history.

---

# 55. Audit storage

Audit MAY be stored in multiple systems for different purposes.

No implementation SHALL assume application logs alone constitute durable audit storage.

---

# 56. Audit access

Audit access SHALL itself be authorised.

---

# 57. Audit access audit

Access to highly sensitive audit records SHOULD itself be auditable.

---

# 58. Native iDempiere audit

Where iDempiere provides native change/audit mechanisms, Baobab SHOULD use them appropriately.

Canonical audit requirements MAY require additional records outside native iDempiere semantics.

---

# 59. Native audit preservation

Baobab SHALL NOT remove useful native ERP audit information merely because canonical audit exists.

---

# 60. Canonical versus native audit

The layers answer different questions.

```text
Canonical audit:
    what Baobab operation occurred?

Native audit:
    what changed inside iDempiere?
```

Both may be needed for investigation.

---

# 61. Reconciliation architecture

Reconciliation SHALL be a first-class production capability.

Its governing rule is:

> **Whenever two independently persisted representations are expected to agree, Baobab SHALL define how disagreement is detected and resolved.**

---

# 62. Reconciliation is inevitable

Event-driven integration reduces coupling.

It does not eliminate:

```text
partial failure
delayed delivery
duplicate processing
operator error
external-system failure
software defects
migration defects
```

Therefore reconciliation is mandatory.

---

# 63. Reconciliation dimensions

Baobab SHALL support reconciliation by:

```text
identity
state
quantity
amount
currency
status
count
time
```

as appropriate.

---

# 64. Identity reconciliation

Identity reconciliation verifies that expected canonical/native mappings exist and remain valid.

Example:

```text
Canonical Product
        ↕
iDempiere M_Product
```

---

# 65. State reconciliation

State reconciliation verifies lifecycle agreement.

Example:

```text
Trade:
    order fulfilled

ERP:
    expected accounting representation missing
```

---

# 66. Quantity reconciliation

Quantity reconciliation compares inventory or movement quantities where two systems maintain relevant representations.

---

# 67. Amount reconciliation

Amount reconciliation compares financial values.

Comparison SHALL account for:

```text
currency
rounding
tax
exchange rates
fees
timing
```

before declaring mismatch.

---

# 68. Count reconciliation

Count reconciliation MAY compare aggregate numbers before expensive record-level comparison.

Example:

```text
Trade orders exported = 1,042
ERP representations expected = 1,042
```

---

# 69. Layered reconciliation

Reconciliation SHOULD proceed from inexpensive to detailed controls.

```text
count
  ↓
aggregate totals
  ↓
entity-level comparison
  ↓
field-level investigation
```

where appropriate.

---

# 70. Reconciliation pair

Every reconciliation definition SHALL identify:

```text
source
target
entity type
scope
comparison rule
tolerance
schedule
owner
resolution policy
```

---

# 71. Authority

Every reconciliation SHALL know which system is authoritative for the field/state being compared.

---

# 72. No universal source of truth

Authority MAY differ by attribute.

Example:

```text
Trade:
    commerce order lifecycle

ERP:
    accounting posting

Payment provider:
    external settlement observation
```

---

# 73. Reconciliation does not mean overwrite

Detection of disagreement SHALL NOT automatically permit one system to overwrite another.

---

# 74. Reconciliation result

Recommended result states:

```text
matched
mismatch
expected_difference
pending
unresolvable
corrected
waived
```

---

# 75. Expected difference

Some differences are legitimate because of timing or domain semantics.

They SHALL be classified rather than treated as errors.

---

# 76. Tolerance

Financial/quantity comparisons MAY require explicit tolerances.

Tolerance SHALL be:

```text
documented
currency/UOM aware
business-approved
```

not arbitrary floating-point epsilon.

---

# 77. Financial precision

Reconciliation SHALL use decimal-safe financial representations.

Binary floating-point SHALL NOT determine financial equality.

---

# 78. Reconciliation scope

A reconciliation run SHALL carry trusted Context.

At minimum:

```text
Tenant
LegalEntity where applicable
Market where applicable
entity family
time window
```

---

# 79. Cross-tenant reconciliation

One Tenant's reconciliation process SHALL not read another Tenant's financial data unless explicitly authorised.

---

# 80. Reconciliation schedule

Reconciliation MAY be:

```text
continuous
event-triggered
hourly
daily
period-end
manual
```

according to business risk.

---

# 81. High-risk reconciliation

Payments and financial postings SHOULD receive stronger reconciliation than low-risk content projections.

---

# 82. Event-triggered reconciliation

An event MAY schedule reconciliation.

It SHALL not prove reconciliation by itself.

---

# 83. Periodic reconciliation

Periodic sweeps SHALL exist for important integrations even when event processing appears healthy.

---

# 84. Missing event detection

Reconciliation SHALL detect situations where:

```text
ERP transaction exists
but
expected canonical event was never consumed
```

or vice versa.

---

# 85. Outbox reconciliation

The ERP SHALL monitor:

```text
committed ERP records
        ↕
expected outbox events
```

for critical event-producing operations.

---

# 86. Outbox backlog

Outbox backlog SHALL be measurable.

---

# 87. Outbox age

The age of the oldest unpublished event SHALL be observable.

This is often more meaningful than backlog count alone.

---

# 88. Published state

An outbox record marked `published` SHALL mean the configured publication boundary has acknowledged it according to transport semantics.

It SHALL not mean every downstream consumer processed it.

---

# 89. Consumer reconciliation

Critical consumers SHALL expose sufficient processing state to determine whether events were:

```text
received
deduplicated
processed
failed
quarantined
```

---

# 90. Inbox observability

Where transactional inbox/deduplication is used, Baobab SHALL observe:

```text
pending
processed
failed
duplicate
dead-lettered
```

states.

---

# 91. Duplicate metric

Duplicate delivery SHOULD be measurable.

Duplicates are expected under at-least-once delivery and do not automatically indicate failure.

---

# 92. Duplicate side effect

A duplicate financial side effect IS a correctness failure.

---

# 93. Mapping reconciliation

Baobab SHALL periodically verify important mappings.

Examples:

```text
mapping points to native record that no longer exists

native record exists but mapping is missing

mapping belongs to wrong Client

duplicate active mapping exists
```

---

# 94. Binding reconciliation

Control Plane SHALL be able to verify that active CapabilityBindings reference:

```text
active Engine
active EngineInstance
compatible IsolationProfile
valid Market
valid capability
```

---

# 95. Configuration reconciliation

Production ERP configuration SHOULD be compared against approved configuration where material.

---

# 96. Financial configuration drift

Changes to:

```text
accounting schema
tax configuration
document type
period controls
currency configuration
```

SHALL be observable and audited.

---

# 97. Localisation reconciliation

ADR-ERP-009 localisation certification SHOULD be reconcilable against deployed:

```text
plugin versions
configuration versions
EngineInstance version
```

---

# 98. Reconciliation record

A reconciliation run SHOULD conceptually contain:

```text
reconciliation_id
definition_id
Context
window_start
window_end
started_at
completed_at
source_count
target_count
matched_count
mismatch_count
status
```

---

# 99. Reconciliation item

Individual mismatches SHOULD conceptually record:

```text
canonical_entity_id
source_reference
target_reference
mismatch_type
expected_value
observed_value
severity
status
```

with sensitive values protected appropriately.

---

# 100. Reconciliation severity

Recommended severity classes:

```text
informational
low
medium
high
critical
```

---

# 101. Critical mismatch

Examples MAY include:

```text
payment settled but no ERP accounting record

supplier invoice posted twice

cross-tenant mapping detected

posted transaction missing expected ledger consequence
```

---

# 102. Reconciliation ownership

Every production reconciliation definition SHALL have an operational/business owner.

---

# 103. Unowned mismatch

A mismatch SHALL never be permitted to remain indefinitely because no team owns it.

---

# 104. Reconciliation queue

Unresolved mismatches SHALL enter a governed work queue.

---

# 105. Reconciliation assignment

A mismatch SHOULD support:

```text
owner
assignee
severity
due date
status
resolution
```

---

# 106. Automated correction

Automated reconciliation repair MAY be allowed only where:

```text
authority is unambiguous
correction is idempotent
risk is understood
operation is auditable
```

---

# 107. Financial automatic repair

Automatic correction of posted financial data SHALL be highly constrained.

---

# 108. Compensating correction

Where historical financial state cannot be rewritten, reconciliation SHALL produce appropriate:

```text
reversal
adjustment
corrective document
```

through ERP business processes.

---

# 109. No SQL repair

Operators SHALL NOT normally resolve financial reconciliation failures by directly editing PostgreSQL rows.

---

# 110. Manual correction

Manual corrections SHALL use authorised ERP/application workflows and remain auditable.

---

# 111. Reconciliation waiver

A mismatch MAY be formally waived where it is an accepted difference.

A waiver SHALL contain:

```text
reason
approver
scope
effective period
```

where appropriate.

---

# 112. Permanent ignore is prohibited

Operators SHALL not suppress mismatches indefinitely through undocumented filters.

---

# 113. Operational control plane

The Baobab Control Plane SHALL expose operational metadata necessary to understand:

```text
Engine
EngineInstance
CapabilityBinding
IsolationProfile
Market
Mapping
```

state.

It SHALL not become the replacement for infrastructure monitoring.

---

# 114. EngineInstance operational state

An EngineInstance SHOULD expose a state model such as:

```text
provisioning
healthy
degraded
maintenance
draining
unavailable
retired
```

distinct from lifecycle status where necessary.

---

# 115. Maintenance

Planned maintenance SHALL be representable.

---

# 116. Draining

Before planned shutdown/migration, an EngineInstance SHOULD support a draining state where new work is redirected or rejected while existing work completes.

---

# 117. Routing and health

Capability routing MAY consider operational health.

However, failover SHALL obey ADR-ERP-003 authority and split-brain rules.

---

# 118. No blind health failover

A failed health check SHALL not automatically make a secondary ERP instance writable.

---

# 119. Authoritative write binding

Only the EngineInstance selected by the authoritative active write binding may accept new canonical write operations.

---

# 120. Incident detection

Incidents MAY originate from:

```text
metrics
logs
traces
security telemetry
reconciliation
business reports
user reports
external provider alerts
```

---

# 121. Incident classification

Baobab SHOULD define severity classes.

Example:

```text
SEV-1
SEV-2
SEV-3
SEV-4
```

with organisation-approved definitions.

---

# 122. Severity is business impact

Incident severity SHALL be based primarily on impact, not log-level volume.

---

# 123. Tenant-specific incident

A severe outage affecting one major Tenant MAY be higher priority than a minor degradation affecting all tenants.

---

# 124. Financial integrity incident

Potential financial corruption or cross-tenant disclosure SHALL receive elevated severity even if transaction volume is small.

---

# 125. Incident Context

Incident records SHOULD identify:

```text
affected EngineInstance
affected capabilities
affected Tenants
affected Markets
affected integrations
start time
detected time
```

where known.

---

# 126. Operational runbooks

Production ERP SHALL have runbooks for recurring failure modes.

---

# 127. Minimum runbooks

Runbooks SHOULD cover at least:

```text
ERP API unavailable

PostgreSQL unavailable

event broker unavailable

outbox backlog

consumer backlog

mapping failure

reconciliation mismatch

failed iDempiere process

EngineInstance failover

certificate expiry

localisation failure

database restore

tenant migration

security incident

regulatory adapter outage
```

---

# 128. Runbook quality

A runbook SHOULD contain:

```text
symptoms
likely causes
diagnostic queries
safe actions
unsafe actions
escalation
recovery verification
```

---

# 129. Unsafe actions

Runbooks SHALL explicitly identify dangerous operations such as:

```text
direct financial SQL edits

clearing outbox tables

replaying arbitrary events

changing AD_Client_ID

opening accounting periods

disabling tenant filters
```

---

# 130. Operational tooling

Operational tools SHALL use authenticated APIs or approved administrative interfaces where possible.

---

# 131. Database console

Database console access SHALL be an exceptional diagnostic/administrative tool, not normal business operations.

---

# 132. Diagnostic query

Read-only diagnostic SQL MAY be permitted to authorised operators.

It SHALL respect data sensitivity and tenant boundaries.

---

# 133. Production mutation

Production data mutation through direct SQL SHALL require exceptional controlled procedures.

---

# 134. Incident timeline

Major incidents SHALL maintain a timeline containing significant:

```text
detection
diagnosis
mitigation
recovery
verification
```

events.

---

# 135. Post-incident review

Material incidents SHOULD result in a post-incident review.

---

# 136. Review purpose

Post-incident review SHALL focus on:

```text
technical causes
systemic causes
detection gaps
control gaps
recovery gaps
preventive actions
```

rather than blame.

---

# 137. Recovery verification

An incident SHALL not be considered resolved merely because HTTP health checks become green.

Verification MAY require:

```text
transaction tests
outbox drainage
consumer recovery
reconciliation
financial validation
```

---

# 138. Alerting

Alerts SHALL represent actionable conditions.

---

# 139. Alert fatigue

Baobab SHALL avoid alerts for conditions that require no action.

---

# 140. Alert ownership

Every production alert SHALL have:

```text
owner
severity
runbook
```

or equivalent operational guidance.

---

# 141. Recommended ERP alerts

Examples:

```text
ERP API sustained error rate

database unavailable

database saturation

outbox oldest-event age threshold

outbox failure rate

dead-letter growth

mapping resolution spike

reconciliation critical mismatch

certificate approaching expiry

disk/storage pressure

backup failure

replication/DR failure
```

---

# 142. Financial alerts

Business/financial controls MAY additionally alert on:

```text
unexpected posting failure

period-control violation

duplicate external payment reference

unbalanced reconciliation

unexpected currency configuration
```

---

# 143. Alert Context

Alerts SHOULD contain enough identifiers to begin investigation without embedding sensitive business data.

---

# 144. Dashboards

Baobab SHOULD maintain different dashboards for different operational questions.

---

# 145. Platform dashboard

Platform dashboard SHOULD show:

```text
ERP availability
latency
errors
resource saturation
database health
event infrastructure
```

---

# 146. Integration dashboard

Integration dashboard SHOULD show:

```text
outbox backlog
event publication delay
consumer lag
DLQ
mapping failures
external adapter health
```

---

# 147. Reconciliation dashboard

Reconciliation dashboard SHOULD show:

```text
runs
mismatches
severity
age
owner
resolution status
```

---

# 148. Tenant dashboard

Where operationally justified, authorised teams MAY view tenant-specific:

```text
service status
processing failures
reconciliation state
```

without exposing other Tenants.

---

# 149. Financial-control dashboard

Finance operations MAY require controls such as:

```text
unposted documents
failed postings
open reconciliation items
payment mismatches
period-close readiness
```

---

# 150. Dashboard is not authority

A dashboard projection SHALL not become the authoritative ERP record.

---

# 151. Period close observability

Accounting period close SHOULD include explicit operational controls.

---

# 152. Period-close checks

Before close, Baobab SHOULD be able to evaluate:

```text
unposted documents
failed integrations
critical reconciliation mismatches
pending payments
unresolved regulatory submissions
```

according to finance policy.

---

# 153. Close gate

Finance governance MAY prohibit period close while defined critical reconciliation controls remain unresolved.

---

# 154. Close evidence

Period-close controls SHOULD produce auditable evidence.

---

# 155. Backups

ERP backup success SHALL be monitored.

---

# 156. Backup success is insufficient

Baobab SHALL periodically verify restoration capability.

A backup that has never been restored is an unproven recovery mechanism.

---

# 157. Restore tests

Restore tests SHALL verify:

```text
database integrity
ERP startup
mapping integrity
tenant isolation
outbox integrity
critical business data
```

as appropriate.

---

# 158. RPO monitoring

Where replication/backups support an RPO, Baobab SHOULD monitor whether actual recovery posture remains within that objective.

---

# 159. RTO exercises

Recovery procedures SHOULD be exercised periodically for critical deployments.

---

# 160. Disaster recovery observability

Primary and recovery environments SHALL expose sufficient telemetry to detect:

```text
replication failure
backup failure
stale recovery data
split-brain risk
```

---

# 161. Event recovery

Outbox state SHALL be included in ERP recovery design.

A restored ERP database SHALL preserve unpublished event intent.

---

# 162. Inbox recovery

Consumer deduplication/inbox state SHALL also be protected where losing it could create duplicate financial effects.

---

# 163. Reconciliation after recovery

Major recovery/failover SHALL trigger targeted reconciliation.

---

# 164. Deployment observability

Every production deployment SHALL be identifiable in telemetry.

Recommended metadata:

```text
service version
commit SHA
image digest
deployment timestamp
EngineInstance
```

---

# 165. Version correlation

Operators SHALL be able to determine which ERP extension/localisation version processed an operation.

---

# 166. Release monitoring

Deployments SHOULD receive elevated monitoring during a defined observation window.

---

# 167. Rollback

Operational rollback SHALL be planned.

Database/schema changes SHALL account for whether application rollback remains possible.

---

# 168. Rollback does not reverse business transactions

Rolling back software SHALL NOT automatically reverse financial transactions created while the release was active.

---

# 169. Feature controls

Risky capabilities MAY use governed feature controls.

Feature controls SHALL be Context-aware where required.

---

# 170. Kill switch

High-risk external integrations MAY support an operational kill switch.

---

# 171. Kill-switch semantics

A kill switch SHALL specify whether it:

```text
blocks new commands
stops outbound delivery
stops inbound processing
switches to queueing
```

rather than ambiguously "disabling integration."

---

# 172. Financial kill switch

Stopping integration SHALL preserve already committed financial/event intent.

---

# 173. Queue preservation

Operators SHALL NOT resolve incidents by deleting queues/outbox records without formal data-loss approval.

---

# 174. Dead-letter handling

DLQ records SHALL be:

```text
observable
owned
diagnosable
replayable where safe
retained according to policy
```

---

# 175. DLQ is not archive

Dead-letter storage SHALL not be treated as permanent business-event archive.

---

# 176. Poison message

Repeatedly failing messages SHALL be isolated so they do not block unrelated workload.

---

# 177. Replay

Replay SHALL be explicit and auditable.

---

# 178. Replay identity

Replaying a canonical event SHALL preserve its original event identity according to ADR-ERP-006.

---

# 179. Replay metadata

Operational replay metadata MAY identify:

```text
replayed_at
replayed_by
replay_reason
replay_batch_id
```

without mutating the original event fact.

---

# 180. Replay verification

After materially significant replay, reconciliation SHALL verify expected downstream state.

---

# 181. Operational API

Baobab MAY expose controlled management-plane resources for:

```text
health
operations
reconciliation
outbox status
EngineInstance state
```

---

# 182. Management-plane separation

Operational APIs SHALL remain separate from ordinary business capability APIs where appropriate.

---

# 183. Operational authorization

Viewing health may be broadly permissible.

Viewing reconciliation financial details or replaying events SHALL require stronger authorization.

---

# 184. Operational mutation

Actions such as:

```text
replay event
retry reconciliation
suspend binding
drain instance
```

SHALL be:

```text
authenticated
authorised
audited
```

---

# 185. Control Plane events

Operationally relevant Control Plane events MAY include:

```text
engine-instance.degraded.v1
engine-instance.maintenance-started.v1
capability-binding.suspended.v1
mapping.suspended.v1
```

provided semantic ownership remains clear.

---

# 186. Operational events versus domain events

An infrastructure failure such as:

```text
erp database connection pool exhausted
```

SHALL not become an ERP business-domain event.

It belongs to observability/operations.

---

# 187. Audit events versus canonical domain events

Some actions MAY produce both:

```text
domain event
```

and:

```text
audit record
```

Example:

```text
supplier invoice posted
```

The domain event informs other systems.

The audit record proves who/what performed the operation.

---

# 188. Audit event loss

A business transaction requiring audit SHALL not be considered correctly implemented if its required audit evidence can silently disappear.

---

# 189. Audit transactional consistency

For high-value actions, audit evidence SHOULD be committed within the same reliable transactional boundary or via another mechanism that provides equivalent integrity.

---

# 190. Observability failure

Temporary telemetry backend failure SHALL not necessarily prevent ordinary ERP business transactions.

---

# 191. Audit failure

Failure of mandatory audit persistence MAY require the operation to fail depending on the control classification.

---

# 192. Reconciliation failure

A failed reconciliation job SHALL alert and retry according to policy.

It SHALL not silently declare the systems reconciled.

---

# 193. Monitoring dependency

ERP correctness SHALL not depend upon the monitoring platform being available.

---

# 194. Telemetry buffering

Where practical, telemetry collectors MAY buffer during short downstream observability outages.

---

# 195. Data residency

Observability data SHALL obey applicable ResidencyPolicy.

---

# 196. Logs are data

Sending logs to another region is a data transfer.

It SHALL be evaluated accordingly.

---

# 197. Traces are data

Trace attributes may contain business metadata and SHALL be classified appropriately.

---

# 198. Audit residency

Audit storage SHALL respect legal/regulatory residency requirements.

---

# 199. Reconciliation residency

Reconciliation processes SHALL not centralise restricted financial data into prohibited regions merely for operational convenience.

---

# 200. Telemetry minimisation

Baobab SHALL avoid placing full ERP payloads into:

```text
logs
traces
metrics
alerts
```

unless specifically justified.

---

# 201. Canonical identifiers

Canonical UUIDs SHOULD be preferred over customer names or native IDs in operational telemetry.

---

# 202. PII

PII SHALL be excluded from telemetry unless operationally necessary and legally permitted.

---

# 203. Retention classes

Observability and audit SHALL have distinct retention policies.

Example conceptual classes:

```text
debug telemetry
operational logs
metrics
traces
security audit
financial audit
reconciliation evidence
```

---

# 204. Retention configuration

Retention SHALL be policy-driven rather than hard-coded.

---

# 205. Cost management

Telemetry volume SHALL be managed intentionally.

Cost reduction SHALL NOT remove required audit or financial reconciliation controls.

---

# 206. Sampling hierarchy

Sampling MAY reduce:

```text
verbose logs
traces
low-value operational events
```

before compromising:

```text
audit
critical security telemetry
reconciliation evidence
```

---

# 207. Operational maturity stages

Baobab MAY evolve operational capability incrementally.

```text
Stage 1:
    structured logs
    health
    basic metrics
    outbox monitoring

Stage 2:
    distributed traces
    alerting
    dashboards
    automated reconciliation

Stage 3:
    SLOs
    error budgets
    advanced anomaly detection
    automated operational controls
```

The architecture SHALL support all stages without redesign.

---

# 208. Initial production minimum

The first production ERP deployment SHALL include at least:

```text
structured logging

correlation IDs

health/readiness

API request metrics

database monitoring

outbox backlog monitoring

oldest-outbox-event monitoring

event publication failures

critical background-job failures

mapping-resolution failures

security audit

financial business audit

reconciliation framework

backup monitoring

basic alerts

operational runbooks
```

---

# 209. Initial reconciliation set

The first production vertical slice SHOULD implement reconciliation for:

```text
CanonicalEntity ↔ iDempiere mapping

purchase order integration

goods receipt integration

supplier invoice integration

payment integration

outbox publication
```

where those capabilities are active.

---

# 210. Reconciliation framework boundary

The reconciliation framework SHOULD define reusable:

```text
ReconciliationDefinition

ReconciliationRun

ReconciliationItem

ReconciliationResult

ReconciliationResolution
```

contracts.

---

# 211. ReconciliationDefinition

Conceptually:

```text
id
code
version
source
target
entity_type
comparison_strategy
schedule
tolerance_policy
severity_policy
owner
status
```

---

# 212. ReconciliationRun

Conceptually:

```text
id
definition_id
context
window
started_at
completed_at
status
statistics
```

---

# 213. ReconciliationItem

Conceptually:

```text
id
run_id
canonical_entity_id
source_reference
target_reference
mismatch_type
severity
status
detected_at
```

---

# 214. ReconciliationResolution

Conceptually:

```text
item_id
resolution_type
reason
resolved_by
resolved_at
corrective_reference
```

---

# 215. Resolution types

Recommended:

```text
source_corrected
target_corrected
compensating_transaction
mapping_corrected
expected_difference
waived
false_positive
```

---

# 216. No reconciliation shadow ERP

The reconciliation system SHALL NOT evolve into another ERP database.

It stores control state and evidence, not duplicate operational ownership.

---

# 217. Control Plane boundary

The Control Plane MAY coordinate reconciliation metadata.

Domain-specific reconciliation logic SHOULD remain with the responsible integration/domain service.

---

# 218. ERP responsibility

`nabhold/baobab-erp` SHALL own reconciliation logic requiring knowledge of ERP semantics.

---

# 219. Shared contracts

`nabhold/shared` SHALL own organisation-wide schemas for:

```text
telemetry conventions
correlation conventions
audit envelopes
reconciliation contracts
```

where cross-repository standardisation is required.

---

# 220. Infrastructure responsibility

`nabhold/infrastructure` SHALL own deployment/configuration of shared observability infrastructure.

---

# 221. No vendor coupling in contracts

Canonical telemetry/audit contracts SHALL not unnecessarily expose implementation-specific vendor concepts.

Baobab SHALL remain capable of changing:

```text
metrics backend
log backend
trace backend
SIEM
```

without changing ERP business contracts.

---

# 222. OpenTelemetry alignment

Baobab SHOULD use OpenTelemetry-compatible instrumentation conventions where practical for cross-language telemetry.

This is especially appropriate because Baobab is polyglot:

```text
Go
Java
TypeScript
Python
```

can participate in one distributed telemetry architecture.

---

# 223. Instrumentation boundary

OpenTelemetry or another telemetry framework SHALL NOT become a business-domain dependency.

Business code emits meaningful instrumentation through controlled abstractions.

---

# 224. Telemetry schema governance

Custom attributes SHALL use Baobab naming conventions.

Avoid each repository independently inventing:

```text
tenant
tenant_id
tenantId
client
customer_tenant
```

for the same Context dimension.

---

# 225. Canonical observability attributes

Baobab SHOULD standardise attributes such as:

```text
baobab.tenant.id
baobab.legal_entity.id
baobab.market.id
baobab.digital_estate.id
baobab.engine.id
baobab.engine_instance.id
baobab.capability
baobab.canonical_entity.id
baobab.correlation.id
```

subject to final telemetry contract design.

---

# 226. Native ERP attributes

Native iDempiere identifiers MAY appear in restricted diagnostic telemetry when required.

They SHALL be clearly namespaced and SHALL not replace canonical identifiers.

---

# 227. Cardinality classification

Each telemetry attribute SHOULD be classified as:

```text
low
bounded
high
sensitive
```

to guide use in metrics/logs/traces.

---

# 228. Operational security

Observability platforms SHALL themselves be access-controlled.

---

# 229. Tenant observability boundary

A Tenant-facing operational portal, if introduced, SHALL expose only that Tenant's authorised telemetry.

---

# 230. Group observability

Group-level administrators MAY receive aggregated cross-entity operational information only through explicit authorization.

Corporate ownership does not automatically grant unrestricted financial telemetry.

---

# 231. Intelligence Engine

The Intelligence Engine MAY consume authorised operational or reconciliation data.

It SHALL not automatically receive unrestricted raw ERP logs.

---

# 232. AI anomaly detection

Future AI/ML MAY assist with:

```text
anomaly detection
reconciliation prioritisation
incident correlation
capacity forecasting
```

but SHALL not become the sole correctness control.

---

# 233. AI corrective action

AI-generated corrective recommendations SHALL pass through ordinary authorization and ERP APIs.

AI SHALL NOT directly mutate financial database records.

---

# 234. Automated remediation

Operational automation MAY perform pre-approved low-risk remediation.

Examples:

```text
restart stateless worker
retry transient publication
scale worker capacity
```

---

# 235. High-risk remediation

Automation SHALL NOT autonomously:

```text
reopen accounting periods
modify posted invoices
change mappings across Tenants
delete outbox events
promote DR writer
```

without explicitly governed authority.

---

# 236. Operational change audit

Changes to:

```text
alerts
reconciliation definitions
SLOs
routing
health thresholds
replay policy
```

SHOULD be version-controlled/auditable where material.

---

# 237. Time synchronization

Production infrastructure SHALL maintain reliable clock synchronization.

---

# 238. Clock correctness

Logs, traces, events and audit become materially harder to correlate when clocks diverge.

---

# 239. Business time remains separate

Infrastructure clock synchronization SHALL not erase ADR-ERP-001's distinctions between:

```text
occurred time
document date
accounting date
posting time
event time
```

---

# 240. Operational invariants

```text
INV-ERP-OPS-001
Observability is not audit.

INV-ERP-OPS-002
Audit is not reconciliation.

INV-ERP-OPS-003
Monitoring health does not prove business consistency.

INV-ERP-OPS-004
Production logs are structured.

INV-ERP-OPS-005
Correlation identifiers propagate across supported boundaries.

INV-ERP-OPS-006
Trace sampling cannot remove required audit.

INV-ERP-OPS-007
Metrics avoid uncontrolled high-cardinality labels.

INV-ERP-OPS-008
Sensitive financial data is not routinely placed in telemetry.

INV-ERP-OPS-009
Liveness and readiness have distinct semantics.

INV-ERP-OPS-010
Broker failure does not erase committed ERP event intent.

INV-ERP-OPS-011
Business readiness is distinct from infrastructure readiness.

INV-ERP-OPS-012
SLO, RTO and RPO remain distinct.

INV-ERP-OPS-013
Audit preserves historical Context.

INV-ERP-OPS-014
Audit history is not casually rewritten.

INV-ERP-OPS-015
Application logs are not the sole financial audit system.

INV-ERP-OPS-016
Reconciliation is mandatory for independently persisted critical representations.

INV-ERP-OPS-017
Every reconciliation knows the authority being compared.

INV-ERP-OPS-018
Reconciliation mismatch does not automatically permit overwrite.

INV-ERP-OPS-019
Financial comparison uses decimal-safe arithmetic.

INV-ERP-OPS-020
Reconciliation is Tenant/Context scoped.

INV-ERP-OPS-021
Important integrations receive periodic reconciliation.

INV-ERP-OPS-022
Outbox backlog and oldest-event age are observable.

INV-ERP-OPS-023
Published does not mean consumed.

INV-ERP-OPS-024
Duplicate event delivery is tolerated.

INV-ERP-OPS-025
Duplicate financial side effects are not tolerated.

INV-ERP-OPS-026
Mapping integrity is reconcilable.

INV-ERP-OPS-027
Critical reconciliation mismatches have an owner.

INV-ERP-OPS-028
Financial reconciliation is not repaired through ordinary direct SQL.

INV-ERP-OPS-029
Corrections use authorised business processes.

INV-ERP-OPS-030
Reconciliation waivers are explicit and auditable.

INV-ERP-OPS-031
Operational health does not automatically transfer write authority.

INV-ERP-OPS-032
Failover never creates split-brain writers.

INV-ERP-OPS-033
Every actionable production alert has ownership.

INV-ERP-OPS-034
Recovery verification includes business correctness where required.

INV-ERP-OPS-035
Backups are periodically restore-tested.

INV-ERP-OPS-036
ERP recovery preserves unpublished outbox intent.

INV-ERP-OPS-037
Material recovery triggers reconciliation.

INV-ERP-OPS-038
Deployment versions are observable.

INV-ERP-OPS-039
Software rollback does not rewrite business history.

INV-ERP-OPS-040
Kill switches preserve committed business/event intent.

INV-ERP-OPS-041
DLQ is not permanent event archive.

INV-ERP-OPS-042
Replay is authorised and auditable.

INV-ERP-OPS-043
Operational APIs enforce authorization.

INV-ERP-OPS-044
Operational events are distinct from ERP domain events.

INV-ERP-OPS-045
Required audit evidence cannot silently disappear.

INV-ERP-OPS-046
Observability backend outage does not automatically corrupt ERP correctness.

INV-ERP-OPS-047
Telemetry obeys ResidencyPolicy.

INV-ERP-OPS-048
Telemetry retention and audit retention are separately governed.

INV-ERP-OPS-049
Reconciliation SHALL NOT become a shadow ERP.

INV-ERP-OPS-050
Operational automation cannot bypass ERP business authorization.
```

---

# 241. End-to-end operational trace

A successful supplier invoice operation SHOULD be reconstructable approximately as:

```text
Trade / Authorised Consumer
          │
          │ correlation_id = C1
          ▼
       Gateway
          │
          ▼
       ERP API
          │
          │ trace_id = T1
          ▼
   Context Resolution
          │
          ▼
   Mapping Resolution
          │
          ▼
 ERP Application Service
          │
          ▼
       iDempiere
          │
          ├── C_Invoice
          │
          ├── accounting consequence
          │
          └── outbox event
          │
          ▼
      DB COMMIT
          │
          ├───────────────┐
          │               │
          ▼               ▼
      API Response      Outbox Publisher
                              │
                              ▼
                       Canonical Event
                              │
                       correlation=C1
                       causation=...
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
               Trade       Analytics    Reconciler
                                            │
                                            ▼
                                         MATCHED
```

---

# 242. Failure reconstruction

If event delivery fails:

```text
ERP transaction
      │
      ▼
   COMMITTED
      │
      ▼
Outbox = PENDING
      │
      ▼
Broker unavailable
      │
      ▼
Publisher retry
      │
      ▼
Operational alert if threshold exceeded
      │
      ▼
Broker recovers
      │
      ▼
Event published
      │
      ▼
Consumer processes
      │
      ▼
Reconciliation verifies
```

The original ERP financial transaction SHALL remain valid.

---

# 243. Reconciliation failure example

```text
Trade Order
    fulfilled
       │
       ▼
expected ERP representation
       │
       X
     missing
       │
       ▼
scheduled reconciliation
       │
       ▼
MISMATCH
       │
       ▼
classification
       │
       ├── event missing?
       ├── mapping missing?
       ├── consumer failed?
       ├── ERP command rejected?
       └── legitimate semantic difference?
       │
       ▼
resolution workflow
       │
       ▼
authorised correction
       │
       ▼
reconciliation rerun
       │
       ▼
MATCHED
```

---

# 244. Period-close operational model

```text
Accounting Period Close Requested
              │
              ▼
       Close Readiness
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
   Unposted  Integration Reconciliation
   Docs      Failures    Mismatches
      │       │        │
      └───────┼────────┘
              ▼
       Critical issue?
          │       │
         YES      NO
          │       │
          ▼       ▼
        BLOCK   Finance
                 Approval
                    │
                    ▼
                 CLOSE
                    │
                    ▼
              Audit Evidence
```

The exact finance policy SHALL determine which controls block close.

---

# 245. Definition of done

ADR-ERP-011 SHALL be considered implemented when:

- [ ] Structured logging conventions exist.
- [ ] Canonical Context attributes are standardised.
- [ ] Correlation IDs propagate through ERP operations.
- [ ] Trace propagation exists across supported synchronous boundaries.
- [ ] Event correlation/causation follows ADR-ERP-006.
- [ ] Metric naming conventions exist.
- [ ] Cardinality policy exists.
- [ ] Sensitive telemetry policy exists.
- [ ] Liveness endpoint exists.
- [ ] Readiness endpoint exists.
- [ ] Critical dependencies are monitored.
- [ ] API availability/error/latency metrics exist.
- [ ] Database health metrics exist.
- [ ] Outbox backlog is observable.
- [ ] Oldest unpublished event age is observable.
- [ ] Publication failures are observable.
- [ ] Inbox/consumer processing is observable where applicable.
- [ ] Mapping failures are observable.
- [ ] Security audit exists.
- [ ] Business audit exists for material financial operations.
- [ ] Administrative audit exists for privileged configuration changes.
- [ ] Historical audit retains canonical Context.
- [ ] Reconciliation framework exists.
- [ ] Reconciliation definitions are versioned.
- [ ] Critical integration reconciliation exists.
- [ ] Mapping reconciliation exists.
- [ ] Financial reconciliation uses decimal-safe comparisons.
- [ ] Mismatches have severity/ownership.
- [ ] Reconciliation correction is auditable.
- [ ] Financial correction avoids ordinary direct SQL.
- [ ] EngineInstance operational state is observable.
- [ ] Maintenance/draining semantics exist.
- [ ] Health cannot create uncontrolled failover.
- [ ] Incident severity model exists.
- [ ] Minimum ERP runbooks exist.
- [ ] Alerts have owners.
- [ ] Platform dashboard exists.
- [ ] Integration dashboard exists.
- [ ] Reconciliation dashboard exists.
- [ ] Backup success is monitored.
- [ ] Restore testing exists.
- [ ] Recovery triggers appropriate reconciliation.
- [ ] Deployment version/image digest is observable.
- [ ] Replay is authorised and audited.
- [ ] DLQ operational process exists.
- [ ] Telemetry obeys ResidencyPolicy.
- [ ] Telemetry and audit retention are separately governed.
- [ ] Operational APIs are secured.
- [ ] Production readiness includes observability/reconciliation review.

---

# 246. Final governing statement

The Baobab ERP operating model SHALL reject the assumption that:

```text
request returned 200
```

means:

```text
business process is correct
```

or that:

```text
all containers are healthy
```

means:

```text
financial state is correct
```

Production confidence requires a chain:

```text
Observe
   │
   ▼
Correlate
   │
   ▼
Audit
   │
   ▼
Reconcile
   │
   ▼
Detect
   │
   ▼
Diagnose
   │
   ▼
Correct
   │
   ▼
Verify
```

The decisive architectural principle is:

> **Observability tells Baobab what the system appears to be doing. Audit establishes accountable history. Reconciliation establishes whether independently maintained business representations actually agree. Operational control provides the governed means to act when they do not.**

For an enterprise ERP platform, all four are required.