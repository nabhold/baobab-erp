# ADR-ERP-016 — Commerce–ERP Integration and Order-to-Cash Architecture

**Status:** Accepted  
**Decision class:** ERP / Commerce / Order-to-Cash / Payments / Returns / Integration  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-trade`, `nabhold/baobab-cp`, Digital Estates, payment-provider integrations, fulfillment integrations and `nabhold/shared`  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-015  
**Date:** 2026-09-02

---

# 1. Decision

Baobab SHALL integrate MedusaJS and iDempiere as **peer domain engines with different authorities**, rather than treating either engine as a persistence adapter for the other.

The principal boundary is:

```text
Medusa / Trade
    owns commerce intent and customer-facing commerce state

iDempiere / ERP
    owns financially authoritative enterprise consequences
```

Therefore:

> **A Commerce Order and an ERP Sales Order are related representations within an order-to-cash process; neither engine's native identifier nor lifecycle becomes the other's canonical contract.**

Integration SHALL occur exclusively through:

- canonical identities;
- `Context`;
- `CapabilityBinding`;
- explicit mappings;
- business APIs;
- canonical/integration events;
- idempotent application services;
- transactional outbox/inbox patterns;
- reconciliation.

Direct database integration is prohibited.

---

# 2. Why this ADR exists

Medusa and iDempiere overlap around:

```text
Customer
Product
Price
Order
Inventory
Fulfillment
Payment
Refund
Return
Tax
```

but their responsibilities are not identical.

Current Medusa documentation models Orders as customer purchases containing items, customer, payment and shipping information. Its commerce modules separately model payments, transactions, fulfillment, returns, claims and related order changes.

Baobab therefore SHALL NOT infer that because both systems contain an "Order", they share authority over the same state.

---

# 3. Order-to-cash bounded contexts

The canonical order-to-cash flow is:

```text
Customer
   │
   ▼
Digital Estate
   │
   ▼
Cart / Checkout
   │
   ▼
Commerce Order
   │
   ▼
ERP Sales Representation
   │
   ├── Inventory consequence
   ├── Shipment consequence
   ├── Customer Invoice
   └── Accounting
   │
   ▼
Settlement / Reconciliation
```

Each transition crosses an explicit domain boundary.

---

# 4. Authority matrix

The initial authority model SHALL be:

| Concern | Primary authority |
|---|---|
| Cart | Medusa |
| Checkout | Medusa |
| Commerce sales channel | Medusa |
| Commerce promotion | Medusa |
| Commerce Order | Medusa |
| Commerce order amendment | Medusa |
| Commerce reservation | Medusa |
| Customer-facing fulfillment workflow | Medusa |
| Payment-provider orchestration | Medusa Payment capability / approved payment service |
| Provider authorization | Payment provider |
| Provider capture | Payment provider |
| Provider refund | Payment provider |
| ERP Sales Order representation | iDempiere |
| Customer Invoice | iDempiere |
| Accounts Receivable | iDempiere |
| Financial inventory consequence | iDempiere |
| Revenue accounting | iDempiere |
| Tax accounting | iDempiere |
| Payment accounting/allocation | iDempiere |
| Canonical identity | Baobab canonical layer |
| Routing | Control Plane |
| Cross-engine mapping | Control Plane |

---

# 5. Cart

A Cart is a commerce-domain object.

It SHALL normally remain entirely within Medusa.

---

# 6. Cart is not ERP Sales Order

The following is prohibited:

```text
Customer adds item to cart
          │
          ▼
Create ERP Sales Order
```

for ordinary commerce.

A cart is mutable customer intent and SHALL not automatically create financial ERP state.

---

# 7. Checkout

Checkout remains a commerce workflow.

It MAY include:

```text
customer validation
address
delivery method
tax quotation
promotion
inventory availability
payment authorization
```

---

# 8. ERP involvement during checkout

ERP MAY provide synchronous capabilities required to validate a transaction, but it SHALL NOT own the checkout session.

---

# 9. Commerce Order

Once commerce order creation reaches the agreed business commitment boundary, Medusa SHALL own the Commerce Order.

Current Medusa documentation defines an Order as a customer purchase and records payment/shipping information and related transactions around that order.

---

# 10. Canonical SalesOrder identity

A committed Commerce Order that requires cross-engine processing SHOULD receive or resolve a canonical:

```text
SalesOrder
```

identity.

---

# 11. Native representations

Example:

```text
Canonical SalesOrder UUID
          │
          ├── Medusa
          │     └── Order order_...
          │
          └── iDempiere
                └── C_Order ...
```

---

# 12. Mapping semantics

This mapping means:

> These engine representations participate as representations of the same canonical sales-order business identity.

It does NOT mean their internal state machines are identical.

---

# 13. Native state independence

Medusa may expose commerce-specific states while iDempiere uses its native document lifecycle.

Baobab SHALL translate between semantic states rather than copying status strings.

---

# 14. No status mirroring

This is prohibited:

```text
Medusa status = "completed"

therefore

UPDATE C_Order
SET DocStatus = "CO"
```

---

# 15. ERP application service

ERP lifecycle changes SHALL invoke approved iDempiere business processes through the Baobab ERP application layer.

---

# 16. Order ingestion

A Commerce Order requiring ERP processing SHALL be transferred through an explicit integration command/event workflow.

---

# 17. Recommended order flow

```text
Medusa
   │
   │ commerce order committed
   ▼
Transactional Outbox
   │
   ▼
commerce.order.placed.v1
   │
   ▼
ERP Integration Consumer
   │
   ▼
Resolve Context
   │
   ▼
Resolve CapabilityBinding
   │
   ▼
Resolve Party/Product mappings
   │
   ▼
Create ERP Sales Order
   │
   ▼
Complete/process according to policy
   │
   ▼
ERP Outbox
   │
   ▼
