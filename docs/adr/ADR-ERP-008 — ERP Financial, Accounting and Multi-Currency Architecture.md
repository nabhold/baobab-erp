# ADR-ERP-008 — ERP Financial, Accounting and Multi-Currency Architecture

**Status:** Accepted  
**Decision class:** ERP / Finance / Accounting / Multi-Currency / Multi-Market / Controls  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-cp`, `nabhold/shared`, `nabhold/baobab-trade`, consuming Digital Estates and analytical systems  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-007  
**Date:** 2026-09-02

---

# 1. Decision

The Baobab ERP Engine SHALL use iDempiere as the authoritative operational accounting engine for ERP-controlled financial state.

The architecture SHALL explicitly distinguish:

```text id="o6v33m"
Legal Entity
Market
Jurisdiction
Accounting Schema
Ledger / Book
Functional Currency
Document Currency
Price-List Currency
Settlement Currency
Reporting Currency
Consolidation Currency
Exchange Rate
Accounting Date
Document Date
Posting Time
Fiscal Calendar
Accounting Period
```

These concepts SHALL NOT be collapsed into a single tenant, market or currency configuration.

The financial architecture SHALL support:

- independent legal entities;
- multiple markets per legal entity;
- multiple currencies;
- multiple accounting/reporting books where required;
- jurisdiction-specific accounting configuration;
- explicit exchange-rate authority;
- controlled accounting periods;
- auditable posting;
- reversal rather than destructive rewriting;
- intercompany transactions;
- consolidation without destroying subsidiary autonomy;
- inventory valuation and costing;
- tax localisation;
- regional deployment;
- eventual financial analytics and intelligence.

---

# 2. Governing principle

The central rule is:

> **Financial truth belongs to the accounting domain, while market, tenant and deployment context determine where and under whose authority that truth is recorded.**

Therefore:

```text id="j60krx"
Market
```

does not automatically determine:

```text id="cczzpn"
Accounting Currency
```

and:

```text id="k3th0r"
EngineInstance Region
```

does not determine:

```text id="4b5wlg"
Legal Jurisdiction
```

and:

```text id="u8dtjq"
Commerce Currency
```

does not automatically become:

```text id="whlcrj"
Ledger Currency
```

---

# 3. Accounting authority

iDempiere SHALL be authoritative for ERP accounting state including, where applicable:

```text id="n25v5x"
General Ledger
Accounts Payable
Accounts Receivable
financial document posting
accounting periods
accounting schemas
costing
inventory valuation
payment accounting
tax accounting
financial document status
```

Other Baobab engines SHALL not independently reproduce these accounting authorities.

---

# 4. No shadow ledger in Medusa

The Trade Engine MAY own:

```text id="kduy80"
cart
checkout
commerce order
sales-channel price
promotion
commercial customer state
commerce payment orchestration
```

but SHALL NOT independently become Baobab's general ledger.

---

# 5. Commerce amount versus accounting amount

A commerce transaction may produce:

```text id="1c8j51"
commerce order total
```

and later:

```text id="jtz65m"
accounting document amount
```

These values SHOULD reconcile.

They are not automatically the same domain fact.

---

# 6. Legal entity accounting boundary

Financial books SHALL ultimately belong to the legal entity responsible for the transaction.

A tenant may contain multiple legal entities.

Therefore:

```text id="yfl4rh"
Tenant
    1
    │
    └── N LegalEntities
             │
             └── financial books
```

is valid.

---

# 7. Tenant is not ledger

A Baobab Tenant SHALL NOT automatically equal:

```text id="upufb8"
one accounting schema
one chart of accounts
one currency
one fiscal calendar
one tax regime
```

Those are separately governed financial configurations.

---

# 8. Legal entity is not market

A legal entity may operate in:

```text id="jnq5nt"
South Africa
Uganda
Kenya
European Union markets
```

without becoming four legal entities merely because it trades in four markets.

Whether local incorporation is required is a legal/business decision, not an ERP identity shortcut.

---

# 9. Market is not accounting book

A Market MAY influence:

```text id="36n5l6"
currency
tax
pricing
language
commercial rules
regulation
```

but does not automatically imply a separate ledger.

---

# 10. Jurisdiction

Baobab SHALL distinguish:

```text id="z8nlpv"
Market
```

from:

```text id="cmxxeo"
Jurisdiction
```

A Market describes commercial operation.

A Jurisdiction describes a legal/regulatory authority relevant to the transaction or entity.

---

# 11. Deployment region

Likewise:

```text id="ksazhz"
DeploymentRegion
```

answers:

> Where does the software run?

It SHALL not answer:

> Which accounting rules apply?

---

# 12. Accounting Schema

iDempiere Accounting Schemas SHALL represent accounting rules appropriate to the legal entity/book.

Relevant configuration includes:

```text id="a6mfx5"
accounting currency
chart of accounts
costing rules
calendar
accounting defaults
posting configuration
```

---

# 13. Accounting Schema is ERP-native

Baobab SHALL not reproduce the entire iDempiere Accounting Schema model in the Control Plane.

The Control Plane MAY retain canonical metadata such as:

```text id="qfm7ha"
legal entity
financial capability
expected functional currency
jurisdiction
ERP EngineInstance
```

while detailed accounting configuration remains ERP-owned.

---

# 14. Multiple accounting schemas

A legal entity MAY require more than one accounting schema/book.

Examples include:

```text id="dqk8ly"
statutory accounting
management accounting
group reporting
alternative accounting standard
```

Such configuration SHALL be introduced only for an actual reporting/accounting requirement.

---

# 15. Do not create accounting schemas casually

Multiple schemas multiply:

```text id="dzjs25"
posting
reconciliation
configuration
testing
reporting
operational complexity
```

Therefore they SHALL not be created merely because the platform supports them.

---

# 16. Chart of Accounts

Each accounting environment SHALL have a governed Chart of Accounts.

The architecture SHALL distinguish:

```text id="nmsl4x"
local statutory accounts
group reporting taxonomy
management reporting dimensions
```

where required.

---

# 17. Group chart versus local chart

Baobab MAY eventually define a group-level reporting taxonomy.

This SHALL NOT require every subsidiary to destroy local statutory accounting requirements.

Possible architecture:

```text id="e9wtus"
Local Chart of Accounts
          │
          ▼
