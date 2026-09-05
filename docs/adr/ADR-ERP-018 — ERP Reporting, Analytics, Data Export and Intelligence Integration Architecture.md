# ADR-ERP-018 — ERP Reporting, Analytics, Data Export and Intelligence Integration Architecture

**Status:** Accepted  
**Decision class:** ERP / Reporting / Analytics / Data Platform / Intelligence / Export / Governance  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`, Baobab Intelligence Engine, analytical infrastructure, Digital Estates and authorised downstream consumers  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-017  
**Date:** 2026-09-02

---

## 1. Decision

Baobab SHALL separate **operational ERP processing** from **analytical consumption**.

iDempiere SHALL remain authoritative for ERP transactional and accounting state.

Reporting, analytics, data science and AI workloads SHALL consume governed projections, exports, events or purpose-built analytical stores rather than treating the production iDempiere PostgreSQL database as an enterprise data warehouse.

The governing principle is:

> **Operational systems establish business facts. Analytical systems interpret those facts. Interpretation does not transfer authority.**

Therefore:

```text
iDempiere
   │
   │ authoritative ERP facts
   ▼
Governed Data Egress
   │
   ├── Operational Reports
   ├── Canonical Events
   ├── Analytical Projections
   ├── Governed Exports
   └── Reconciliation Feeds
            │
            ▼
     Analytics / Intelligence
```

The Baobab Intelligence Engine MAY analyse ERP information but SHALL NOT become the financial system of record.

---

# Part I — Architectural Boundaries

## 2. Four information planes

Baobab SHALL distinguish:

```text
Transactional Plane
Reporting Plane
Analytical Plane
Intelligence Plane
```

### Transactional Plane

Owns operational business state.

For ERP:

```text
iDempiere + PostgreSQL
```

### Reporting Plane

Produces operational/statutory/business reports closely tied to authoritative ERP state.

### Analytical Plane

Supports historical, aggregated, multidimensional and cross-domain analysis.

### Intelligence Plane

Supports:

```text
prediction
forecasting
classification
anomaly detection
recommendation
scenario analysis
AI-assisted decision support
```

---

## 3. Authority does not move downstream

Copying ERP data into:

```text
warehouse
lake
lakehouse
BI platform
search index
vector database
feature store
AI context store
```

does NOT make that system authoritative for ERP state.

---

## 4. Projection principle

Downstream analytical representations SHALL be considered:

```text
derived
rebuildable where practical
traceable to source
```

unless explicitly designated as authoritative for a separate domain.

---

## 5. No production database as enterprise warehouse

The production iDempiere PostgreSQL database SHALL NOT become Baobab's general-purpose analytical database.

Prohibited patterns include:

```text
BI Tool ───────► ERP Primary DB

Intelligence Engine ───────► ERP Primary DB

Digital Estate ───────► ERP Primary DB

Data Scientist ───────► ERP Primary DB
```

---

## 6. Why

Operational ERP databases are optimized around:

```text
transactional integrity
document processing
posting
workflow
concurrency
operational availability
```

Analytical workloads commonly require:

```text
large scans
historical aggregation
cross-domain joins
feature generation
exploratory queries
```

These concerns SHALL be isolated.

---

# Part II — Reporting Classes

## 7. Report classification

Baobab SHALL classify ERP reporting into at least:

```text
Operational Reporting
Financial Reporting
Statutory Reporting
Management Reporting
Analytical Reporting
Ad-hoc Analysis
```

---

## 8. Operational reporting

Operational reports MAY run close to ERP transactional state.

Examples:

```text
open purchase orders
unreceived purchases
unposted invoices
inventory movement
outstanding receivables
pending payments
```

---

## 9. Financial reporting

Financial reports derive from authoritative ERP accounting state.

Examples:

```text
trial balance
general ledger
balance sheet
income statement
cash-flow supporting schedules
accounts receivable aging
accounts payable aging
```

---

## 10. Financial report authority

Where a report represents official accounting state, its values SHALL derive from the authoritative ERP ledger/configuration.

---

## 11. Statutory reporting

Statutory reports SHALL follow ADR-ERP-008 and ADR-ERP-009.

---

## 12. Management reporting

Management reporting MAY introduce:

```text
Market
DigitalEstate
business unit
product category
customer segment
channel
```

dimensions.

These dimensions SHALL NOT alter statutory books.

---

## 13. Analytical reporting

Analytical reporting SHOULD normally operate from downstream analytical stores.

---

## 14. Ad-hoc analysis

Unbounded exploratory queries SHALL NOT execute against production ERP merely because a user has read permission.

---

# Part III — Data Egress

## 15. Approved ERP data-egress mechanisms

ERP data SHALL leave its operational boundary through approved mechanisms such as:

```text
Canonical Events
Governed APIs
Scheduled Exports
Analytical Replication
Approved CDC
Reporting Read Models
```

---

## 16. No cross-engine SQL

Cross-engine SQL joins remain prohibited.

Example:

```text
SELECT *
FROM medusa.orders
JOIN idempiere.c_invoice ...
```

is not a Baobab integration architecture.

---

## 17. Events

Canonical events are the preferred mechanism for propagating meaningful incremental business facts where event semantics are appropriate.

---

## 18. Events are not complete analytical history

The event stream SHALL NOT automatically be assumed to contain every field needed to reconstruct the ERP database.

---

## 19. Event contract

Canonical events SHALL follow ADR-ERP-006.

---

## 20. APIs

Governed APIs SHALL support targeted authoritative queries.

They SHALL NOT become arbitrary analytical SQL tunnels.

---

## 21. Scheduled exports

Scheduled exports MAY be used for:

```text
finance extracts
regulatory feeds
partner reporting
warehouse loading
historical snapshots
```

---

## 22. Export contract

A production export SHALL have an explicit:

```text
owner
purpose
schema
scope
classification
destination
frequency
retention
consumer
```

---

## 23. CDC

Change Data Capture MAY be used for analytical replication where justified.

---

## 24. CDC boundary

Raw CDC SHALL be considered infrastructure-level change data.

It SHALL NOT automatically become a canonical business event contract.

Thus:

```text
CDC event
   !=