erp.sales-order.accepted.v1
```

---

# 18. Synchronous alternative

Where the customer journey requires immediate ERP acceptance, Trade MAY call a canonical ERP command synchronously.

However:

```text
HTTP success
```

SHALL NOT be confused with all downstream financial processing being complete.

---

# 19. Integration strategy

The architecture SHALL permit:

```text
synchronous command + asynchronous facts
```

as the normal pattern.

---

# 20. No distributed transaction

Baobab SHALL NOT attempt a distributed ACID transaction spanning:

```text
Medusa PostgreSQL
+
iDempiere PostgreSQL
+
payment provider
```

---

# 21. Local transaction principle

Each system commits its own authoritative state locally.

Cross-system convergence occurs through durable integration.

---

# 22. Commerce Order acceptance

Baobab SHALL distinguish:

```text
Commerce Order created

ERP Order accepted

ERP Order completed

Customer Invoice posted

Payment captured

Payment accounted
```

These are different facts.

---

# 23. Order acknowledgement

ERP SHOULD publish an acknowledgement/fact after successfully creating the ERP representation.

---

# 24. Mapping creation

Once the ERP representation exists, its `ExternalReference` and `Mapping` SHALL be established idempotently.

---

# 25. ERP creation failure

If ERP cannot create the representation:

```text
Commerce Order
    remains a valid commerce fact
```

unless business policy explicitly defines otherwise.

The failure SHALL enter retry/reconciliation/exception handling.

---

# 26. No silent order loss

A failed ERP integration SHALL never silently discard a committed Commerce Order.

---

# 27. Customer identity

Commerce customer identity SHALL resolve to canonical Party identity where ERP processing requires it.

---

# 28. Guest checkout

Guest checkout SHALL not require the customer to become a long-lived registered platform user.

---

# 29. Guest Party representation

ERP MAY still require an appropriate customer/BPartner representation.

Provisioning policy SHALL determine whether that is:

```text
individual Party
guest/anonymous customer account
cash customer representation
```

according to business/accounting requirements.

---

# 30. B2B buyer

For B2B:

```text
authenticated user
      !=
buyer organisation
      !=
canonical Party
      !=
ERP C_BPartner
```

Relationships SHALL be explicit.

---

# 31. Legal buyer

ERP Sales Order and Customer Invoice SHALL identify the actual contracting/customer Party required for financial records.

---

# 32. Product mapping

Every ERP-relevant Commerce Order line SHALL resolve to an ERP Product representation.

---

# 33. Missing Product mapping

A missing required Product mapping SHALL fail the ERP integration.

Runtime name/SKU guessing is prohibited.

---

# 34. Order snapshot

A committed Commerce Order SHALL preserve the commercial facts agreed with the customer.

These MAY include:

```text
product description
SKU
quantity
unit price
discount
tax
currency
shipping
```

as an order snapshot.

---

# 35. Later Product changes

Changing Product master data after purchase SHALL not rewrite historical Commerce Order economics.

---

# 36. Currency

Commerce Order currency SHALL be explicit.

---

# 37. ERP document currency

ERP SHALL receive the authoritative transaction currency as part of the integration contract.

---

# 38. FX

Commerce pricing FX and ERP accounting FX SHALL remain distinct under ADR-ERP-008.

---

# 39. Pricing

Medusa SHALL normally own the customer-facing commercial price determination.

---

# 40. ERP price reconstruction

ERP SHALL not independently reprice a committed Commerce Order unless the business contract explicitly requires it.

---

# 41. ERP validation

ERP MAY validate:

```text
currency
Product mapping
customer eligibility
tax/accounting prerequisites
legal entity
period
```

without silently replacing the commercial agreement.

---

# 42. Price difference

If ERP cannot accept the Commerce Order economics, the integration SHALL produce an explicit exception.

---

# 43. Discounts

Commerce discounts SHALL be transferred with sufficient semantic detail for ERP accounting.

---

# 44. Promotion identity

A Medusa promotion identifier SHALL not automatically become ERP accounting identity.

---

# 45. Discount accounting

ERP determines how discounts are financially represented according to accounting configuration.

---

# 46. Tax

Commerce may calculate/display tax during checkout.

ERP remains authoritative for tax accounting on ERP financial documents.

---

# 47. Tax consistency

Baobab SHALL reconcile material differences between:

```text
commerce tax expectation
and
ERP posted tax
```

---

# 48. Tax difference

A difference SHALL not automatically imply ERP should copy Commerce tax.

The responsible tax authority/configuration SHALL determine correct treatment.

---

# 49. Sales channel

Commerce Sales Channel SHALL remain a Medusa concept.

---

# 50. ERP management dimension

Sales Channel MAY map to an ERP management/accounting dimension where useful.

It SHALL not automatically become `AD_Org`.

---

# 51. Digital Estate

DigitalEstate MAY identify order origin.

Example:

```text
THAMANI_WEB
THAMANI_MOBILE
ZURIBEANS_B2B
```

It SHALL not determine financial ownership by itself.

---

# 52. LegalEntity

The selling LegalEntity SHALL be explicitly resolved.

---

# 53. Seller of record

Every financially consequential Commerce Order SHALL resolve the seller of record.

---

# 54. Market

Market SHALL be explicit where required for:

```text
commercial policy
tax
localisation
fulfillment
```

but Market SHALL not substitute for seller LegalEntity.

---

# 55. Context

Order integration SHALL preserve immutable transaction Context.

At minimum, where applicable:

```text
Tenant
LegalEntity
Market
DigitalEstate
Capability
EngineInstance
```

---

# 56. Inventory reservation

Commerce reservation remains Medusa-owned as established by ADR-ERP-015.

---

# 57. Reservation versus sale

Reservation SHALL not create accounting revenue.

---

# 58. Reservation versus shipment

Reservation SHALL not create ERP shipment.

---

# 59. Fulfillment

Medusa owns customer-facing commerce fulfillment workflow.

---

# 60. ERP shipment

ERP owns financially relevant material shipment/inventory movement.

---

# 61. Fulfillment mapping

Where they represent the same business shipment:

```text
Canonical Shipment
       │
       ├── Medusa Fulfillment
       └── iDempiere Shipment
```

MAY be mapped.

---

# 62. Mapping is conditional

Not every Medusa Fulfillment must map 1:1 to one ERP Shipment.

Examples:

```text
one fulfillment → several physical shipments

several fulfillment records → one ERP shipment