Group Account Mapping
          │
          ▼
Consolidated Reporting Taxonomy
```

---

# 18. Account mapping

Group reporting mappings SHALL be explicit.

They SHALL not rely solely on identical account numbers across subsidiaries.

---

# 19. Functional currency

Each financial book SHALL have an explicitly configured functional/accounting currency.

Example:

```text id="z60etv"
Thamani South African legal entity

Functional Currency:
    ZAR
```

This does not prohibit transactions in:

```text id="ed0htf"
USD
EUR
UGX
KES
```

---

# 20. Functional currency is not tenant currency

Baobab SHALL NOT define one universal:

```text id="8bwpnx"
tenant.currency
```

and assume it solves financial currency semantics.

---

# 21. Document currency

Every monetary business document SHALL have an explicit document currency.

Example:

```text id="0kr6na"
Supplier Invoice
    currency = USD
```

while:

```text id="p3t9wl"
Accounting Schema
    currency = ZAR
```

---

# 22. Foreign-currency transaction

Example:

```text id="htc59l"
South African entity
Functional currency = ZAR

Supplier invoice
Document currency = USD

Invoice amount
USD 10,000
```

The ERP SHALL determine the corresponding accounting amount using the authorised exchange rate.

---

# 23. Price-list currency

Commerce or ERP price lists MAY operate in currencies different from functional currency.

Example:

```text id="0k6cme"
ZA B2B price list = ZAR
Uganda B2B price list = UGX
Export price list = USD
```

These SHALL remain commercial pricing concerns.

---

# 24. Settlement currency

The currency in which a transaction is settled MAY differ from document or accounting currency where business rules permit.

Therefore:

```text id="v4m1d8"
document currency
settlement currency
functional currency
```

SHALL remain distinguishable.

---

# 25. Reporting currency

Management reporting MAY require:

```text id="omv5ax"
USD
ZAR
EUR
```

or another reporting currency independent of the legal entity's functional currency.

Reporting currency SHALL not silently replace accounting currency.

---

# 26. Consolidation currency

Group consolidation MAY use a designated consolidation currency.

Example:

```text id="frx7ru"
Subsidiary A → ZAR
Subsidiary B → UGX
Subsidiary C → KES

             ↓

Group Consolidation
        currency = USD
```

The actual chosen currency is a governance decision.

---

# 27. Currency model

Baobab SHALL therefore recognise:

```text id="g6ylkw"
FunctionalCurrency
DocumentCurrency
PriceListCurrency
SettlementCurrency
ReportingCurrency
ConsolidationCurrency
```

as distinct roles.

A currency code may occupy several roles, but the roles SHALL not be conflated.

---

# 28. Canonical money representation

Cross-engine contracts SHALL represent money as:

```json id="zw5e09"
{
  "amount": "1250.50",
  "currency": "ZAR"
}
```

Binary floating point SHALL NOT be used for canonical financial values.

---

# 29. Decimal precision

Financial amounts SHALL use exact decimal arithmetic.

Precision and scale SHALL be governed by:

```text id="d5hwkd"
currency
document
tax
pricing
accounting
```

requirements.

---

# 30. No universal two-decimal assumption

Baobab SHALL NOT assume:

```text id="kx1n37"
all currencies = 2 decimals
```

Currency precision SHALL be data-driven.

---

# 31. Quantity precision

Quantity precision SHALL remain separate from monetary precision.

Example:

```text id="8k1r0e"
Coffee quantity:
    18,750.375 KG

Unit price:
    USD 4.8725 / KG
```

may require more precision than final currency rounding.

---

# 32. Rounding

Rounding SHALL occur according to explicit domain rules.

The system SHALL distinguish:

```text id="ud0lfc"
unit-price rounding
line rounding
tax rounding
document-total rounding
currency rounding
accounting conversion rounding
```

---

# 33. Rounding reconciliation

Where rounding creates differences, ERP SHALL use controlled accounting mechanisms rather than silently modifying line values.

---

# 34. Exchange rates

Exchange rates SHALL be governed financial data.

An exchange rate SHALL conceptually include:

```text id="ah9ue4"
from_currency
to_currency
rate
rate_type
valid_from
valid_to
source
authority
created_at
approved_at where required
```

---

# 35. Exchange-rate authority

Baobab SHALL distinguish:

```text id="du06rt"
market FX observation
```

from:

```text id="34csob"
authorised accounting exchange rate
```

An external market-data feed SHALL NOT automatically become the accounting rate merely because it is newer.

---

# 36. FX sources

Possible sources MAY include:

```text id="b6zz5l"
central bank
commercial bank
approved financial-data provider
manual treasury rate
contractual rate
```

The permitted source depends on legal entity, transaction and policy.

---

# 37. Rate type

Rates MAY require explicit types such as:

```text id="8vhmqv"
spot
daily accounting
monthly average
month-end closing
contractual
customs
management reporting
```

These SHALL not be interchangeable.

---

# 38. Effective date

Every exchange-rate application SHALL identify the date/time basis used to select the rate.

---

# 39. Accounting rate provenance

For financially material conversions, Baobab SHOULD be able to answer:

> Which exchange rate was used?

> Which source supplied it?

> Which rate type applied?

> For what effective date?

---

# 40. Historical rate integrity

Posting history SHALL not change merely because a newer exchange rate becomes available.

---

# 41. FX correction

If an incorrect accounting rate was used, correction SHALL follow authorised accounting adjustment/reversal mechanisms.

The historical transaction SHALL not silently recalculate itself.

---

# 42. Unrealised FX

Where applicable, foreign-currency open balances MAY require unrealised gain/loss revaluation.

This SHALL be performed by ERP financial processes.

---

# 43. Realised FX

Settlement of foreign-currency receivables/payables MAY produce realised exchange gains/losses.

ERP SHALL remain authoritative for these accounting effects.

---

# 44. Trade Engine and FX

Medusa MAY calculate/display commerce prices using approved commerce FX rules.

Those rates SHALL not automatically be used for ledger posting.

---

# 45. Accounting date

Every financial document SHALL preserve an explicit:

```text id="2zyx0n"
accounting_date
```

where applicable.

This determines the accounting period into which the transaction posts.

---

# 46. Document date

`document_date` represents the business/document date.

It MAY differ from accounting date.

Example:

```text id="9x5c29"
Supplier invoice date:
    31 August