Canonical Domain Event
```

---

## 25. Database implementation leakage

Consumers SHALL NOT build permanent enterprise semantics directly from undocumented iDempiere table changes.

---

# Part IV — Analytical Architecture

## 26. Logical analytical flow

The target architecture is:

```text
                     iDempiere
                         │
            ┌────────────┼─────────────┐
            │            │             │
            ▼            ▼             ▼
         Events        Exports      Replication
            │            │             │
            └────────────┼─────────────┘
                         ▼
                Data Ingestion Layer
                         │
                         ▼
                Governed Data Store
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
          Finance        BI      Intelligence
         Analytics                 Engine
```

---

## 27. Analytical store

Baobab MAY adopt:

```text
data warehouse
data lake
lakehouse
columnar analytical database
```

according to future requirements.

This ADR deliberately does not select one.

---

## 28. Technology neutrality

The canonical contracts SHALL not assume a particular warehouse vendor.

---

## 29. Raw zone

Where a layered analytical architecture is adopted, a raw ingestion layer MAY preserve source-aligned data.

---

## 30. Raw is not trusted semantic data

Raw ingestion SHALL not automatically be exposed to business users or AI.

---

## 31. Curated layer

A curated analytical layer SHOULD:

```text
normalize identity
apply canonical mappings
resolve Context
standardize types
apply classifications
record provenance
```

---

## 32. Semantic layer

Business-facing analytical metrics SHOULD use governed semantic definitions.

---

## 33. Metric governance

Terms such as:

```text
Revenue
Gross Margin
Net Sales
Active Customer
Inventory Value
Outstanding Receivable
```

SHALL have explicit definitions.

---

## 34. No metric-by-dashboard

A dashboard SHALL not independently redefine a governed financial metric.

---

## 35. ERP accounting definitions

Metrics derived from accounting SHALL remain traceable to ERP financial definitions.

---

# Part V — Canonical Identity in Analytics

## 36. Canonical IDs

Analytical data SHOULD retain canonical identifiers for cross-domain correlation.

Example:

```text
canonical_party_id
canonical_product_id
canonical_sales_order_id
canonical_invoice_id
canonical_payment_id
```

---

## 37. Native IDs

Native ERP identifiers MAY be retained for lineage/debugging.

They SHALL not become cross-platform identity.

---

## 38. Historical mapping

Analytical ingestion SHALL respect temporal mappings.

---

## 39. Current mapping is insufficient

Historical reporting SHALL NOT assume today's mapping existed when an old transaction occurred.

---

## 40. Slowly changing business structure

Analytics SHALL preserve historical interpretation where required for changes in:

```text
LegalEntity
Market
organisation
Product hierarchy
customer segment
DigitalEstate
```

---

## 41. Reorganization

A corporate reorganization SHALL not silently rewrite historical facts.

---

# Part VI — Time Semantics

## 42. Multiple time dimensions

ERP analytics SHALL distinguish:

```text
occurred_at
document_date
accounting_date
posted_at
event_time
ingested_at
processed_at
```

where applicable.

---

## 43. Accounting analytics

Financial period reporting SHALL normally use accounting semantics rather than ingestion time.

---

## 44. Event delay

Late event delivery SHALL not move a transaction into the wrong accounting period.

---

## 45. Restatement

Where accounting restatement occurs, analytics SHALL support explicit restated views rather than silently mutating historical published results.

---

## 46. Snapshot reporting

Period-end snapshots MAY be retained for reproducibility.

---

# Part VII — Currency Analytics

## 47. Currency dimensions

Analytics SHALL preserve:

```text
transaction currency
functional currency
reporting currency
consolidation currency
```

where applicable.

---

## 48. Original amount preservation

Original transaction amounts SHALL be retained.

---

## 49. Conversion metadata

Converted values SHOULD identify:

```text
target currency
rate
rate type
effective date
source
```

where material.

---

## 50. No arbitrary BI FX

Official financial reports SHALL NOT use an analyst-selected market FX rate in place of approved accounting/consolidation policy.

---

## 51. Analytical scenario FX

Scenario analysis MAY use hypothetical FX rates.

Such results SHALL be clearly identified as analytical scenarios.

---

# Part VIII — Financial Analytics

## 52. Ledger-derived facts

Financial analytical models SHOULD derive from controlled ERP accounting exports/projections.

---

## 53. Double-entry preservation

Where ledger-level analytics is required, debit/credit relationships SHALL remain reconstructable.

---

## 54. Trial balance reconciliation

Analytical financial datasets SHALL reconcile to ERP trial balance for applicable scope/period.

---

## 55. Reconciliation gate

A financial analytical dataset that materially fails reconciliation SHALL NOT be labelled authoritative financial reporting.

---

## 56. Consolidation

Group analytics MAY consolidate independently governed LegalEntities.

---

## 57. Consolidation does not change ownership

Group reporting SHALL NOT collapse subsidiary transaction authority into Nabhold simply because Nabhold owns the group.

---

## 58. Intercompany

Intercompany transactions SHALL remain separately identifiable.

---

## 59. Eliminations

Consolidation eliminations SHALL be explicit analytical/consolidation facts.

They SHALL not silently rewrite subsidiary ledgers.

---

# Part IX — Inventory Analytics

## 60. Inventory analytics

ERP analytical projections MAY include:

```text
on-hand
movement
valuation
cost
warehouse
lot
expiry
landed cost
```

according to authorization.

---

## 61. Inventory authority

Analytical inventory is not operational availability authority.

---

## 62. Commerce availability

Medusa/Trade SHALL use the approved operational inventory contract from the relevant inventory ADRs, not yesterday's warehouse snapshot.

---

## 63. Historical valuation

Historical inventory valuation SHALL use ERP costing/accounting semantics.

---

# Part X — Commerce Analytics

## 64. Cross-engine analytics

Baobab analytics MAY combine:

```text
Digital Estate traffic
Medusa commerce
ERP accounting
Payload content
payment-provider facts
```

using canonical identities and governed relationships.

---

## 65. Commerce revenue versus accounting revenue

These SHALL remain distinct metrics unless explicitly reconciled.

```text
Commerce GMV
      !=