3PL shipment → ERP material shipment
```

may occur.

---

# 63. Partial fulfillment

Partial fulfillment SHALL be supported.

---

# 64. Partial shipment

ERP SHALL preserve actual shipped quantities.

---

# 65. Fulfillment completion

Commerce SHALL not mark physical fulfillment successful solely because an ERP command was accepted asynchronously.

---

# 66. Shipment fact

ERP or the authoritative warehouse execution system SHALL publish the authoritative physical shipment fact.

---

# 67. Payment architecture

Baobab SHALL distinguish:

```text
Payment Intent / Session

Authorization

Capture

Provider Transaction

ERP Payment

Allocation

Settlement

Bank Reconciliation
```

---

# 68. Medusa Payment Module

Current Medusa documentation provides payment authorization, capture and refund capabilities and supports integration with external payment providers.

Baobab SHALL use these commerce capabilities without making Medusa the accounting ledger.

---

# 69. Payment authorization

Authorization means the payment provider has authorised an amount according to provider semantics.

It does NOT mean ERP has recognised cash.

---

# 70. Payment capture

Capture represents processing/capturing the payment through the payment provider.

Medusa currently models captures separately and supports multiple/incremental captures.

---

# 71. Payment accounting

ERP SHALL create/account for the corresponding financial payment according to:

```text
payment method
clearing account
currency
provider
settlement process
LegalEntity
```

---

# 72. Provider transaction is not ERP Payment

A payment-provider transaction and iDempiere Payment are different domain entities.

They SHALL normally be related rather than declared the same canonical representation.

---

# 73. Payment relationship

Conceptually:

```text
Commerce Order
      │
      ▼
Payment Authorization
      │
      ▼
Provider Capture
      │
      ▼
Payment Integration Fact
      │
      ▼
ERP Payment
      │
      ▼
Customer Invoice Allocation
      │
      ▼
Bank/Provider Settlement
```

---

# 74. Multiple captures

Multiple provider captures MAY correspond to:

```text
one ERP Payment
or
multiple ERP Payments
```

according to accounting policy.

---

# 75. Multiple payment methods

An Order MAY be paid through several payment methods where commerce supports it.

ERP SHALL preserve correct financial representation.

---

# 76. Payment status

Commerce payment status SHALL NOT be copied directly into ERP payment status.

---

# 77. Payment events

Initial payment integration facts SHOULD include:

```text
commerce.payment.authorized.v1

commerce.payment.captured.v1

commerce.payment.refunded.v1
```

or equivalent approved canonical names.

---

# 78. Sensitive payment data

Canonical events SHALL NOT contain:

```text
PAN
CVV
raw provider credentials
payment tokens not intended for distribution
```

---

# 79. PCI boundary

Baobab SHALL minimise the platform's exposure to regulated payment-card data.

---

# 80. Payment idempotency

Payment integration SHALL be strongly idempotent.

A duplicate:

```text
payment captured
```

event SHALL not create duplicate ERP payments.

---

# 81. Provider reference

Provider transaction identifiers SHALL be retained as typed ExternalReferences/integration references where needed for reconciliation.

---

# 82. Settlement

Provider capture and bank settlement are different events.

---

# 83. Settlement delay

A provider may capture today and settle later.

ERP SHALL support clearing-account semantics where Finance requires them.

---

# 84. Payment fees

Provider fees SHALL be accounted separately from customer payment where financially required.

---

# 85. Settlement reconciliation

Baobab SHALL reconcile:

```text
Provider captures
Provider refunds
Provider fees
Provider settlements
ERP payments
ERP allocations
Bank transactions
```

---

# 86. Customer Invoice

iDempiere SHALL own the financially authoritative Customer Invoice.

---

# 87. Commerce Order is not invoice

```text
Commerce Order != Customer Invoice
```

---

# 88. Sales Order is not invoice

```text
ERP Sales Order != Customer Invoice
```

---

# 89. Invoice timing

Invoice creation MAY occur:

```text
at order acceptance
at shipment
at fulfillment
periodically
```

depending on LegalEntity/Market/business policy.

---

# 90. Invoice policy

Invoice timing SHALL be configuration/policy driven.

---

# 91. Invoice identity

Customer Invoice SHALL receive its own canonical identity where cross-engine interoperability requires it.

---

# 92. Invoice number

Statutory invoice number SHALL NOT be canonical UUID identity.

---

# 93. Invoice posting

ERP SHALL own invoice posting and accounting.

---

# 94. Posted invoice immutability

A posted invoice SHALL not be rewritten because the Commerce Order later changes.

Corrections SHALL use approved accounting documents.

---

# 95. Commerce order modification

Medusa supports post-order commerce operations and tracks transactions/outstanding amounts as order economics change.

Baobab SHALL treat those changes as new integration facts rather than mutating historical ERP postings blindly.

---

# 96. Order amendment

An amendment MAY require:

```text
additional invoice
credit note
additional payment
refund
inventory adjustment
replacement shipment
```

depending on what changed.

---

# 97. No historical rewrite

A commerce edit SHALL not directly modify posted ERP accounting entries.

---

# 98. Outstanding amount

Current Medusa order transaction semantics calculate outstanding amount from order total versus transaction amounts.

That commerce balance SHALL remain distinct from ERP Accounts Receivable balance.

---

# 99. Balance reconciliation

Where both apply:

```text
Commerce outstanding amount
```

and:

```text
ERP receivable balance
```

SHALL be reconcilable according to defined timing and accounting rules.

---

# 100. Returns

Medusa SHALL own the customer-facing return/RMA workflow.

Current Medusa supports customer/merchant return requests, receipt of returned items, damaged quantities and refund-related return economics.

---

# 101. Return is not refund

```text
Return
   !=
Refund
```

A Return is a goods/logistics event.

A Refund is a payment event.

---

# 102. Return is not credit note

```text
Return
   !=
Credit Note
```

A Credit Note is an accounting document.

---

# 103. Return architecture

```text
Customer
   │
   ▼
Return Request
   │
   ▼
RMA Approval
   │
   ▼
Physical Return
   │
   ▼
Inspection
   │
   ├── sellable
   └── damaged
   │
   ▼
ERP Inventory Consequence
   │
   ▼
Credit/Adjustment
   │
   ▼