Received:
    2 September

Accounting date:
    2 September
```

---

# 47. Posting timestamp

`posted_at` represents the actual system instant at which posting completed.

It SHALL not replace accounting date.

---

# 48. Temporal model

Financial contracts SHALL preserve:

```text id="f38mup"
document_date
accounting_date
occurred_at where applicable
posted_at
created_at
updated_at
```

as distinct concepts.

---

# 49. Time zones

Business dates SHALL be interpreted according to the appropriate legal/entity/ERP business timezone.

They SHALL not be derived casually by truncating UTC timestamps.

---

# 50. Accounting calendar

Each accounting book SHALL use an explicitly governed accounting calendar.

---

# 51. Accounting periods

Accounting periods SHALL have controlled lifecycle such as:

```text id="ujb96h"
open
closed
temporarily reopened
permanently closed
```

according to ERP capabilities and finance policy.

---

# 52. Closed period

A normal business API SHALL NOT post a transaction into a closed accounting period.

Expected result:

```text id="h33jha"
ERP_ACCOUNTING_PERIOD_CLOSED
```

---

# 53. Reopening periods

Period reopening SHALL be a privileged financial operation.

It SHOULD require:

```text id="12g97d"
authorised role
reason
audit
approval where policy requires
```

---

# 54. Backdating

Backdated posting SHALL be controlled.

Possession of API write permission SHALL not automatically grant authority to post into arbitrary historical periods.

---

# 55. Future dating

Future accounting dates SHALL likewise follow explicit policy.

---

# 56. Posting

Financial posting SHALL use native iDempiere document-processing/accounting mechanisms.

Baobab SHALL NOT implement a parallel posting engine.

---

# 57. Posted state

Once a financial document is posted, ordinary API mutation SHALL be heavily restricted.

---

# 58. Immutability after posting

Posted financial facts SHALL be treated as economically immutable.

Corrections SHALL normally use:

```text id="h2bpnf"
reversal
credit note
debit note
adjustment
correcting journal
```

according to document type.

---

# 59. No DELETE posted invoice

This SHALL never be an ordinary business operation:

```http id="sotzw4"
DELETE /erp/v1/supplier-invoices/{posted-invoice}
```

---

# 60. No PATCH accounting history

Likewise:

```http id="u4gxfk"
PATCH /erp/v1/supplier-invoices/{id}

{
  "total": "different value"
}
```

SHALL not rewrite a posted accounting fact.

---

# 61. Reversal linkage

A reversal SHALL preserve explicit relationship to the original document.

Conceptually:

```text id="n1ag6n"
Original Invoice
      │
      ▼
Reversal Document
```

Both remain auditable.

---

# 62. Reversal event

Canonical events SHOULD include:

```text id="9g8vmm"
erp.supplier-invoice.reversed.v1
```

rather than deleting the earlier:

```text id="twax5k"
erp.supplier-invoice.posted.v1
```

event.

---

# 63. Audit trail

Financial audit SHALL preserve:

```text id="j2o6qz"
who initiated
who approved
who posted
when
accounting date
source system
correlation ID
original document
reversal/correction relationship
```

where applicable.

---

# 64. Source document

Financial documents created from another Baobab engine SHALL retain canonical source references.

Example:

```text id="k6y6z1"
ERP CustomerInvoice
       │
       └── source:
              Canonical SalesOrder
```

---

# 65. Source system does not own posting

A Trade-originated invoice instruction does not mean Trade owns accounting posting.

ERP validates and posts according to ERP rules.

---

# 66. Sales flow

Recommended high-level flow:

```text id="gzt8b6"
Digital Estate
      ↓
Trade Engine
      ↓
Commerce Order
      ↓
Canonical integration
      ↓
ERP
      ↓
Customer Invoice
      ↓
Posting
      ↓
General Ledger
```

---

# 67. Procurement flow

```text id="3dvnd6"
ERP Purchase Order
      ↓
Goods Receipt
      ↓
Supplier Invoice
      ↓
Matching / validation
      ↓
Posting
      ↓