ERP Revenue
```

---

## 66. Order value versus invoice value

```text
Commerce Order Total
      != necessarily
ERP Posted Invoice Total
```

because of timing, returns, credits, taxes, cancellations or policy.

---

## 67. Metric naming

Dashboards SHALL not label Commerce GMV as accounting revenue without an approved definition.

---

# Part XI — Intelligence Engine Integration

## 68. Intelligence role

The Baobab Intelligence Engine MAY consume authorised ERP-derived datasets for:

```text
forecasting
anomaly detection
cash-flow prediction
inventory optimization
procurement analysis
customer analysis
margin analysis
scenario modelling
risk analysis
```

---

## 69. Intelligence is downstream

The Intelligence Engine SHALL normally consume governed analytical products rather than unrestricted ERP tables.

---

## 70. AI direct database access

Production AI agents SHALL NOT receive unrestricted direct access to the ERP database.

---

## 71. AI access path

Preferred:

```text
Intelligence Engine
       │
       ▼
Governed Data Product / API
       │
       ▼
Authorized ERP-derived Data
```

---

## 72. AI read versus action

AI analysis and AI action SHALL be separate capabilities.

---

## 73. AI recommendation

An AI model MAY recommend:

```text
reorder stock
contact debtor
adjust forecast
investigate invoice
```

---

## 74. AI mutation

To perform an ERP mutation, the action SHALL pass through an authorised business command.

---

## 75. No AI SQL mutation

Prohibited:

```text
LLM
 │
 ▼
UPDATE C_Invoice ...
```

---

## 76. Financial posting

AI SHALL NOT autonomously post financial documents by default.

Any future autonomous authority requires explicit policy and separate governance.

---

## 77. Explainability

Material AI-supported financial/business decisions SHOULD retain sufficient:

```text
model identity
input lineage
output
timestamp
policy
human approval where applicable
```

for governance.

---

## 78. Model identity

Analytical output SHOULD identify the model/version where material.

---

## 79. Model does not become data authority

A prediction SHALL remain:

```text
prediction
```

not fact.

---

## 80. Prediction storage

Predictions MAY be persisted as derived analytical entities with provenance.

---

## 81. Forecast versus actual

```text
Forecast
   !=
Budget
   !=
Actual
```

unless explicitly defined.

---

# Part XII — AI Data Governance

## 82. Purpose limitation

ERP data SHALL only be supplied to AI for authorised purposes.

---

## 83. Training data

Operational ERP data SHALL NOT automatically become model-training data.

---

## 84. External models

Sending ERP data to external model providers SHALL require:

```text
classification review
contractual approval
privacy review
residency review
security approval
```

according to policy.

---

## 85. Prompt minimisation

AI prompts SHOULD contain the minimum necessary ERP data.

---

## 86. Secrets

ERP secrets SHALL never be supplied to AI context.

---

## 87. Payment data

Sensitive payment credentials SHALL never enter model context.

---

## 88. PII

Personal information SHALL be minimised, masked or pseudonymised where appropriate.

---

## 89. Tenant separation

AI retrieval SHALL preserve Tenant isolation.

---

## 90. Cross-tenant AI analysis

Cross-tenant analysis SHALL require explicit authority.

---

## 91. Group intelligence

Nabhold ownership SHALL not automatically authorize unrestricted subsidiary data ingestion into group AI models.

---

## 92. Aggregated intelligence

Group analytics MAY use appropriately governed aggregated/anonymised datasets where permitted.

---

# Part XIII — Retrieval-Augmented Intelligence

## 93. RAG

The Intelligence Engine MAY use retrieval-augmented generation over authorised ERP-derived information.

---

## 94. Retrieval authorization

Authorization SHALL occur before retrieval results enter model context.

---

## 95. Post-retrieval filtering is insufficient

The pattern:

```text
retrieve everything
       │
       ▼