Refund
```

Individual steps MAY vary by policy.

---

# 104. Returned inventory

Returned goods SHALL not automatically become sellable inventory.

---

# 105. Inspection

Returned Product MAY become:

```text
sellable
damaged
quarantined
refurbishment
scrap
```

---

# 106. Medusa return inventory

Current Medusa distinguishes received quantity from damaged quantity when receiving returns.

Baobab SHALL map this commerce workflow to the appropriate ERP physical/financial inventory consequence rather than blindly increasing ERP stock.

---

# 107. Return mapping

Where appropriate:

```text
Canonical Return
     │
     ├── Medusa Return
     └── ERP Return Material Movement
```

MAY be established.

---

# 108. Refund

Payment refund SHALL normally be executed through the original/approved payment capability.

Medusa currently supports full and partial refunds of captured payments.

---

# 109. Refund is not payment deletion

A refund SHALL be represented as a new financial fact.

Original payment history remains.

---

# 110. Partial refund

Partial refunds SHALL be supported.

---

# 111. Multiple refunds

A captured payment MAY have multiple refund transactions where provider/business semantics allow it. Current Medusa explicitly models multiple refunds against a payment.

---

# 112. Refund accounting

ERP SHALL receive the financial consequence through a governed integration.

---

# 113. Credit note

Where accounting rules require reduction/reversal of a posted Customer Invoice, ERP SHALL issue the appropriate credit document.

---

# 114. Refund and credit note relationship

A refund and credit note may be related but SHALL remain distinct:

```text
Credit Note
   → changes receivable/revenue/tax accounting

Refund
   → returns funds to customer
```

---

# 115. Refund without return

Baobab SHALL support policy-approved refund without physical return.

Current Medusa versions support direct refunds independently of creating a return.

---

# 116. Return without immediate refund

A Return MAY precede refund pending:

```text
inspection
approval
restocking determination
fraud review
```

---

# 117. Exchange

An Exchange SHALL be treated as a compound commerce workflow.

Conceptually:

```text
Inbound return
+
Outbound replacement
+
possible price difference
+
possible additional payment/refund
```

---

# 118. Claim

Medusa supports claims for defective/incorrect items, including refund or replacement flows.

ERP SHALL consume only the financial/inventory consequences required by its authority.

---

# 119. Replacement

Replacement shipment SHALL create the appropriate inventory movement.

---

# 120. Free replacement

A replacement with zero additional customer charge MAY still have:

```text
inventory
COGS
tax
warranty
```

accounting consequences.

---

# 121. Cancellation

Cancellation semantics SHALL depend on lifecycle stage.

---

# 122. Pre-ERP cancellation

A Commerce Order cancelled before ERP acceptance MAY require no ERP business document.

---

# 123. Post-ERP cancellation

After ERP Sales Order creation, cancellation SHALL invoke ERP-supported document lifecycle.

---

# 124. Post-invoice cancellation

After invoice posting, cancellation generally becomes accounting correction rather than deletion.

---

# 125. Post-shipment cancellation

After shipment, a simple cancellation may no longer be semantically valid.

Return/reversal processes may be required.

---

# 126. State-aware commands

Cross-engine workflows SHALL therefore be state-aware.

---

# 127. Compensation

Cross-engine failure SHALL use business compensation rather than distributed rollback.

---

# 128. Compensation example

```text
Order placed
   │
   ▼
Payment captured
   │
   ▼
ERP rejects order permanently
```

Policy MAY require:

```text
cancel commerce order
+
refund captured payment
```

rather than attempting database rollback.

---

# 129. Compensation is business activity

Compensating actions SHALL themselves be:

```text
authorised
idempotent
auditable
observable
```

---

# 130. Saga architecture

Long-running order-to-cash processes MAY use saga-style orchestration/choreography.

---

# 131. No generic saga database as authority

Saga state coordinates work.

It SHALL NOT replace Medusa or ERP domain state.

---

# 132. Orchestration versus choreography

Baobab MAY use:

```text
orchestration
```

for complex policy-sensitive workflows and:

```text
event choreography
```

for loosely coupled reactions.

---

# 133. Avoid event spaghetti

Critical financial flows SHALL have an identifiable process owner and state model.

---

# 134. Workflow identity

Long-running order-to-cash flows SHOULD carry a canonical:

```text
correlation_id
```

---

# 135. Causation

Every resulting event SHOULD preserve immediate `causation_id`.

---

# 136. Trace propagation

`trace_id` SHALL propagate across synchronous and asynchronous boundaries where supported.

---

# 137. Retry

Technical retry SHALL be distinguished from business retry.

---

# 138. Technical retry

Examples:

```text
timeout
temporary broker outage
503
```

MAY be automatically retried.

---

# 139. Business rejection

Examples:

```text
invalid accounting period
missing Product mapping
customer blocked
unsupported currency
```

SHALL not be infinitely retried.

---

# 140. Exception queue

Non-retriable integration failures SHALL enter governed exception/reconciliation workflow.

---

# 141. Idempotency domains

At minimum idempotency SHALL cover:

```text
ERP Sales Order creation
ERP invoice creation
ERP payment creation
refund processing
shipment integration
return integration
```

where retries can occur.

---

# 142. Idempotency key scope

Idempotency SHALL include sufficient Context to prevent cross-tenant collision.

---

# 143. Duplicate Commerce Order event

Duplicate delivery SHALL resolve to the existing ERP representation.

It SHALL not create another Sales Order.

---

# 144. Exactly-once rejection

Baobab SHALL not claim global exactly-once delivery.

Business correctness SHALL come from:

```text
at-least-once delivery
+
idempotency
+
uniqueness constraints
+
reconciliation
```

---

# 145. Ordering

Baobab SHALL not require global Order event ordering.

Ordering MAY be scoped by canonical SalesOrder.

---

# 146. Order version

Where commerce supports order versions/changes, integration SHALL preserve sufficient source versioning to reject stale state.

Medusa currently increments order versions for operations including return lifecycle changes.

---

# 147. Stale event

An older Commerce Order version SHALL not overwrite a newer processed state.

---

# 148. Reconciliation

Order-to-cash reconciliation is mandatory.

---

# 149. Order reconciliation

At minimum:

```text
Commerce Order
↔
ERP Sales Order
```

---

# 150. Fulfillment reconciliation

```text
Medusa Fulfillment
↔
ERP/warehouse Shipment
```

where mapping applies.

---

# 151. Invoice reconciliation

```text
Commerce economic expectation
↔
ERP Customer Invoice
```

---

# 152. Payment reconciliation

```text
Medusa/provider capture
↔
ERP Payment
```

---

# 153. Allocation reconciliation

```text
ERP Payment
↔
ERP Customer Invoice allocation
```

---

# 154. Settlement reconciliation

```text
Provider settlement
↔
ERP clearing/bank accounting
```

---

# 155. Return reconciliation

```text
Medusa Return
↔
ERP return inventory movement
```

where applicable.

---

# 156. Refund reconciliation

```text
Provider Refund
↔
ERP financial refund/payment consequence
```

---

# 157. Credit reconciliation

```text
Commerce return/refund economics
↔
ERP Credit Note
```

where required.

---

# 158. Reconciliation timing

Reconciliation MAY be:

```text
continuous
scheduled
on-demand
post-incident
post-replay
post-migration
```

---

# 159. Expected temporary mismatch

Not every mismatch is immediately erroneous.

Example:

```text
payment captured
but
ERP payment event pending
```

may be within normal convergence window.

---

# 160. Reconciliation freshness

Controls SHALL therefore understand expected synchronization latency.

---

# 161. Financial mismatch severity

Persistent mismatches involving:

```text
money
tax
payment
invoice
inventory
```

SHALL receive elevated operational severity.

---

# 162. Repair

Reconciliation repair SHALL use authoritative business APIs/processes.

Direct SQL repair is exceptional and governed.

---

# 163. Security

All Commerce→ERP commands SHALL satisfy ADR-ERP-010.

---

# 164. No trusted-engine shortcut

Medusa is a peer engine.

Its requests SHALL still be:

```text
authenticated
authorised
Context-resolved
capability-checked
mapping-validated
```

---

# 165. Service identity

Trade SHALL use a dedicated workload/service identity.

---

# 166. Least privilege

Trade SHALL receive only the ERP capabilities required for commerce integration.

---

# 167. Example scopes

Possible scopes:

```text
erp.sales-orders.create