Accounts Payable / GL
```

---

# 68. Purchase-to-pay authority

The ERP Engine SHALL own procurement accounting consequences.

Digital Estates SHALL not directly create journal entries to represent procurement.

---

# 69. Order-to-cash authority

Commerce may own order capture.

ERP SHALL own accounting consequences such as:

```text id="sjuyqg"
customer receivable
revenue posting
tax posting
cost accounting
```

where ERP is configured as financial authority.

---

# 70. Payment orchestration

Commerce/payment services MAY interact with payment providers.

ERP SHALL receive the canonical financial fact required to represent settlement.

---

# 71. Payment intent versus payment

Baobab SHALL distinguish:

```text id="q6rr4u"
PaymentIntent
PaymentProviderTransaction
Payment
PaymentAllocation
```

where domain semantics require.

These SHALL not automatically share one canonical ID.

---

# 72. Payment allocation

ERP SHALL remain authoritative for allocation of accounting payments to:

```text id="94jv7d"
invoices
credit memos
other open items
```

where applicable.

---

# 73. Bank reconciliation

Bank reconciliation SHALL be an ERP/finance capability.

External bank feeds may provide observations.

They SHALL not directly mutate the ledger without governed reconciliation.

---

# 74. Tax

Tax determination SHALL be governed according to:

```text id="fsz3cp"
legal entity
jurisdiction
transaction
product/service
customer/supplier status
document date
```

and other applicable rules.

---

# 75. Market does not equal tax regime

A Market may participate in tax determination.

It SHALL not be the sole tax authority.

---

# 76. Tax configuration

iDempiere localisation/configuration SHALL hold ERP tax structures where appropriate.

Baobab canonical contracts SHOULD expose tax results without leaking internal tax table IDs.

---

# 77. Canonical tax amount

Example:

```json id="jj94wo"
{
  "tax": {
    "amount": "2250.00",
    "currency": "ZAR"
  }
}
```

Native tax IDs remain implementation details unless an explicitly canonical tax classification is defined.

---

# 78. Tax rates are temporal

Tax rates SHALL have effective dates.

Historical posted transactions SHALL preserve the applied rate/result.

---

# 79. Tax change

A future VAT-rate change SHALL not retroactively alter already posted historical documents.

---

# 80. Localisation

Jurisdiction-specific ERP localisation SHALL use supported iDempiere extension/configuration mechanisms.

No localisation SHALL require an uncontrolled permanent fork of iDempiere.

---

# 81. Localisation does not equal EngineInstance

Multiple localisations MAY coexist where technically safe.

A separate EngineInstance SHALL be required only when isolation, incompatibility, regulation or operational concerns justify it.

---

# 82. Inventory accounting

Where inventory is financially valued, ERP SHALL own:

```text id="4czs9u"
inventory valuation
costing
accounting consequences of receipts/issues
```

---

# 83. Commerce inventory versus accounting inventory

Medusa may maintain commerce-facing availability.

ERP may maintain accounting inventory.

These are related but not automatically identical quantities.

---

# 84. Inventory concepts

Baobab SHALL distinguish where necessary:

```text id="n7s2qn"
physical on-hand
available-to-promise
reserved
in-transit
accounting inventory
commerce availability
```

---

# 85. Costing method

Costing method SHALL be an ERP/accounting configuration.

Possible methods depend on iDempiere capability and business policy.

The canonical platform SHALL not hard-code one universal costing method.

---

# 86. Costing scope

Costing may vary according to ERP configuration such as:

```text id="1mfnw4"
product
organization
warehouse
accounting schema
```

where supported/required.

---

# 87. Cost changes

A change in product cost SHALL not automatically rewrite previously posted accounting entries.

---

# 88. Landed cost

Import-heavy businesses MAY require landed-cost accounting.

Relevant costs can include:

```text id="i7nw7v"
freight
insurance
customs duty
port charges
inspection
clearing
inland transport
```

---

# 89. Landed cost architecture

Landed-cost allocation SHALL be performed in ERP according to approved accounting policy.

Trade SHALL not independently calculate authoritative inventory valuation.

---

# 90. Import procurement

For imported goods:

```text id="k9dzxp"
Foreign Supplier
      ↓
Purchase Order
      ↓
Shipment
      ↓
Goods Receipt
      ↓
Supplier Invoice
      ↓
Freight / Duty / Charges
      ↓
Landed Cost Allocation
      ↓
Inventory Valuation
```

shall be representable without assuming one currency.

---

# 91. Customs currency

Customs valuation currency/rate MAY differ from:

```text id="ww5j97"
supplier invoice currency
functional currency
settlement currency
```

where jurisdictional rules require.

This SHALL be explicitly modelled where needed.

---

# 92. Intercompany transactions

Baobab SHALL treat independent legal entities as independent accounting parties.

A transaction between subsidiaries is not an internal database shortcut.

---

# 93. Intercompany representation

Example:

```text id="bh03aq"
Legal Entity A
      │
      │ sells goods
      ▼
Legal Entity B
```

shall normally produce corresponding:

```text id="a2k5uq"
seller-side transaction
buyer-side transaction
```

according to accounting policy.

---

# 94. No cross-client journal shortcut

Where legal entities occupy different `AD_Client`s, Baobab SHALL NOT create cross-client SQL transactions to simulate intercompany accounting.

---

# 95. Intercompany orchestration

Intercompany workflows SHALL use:

```text id="n6dkxn"
canonical identity
APIs
events
reconciliation
```

between the relevant accounting contexts.

---

# 96. Intercompany Party representation

Each legal entity may need the other represented as a Business Partner in its ERP Client.

Example:

```text id="dn64g1"
Canonical LegalEntity B
        │
        ▼
Party representation in Entity A ERP context
        │
        ▼
C_BPartner
```

This does not merge their accounting boundaries.

---

# 97. Transfer pricing

Intercompany pricing SHALL follow approved business/tax policy.

The platform SHALL not infer transfer pricing merely from shared ownership.

---

# 98. Consolidation

Group consolidation SHALL occur above independent subsidiary accounting books.

---

# 99. Consolidation does not justify shared ledger

The need to produce:

```text id="a6p4pf"
Nabhold Group consolidated statements
```

SHALL NOT by itself justify placing every subsidiary inside one `AD_Client`.

---

# 100. Consolidation architecture

Conceptually:

```text id="7e7agc"
Nabhold books ───────┐
                     │
Thamani books ───────┼──► Consolidation Layer
                     │