ask model not to reveal it
```

is prohibited.

---

## 96. Context-aware retrieval

Retrieval SHALL incorporate trusted:

```text
Tenant
LegalEntity
Market
classification
purpose
principal
```

where applicable.

---

## 97. Vector databases

Vector databases SHALL be treated as governed data stores.

---

## 98. Embeddings

Embeddings may encode sensitive information.

They SHALL inherit appropriate security/residency controls.

---

## 99. Vector deletion

Retention/deletion requirements SHALL propagate to vector representations where required.

---

## 100. Vector store is not ERP authority

Semantic similarity SHALL never establish accounting truth.

---

# Part XIV — Data Products

## 101. Data-product model

Important analytical datasets SHOULD be treated as governed Data Products.

---

## 102. Data Product definition

A Data Product SHOULD identify:

```text
name
owner
purpose
source
schema
classification
freshness
quality expectations
consumers
retention
lineage
```

---

## 103. Example products

Potential ERP-derived Data Products:

```text
ERP Financial Actuals
ERP Accounts Receivable
ERP Accounts Payable
ERP Inventory Valuation
ERP Procurement
ERP Sales Accounting
ERP Payment Settlement
ERP Landed Cost
```

---

## 104. Ownership

Data Product ownership SHALL be explicit.

---

## 105. Product contract

Consumers SHALL depend on versioned Data Product contracts rather than undocumented warehouse tables.

---

# Part XV — Data Quality

## 106. Data quality

Analytical datasets SHALL expose measurable quality where business critical.

---

## 107. Dimensions

Possible dimensions:

```text
completeness
validity
uniqueness
consistency
timeliness
reconciliation
```

---

## 108. Freshness

Every important Data Product SHOULD define expected freshness.

---

## 109. Freshness is not correctness

A dataset can be fresh and wrong.

---

## 110. Quality state

A Data Product MAY expose:

```text
healthy
degraded
stale
failed
```

---

## 111. Financial quality

Financial datasets SHOULD include reconciliation status.

---

## 112. Missing mappings

Missing canonical mappings SHALL produce explicit quality failures.

---

## 113. Late data

Late-arriving data SHALL be observable.

---

## 114. Duplicate data

Duplicate event ingestion SHALL not duplicate analytical facts.

---

## 115. Idempotent ingestion

Analytical pipelines SHOULD be idempotent.

---

# Part XVI — Lineage

## 116. Lineage

Material analytical outputs SHALL be traceable to their sources.

---

## 117. Lineage levels

Lineage MAY include:

```text
source system
source entity
canonical entity
ingestion job
transformation version
Data Product
report/model
```

---

## 118. Financial lineage

Official financial reporting SHOULD support:

```text
Report
  │
  ▼
Metric
  │
  ▼
Analytical Fact
  │
  ▼
ERP Financial Record
```

---

## 119. AI lineage

Material AI outputs SHOULD support:

```text
AI Output
   │
   ├── Model Version
   ├── Data Product Version
   ├── Retrieval Context
   └── Generation Time
```

subject to privacy/security.

---

# Part XVII — Export Architecture

## 120. Export classes

Exports SHALL be classified as:

```text
Operational
Financial
Regulatory
Partner
Tenant
Analytical
Administrative
```

---

## 121. Export authorization

Export permission SHALL be separate from ordinary read permission where risk warrants.

---

## 122. Bulk export risk

Bulk extraction has greater data-exfiltration risk than viewing one ERP record.

---

## 123. Export audit

Sensitive exports SHOULD record:

```text
principal
Tenant
LegalEntity
dataset
scope
purpose
time
format
destination where governed
```

---

## 124. Export formats

Approved formats MAY include:

```text
CSV
JSON
JSONL
Parquet
XML
PDF
```

depending on purpose.

---

## 125. Format is not semantics

CSV does not define the business contract.

---

## 126. Schema version

Machine-readable exports SHALL have versioned schemas.

---

## 127. Decimal integrity

Financial exports SHALL preserve exact decimal values.

---

## 128. Time integrity

Exports SHALL preserve timezone/date semantics.

---

## 129. Currency

Currency SHALL never be inferred solely from column names or environment.

---

## 130. Export manifest

Large/batch exports SHOULD include a manifest with:

```text
export_id
schema_version
scope
created_at
record_count
checksums
classification
```

---

## 131. Integrity

Exports MAY be cryptographically digested/signed where appropriate.

---

## 132. Temporary export storage

Temporary exports SHALL expire according to policy.

---

## 133. Export URL

Sensitive exports SHALL not use permanent public URLs.

---

# Part XVIII — Tenant and Legal-Entity Isolation

## 134. Analytical Tenant boundary

Tenant isolation SHALL continue after data leaves ERP.

---

## 135. Warehouse is not trusted exception

Moving data to a warehouse does NOT remove Tenant isolation requirements.

---

## 136. LegalEntity isolation

LegalEntity access SHALL remain independently enforceable where required.

---

## 137. Group consolidation

Group consolidation access SHALL be explicit.

---

## 138. Market

Market filtering SHALL not substitute for Tenant/LegalEntity authorization.

---

## 139. Row-level controls

Analytical platforms MAY use row-level security where appropriate.

It SHALL complement, not replace, broader isolation architecture.

---

## 140. Dataset-level isolation

Highly sensitive tenants MAY require dedicated datasets/storage.

---

## 141. IsolationProfile

Analytical architecture SHOULD honour applicable `IsolationProfile` and data-classification requirements.

---

# Part XIX — Residency

## 142. Analytical copies are data copies

A warehouse copy is subject to residency rules.

---

## 143. Residency applies to

```text
raw ingestion
curated data
warehouse
exports
BI cache
ML features
vector stores
backups
model context
```

---

## 144. Cross-region analytics

Cross-region replication SHALL require policy authorization.

---

## 145. Market is not residency

Market location SHALL not be used as a shortcut for data-residency decisions.

---

## 146. Global reporting

Global/group reporting MAY require:

```text
approved aggregation
regional processing
pseudonymisation
data minimisation
```

rather than copying all detailed records centrally.

---

# Part XX — Security

## 147. Least privilege

Analytics identities SHALL receive only required datasets.

---

## 148. Shared BI account

A universal:

```text
baobab-bi-admin
```

identity SHALL NOT become the ordinary consumer credential.

---

## 149. Service identity

Ingestion pipelines SHALL use dedicated workload identities.

---

## 150. Read-only source access

Where direct replication/source reading is approved, credentials SHOULD be read-only and purpose-specific.

---

## 151. Database superuser

Analytics SHALL not use ERP PostgreSQL superuser credentials.

---

## 152. Query controls

Ad-hoc query capabilities SHALL be bounded by authorization and workload controls.

---

## 153. Sensitive fields

High-risk fields MAY require:

```text
masking
tokenisation
pseudonymisation
column-level authorization
```

---

## 154. Logging

Analytical query logs SHALL not unnecessarily reproduce sensitive result data.

---

# Part XXI — Operational Isolation

## 155. Workload isolation

Heavy analytical workloads SHALL be isolated from ERP transactional resources.

---

## 156. Resource competition

A month-end BI query SHALL not prevent ERP invoice posting.

---

## 157. Read replicas

Read replicas MAY support certain operational reporting.

---

## 158. Replica is not warehouse

A PostgreSQL read replica SHALL not automatically become Baobab's enterprise analytical platform.

---

## 159. Replica lag

Reports using replicas SHALL understand replication lag.

---

## 160. Financial freshness

A report requiring exact current financial state MAY need a different execution path than a dashboard tolerant of lag.

---

# Part XXII — Near-Real-Time Analytics

## 161. Near-real-time

Canonical events MAY support near-real-time analytical projections.

---

## 162. Eventual consistency

Such projections SHALL expose their eventual-consistency characteristics.

---

## 163. Dashboard timestamp

Dashboards SHOULD expose data freshness.

---

## 164. No false real-time claim

A dashboard updated every fifteen minutes SHALL not be represented as authoritative real-time ERP state.

---

# Part XXIII — Batch Analytics

## 165. Batch

Batch pipelines remain valid for:

```text
daily financial aggregation
period-end processing
large historical transformations
ML training datasets
```

---

## 166. Event-only rejection

Baobab SHALL NOT force every analytical use case through real-time events.

---

## 167. Hybrid architecture

Baobab MAY combine:

```text
streaming
+
batch
```

where appropriate.

---

# Part XXIV — Reconciliation

## 168. Analytical reconciliation

Critical analytical products SHALL reconcile to authoritative sources.

---

## 169. Reconciliation hierarchy

For financial datasets:

```text
record counts
      │
      ▼