erp.sales-orders.read

erp.shipments.read

erp.customer-invoices.read

erp.payments.record
```

Actual authorization contracts SHALL be defined separately.

---

# 168. No generic ERP administrator

Trade SHALL NOT authenticate as an ERP System Administrator.

---

# 169. Native IDs

Trade SHALL not submit arbitrary:

```text
AD_Client_ID
AD_Org_ID
C_BPartner_ID
M_Product_ID
```

to select business context.

---

# 170. Server-side resolution

The ERP integration layer SHALL resolve native IDs from trusted canonical Context/mappings.

---

# 171. Cross-tenant protection

A valid Order UUID from another Tenant SHALL not permit access or mutation.

---

# 172. Digital Estate boundary

Digital Estates SHOULD normally interact with Trade, not directly with ERP order-to-cash internals.

---

# 173. Direct ERP estate capability

A Digital Estate MAY consume a narrow ERP capability only where architecture explicitly assigns it.

---

# 174. Payment-provider webhook

Payment-provider callbacks SHALL terminate at the approved payment integration boundary.

---

# 175. Webhook validation

Webhook processing SHALL verify:

```text
signature
provider
timestamp/replay protection where supported
event identity
Context mapping
```

---

# 176. Webhook is untrusted input

A webhook SHALL never be trusted merely because it arrived at a provider-specific endpoint.

---

# 177. Payment event replay

Replayed provider events SHALL remain idempotent.

---

# 178. Event privacy

Order events SHALL minimise:

```text
customer PII
addresses
payment information
```

to what consumers require.

---

# 179. Order data residency

Order/invoice/payment events SHALL obey applicable ResidencyPolicy.

---

# 180. Audit

Baobab SHALL be able to reconstruct:

```text
who/what placed order
which Digital Estate
which Tenant
which LegalEntity
which Market
which Commerce Order
which ERP Sales Order
which invoice
which payment
which shipment
which refund/return
```

subject to retention/privacy policy.

---

# 181. Business audit versus accounting audit

Commerce order activity and ERP accounting audit remain separate evidence streams connected by canonical identifiers.

---

# 182. Observability

Operational dashboards SHOULD expose:

```text
orders awaiting ERP acceptance
ERP ingestion failures
mapping failures
invoice lag
payment-accounting lag
shipment lag
refund lag
reconciliation findings
dead-letter counts
```

---

# 183. SLI — ERP acceptance

A useful integration SLI is:

```text
time from committed Commerce Order
to accepted ERP representation
```

---

# 184. SLI — payment accounting

Another:

```text
time from provider capture
to ERP financial representation
```

---

# 185. SLI — invoice generation

Where policy requires rapid invoicing:

```text
time from invoice-triggering business event
to posted/issued invoice
```

MAY be measured.

---

# 186. Correctness over availability

Baobab SHALL prefer delaying a financial operation over creating knowingly ambiguous financial state.

---

# 187. Degraded mode

Trade MAY continue non-financial operations during ERP degradation where safe.

Examples:

```text
catalogue browsing
content
possibly cart creation
```

---

# 188. Checkout degradation

Whether checkout may continue while ERP is unavailable SHALL be a capability/Market risk decision.

---

# 189. B2C tolerance

Some B2C scenarios MAY accept an Order into durable commerce state and asynchronously synchronize ERP.

---

# 190. B2B tolerance

Some B2B scenarios MAY require synchronous ERP checks for:

```text
credit
contract terms
account status
availability
```

before order acceptance.

---

# 191. One integration policy is insufficient

Baobab SHALL permit order-to-cash policy to vary by:

```text
Tenant
LegalEntity
Market
DigitalEstate
customer type
Capability
```

without changing engine boundaries.

---

# 192. B2B credit

Where ERP owns customer credit controls, B2B checkout MAY synchronously query an ERP credit-decision capability.

---

# 193. Credit data minimisation

Trade SHOULD receive:

```text
approved / declined
available credit
reason category
```

only as needed rather than unrestricted receivables detail.

---

# 194. Purchase-on-account

B2B Orders may use:

```text
invoice terms
credit account
bank transfer
```

rather than immediate card capture.

ERP SHALL remain authority for receivable terms.

---

# 195. Payment terms

ERP-owned Payment Terms SHALL be projected/validated for commerce where needed.

---

# 196. B2C prepaid

For prepaid B2C:

```text
Order
→ Payment Authorization/Capture
→ ERP Order
→ Invoice
→ Payment Allocation
```

is a possible policy.

---

# 197. B2B account sale

For account sale:

```text
Order
→ ERP credit validation
→ ERP Sales Order
→ Shipment
→ Customer Invoice
→ Accounts Receivable
→ later Payment
```

is a possible policy.

---

# 198. Architecture supports both

Neither flow SHALL require a different canonical platform model.

---

# 199. Initial B2C flow

The initial B2C implementation SHOULD prove:

```text
Digital Estate
      │
      ▼