Zuribeans books ─────┘
```

---

# 101. Consolidation mapping

Consolidation MAY require:

```text id="xkm76f"
account mapping
currency translation
intercompany elimination
ownership percentage
reporting-period alignment
```

These SHALL be explicit.

---

# 102. Intercompany elimination

Consolidation SHALL eliminate relevant intercompany balances/transactions according to group accounting policy.

Operational source transactions SHALL remain intact.

---

# 103. Consolidation is not source mutation

The consolidated result SHALL not rewrite subsidiary books.

---

# 104. Fiscal calendars

Different legal entities MAY operate different fiscal calendars where required.

The architecture SHALL not assume every tenant closes on the same calendar.

---

# 105. Reporting period alignment

Consolidation across different calendars SHALL use explicit period-alignment rules.

---

# 106. Financial dimensions

Management accounting MAY require dimensions such as:

```text id="h4o73r"
legal entity
organization
business unit
product
market
project
cost center
profit center
```

These SHALL be mapped deliberately to ERP accounting dimensions.

---

# 107. Do not copy canonical hierarchy blindly

The Baobab organisation hierarchy SHALL not automatically become ERP accounting dimensions.

Only financially meaningful dimensions SHALL be represented.

---

# 108. Market reporting

Market profitability MAY be required without creating one `AD_Org` per Market.

Possible mechanisms include:

```text id="4i8l9j"
accounting dimension
product/category
campaign
project
custom dimension
analytical projection
```

depending on ERP design.

---

# 109. Digital Estate reporting

A Digital Estate MAY be useful as a management reporting dimension.

It SHALL NOT automatically become an accounting organisation.

---

# 110. Financial event architecture

Financial events SHALL represent completed authoritative facts.

Examples:

```text id="vz9c4l"
erp.supplier-invoice.posted.v1
erp.customer-invoice.posted.v1
erp.payment.completed.v1
erp.payment.allocated.v1
erp.goods-receipt.completed.v1
erp.accounting-period.closed.v1
```

---

# 111. Event immutability

Once emitted:

```text id="l71c9j"
invoice.posted
```

SHALL not be modified because a later reversal occurred.

Instead:

```text id="5wqpvb"
invoice.reversed
```

is emitted.

---

# 112. Event money

Financial event payloads SHALL always include explicit currency for monetary amounts.

---

# 113. Event accounting date

Posting-related events SHOULD include:

```text id="ifk2ss"
accounting_date
posted_at
```

as distinct values.

---

# 114. Event exchange-rate metadata

Where cross-engine consumers genuinely require it, an event MAY include:

```text id="xmq48z"
transaction currency
accounting currency
exchange rate/reference
```

Sensitive or unnecessary accounting internals SHALL not be broadcast.

---

# 115. API command validation

ERP financial commands SHALL validate:

```text id="gqt8ry"
Context
legal entity
currency
accounting period
counterparty mapping
product mapping
document state
authorization
```

before completing authoritative processing.

---

# 116. Financial idempotency

Create/post/payment commands SHALL support idempotency where retries could otherwise create duplicate financial effects.

---

# 117. Duplicate supplier invoice prevention

ERP SHOULD support controls using combinations such as:

```text id="em67c0"
supplier
supplier invoice number
legal entity
document type
invoice date
```

according to policy.

Canonical idempotency SHALL complement—not replace—ERP duplicate-document controls.

---

# 118. Duplicate payment prevention

Payment integration SHALL preserve provider/bank references and canonical idempotency sufficient to prevent accidental duplicate representation.

---

# 119. Three-way matching

Procurement policy MAY require:

```text id="48lpsr"
Purchase Order
     +
Goods Receipt
     +
Supplier Invoice
```

matching before payment/accounting approval.

This SHALL remain an ERP business capability.

---

# 120. Approval workflows

Financial approvals SHALL be policy-driven.

Examples:

```text id="l7ynlf"
purchase approval
invoice approval
payment approval
journal approval
period reopening
```

---

# 121. Separation of duties

Production financial authorization SHALL support separation of duties.

A single service identity SHALL not automatically be able to:

```text id="xsz0am"
create supplier
create invoice
approve invoice
create payment
approve payment
reconcile payment
```

without explicit policy.

---

# 122. Machine identities

Automation MAY perform authorised financial operations.

Machine identity SHALL remain:

```text id="0is6wu"
traceable
least-privileged
tenant-scoped
capability-scoped
```

---

# 123. Human approval

Where financial policy requires human approval, an automated integration SHALL not bypass that workflow merely because it can call the API.

---

# 124. Journal entries

Direct journal APIs SHALL be highly restricted.

Most business accounting SHOULD originate from appropriate subledger documents/processes.

---

# 125. Manual journal

Manual journal creation SHALL require dedicated finance authorization and audit.

---

# 126. No generic ledger write API

Baobab SHALL NOT expose:

```http id="lv5gpi"
POST /erp/v1/general-ledger/write-anything
```

to ordinary consumers.

---

# 127. Analytical reads

Detailed ledger data SHOULD be supplied to analytics through:

```text id="a35w5d"
approved reporting APIs
read replicas
data exports
event-driven projections
analytical pipelines
```

rather than unrestricted production database access.

---

# 128. Operational database protection

BI tools SHALL NOT run arbitrary heavyweight queries against the primary ERP transactional database.

---

# 129. Financial snapshots

Analytical pipelines MAY create:

```text id="uv2mzk"
trial balance snapshots
aged receivable snapshots
aged payable snapshots
inventory valuation snapshots
```

according to reporting requirements.

---

# 130. Intelligence Engine

The Intelligence Engine MAY analyse:

```text id="hdm5xr"
cash flow
working capital
FX exposure
inventory
procurement
payment behaviour
financial anomalies
```

from authorised financial projections/events.

---

# 131. AI does not post autonomously by default

AI analysis SHALL NOT directly create authoritative journal postings merely because a model recommends them.

Financial mutations SHALL return through controlled ERP commands/workflows.

---

# 132. Financial recommendation flow

```text id="b96g6g"
ERP financial data
       ↓
Intelligence Engine
       ↓
recommendation
       ↓
authorised workflow
       ↓
ERP command
       ↓