control totals
      │
      ▼
account balances
      │
      ▼
document-level exceptions
```

---

## 170. Control totals

Examples:

```text
invoice count
invoice total
debit total
credit total
payment total
inventory valuation
```

---

## 171. Reconciliation window

Expected ingestion latency SHALL be considered before declaring mismatch.

---

## 172. Persistent mismatch

Persistent unexplained mismatch SHALL create an operational reconciliation finding.

---

## 173. Repair

Analytical repair SHALL normally rebuild/correct the projection.

It SHALL not mutate ERP merely to make the warehouse agree.

---

## 174. Source correction

If ERP is wrong, correction SHALL occur through ERP business/accounting processes.

---

# Part XXV — Data Deletion and Retention

## 175. Analytical retention

Analytical copies SHALL have explicit retention policies.

---

## 176. Source retention != analytical retention

A source record's retention period SHALL not automatically justify indefinite retention in every downstream system.

---

## 177. Deletion propagation

Privacy/legal deletion SHALL propagate to downstream copies where legally required.

---

## 178. Financial retention exception

Financial/legal retention obligations may prevent deletion of some records.

Such exceptions SHALL be explicit.

---

## 179. AI features

Feature stores and vector indexes SHALL participate in deletion/retention workflows.

---

## 180. Backups

Analytical backup retention SHALL also comply with applicable policy.

---

# Part XXVI — Schema Evolution

## 181. ERP upgrades

iDempiere upgrades may change physical schema.

Downstream canonical contracts SHOULD insulate consumers from such changes.

---

## 182. Raw CDC sensitivity

Raw CDC consumers are particularly sensitive to physical schema changes.

---

## 183. Compatibility tests

ERP upgrades SHALL test:

```text
events
exports
CDC where used
analytical transformations
financial reconciliation
```

before production promotion.

---

## 184. Data Product versioning

Breaking Data Product schema changes SHALL be versioned.

---

## 185. Consumer compatibility

Downstream consumers SHALL be tested against supported versions.

---

# Part XXVII — Analytics Development

## 186. Production access

Analysts SHOULD NOT require production ERP administrator access to build reports.

---

## 187. Development datasets

Analytics development SHOULD use:

```text
synthetic
masked
sampled
approved
```

datasets.

---

## 188. Reproducibility

Material analytical transformations SHOULD be source controlled.

---

## 189. Transformation review

Financial transformations SHOULD receive appropriate Finance/data review.

---

## 190. SQL governance

Business-critical SQL SHALL not live only inside an individual's desktop BI workbook.

---

## 191. Semantic definitions as code

Where practical, governed metrics and transformations SHOULD be version controlled.

---

# Part XXVIII — Reporting API

## 192. Reporting API

Baobab MAY expose reporting capabilities through dedicated APIs.

---

## 193. Reporting API != ERP CRUD API

Reporting endpoints SHOULD represent reporting/query use cases.

---

## 194. Asynchronous report generation

Large reports SHOULD be generated asynchronously.

Example:

```text
POST /reports
       │
       ▼