Medusa Cart
      │
      ▼
Checkout
      │
      ▼
Payment Authorization
      │
      ▼
Commerce Order
      │
      ▼
ERP Sales Order
      │
      ▼
Shipment
      │
      ▼
ERP Customer Invoice
      │
      ▼
Payment Capture/Accounting
      │
      ▼
Reconciliation
```

Actual capture timing is business policy.

---

# 200. Initial B2B flow

The initial B2B implementation SHOULD prove:

```text
Buyer Organisation
      │
      ▼
Commerce Order
      │
      ▼
Credit/Terms Validation
      │
      ▼
ERP Sales Order
      │
      ▼
Goods Shipment
      │
      ▼
Customer Invoice
      │
      ▼
Accounts Receivable
      │
      ▼
Payment
      │
      ▼
Allocation
```

---

# 201. Return flow

Initial return integration SHOULD prove:

```text
Medusa Return Request
       │
       ▼
Approval
       │
       ▼
Returned Goods Received
       │
       ▼
ERP Inventory Return
       │
       ▼
ERP Credit Note
       │
       ▼
Payment Refund
       │
       ▼
Reconciliation
```

---

# 202. Partial return

Partial return SHALL preserve quantities and monetary allocations at line level.

---

# 203. Tax on return

Tax reversal/correction SHALL follow ERP/localisation rules.

---

# 204. Shipping refund

Refunding shipping cost SHALL be explicitly represented.

---

# 205. Restocking fee

A restocking fee, where legal/business policy permits it, SHALL be represented as an explicit commercial/accounting component.

---

# 206. Gift cards/store credit

Store credit or gift-value instruments SHALL not automatically be treated as cash payment.

Their accounting classification SHALL be explicit.

---

# 207. Loyalty

Loyalty value SHALL remain separate from ERP cash/payment unless accounting policy requires financial representation.

---

# 208. Manual payment

Commerce may record an externally handled payment.

Current Medusa administration supports marking outstanding amounts as paid without processing the payment through its associated provider.

Baobab SHALL require explicit source/provenance so this cannot create unexplained ERP cash.

---

# 209. Cash-on-delivery

Cash-on-delivery SHALL be modelled as a distinct payment/settlement policy.

Order acceptance does not imply cash received.

---

# 210. Bank transfer

Bank transfer orders SHALL remain outstanding until the appropriate settlement/payment evidence exists.

---

# 211. Fraud

Fraud/risk checks MAY delay:

```text
capture
fulfillment
ERP processing
```

according to policy.

---

# 212. Fraud decision authority

A fraud engine's decision SHALL be represented as a policy decision, not as accounting state.

---

# 213. Chargeback

Chargeback SHALL be distinct from ordinary refund.

---

# 214. Chargeback accounting

ERP SHALL account for chargebacks according to financial policy.

---

# 215. Disputes

Payment disputes MAY require a dedicated integration lifecycle.

They SHALL not rewrite original payment history.

---

# 216. Invoice delivery

Invoice rendering/delivery MAY be provided through ERP, document service or Digital Estate.

The accounting invoice authority remains ERP.

---

# 217. Invoice content

Customer-facing invoice rendering SHALL use authoritative ERP financial facts.

---

# 218. Invoice publication

An invoice SHALL not be presented as final/statutory before ERP/localisation requirements have been satisfied.

---

# 219. Regulatory fiscalisation

Where a Market requires e-invoicing/fiscalisation:

```text
ERP Invoice
   │
   ▼
Regulatory Adapter
   │
   ▼
Authority
   │
   ▼
Accepted/Rejected
```

SHALL follow ADR-ERP-009.

---

# 220. Regulatory identifier

Government-issued fiscal invoice IDs SHALL be ExternalReferences, not canonical invoice identity.

---

# 221. Order-to-cash canonical events

Initial event families SHOULD include:

```text
commerce.order.placed.v1

commerce.order.cancelled.v1

commerce.fulfillment.completed.v1

commerce.payment.authorized.v1

commerce.payment.captured.v1

commerce.payment.refunded.v1

commerce.return.received.v1

erp.sales-order.accepted.v1

erp.goods-shipment.completed.v1

erp.customer-invoice.posted.v1

erp.payment.completed.v1

erp.payment.allocated.v1
```

Final naming SHALL be governed by `nabhold/shared`.

---

# 222. Event ownership

Commerce facts SHALL be published by the commerce authority.

ERP financial facts SHALL be published by ERP.

---

# 223. No echo events

ERP SHALL not republish:

```text
commerce.order.placed
```

as though ERP originated the fact.

It MAY publish:

```text
erp.sales-order.accepted
```

as its own resulting fact.

---

# 224. No ping-pong

Consumers SHALL not transform projection updates into false new authoritative events.

---

# 225. Canonical identifiers

Cross-engine messages SHOULD use canonical identifiers as primary interoperability identity.

---

# 226. Native references

Native identifiers MAY appear in tightly controlled diagnostics/provenance.

Consumers SHALL not depend on them.

---

# 227. Correlation

All events belonging to one order-to-cash journey SHOULD share a durable workflow correlation identifier.

---

# 228. Reprocessing

Reprocessing an event SHALL preserve original event identity where it is a replay.

---

# 229. Correction

A genuinely new corrective business fact SHALL receive a new event ID and causation link.

---

# 230. Migration

If Medusa or iDempiere is migrated/replaced:

```text
Canonical SalesOrder UUID
Canonical Invoice UUID
Canonical Party UUID
Canonical Product UUID
```

SHALL survive.

---

# 231. Engine replacement

No Digital Estate SHALL need to understand iDempiere `C_Order_ID` to survive an ERP replacement.

---

# 232. Independent deployment

Trade and ERP SHALL remain independently deployable.

---

# 233. Version compatibility

Supported Trade and ERP versions SHALL communicate through versioned canonical contracts.

---

# 234. Contract testing

CI SHALL test:

```text
Trade producer → shared schema