ERP validation/posting
```

---

# 133. Financial data classification

Financial data SHALL generally be treated as confidential.

Specific classifications SHALL distinguish:

```text id="1ksvq1"
transaction amounts
bank information
tax identifiers
payroll where later introduced
supplier terms
customer credit
ledger detail
```

---

# 134. Tenant isolation

Financial data from Tenant A SHALL not be visible to Tenant B merely because both share one EngineInstance.

---

# 135. Legal-entity isolation

Even within a broader Tenant, legal-entity financial visibility SHALL follow explicit authorization.

---

# 136. Group access

Group-level finance roles MAY have authorised visibility across subsidiaries.

Such access SHALL be:

```text id="d8ak5g"
explicit
audited
role-based
```

not implied merely by ownership hierarchy.

---

# 137. Data residency

Financial data placement SHALL comply with applicable ResidencyPolicy.

This includes:

```text id="7qdhqm"
primary database
replicas
backups
exports
event payloads
logs
analytical copies
```

---

# 138. Cross-border reporting

Where financial data cannot leave a region in raw form, Baobab MAY use:

```text id="1n27fl"
aggregated reporting
approved projections
regional analytics
metadata-only events
```

according to policy.

---

# 139. Backup

ERP financial databases SHALL receive production-grade backup and point-in-time recovery according to approved RPO/RTO.

---

# 140. Financial restore testing

Backup existence is insufficient.

Restore tests SHALL validate that:

```text id="svt99b"
documents
postings
accounting periods
mappings
outbox events
```

remain coherent.

---

# 141. Reconciliation after restore

After point-in-time recovery, ERP SHALL reconcile:

```text id="t7k9gn"
canonical mappings
integration inbox
transactional outbox
external payment state
commerce integration state
```

before unrestricted processing resumes.

---

# 142. Financial reconciliation

Baobab SHALL support reconciliation across bounded contexts.

Examples:

```text id="2px63q"
Trade orders
    ↔
ERP customer invoices

Payment provider transactions
    ↔
ERP payments

Goods receipts
    ↔
supplier invoices

ERP subledgers
    ↔
general ledger
```

---

# 143. Reconciliation does not create shared ownership

Reconciliation compares authoritative facts.

It does not make both systems authoritative for the same fact.

---

# 144. Daily controls

Production operations SHOULD eventually support scheduled controls such as:

```text id="6vgds9"
unposted document review
unallocated payment review
outbox backlog
integration failures
mapping failures
subledger/GL reconciliation
FX-rate completeness
closed-period violations
```

---

# 145. Financial observability

Metrics SHOULD include:

```text id="xpk3dj"
posting_failures_total
closed_period_rejections_total
currency_conversion_failures_total
missing_fx_rate_total
payment_allocation_failures_total
financial_reconciliation_failures_total
```

without leaking sensitive financial values into metric labels.

---

# 146. Audit observability

Logs SHALL allow authorised operators to trace:

```text id="a8br2u"
canonical document
ERP document
correlation ID
EngineInstance
Tenant
LegalEntity
Market
posting outcome
```

---

# 147. No amount in routine log labels

Financial amounts, account numbers and personal banking details SHALL not become routine observability labels.

---

# 148. Configuration as code

Stable financial configuration templates MAY be version-controlled where appropriate.

Examples:

```text id="6lqu62"
accounting template definitions
integration configuration
localisation configuration
approved chart templates
```

---

# 149. Master data is not deployment configuration

Operational financial master data SHALL not be treated as ordinary infrastructure configuration.

For example:

```text id="91hvjl"
supplier
invoice
payment
exchange rate
```

is not Terraform-style deployment state.

---

# 150. Financial configuration promotion

Changes to:

```text id="55bl23"
chart of accounts
posting rules
costing
tax
accounting schema
```

SHALL follow controlled change-management procedures.

---

# 151. Testing

Financial architecture SHALL have dedicated regression tests.

---

# 152. Posting regression tests

Tests SHALL verify that representative documents produce expected accounting consequences.

---

# 153. Multi-currency tests

Tests SHALL cover:

```text id="krs5sh"
same-currency posting
foreign-currency invoice
foreign-currency settlement
rate changes
rounding
missing rate
realised FX
revaluation where configured
```

---

# 154. Accounting-date tests

Tests SHALL cover:

```text id="4rkw1a"
open period
closed period
backdated transaction
future transaction
period boundary
timezone boundary
```

---

# 155. Tax tests

Every supported localisation SHALL include tax regression scenarios.

---

# 156. Inventory valuation tests

Costing and landed-cost changes SHALL have regression tests before production release.

---

# 157. Intercompany tests

Intercompany flows SHALL verify:

```text id="p72jcm"
separate legal entity context
correct counterparty
correct currency
correct mappings
correct events
no cross-client leakage
```

---

# 158. Upgrade testing

Every iDempiere upgrade SHALL include financial regression testing.

Passing unit tests alone is insufficient.

---

# 159. Golden accounting scenarios

Baobab SHOULD maintain a set of known financial scenarios with expected accounting outputs.

Examples:

```text id="r1fqvs"
domestic purchase
foreign purchase
import landed cost
domestic sale
foreign sale
customer payment
supplier payment
credit note
reversal
intercompany transaction
```

---

# 160. Financial contract tests

OpenAPI and AsyncAPI contracts SHALL test:

```text id="rypgnc"
money precision
currency presence
accounting date
canonical identity
idempotency
reversal relationships
```

---

# 161. Rejected alternative — one currency per Tenant

**Rejected.**

Tenant is not an accounting currency boundary.

---

# 162. Rejected alternative — currency determined from Market

**Rejected.**

Market and transaction currency are different concepts.

---

# 163. Rejected alternative — use commerce FX directly for accounting

**Rejected.**

Accounting rates require explicit financial authority.

---

# 164. Rejected alternative — Medusa as accounting ledger

**Rejected.**

Commerce and accounting are separate bounded contexts.

---

# 165. Rejected alternative — one AD_Client for group consolidation

**Rejected.**

Consolidation does not justify weakening subsidiary isolation.

---

# 166. Rejected alternative — one AD_Org per Market automatically

**Rejected.**

Market is not universally an accounting organisation.

---

# 167. Rejected alternative — rewrite posted documents

**Rejected.**

Corrections SHALL preserve financial history.

---

# 168. Rejected alternative — delete reversed documents

**Rejected.**

Original and correcting facts must remain auditable.

---

# 169. Rejected alternative — latest FX rate retroactively recalculates history

**Rejected.**

Historical accounting must remain stable.

---

# 170. Rejected alternative — floating-point money

**Rejected.**

Financial arithmetic requires decimal-safe representation.

---

# 171. Rejected alternative — universal two-decimal precision

**Rejected.**

Currency and business precision vary.

---

# 172. Rejected alternative — direct general-ledger access for every engine

**Rejected.**

Subledger/business processes SHALL mediate ordinary financial operations.

---

# 173. Rejected alternative — shared database for consolidation

**Rejected.**

Consolidation occurs through governed financial reporting, not cross-engine SQL.

---

# 174. Rejected alternative — analytics queries against primary ERP DB

**Rejected as normal architecture.**

Operational financial systems require workload isolation.

---

# 175. Rejected alternative — AI directly adjusts the ledger

**Rejected as default architecture.**

AI recommendations require authorised financial workflows.

---

# 176. Non-negotiable invariants

```text id="2g3x6b"
INV-ERP-FIN-001
iDempiere is authoritative for ERP accounting state.