202 Accepted
       │
       ▼
Report Job
       │
       ▼
Generated Artifact
```

---

## 195. Report artifact

Generated report files SHALL follow ADR-ERP-017.

---

## 196. Report authorization

Authorization SHALL be evaluated when requesting the report and, where appropriate, again when retrieving it.

---

## 197. Report snapshot

A generated financial report SHOULD identify:

```text
scope
period
generated_at
data_as_of
definition/version
```

---

# Part XXIX — Intelligence Feedback

## 198. Intelligence feedback loop

AI output MAY generate recommendations.

Conceptually:

```text
ERP Facts
   │
   ▼
Analytics
   │
   ▼
Intelligence
   │
   ▼
Recommendation
   │
   ▼
Human / Policy Decision
   │
   ▼
Governed ERP Command
```

---

## 199. Feedback is explicit

Prediction output SHALL NOT automatically mutate its own source data.

---

## 200. Automation

Future autonomous workflows MAY be introduced only through explicit capability authorization and risk controls.

---

## 201. Example — inventory forecast

```text
ERP Inventory History
        │
        ▼
Demand Data Product
        │
        ▼
Forecast Model
        │
        ▼
Recommended Reorder
        │
        ▼
Procurement Policy
        │
        ▼
Approved Purchase Requisition
```

---

## 202. Forecast does not create PO directly

Unless specifically authorised by future policy, model output SHALL not bypass procurement approval.

---

## 203. Example — receivables intelligence

```text
ERP AR
   │
   ▼
Receivables Data Product
   │
   ▼
Risk Model
   │
   ▼
Collection Priority
```

The risk score SHALL not rewrite the receivable.

---

## 204. Example — margin analysis

Cross-domain analytics MAY combine:

```text
Medusa selling price
ERP COGS
ERP landed cost
payment fees
fulfillment cost
```

to estimate contribution margin.

---

## 205. Analytical calculation

The resulting margin metric SHALL identify its governed definition.

---

# Part XXX — Data Contracts

## 206. Shared ownership

`nabhold/shared` SHALL own organisation-wide analytical contract standards.

---

## 207. ERP ownership

`nabhold/baobab-erp` SHALL own ERP-specific producers and ERP semantic transformations.

---

## 208. Intelligence ownership

The Intelligence Engine SHALL own models and intelligence-specific derived products, not ERP truth.

---

## 209. Infrastructure ownership

`nabhold/infrastructure` SHALL own deployment of analytical infrastructure.

---

## 210. Control Plane ownership

Control Plane SHALL own topology, Context, capability and isolation metadata needed to govern analytical access.

---

## 211. No central god service

No single component SHALL own:

```text
ERP state
commerce state
content state
analytics
AI
topology
```

merely for architectural convenience.

---

# Part XXXI — Observability

## 212. Pipeline observability

Analytical pipelines SHALL expose:

```text
ingestion lag
failed jobs
record counts
schema errors
mapping failures
quality failures
reconciliation failures
```

---

## 213. Intelligence observability

AI integrations SHOULD expose:

```text
model version
request volume
latency
failures
data-product freshness
```

without leaking protected input/output into metric labels.

---

## 214. Data freshness SLI

Critical Data Products SHOULD have freshness SLIs.

---

## 215. Reconciliation SLI

Financial Data Products MAY have reconciliation-success SLIs.

---

## 216. Pipeline health != data health

A pipeline can run successfully while producing incorrect data.

Both SHALL be measured separately.

---

# Part XXXII — Disaster Recovery

## 217. Analytical DR

Analytical systems SHALL have recovery policies proportional to business criticality.

---

## 218. Rebuildable data

Where an analytical projection can safely be reconstructed from durable authoritative sources, rebuilding MAY be preferred over expensive HA.

---

## 219. Irreplaceable analytical artifacts

Non-reproducible:

```text
model training datasets
approved forecasts
regulatory exports
signed reports
```

MAY require stronger preservation.

---

## 220. ERP priority

Loss of an analytical dashboard SHALL not automatically trigger ERP failover.

---

## 221. Post-recovery

Recovered analytical stores SHALL reconcile to ERP before being considered trustworthy for critical financial use.

---

# Part XXXIII — Anti-Patterns

## 222. Rejected — BI on ERP primary

```text
Power BI/Tableau/etc.
       │
       ▼
ERP Primary PostgreSQL
```

as the default enterprise reporting architecture.

---

## 223. Rejected — AI database superuser

```text
LLM Agent
   │
   ▼
PostgreSQL superuser
```

---

## 224. Rejected — warehouse as master

The analytical warehouse SHALL not become the source used to correct ERP simply because analysts prefer its schema.

---

## 225. Rejected — native IDs as enterprise dimensions

`C_BPartner_ID` SHALL not become the group-wide customer identity.

---

## 226. Rejected — dashboard-owned metrics

Business definitions SHALL not exist only in visualization configuration.

---

## 227. Rejected — Market as security boundary

Market filters SHALL not substitute for Tenant/LegalEntity authorization.

---

## 228. Rejected — unrestricted subsidiary pooling

Group ownership does not justify uncontrolled pooling of all subsidiary raw data.

---

## 229. Rejected — AI inference as fact

A model's prediction SHALL not be stored as though it were an ERP-observed fact.

---

## 230. Rejected — event stream as warehouse substitute

Events alone SHALL not be assumed to satisfy all historical analytical requirements.

---

## 231. Rejected — CDC as canonical event contract

Physical row changes SHALL not become the public semantic contract by default.

---

# Part XXXIV — Non-Negotiable Invariants

## 232. Invariants

```text
INV-ERP-ANA-001
iDempiere remains authoritative for ERP operational and accounting state.