ERP consumer → shared schema

ERP producer → shared schema

Trade consumer → shared schema
```

---

# 235. Integration test matrix

At minimum test:

```text
happy-path order
duplicate order event
missing Party mapping
missing Product mapping
partial fulfillment
partial payment
multiple captures
invoice generation
payment allocation
cancellation before shipment
cancellation after invoice
partial return
damaged return
partial refund
duplicate refund event
ERP outage
payment-provider outage
broker outage
out-of-order event
replay
cross-tenant attack
```

---

# 236. Golden financial scenarios

Baobab SHALL maintain golden order-to-cash financial scenarios whose expected accounting results are known.

---

# 237. Golden B2C scenario

Example:

```text
Order
ZAR 1,000 goods
+ tax
payment captured
goods shipped
invoice posted
payment allocated
```

Expected accounting SHALL be validated.

---

# 238. Golden return scenario

Example:

```text
partial return
partial inventory restoration
partial credit
partial refund
```

Expected accounting SHALL be validated.

---

# 239. Golden B2B scenario

Example:

```text
credit sale
invoice
30-day receivable
later bank payment
allocation
```

---

# 240. Multi-currency scenario

Example:

```text
Commerce Order currency ≠ LegalEntity functional currency
```

SHALL verify ADR-ERP-008 treatment.

---

# 241. Multi-LegalEntity scenario

The same Medusa/Trade engine MAY support multiple independently governed LegalEntities only where Context and isolation architecture permit it.

---

# 242. Seller resolution

The selling LegalEntity SHALL be resolved before ERP mutation.

---

# 243. No accidental Nabhold consolidation

Orders belonging to independent subsidiaries SHALL not become Nabhold Group ERP transactions merely because Nabhold owns the platform.

---

# 244. Control Plane role

Control Plane SHALL resolve:

```text
Context
CapabilityBinding
EngineInstance
MappingScope
```

It SHALL NOT orchestrate every order-to-cash business step.

---

# 245. Workflow ownership

Commerce/ERP integration workflow belongs to the integration/application domain, not the platform topology registry.

---

# 246. Intelligence Engine

Intelligence MAY consume authorised order-to-cash events for:

```text
forecasting
margin analysis
fraud analytics
customer intelligence
demand prediction
```

---

# 247. Intelligence is not financial authority

AI SHALL not directly modify posted invoices/payments.

---

# 248. AI actions

AI-proposed action SHALL pass through the same governed ERP/Trade command interfaces as human/system actions.

---

# 249. Order-to-cash invariants

```text
INV-ERP-O2C-001
Medusa and iDempiere are peer engines.

INV-ERP-O2C-002
Cart remains commerce-owned.

INV-ERP-O2C-003
Cart creation does not create ERP financial state.

INV-ERP-O2C-004
Commerce Order and ERP Sales Order have independent native lifecycles.

INV-ERP-O2C-005
Native order statuses are never blindly mirrored.

INV-ERP-O2C-006
Committed cross-engine Orders use canonical identity.

INV-ERP-O2C-007
Native IDs are not cross-engine identity.

INV-ERP-O2C-008
Order ingestion is idempotent.

INV-ERP-O2C-009
Duplicate events do not create duplicate ERP Orders.

INV-ERP-O2C-010
No distributed ACID spans Trade, ERP and payment provider.

INV-ERP-O2C-011
ERP integration failure never silently loses a Commerce Order.

INV-ERP-O2C-012
Party mapping is explicit.

INV-ERP-O2C-013
Product mapping is explicit.

INV-ERP-O2C-014
Runtime SKU/name guessing is prohibited.

INV-ERP-O2C-015
Committed commerce economics are historically preserved.

INV-ERP-O2C-016
Commerce pricing and ERP accounting remain distinct authorities.

INV-ERP-O2C-017
Tax expectation and tax accounting are reconcilable but not blindly copied.

INV-ERP-O2C-018
DigitalEstate does not determine seller of record.

INV-ERP-O2C-019
Seller LegalEntity is explicit.

INV-ERP-O2C-020
Reservation does not create revenue.

INV-ERP-O2C-021
Reservation does not create ERP shipment.

INV-ERP-O2C-022
Commerce fulfillment and ERP shipment remain distinct.

INV-ERP-O2C-023
Partial fulfillment is supported.

INV-ERP-O2C-024
Payment authorization is not payment accounting.

INV-ERP-O2C-025
Provider capture is not ERP Payment.

INV-ERP-O2C-026
Provider transaction and ERP Payment remain distinct entities.

INV-ERP-O2C-027
Payment integration is idempotent.

INV-ERP-O2C-028
Sensitive payment credentials never enter canonical events.

INV-ERP-O2C-029
Capture and settlement remain distinct.

INV-ERP-O2C-030
Customer Invoice is ERP-owned.

INV-ERP-O2C-031
Commerce Order is not Customer Invoice.

INV-ERP-O2C-032
Posted invoices are not rewritten by commerce edits.

INV-ERP-O2C-033
Commerce outstanding amount and ERP receivable balance remain distinct.

INV-ERP-O2C-034
Return, Refund and Credit Note remain distinct concepts.

INV-ERP-O2C-035
Returned goods do not automatically become sellable.

INV-ERP-O2C-036
Refund is represented as a new financial fact.

INV-ERP-O2C-037
Partial and multiple refunds are supported where policy permits.

INV-ERP-O2C-038
Accounting correction uses ERP financial documents.

INV-ERP-O2C-039
Cancellation behaviour is lifecycle-aware.