INV-ERP-FIN-002
Trade does not become the general ledger.

INV-ERP-FIN-003
Tenant is not equivalent to accounting book.

INV-ERP-FIN-004
LegalEntity is not equivalent to Market.

INV-ERP-FIN-005
Market is not equivalent to accounting currency.

INV-ERP-FIN-006
DeploymentRegion does not determine accounting jurisdiction.

INV-ERP-FIN-007
Functional currency and document currency are distinct concepts.

INV-ERP-FIN-008
Price-list currency and functional currency are distinct concepts.

INV-ERP-FIN-009
Settlement currency and document currency may differ.

INV-ERP-FIN-010
Reporting currency does not replace accounting currency.

INV-ERP-FIN-011
Consolidation currency does not replace subsidiary functional currencies.

INV-ERP-FIN-012
Canonical monetary values use exact decimal semantics.

INV-ERP-FIN-013
Currency is explicit in canonical monetary contracts.

INV-ERP-FIN-014
Currency precision is data-driven.

INV-ERP-FIN-015
Accounting FX rates have explicit authority and provenance.

INV-ERP-FIN-016
Market FX observations do not automatically become accounting rates.

INV-ERP-FIN-017
Historical posted transactions are not silently recalculated with new FX rates.

INV-ERP-FIN-018
Accounting Date is distinct from Document Date.

INV-ERP-FIN-019
Accounting Date is distinct from posting timestamp.

INV-ERP-FIN-020
Closed accounting periods reject ordinary posting.

INV-ERP-FIN-021
Period reopening is privileged and audited.

INV-ERP-FIN-022
Financial posting uses native ERP processing.

INV-ERP-FIN-023
Posted financial documents are not destructively rewritten.

INV-ERP-FIN-024
Corrections preserve original financial history.

INV-ERP-FIN-025
Financial reversals maintain relationship to the original document.

INV-ERP-FIN-026
Inventory valuation remains ERP/accounting authority.

INV-ERP-FIN-027
Commerce availability is not automatically accounting inventory.

INV-ERP-FIN-028
Landed cost is an ERP financial capability.

INV-ERP-FIN-029
Independent legal entities remain independent accounting parties.

INV-ERP-FIN-030
Intercompany accounting does not use cross-client database shortcuts.

INV-ERP-FIN-031
Group consolidation does not mutate subsidiary books.

INV-ERP-FIN-032
Consolidation does not justify collapsing legal entities into one AD_Client.

INV-ERP-FIN-033
Tax configuration is temporal and jurisdiction-aware.

INV-ERP-FIN-034
Tax changes do not rewrite posted historical transactions.

INV-ERP-FIN-035
Direct ledger write capability is highly restricted.

INV-ERP-FIN-036
Financial create/post commands are idempotent where retry could duplicate effects.

INV-ERP-FIN-037
Financial data remains tenant-isolated.

INV-ERP-FIN-038
Group-level access is explicit rather than inherited automatically.

INV-ERP-FIN-039
Financial events preserve accounting date and canonical identity.

INV-ERP-FIN-040
Financial event corrections occur through subsequent events.

INV-ERP-FIN-041
Analytical systems do not own operational accounting state.

INV-ERP-FIN-042
AI does not acquire ledger authority by consuming financial data.

INV-ERP-FIN-043
Financial database recovery includes integration reconciliation.

INV-ERP-FIN-044
iDempiere upgrades require financial regression testing.

INV-ERP-FIN-045
Canonical financial contracts remain independent of iDempiere native IDs.
```

---

# 177. Initial Baobab financial model

For each ERP-enabled legal entity, provisioning SHALL determine at least:

```text id="o3x04j"
LegalEntity
    │
    ├── ERP CapabilityBinding
    ├── EngineInstance
    ├── AD_Client representation
    ├── Accounting Schema
    ├── Functional Currency
    ├── Fiscal Calendar
    ├── Chart of Accounts
    ├── Tax Configuration
    ├── Costing Configuration
    └── ERP Organizations as required
```

---

# 178. Example — South African operating entity

Illustrative only:

```text id="u3crfn"
LegalEntity
    Thamani South Africa

Tenant
    Thamani

Market
    South Africa

ERP
    ERP-AF-SOUTH-01

Functional Currency
    ZAR

Possible transaction currencies
    ZAR
    USD
    EUR
```

A USD coffee import SHALL therefore not require creating a USD tenant or USD legal entity.

---

# 179. Example — regional expansion

Suppose the same business later operates commercially in Uganda.

The architecture SHALL permit:

```text id="3cgnct"
Tenant
    Thamani

LegalEntity
    existing or newly incorporated entity
    according to actual legal structure

Market
    Uganda

Commerce currency
    UGX and/or other approved currency

ERP EngineInstance
    resolved by CapabilityBinding

Accounting currency
    determined by actual legal/accounting structure