INV-ERP-ANA-002
Analytical copies do not acquire ERP authority.

INV-ERP-ANA-003
Production ERP PostgreSQL is not the enterprise data warehouse.

INV-ERP-ANA-004
Cross-engine SQL integration is prohibited.

INV-ERP-ANA-005
Operational, reporting, analytical and intelligence workloads remain distinguishable.

INV-ERP-ANA-006
Canonical events and CDC remain distinct concepts.

INV-ERP-ANA-007
CDC does not automatically become a business contract.

INV-ERP-ANA-008
Analytical consumers do not depend on undocumented iDempiere schema semantics.

INV-ERP-ANA-009
Critical Data Products have explicit ownership.

INV-ERP-ANA-010
Critical Data Products have versioned schemas.

INV-ERP-ANA-011
Financial metrics have governed definitions.

INV-ERP-ANA-012
Dashboard configuration does not define accounting truth.

INV-ERP-ANA-013
Canonical IDs are preferred for cross-domain analytical identity.

INV-ERP-ANA-014
Native IDs remain source-specific.

INV-ERP-ANA-015
Historical mappings are temporally respected.

INV-ERP-ANA-016
Corporate reorganizations do not silently rewrite history.

INV-ERP-ANA-017
Accounting date remains distinct from ingestion time.

INV-ERP-ANA-018
Late events do not redefine accounting periods.

INV-ERP-ANA-019
Original transaction currency is preserved.

INV-ERP-ANA-020
Official financial analytics uses governed FX semantics.

INV-ERP-ANA-021
Scenario FX is clearly identified as analytical.

INV-ERP-ANA-022
Financial analytical datasets reconcile to ERP.

INV-ERP-ANA-023
Group consolidation does not transfer subsidiary transaction authority.

INV-ERP-ANA-024
Intercompany eliminations remain explicit.

INV-ERP-ANA-025
Analytical inventory does not become operational availability authority.

INV-ERP-ANA-026
Commerce GMV is not automatically ERP revenue.

INV-ERP-ANA-027
Commerce Order totals are not automatically posted invoice totals.

INV-ERP-ANA-028
The Intelligence Engine consumes governed ERP-derived information.

INV-ERP-ANA-029
AI does not receive unrestricted ERP database access.

INV-ERP-ANA-030
AI analysis and ERP mutation remain separate capabilities.

INV-ERP-ANA-031
AI never directly modifies ERP SQL state.

INV-ERP-ANA-032
Predictions remain distinguishable from facts.

INV-ERP-ANA-033
ERP data is not automatically model-training data.

INV-ERP-ANA-034
AI retrieval enforces authorization before model context construction.

INV-ERP-ANA-035
Vector stores inherit security, residency and retention obligations.

INV-ERP-ANA-036
Data quality and pipeline health remain separate.

INV-ERP-ANA-037
Financial Data Products expose reconciliation quality.

INV-ERP-ANA-038
Material analytical outputs preserve lineage.

INV-ERP-ANA-039
Bulk exports receive explicit authorization.

INV-ERP-ANA-040
Machine-readable exports have versioned schemas.

INV-ERP-ANA-041
Financial exports preserve decimal precision.

INV-ERP-ANA-042
Tenant isolation survives analytical replication.

INV-ERP-ANA-043
LegalEntity access survives analytical replication.

INV-ERP-ANA-044
Market does not substitute for security authorization.

INV-ERP-ANA-045
Analytical copies obey ResidencyPolicy.

INV-ERP-ANA-046
Analytics workloads do not use ERP DB superuser credentials.

INV-ERP-ANA-047
Heavy analytical workloads do not compete with ERP transaction processing by design.

INV-ERP-ANA-048
Read replicas are not automatically enterprise warehouses.

INV-ERP-ANA-049
Near-real-time projections expose freshness.

INV-ERP-ANA-050
Batch remains valid where appropriate.

INV-ERP-ANA-051
Critical analytical projections are reconcilable.

INV-ERP-ANA-052
Analytical correction does not mutate ERP merely to force agreement.

INV-ERP-ANA-053
Retention applies independently to downstream analytical copies.

INV-ERP-ANA-054
ERP upgrades include analytical compatibility testing.

INV-ERP-ANA-055
Critical analytical transformations are source controlled.

INV-ERP-ANA-056
Financial transformations receive appropriate governance.

INV-ERP-ANA-057
Large reports are not forced through synchronous transactional APIs.

INV-ERP-ANA-058
AI feedback enters ERP through governed commands.

INV-ERP-ANA-059
Analytical infrastructure does not become a central god service.

INV-ERP-ANA-060
A successful pipeline does not by itself prove correct data.
```

---

# Part XXXV — Initial Implementation

## 233. Initial analytical slice

The first production slice SHOULD establish:

```text
ERP
 │
 ├── Canonical Events
 │
 ├── Financial Export
 │
 └── Inventory Export
          │
          ▼
     Ingestion Layer
          │
          ▼
     Curated Store
          │
     ┌────┼─────────┐
     ▼    ▼         ▼
 Finance  BI   Intelligence