INV-ERP-O2C-040
Cross-engine failure uses business compensation, not distributed rollback.

INV-ERP-O2C-041
Compensation is authorised, idempotent and audited.

INV-ERP-O2C-042
Technical retry and business rejection remain distinct.

INV-ERP-O2C-043
At-least-once delivery is assumed.

INV-ERP-O2C-044
Global exactly-once delivery is not assumed.

INV-ERP-O2C-045
Stale order versions cannot overwrite newer state.

INV-ERP-O2C-046
Order-to-cash reconciliation is mandatory.

INV-ERP-O2C-047
Payment-provider settlement is reconciled to ERP.

INV-ERP-O2C-048
Trade is not trusted merely because it is an internal engine.

INV-ERP-O2C-049
Trade never receives generic ERP administrator authority.

INV-ERP-O2C-050
Caller-controlled native ERP Context is prohibited.

INV-ERP-O2C-051
Payment-provider webhooks are authenticated and idempotent.

INV-ERP-O2C-052
Order events minimise PII.

INV-ERP-O2C-053
Order-to-cash events obey ResidencyPolicy.

INV-ERP-O2C-054
B2B and B2C may use different integration policies without changing canonical architecture.

INV-ERP-O2C-055
ERP credit authority is not duplicated in Trade.

INV-ERP-O2C-056
Regulatory invoice identifiers are ExternalReferences.

INV-ERP-O2C-057
Event ownership follows domain authority.

INV-ERP-O2C-058
Projection updates cannot create event ping-pong.

INV-ERP-O2C-059
Canonical identity survives engine migration.

INV-ERP-O2C-060
AI remains a consumer/advisor, not financial authority.
```

---

# 250. Reference end-to-end architecture

```text
                         CUSTOMER
                            │
                            ▼
                     DIGITAL ESTATE
                            │
                            ▼
                   BAOBAB TRADE ENGINE
                         MEDUSA
        ┌───────────────────┼──────────────────┐
        ▼                   ▼                  ▼
      Cart               Order             Payment
        │                   │                  │
        │                   │             Provider
        │                   │                  │
        │                   ▼                  ▼
        │             Trade Outbox       Auth/Capture
        │                   │                  │
        │                   ▼                  │
        │          Canonical Integration       │
        │                   │                  │
        └───────────────────┼──────────────────┘
                            ▼
                     BAOBAB ERP API
                            │
                            ▼
                         iDempiere
          ┌─────────────────┼───────────────────┐
          ▼                 ▼                   ▼
      Sales Order       Shipment            Invoice
                                                 │
                                                 ▼
                                             Accounts
                                            Receivable
                                                 │
                           Provider Fact ────────┤
                                                 ▼
                                              Payment
                                                 │
                                                 ▼
                                             Allocation
                                                 │
                                                 ▼
                                            Accounting
                                                 │
                                                 ▼
                                             ERP Outbox
                                                 │
                                                 ▼
                                         Canonical Events
                                                 │
                       ┌─────────────────────────┼───────────┐
                       ▼                         ▼           ▼
                     Trade               Reconciliation Intelligence
```

---

# 251. Definitive order-to-cash rule

The complete architectural distinction is:

```text
CUSTOMER INTENT
      │
      ▼
    MEDUSA
      │
      │ committed commerce fact
      ▼
CANONICAL CONTRACT
      │
      ▼
  iDEMPIERE
      │
      │ financial consequence
      ▼
ACCOUNTING TRUTH
```

Therefore:

> **Medusa owns the customer's commercial journey; iDempiere owns the enterprise's accounting consequence of that journey.**

And:

> **A successful customer purchase is not made reliable by forcing both engines into one transaction. It is made reliable by durable local transactions, canonical identity, explicit authority, idempotent integration, business compensation and reconciliation.**

This keeps the Baobab Trade Engine genuinely headless and commerce-native while preserving iDempiere as an independent, financially authoritative ERP engine rather than reducing either platform to an implementation detail of the other.

---

# 252. Definition of done

ADR-ERP-016 is implemented when:

- [ ] Commerce/ERP authority matrix is machine-readable or formally documented.
- [ ] Canonical SalesOrder identity exists.
- [ ] Medusa Order ↔ canonical mapping exists.
- [ ] ERP Sales Order ↔ canonical mapping exists.
- [ ] Seller LegalEntity resolution exists.
- [ ] Party mapping is enforced.
- [ ] Product mapping is enforced.
- [ ] Commerce Order ingestion is idempotent.
- [ ] ERP acceptance event exists.
- [ ] commerce pricing is preserved.
- [ ] tax reconciliation exists.
- [ ] fulfillment/shipment boundary is implemented.
- [ ] partial fulfillment is supported.
- [ ] payment authorization/capture/accounting are distinct.
- [ ] provider references are preserved.
- [ ] ERP Payment integration is idempotent.
- [ ] payment allocation is implemented.
- [ ] provider settlement reconciliation exists.
- [ ] Customer Invoice is ERP authoritative.
- [ ] invoice timing policy exists.
- [ ] posted invoice corrections use financial documents.
- [ ] Return integration exists.
- [ ] damaged/sellable returned stock is distinguished.
- [ ] Refund integration exists.
- [ ] Credit Note integration exists where required.
- [ ] partial refunds are supported.
- [ ] cancellation is lifecycle-aware.
- [ ] compensation workflows exist.
- [ ] non-retriable business exceptions are quarantined.
- [ ] order version/staleness handling exists.
- [ ] Order reconciliation exists.
- [ ] fulfillment reconciliation exists.
- [ ] invoice reconciliation exists.
- [ ] payment reconciliation exists.
- [ ] return/refund reconciliation exists.
- [ ] Trade uses least-privilege ERP credentials.
- [ ] cross-tenant integration tests exist.
- [ ] payment webhooks are secured.
- [ ] PII minimisation is implemented.
- [ ] order-to-cash telemetry exists.
- [ ] B2C golden financial tests exist.
- [ ] B2B golden financial tests exist.
- [ ] return/refund golden tests exist.
- [ ] multi-currency tests exist.
- [ ] contract compatibility tests run in CI.
- [ ] engine replacement does not change canonical identity.