```

Nothing in the architecture automatically declares:

```text id="4kzqlm"
Uganda Market = UGX ledger
```

until the financial/legal configuration says so.

---

# 180. Example — imported coffee

```text id="98f46f"
Supplier
    Uganda

Invoice
    USD 100,000

Buyer
    South African legal entity

Functional Currency
    ZAR

Additional costs
    Freight USD
    Insurance USD
    Customs/Duty ZAR
    Clearing ZAR
```

ERP SHALL be capable of producing:

```text id="6fop47"
purchase liability
currency conversion
landed cost
inventory valuation
tax/customs accounting
supplier payment
FX differences
```

without pushing accounting responsibility into Trade.

---

# 181. Example — group consolidation

```text id="1wpp69"
Nabhold
    Functional currency A

Thamani
    Functional currency B

Zuribeans
    Functional currency C

        │
        ▼
Group Consolidation
        │
        ├── account mapping
        ├── currency translation
        ├── intercompany elimination
        └── consolidated statements
```

Canonical legal entity identity allows consolidation without requiring shared operational ledgers.

---

# 182. Financial architecture model

```text id="6wnp0d"
                   BAOBAB CONTROL PLANE

                        Tenant
                          │
                     LegalEntity
                          │
                         Market
                          │
                 CapabilityBinding
                          │
                          ▼
                    EngineInstance
                          │
                          ▼
                      iDempiere
                          │
            ┌─────────────┼─────────────┐
            │             │             │
            ▼             ▼             ▼
      Accounting       Currency       Calendar
        Schema           Rules         Periods
            │
            ▼
        Documents
            │
            ▼
         Posting
            │
       ┌────┴────┐
       ▼         ▼
   Subledger      GL
       │
       ▼
  Financial Events
       │
       ▼
Analytics / Consolidation / Intelligence
```

---

# 183. Definition of done

ADR-ERP-008 SHALL be considered implemented when:

- [ ] ERP accounting authority is documented.
- [ ] LegalEntity financial ownership is explicit.
- [ ] Tenant and ledger are not conflated.
- [ ] Market and accounting book are not conflated.
- [ ] Functional currency is configured per applicable accounting book.
- [ ] Document currency is explicit.
- [ ] Price-list currency is explicit.
- [ ] Settlement currency can be represented separately.
- [ ] Reporting/consolidation currencies are separately governed.
- [ ] Canonical Money schema uses exact decimals.
- [ ] Currency precision is configurable.
- [ ] FX-rate source and rate type are governed.
- [ ] Accounting FX rates have provenance.
- [ ] Historical rate integrity is preserved.
- [ ] Accounting Date is represented distinctly.
- [ ] Closed-period enforcement exists.
- [ ] Period reopening is privileged.
- [ ] Posting uses native iDempiere processing.
- [ ] Posted-document mutation is restricted.
- [ ] Reversal/correction workflow exists.
- [ ] Tax configuration is localisation-aware.
- [ ] Tax rates preserve effective periods.
- [ ] Costing configuration is explicit.
- [ ] Inventory valuation is ERP-owned.
- [ ] Landed-cost capability is designed for import workflows.
- [ ] Intercompany flows preserve legal-entity isolation.
- [ ] Consolidation does not require shared AD_Client.
- [ ] Financial APIs use canonical IDs.
- [ ] Financial APIs enforce idempotency where required.
- [ ] Financial events use canonical IDs.
- [ ] Financial events preserve currency/accounting-date semantics.
- [ ] Financial data classification is established.
- [ ] Financial observability avoids sensitive-value leakage.
- [ ] Reconciliation processes exist.
- [ ] DR recovery includes financial/integration reconciliation.
- [ ] Golden accounting scenarios exist.
- [ ] Multi-currency regression tests exist.
- [ ] Tax regression tests exist per supported localisation.
- [ ] Costing/landed-cost regression tests exist where enabled.
- [ ] iDempiere upgrade gates include financial regression tests.

---

# 184. Final governing model

The financial architecture SHALL preserve:

```text id="z6c0qe"
WHO OWNS THE TRANSACTION?
        │
        ▼
    LegalEntity

WHERE IS BUSINESS CONDUCTED?
        │
        ▼
       Market

WHICH LAW/RULES APPLY?
        │
        ▼
    Jurisdiction

WHERE DOES ERP RUN?
        │
        ▼
   EngineInstance

WHICH BOOK RECEIVES THE ENTRY?
        │
        ▼
 Accounting Schema

IN WHAT CURRENCY IS THE BOOK KEPT?
        │
        ▼
 Functional Currency

IN WHAT CURRENCY WAS THE BUSINESS DOCUMENT?
        │
        ▼
 Document Currency

WHAT RATE TRANSLATES THEM?
        │
        ▼
 Authorised Exchange Rate

WHEN DOES THE ENTRY BELONG?
        │
        ▼
 Accounting Date / Period

WHAT MAKES IT FINANCIAL TRUTH?
        │
        ▼
 Native ERP Posting
```

None of these questions SHALL be answered merely by looking at a tenant name or country code.

---

# 185. Governing statement

Baobab SHALL never adopt the seductive but incorrect simplification:

```text id="6a0j1d"
one tenant
=
one company
=
one market
=
one country
=
one currency
=
one ledger
=
one ERP deployment
```

Instead:

```text id="j16lmr"
Tenant
LegalEntity
Market
Jurisdiction
Currency
AccountingBook
EngineInstance
```

remain independent dimensions connected by explicit contracts and policy.

That independence is what allows the platform to support:

```text id="0eyue4"
a South African entity importing in USD,
selling in ZAR,
reporting to a group in another currency,
operating in several markets,
running ERP in a regional deployment,
and later migrating that deployment
```

without redefining the enterprise every time one dimension changes.

The definitive financial rule is therefore:

> **Accounting configuration follows economic and legal reality; it must never be inferred from platform topology.**

And its architectural counterpart is:

> **Baobab owns the context in which accounting occurs; iDempiere owns the accounting consequences within that context.**