```

---

## 234. Initial Data Products

The initial ERP analytical Data Products SHOULD be:

```text
ERP Financial Actuals
ERP Accounts Receivable
ERP Accounts Payable
ERP Inventory Position
ERP Procurement
ERP Sales Accounting
```

---

## 235. Financial Actuals

`ERP Financial Actuals` SHALL preserve at minimum:

```text
canonical LegalEntity
accounting period
account
debit/credit
functional currency
original currency where applicable
canonical business reference
posting provenance
```

---

## 236. Accounts Receivable

The AR product SHOULD support:

```text
customer/Party
invoice
due date
currency
open amount
aging
payment/allocation status
LegalEntity
```

---

## 237. Inventory

The Inventory product SHOULD support:

```text
canonical Product
warehouse
quantity
valuation where authorised
cost
as_of
LegalEntity
```

---

## 238. Intelligence initial use cases

The Intelligence Engine SHOULD initially consume these products for low-risk analytical use cases such as:

```text
cash-flow forecasting
AR prioritisation
inventory demand forecasting
procurement analysis
margin analysis
```

rather than autonomous ERP mutation.

---

# Part XXXVI — Reference Architecture

## 239. End-to-end architecture

```text
                           BAOBAB PLATFORM

 ┌────────────────────────────────────────────────────────────┐
 │                   OPERATIONAL ENGINES                      │
 │                                                            │
 │  Payload        Medusa                 iDempiere           │
 │     │              │                       │               │
 └─────┼──────────────┼───────────────────────┼───────────────┘
       │              │                       │
       │              │             Authoritative ERP Facts
       │              │                       │
       └──────────────┼───────────────┬───────┘
                      │               │
                      ▼               ▼
                Canonical Events   Governed Export/
                                   Replication
                      │               │
                      └───────┬───────┘
                              ▼
                     DATA INGESTION
                              │
                              ▼
                      GOVERNED DATA
                         PLATFORM
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
                 Raw/Data   Curated   Semantic
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
           FINANCE BI      OPERATIONS    INTELLIGENCE
                                             │
                                             ▼
                                        Predictions
                                             │
                                             ▼
                                      Recommendations
                                             │
                                             ▼
                                      Governed Commands
                                             │
                                             ▼
                                         iDempiere
```

---

# Part XXXVII — Definition of Done

## 240. ADR implementation is complete when

- [ ] Production ERP database is not exposed as general BI infrastructure.
- [ ] approved ERP data-egress mechanisms exist.
- [ ] canonical events remain distinct from CDC.
- [ ] financial export contract exists.
- [ ] inventory export contract exists.
- [ ] analytical ingestion is idempotent.
- [ ] canonical IDs survive into curated analytical data.
- [ ] historical mappings are preserved.
- [ ] accounting-date semantics are preserved.
- [ ] currency semantics are preserved.
- [ ] financial Data Products reconcile to ERP.
- [ ] metric definitions are governed.
- [ ] Data Product ownership is assigned.
- [ ] Data Product schemas are versioned.
- [ ] freshness expectations are documented.
- [ ] quality checks exist.
- [ ] reconciliation checks exist.
- [ ] lineage exists for material financial outputs.
- [ ] Tenant isolation survives ingestion.
- [ ] LegalEntity isolation survives ingestion.
- [ ] ResidencyPolicy applies to analytical stores.
- [ ] analytical workload credentials are least privilege.
- [ ] ERP DB superuser is unavailable to analytics.
- [ ] bulk exports are separately authorised.
- [ ] export activity is auditable where required.
- [ ] temporary exports expire.
- [ ] report artifacts follow ADR-ERP-017.
- [ ] Intelligence consumes governed Data Products.
- [ ] Intelligence has no unrestricted ERP database access.
- [ ] AI predictions remain distinct from facts.
- [ ] AI recommendations use governed commands for mutation.
- [ ] AI retrieval applies authorization before retrieval.
- [ ] vector/feature stores participate in data governance.
- [ ] ERP data is not automatically model-training data.
- [ ] pipeline observability exists.
- [ ] data-quality observability exists.
- [ ] financial reconciliation alerts exist.
- [ ] ERP upgrade testing includes analytics compatibility.
- [ ] analytical transformations are source controlled.
- [ ] financial transformation changes are reviewable.
- [ ] recovery procedures include post-restore reconciliation.
- [ ] initial Finance, AR, AP, Inventory and Procurement products are tested.

---

# 241. Final architectural distinction

```text
TRANSACTION
     │
     ▼
  iDempiere
     │
     │ establishes
     ▼
 BUSINESS FACT
     │
     ├──────────────► Operational Report
     │
     ├──────────────► Financial Report
     │
     ├──────────────► Data Product
     │
     └──────────────► Analytical Projection
                              │
                              ▼
                         Intelligence
                              │
                              ▼
                         Prediction
                              │
                              ▼
                       Recommendation
```

These concepts SHALL never collapse into:

```text
Prediction = Fact
Dashboard = Ledger
Warehouse = ERP
AI = Accountant
CDC = Business Contract
```

---

# 242. Definitive statements

> **iDempiere owns ERP facts; the analytical platform owns derived analytical representations of those facts.**

> **The closer a result is presented as financial truth, the stronger its lineage and reconciliation to iDempiere must be.**

> **The Baobab Intelligence Engine may reason over ERP information, but reasoning about financial state does not confer authority to create financial state.**

And finally:

> **Baobab SHALL move computation to governed copies of ERP data rather than moving uncontrolled analytical computation onto the ERP system of record.**

This preserves iDempiere as a stable transactional and accounting authority while allowing the Baobab Platform to develop sophisticated reporting, group analytics, forecasting and AI capabilities independently of the ERP engine's operational lifecycle.