# ADR-ERP-015 — ERP Inventory, Warehouse, Procurement and Supply-Chain Architecture

**Status:** Accepted  
**Decision class:** ERP / Inventory / Warehousing / Procurement / Supply Chain / Commerce Integration  
**Scope:** `nabhold/baobab-erp`, `nabhold/baobab-trade`, `nabhold/baobab-cp`, Digital Estates, logistics integrations, supplier integrations and `nabhold/shared`  
**Parent ADRs:** ADR-ERP-001 through ADR-ERP-014  
**Date:** 2026-09-02

---

# 1. Decision

Baobab SHALL treat iDempiere as the authoritative ERP system for financially consequential inventory, procurement, warehouse accounting and procure-to-pay state.

Medusa SHALL remain authoritative for commerce-local inventory reservations, sales-channel availability and fulfillment-facing commerce state.

The two engines SHALL NOT share operational inventory tables.

They SHALL integrate through canonical identifiers, approved APIs, canonical/integration events and reconciliation.

The governing principle is:

> **Commerce answers what can be offered and reserved for sale; ERP answers what inventory legally and financially exists, moved, was received, cost, and must be accounted for.**

Therefore:

```text
Physical Stock
      ≠
Financial Inventory
      ≠
Commerce Availability
      ≠
Reserved Quantity
      ≠
Available-to-Sell
```

These quantities may be related, but SHALL NOT be collapsed into one field.

---

# 2. Scope

This ADR governs:

```text
Supplier
Purchase Requisition
Request for Quotation
Purchase Order
Material Receipt
Vendor Return
Supplier Invoice
PO / Receipt / Invoice Matching

Warehouse
Locator
Stock Location
Inventory Item
Inventory Level

Lot
Batch
Serial Number

Inventory Movement
Adjustment
Transfer
Reservation
Available-to-Sell

Landed Cost
Freight
Customs
Duty
Insurance
Clearing
Handling

Import Logistics
Ownership Transfer
Intercompany Movement
```

---

# 3. ERP supply-chain authority

iDempiere SHALL own ERP state required for:

- procurement;
- purchase-order lifecycle;
- goods/material receipt;
- vendor returns;
- ERP warehouses and locators;
- stock accounting;
- inventory movements;
- costing;
- inventory valuation;
- landed cost;
- supplier invoices;
- matching;
- accounting consequences;
- financially relevant stock corrections.

---

# 4. Commerce authority

Medusa SHALL own commerce-local concerns such as:

```text
reservation lifecycle
commerce inventory representation
sales-channel availability
commerce stock-location relationships
checkout availability
fulfillment-facing commerce state
```

Current Medusa documentation explicitly models inventory items, quantities across locations and reservations. Reservations hold quantities for purchases not yet fulfilled and reduce available quantity without reducing the physical stocked quantity.

---

# 5. No universal inventory authority

Baobab SHALL NOT create a generic global `inventory_quantity` and declare it authoritative everywhere.

Instead:

```text
Quantity Type                    Authority

ERP physical/accounting stock    iDempiere
ERP inventory valuation          iDempiere
Commerce reservation             Medusa
Commerce availability            Medusa projection/calculation
Canonical warehouse identity     Canonical mapping layer
```

---

# 6. Inventory quantity taxonomy

At minimum Baobab SHALL distinguish:

```text
on_hand

reserved

available_to_sell

in_transit

expected

received

damaged

quarantined

financially_owned

physically_present
```

where supported by the applicable domain.

Not every engine must persist all categories.

---

# 7. On-hand inventory

`on_hand` SHALL represent physical/system-recorded inventory in the authoritative inventory domain.

It SHALL NOT automatically mean:

```text
sellable
available
unreserved
financially owned
```

---

# 8. Reserved inventory

Reservation SHALL represent quantity temporarily committed against anticipated commerce fulfillment.

Current Medusa semantics keep reserved quantity physically stocked but remove it from availability calculations.

---

# 9. Available-to-sell

Available-to-sell SHALL be treated as derived state.

A simplified commerce formula MAY resemble:

```text
available_to_sell
    =
stocked_quantity
    -
reserved_quantity
```

which corresponds to current Medusa reservation semantics.

Baobab SHALL nevertheless permit more sophisticated future rules involving:

```text
safety stock
damaged stock
quarantine
channel allocation
overselling policy
expected receipts
```

---

# 10. Physical presence versus ownership

A Product being physically present in a warehouse does not necessarily mean the LegalEntity owns it.

Examples include:

```text
consignment
bonded inventory
third-party stock
customer-owned material
supplier-held stock
```

Ownership and physical location SHALL therefore remain conceptually distinct.

---

# 11. Financial inventory

Financial inventory SHALL mean inventory whose quantity/value has accounting consequences in the responsible LegalEntity's books.

iDempiere SHALL own that consequence.

---

# 12. Warehouse

A canonical Warehouse represents a governed storage/operational facility when cross-engine identity is required.

An ERP representation MAY map to:

```text
M_Warehouse
```

---

# 13. Warehouse semantics

The iDempiere model identifies `M_Warehouse` as the warehouse/storage facility used in procurement and material processes. Its documentation also distinguishes warehouse locators inside a warehouse.

---

# 14. Warehouse is not organisation

The following remain distinct:

```text
Warehouse
LegalEntity
Tenant
AD_Client
AD_Org
Market
DeploymentRegion
```

Relationships MAY exist, but identity SHALL not be inferred.

---

# 15. Locator

A Locator represents a physical/storage subdivision within an ERP Warehouse.

Examples:

```text
aisle
bay
rack
bin
floor
cold room
quarantine area
```

where implementation requires them.

iDempiere documentation describes the Locator as a location within a Warehouse.

---

# 16. Medusa Stock Location

Medusa Stock Location is a commerce/fulfillment concept.

Current Medusa documentation describes a stock location as a physical stocking location, such as a warehouse, associated with inventory quantities, sales channels, fulfillment providers and shipping options.

---

# 17. Stock Location is not automatically ERP Warehouse

A Medusa Stock Location MAY map to:

```text
one ERP Warehouse
multiple ERP Warehouses
a 3PL location
a virtual fulfillment location
```

depending on operating design.

Therefore:

> **StockLocation ↔ Warehouse equivalence SHALL always be explicit.**

---

# 18. Canonical warehouse mapping

Example:

```text
Canonical Warehouse
        │
        ├── ERP
        │    └── M_Warehouse
        │
        └── Trade
             └── Stock Location
```

The canonical identity MAY connect the two representations.

---

# 19. Product inventory identity

Inventory SHALL reference canonical Product/ProductVariant identity where cross-engine coordination requires it.

Native Product IDs SHALL remain engine-scoped.

---

# 20. Lot and batch

Lot/Batch identity SHALL be preserved where:

```text
traceability
food safety
quality control
recall
expiry
origin
regulatory reporting
```

requires it.

---

# 21. Serial number

Serialized Products SHALL preserve individual serial identity where required.

---

# 22. Traceability

Inventory traceability SHOULD permit reconstruction of:

```text
supplier
purchase order
receipt
lot/batch
warehouse
movement
shipment
customer/order
```

where required by the Product and jurisdiction.

---

# 23. Coffee-specific applicability

For imported agricultural commodities such as green coffee, traceability MAY additionally require:

```text
origin country
producer/cooperative
crop/harvest
grade
lot
bag count
gross weight
net weight
container
bill of lading
customs entry
inspection/certificate
warehouse
```

These are business-domain attributes, not universal Product identity.

---

# 24. Procurement architecture

Baobab procurement SHALL follow an ERP-governed lifecycle.

Conceptually:

```text
Demand
   │
   ▼
Requisition
   │
   ▼
Sourcing / RFQ
   │
   ▼
Supplier Selection
   │
   ▼
Purchase Order
   │
   ▼
Shipment / Transit
   │
   ▼
Material Receipt
   │
   ▼
Supplier Invoice
   │
   ▼
Matching
   │
   ▼
Payment
```

Not every business process requires every stage.

---

# 25. Purchase Requisition

A Purchase Requisition represents internal demand for procurement.

It SHALL not itself represent an external supplier commitment.

---

# 26. Purchase Order

A Purchase Order SHALL represent an authorised procurement commitment to a supplier.

ERP SHALL own its procurement lifecycle.

---

# 27. PO approval

Purchase Orders MAY require approval based on:

```text
value
currency
department
supplier
Product category
LegalEntity
risk
```

---

# 28. Purchase Order state

Consumers SHALL interact with canonical procurement lifecycle rather than patch native `DocStatus`.

---

# 29. Purchase-order commands

Examples:

```text
create purchase order
submit purchase order
approve purchase order
complete purchase order
cancel purchase order
close purchase order
```

---

# 30. Procurement is LegalEntity scoped

Every Purchase Order SHALL resolve the purchasing LegalEntity.

A Tenant containing multiple LegalEntities SHALL not blur the buyer of record.

---

# 31. Supplier identity

The supplier SHALL resolve through canonical Party mapping to the appropriate ERP `C_BPartner` representation.

---

# 32. Supplier representation plurality

The same external supplier MAY have:

```text
Canonical Party
   ├── LegalEntity A ERP BPartner
   └── LegalEntity B ERP BPartner
```

with independent:

```text
payment terms
currency
tax registration
credit/accounting configuration
```

---

# 33. Purchase-order currency

Purchase Order currency SHALL be explicit.

It SHALL NOT be inferred from Market.

---

# 34. Procurement unit of measure

Purchase UOM MAY differ from:

```text
inventory UOM
sales UOM
commerce unit
```

Conversions SHALL be explicit.

---

# 35. Procurement pricing

Supplier purchase prices are ERP procurement data.

They SHALL not automatically become consumer-facing commerce prices.

---

# 36. Material Receipt

A Material Receipt records receipt of Product/material from a supplier.

Current iDempiere documentation describes Material Receipt as the vendor shipment/receipt mechanism and allows it to be related to a Purchase Order or Vendor Invoice.

---

# 37. Receipt is not invoice

```text
Material Receipt
      !=
Supplier Invoice
```

Receipt answers:

> What physically arrived?

Invoice answers:

> What does the supplier claim we owe?

---

# 38. Receipt date versus accounting date

Receipt processing SHALL preserve distinctions between:

```text
physical receipt/movement date
document date
accounting date
```

iDempiere's Material Receipt model itself distinguishes Movement Date from Account Date.

---

# 39. Partial receipt

A Purchase Order SHALL support partial receipt where business process allows it.

Example:

```text
PO quantity: 1,000 bags

Receipt 1: 600
Receipt 2: 400
```

---

# 40. Over-receipt

Over-receipt SHALL follow explicit procurement policy.

It SHALL not be silently accepted because a warehouse worker entered a larger quantity.

---

# 41. Under-receipt

Under-receipt SHALL leave remaining quantity open/backordered or close it according to document policy.

---

# 42. Quality inspection

Receipt MAY enter:

```text
inspection
quarantine
quality hold
```

before becoming sellable inventory.

---

# 43. Receipt does not guarantee sellability

A completed Material Receipt MAY increase ERP inventory without immediately increasing commerce available-to-sell.

---

# 44. Receipt event

ERP MAY publish:

```text
erp.goods-receipt.completed.v1
```

after authoritative completion.

---

# 45. Receipt projection

Trade MAY consume authorised receipt/inventory events to refresh commerce inventory projections.

---

# 46. No synchronous stock mutation from Trade

Trade SHALL NOT update iDempiere inventory tables directly after commerce fulfillment.

---

# 47. Vendor Return

Vendor returns SHALL be ERP-controlled inventory movements.

They SHALL maintain:

```text
Product
quantity
warehouse/locator
supplier
original receipt where applicable
financial consequence
```

---

# 48. Purchase Order–Receipt–Invoice matching

iDempiere supports matching relationships between Purchase Order, Material Receipt and Vendor Invoice. Its documentation describes matched purchase orders and matched invoices linking those documents and contributing to quantity, costing and accounting effects.

Baobab SHALL preserve this ERP ownership.

---

# 49. Three-way matching

Where business policy requires:

```text
Purchase Order
      ↕
Goods Receipt
      ↕
Supplier Invoice
```

shall be reconciled before payment/posting approval.

---

# 50. Matching dimensions

Matching MAY evaluate:

```text
Product
quantity
unit
price
currency
tax
supplier
PO line
receipt line
invoice line
```

---

# 51. Matching tolerance

Tolerance SHALL be policy-controlled.

Examples:

```text
quantity tolerance
price tolerance
freight tolerance
currency rounding tolerance
```

---

# 52. Match exception

Material mismatches SHALL create governed exceptions.

They SHALL not be silently forced into balance.

---

# 53. Supplier Invoice

Supplier Invoice SHALL be authoritative ERP accounts-payable state.

---

# 54. Invoice receipt timing

A supplier invoice MAY arrive:

```text
before goods
with goods
after goods
```

The ERP process SHALL support legitimate timing differences.

---

# 55. Invoice posting

Supplier Invoice posting SHALL follow ADR-ERP-008.

---

# 56. No procurement payment in commerce

Medusa SHALL not become the supplier accounts-payable engine.

---

# 57. Landed cost

Landed cost SHALL be an ERP financial concept.

It MAY include:

```text
purchase price
international freight
insurance
customs duty
port charges
clearing
inspection
handling
inland transport
other attributable acquisition costs
```

---

# 58. iDempiere landed cost capability

iDempiere documents landed cost as including costs such as customs, freight and handling in addition to purchase price, and documents allocation/posting behaviour that can ultimately add landed cost to Product cost.

Baobab SHALL use supported ERP mechanisms rather than inventing parallel landed-cost accounting in Trade.

---

# 59. Estimated versus actual landed cost

Baobab SHOULD distinguish:

```text
estimated landed cost

actual landed cost
```

---

# 60. Estimated landed cost

Estimated cost MAY support:

```text
commercial pricing
margin estimation
inventory planning
purchase approval
```

before actual supplier/service invoices arrive.

---

# 61. Actual landed cost

Actual landed cost SHALL be determined from authoritative financial documents and allocation rules.

---

# 62. Landed-cost allocation

Allocation MAY use:

```text
quantity
weight
volume
value
container
line
other approved basis
```

depending on cost type.

---

# 63. Allocation rule is financial policy

Allocation basis SHALL be explicit and auditable.

---

# 64. Import shipment

For imported Product, Baobab MAY model an import shipment/container as a separate supply-chain entity where business workflows require it.

---

# 65. Import shipment is not Purchase Order

One import shipment MAY contain:

```text
multiple POs
multiple suppliers
multiple lots
multiple Products
```

---

# 66. Purchase Order is not container

Conversely, one Purchase Order may be fulfilled through multiple shipments.

---

# 67. In-transit inventory

Baobab SHALL explicitly decide when inventory becomes:

```text
owned
in_transit
received
available
```

based on commercial/legal terms.

---

# 68. Incoterms

Incoterms SHALL inform:

```text
risk transfer
cost responsibility
logistics obligations
```

where legally relevant.

They SHALL not be treated merely as shipping labels.

---

# 69. Ownership transfer

Ownership/risk transfer date MAY differ from physical warehouse receipt.

---

# 70. Goods in transit

Where accounting policy requires, ERP MAY recognise goods in transit before physical warehouse receipt.

---

# 71. Customs

Customs state MAY include:

```text
commodity classification
origin
customs value
duty
VAT/import tax
customs entry
clearance status
```

---

# 72. Customs Product classification

Tariff/commodity classification SHALL remain contextual and jurisdiction-specific.

It SHALL not replace Product canonical identity.

---

# 73. Origin

Baobab SHALL distinguish:

```text
country of origin
supplier country
shipping origin
Market
destination
```

---

# 74. Import currency

Purchase currency, customs valuation currency, functional currency and settlement currency MAY differ.

ADR-ERP-008 governs accounting treatment.

---

# 75. Freight provider

Freight forwarders, customs brokers and carriers SHALL be Parties with explicit roles where canonical identity is necessary.

---

# 76. Supply-chain document identifiers

Identifiers such as:

```text
bill of lading
air waybill
container number
customs declaration
commercial invoice
packing list
certificate number
```

SHALL be typed external/business references.

They SHALL not replace canonical entity identity.

---

# 77. Container identity

Container identifier MAY be globally meaningful in logistics but SHALL remain domain-specific rather than a canonical Product identity.

---

# 78. Warehouse transfer

Movement between warehouses SHALL be an ERP-controlled inventory process when financially/materially relevant.

---

# 79. Intra-LegalEntity transfer

An internal transfer MAY move inventory without changing ownership.

---

# 80. Inter-LegalEntity transfer

Movement between different LegalEntities SHALL NOT be treated as a simple warehouse transfer if legal ownership changes.

It MAY require:

```text
intercompany sale
purchase
shipment
receipt
invoice
transfer pricing
```

according to business/legal structure.

---

# 81. AD_Client isolation

Inventory belonging to separate tenant/client boundaries SHALL not be transferred by direct cross-client database manipulation.

---

# 82. Intercompany integration

Intercompany flows SHALL use ERP business processes, APIs/events and reconciliation.

---

# 83. Intercompany canonical identity

The same Product MAY retain one canonical identity while each LegalEntity has independent ERP representation/accounting state.

---

# 84. Inventory adjustment

Inventory adjustment SHALL be an explicitly authorised ERP operation.

---

# 85. Adjustment reasons

Adjustment SHALL require controlled reason codes where appropriate.

Examples:

```text
damage
shrinkage
count correction
expiry
quality rejection
theft
administrative correction
```

---

# 86. Inventory adjustment audit

Material inventory adjustments SHALL be auditable.

---

# 87. Cycle counting

Baobab MAY support cycle counting and physical inventory verification through ERP processes.

---

# 88. Count variance

Physical count variance SHALL create controlled adjustment rather than silent quantity replacement.

---

# 89. Inventory reconciliation

At minimum Baobab SHALL reconcile:

```text
ERP physical quantity
ERP valuation

Trade projected quantity
Trade reservations
Commerce availability
```

according to defined semantics.

---

# 90. Do not reconcile unlike values

This is invalid:

```text
ERP on_hand == Medusa available_to_sell
```

unless policy proves equivalence.

---

# 91. Correct reconciliation

A reconciliation rule might instead establish:

```text
Trade stocked projection
        ≈
eligible ERP stock projected to Trade
```

then separately verify:

```text
Trade available
 =
Trade stocked
 -
Trade reservations
 -
other commerce restrictions
```

---

# 92. Inventory projection policy

Baobab SHALL define which ERP stock is eligible for commerce projection.

Possible exclusions:

```text
quarantine
damaged
reserved for wholesale
restricted
quality hold
non-saleable
specific warehouse
```

---

# 93. Stock allocation

Inventory allocation across:

```text
B2B
B2C
Market A
Market B
specific Digital Estates
```

SHALL be explicit.

---

# 94. Sales channel allocation

Medusa stock locations may be associated with sales channels under its current model.

Baobab MAY use that capability as part of commerce allocation, but ERP remains authority for the underlying financially consequential inventory where applicable.

---

# 95. Overselling

Overselling policy SHALL be commerce policy.

It SHALL NOT mutate ERP financial inventory to fabricate stock.

---

# 96. Safety stock

Safety stock MAY reduce commerce availability without changing ERP on-hand quantity.

---

# 97. Reservation lifecycle

Commerce reservation SHALL have clear lifecycle:

```text
requested
   │
   ▼
reserved
   │
   ├── fulfilled → released/consumed
   │
   └── cancelled/expired → released
```

Medusa currently creates reservation state for purchased inventory-managed variants and removes reservations when fulfillment occurs.

---

# 98. Reservation is not ERP movement

Creating a Medusa reservation SHALL NOT automatically create an ERP inventory movement.

---

# 99. Fulfillment

Commerce fulfillment and ERP physical shipment are related but distinct domain operations.

---

# 100. Fulfillment authority

Trade MAY own commerce fulfillment workflow.

ERP SHALL own financially relevant material shipment/inventory consequence.

---

# 101. Fulfillment integration

Conceptually:

```text
Commerce Order
      │
      ▼
Trade Reservation
      │
      ▼
Fulfillment Requested
      │
      ▼
ERP / Warehouse Shipment
      │
      ▼
ERP Stock Movement
      │
      ▼
Canonical Shipment Event
      │
      ▼
Trade Fulfillment Projection
```

Exact orchestration is defined by the Trade integration ADRs.

---

# 102. Shipment duplication

A commerce fulfillment and ERP shipment SHALL not be assumed identical canonical entities unless semantics justify mapping them as the same business shipment.

---

# 103. ERP Shipment

ERP shipment/material movement may include accounting/logistics state beyond commerce fulfillment.

---

# 104. Third-party logistics

A 3PL MAY maintain its own physical warehouse state.

---

# 105. 3PL authority

Where a 3PL physically operates stock:

```text
3PL
```

may be operational authority for physical observation while ERP remains authority for financial inventory.

---

# 106. 3PL integration

3PL integration SHALL use:

```text
shipment advice
receipt advice
inventory reports
events/APIs
reconciliation
```

not database access.

---

# 107. Warehouse management system

A future specialist WMS MAY become physical warehouse execution authority.

This ADR SHALL support that without forcing ERP to remain operational execution authority forever.

---

# 108. Future WMS boundary

If a WMS is introduced:

```text
WMS
    physical execution

iDempiere
    financial inventory/accounting

Medusa
    commerce reservations/availability
```

with explicit synchronization.

---

# 109. ERP inventory is not permanent architecture monopoly

iDempiere is the initial authoritative ERP inventory engine.

A specialised WMS may later own selected warehouse-execution facts.

Canonical identity prevents redesign.

---

# 110. Inventory event families

Initial ERP events SHOULD include:

```text
erp.goods-receipt.completed.v1

erp.inventory-movement.completed.v1

erp.inventory-adjustment.completed.v1

erp.goods-shipment.completed.v1

erp.inventory-balance.changed.v1
```

where event-volume and semantic design justify them.

---

# 111. Balance event caution

Inventory balance can change frequently.

Baobab SHALL avoid indiscriminate event flooding.

---

# 112. Movement versus snapshot

The architecture SHALL distinguish:

```text
Inventory Movement Event
```

from:

```text
Inventory Balance Snapshot
```

---

# 113. Movement event

Movement event represents a business fact.

---

# 114. Balance projection

Balance is typically derived/current state.

---

# 115. Inventory sequence

Where consumers build inventory projections, events SHOULD provide entity/location-level ordering/version information where technically needed.

---

# 116. Global ordering rejected

Baobab SHALL NOT require global ordering of every inventory event.

---

# 117. Idempotency

Inventory event consumers SHALL be idempotent.

---

# 118. Duplicate movement

Duplicate event delivery SHALL not create a second inventory movement.

---

# 119. Inventory command idempotency

Commands such as external receipt/shipment creation SHALL support idempotency where retries are expected.

---

# 120. External logistics reference

An external logistics provider reference MAY form part of the idempotency scope.

---

# 121. Supply-chain API

Canonical ERP endpoints SHOULD express business intent.

Examples:

```text
POST /erp/v1/purchase-orders

POST /erp/v1/purchase-orders/{id}/complete

POST /erp/v1/goods-receipts

POST /erp/v1/goods-receipts/{id}/complete

POST /erp/v1/inventory-transfers

POST /erp/v1/inventory-adjustments
```

---

# 122. No native material-table API

Baobab SHALL NOT expose:

```text
POST /M_InOut
POST /M_Transaction
PATCH /M_Storage...
```

as the platform contract.

---

# 123. Stock query

Canonical query APIs MAY expose:

```text
inventory position
warehouse stock
inventory availability projection
```

with clear semantics.

---

# 124. Quantity response

Every quantity SHALL identify its semantic class.

Avoid:

```json
{
  "quantity": 100
}
```

Prefer conceptually:

```json
{
  "on_hand": "100.000",
  "uom": "KG"
}
```

or:

```json
{
  "available_to_sell": "82.000",
  "uom": "KG"
}
```

---

# 125. Decimal quantities

Quantities SHALL use decimal-safe representations appropriate to UOM precision.

---

# 126. Negative stock

Negative inventory policy SHALL be explicit.

---

# 127. ERP negative stock

If native ERP permits certain negative states, Baobab SHALL determine whether each Tenant/warehouse permits them.

---

# 128. Commerce negative stock

Commerce overselling policy SHALL remain separate.

---

# 129. Inventory timestamp

Inventory state SHALL distinguish:

```text
movement_time
recorded_time
accounting_date
projection_time
```

where needed.

---

# 130. Stale inventory

Commerce SHOULD know when an inventory projection was last updated.

---

# 131. Staleness policy

If inventory projection exceeds acceptable staleness, commerce policy MAY:

```text
degrade
block checkout
apply safety margin
query authoritative service
```

depending on risk.

---

# 132. ERP outage

During ERP outage, Trade MAY continue using bounded local inventory projection where explicitly permitted.

---

# 133. ERP outage does not confer authority

Trade SHALL not become financial inventory authority during the outage.

---

# 134. Deferred shipment

ERP-dependent material movements SHALL queue/defer where safe.

---

# 135. Recovery reconciliation

After ERP recovery, Trade/ERP inventory SHALL be reconciled before assuming convergence.

---

# 136. Procurement segregation of duties

Procurement SHOULD distinguish permissions for:

```text
request
approve
order
receive
invoice
pay
```

where risk warrants.

---

# 137. Same-user restriction

High-value procurement policy MAY prohibit one principal from controlling every stage.

---

# 138. Receiving independence

Receipt authorization MAY be separate from purchase-order approval.

---

# 139. Invoice approval

Supplier invoice approval MAY require independent verification.

---

# 140. Payment separation

Payment authority SHALL follow financial SoD policy.

---

# 141. Supplier master fraud risk

Changing:

```text
supplier bank details
payment terms
supplier status
```

is high-risk and SHALL receive stronger authorization/audit.

---

# 142. Warehouse adjustment risk

Large inventory adjustments SHALL trigger elevated controls.

---

# 143. Procurement audit

ERP SHALL preserve audit of:

```text
requester
approver
supplier
PO changes
receipt
invoice
matching exception
payment reference
```

where applicable.

---

# 144. Supply-chain observability

ADR-ERP-011 SHALL monitor at least:

```text
failed receipts
failed inventory postings
inventory event backlog
projection lag
mapping failures
unmatched receipts
unmatched invoices
critical stock reconciliation differences
```

---

# 145. Procurement reconciliation

Baobab SHOULD provide controls for:

```text
PO ordered vs received

received vs invoiced

invoiced vs paid
```

---

# 146. Open receipt liability

Goods received but not invoiced SHALL remain visible as a financial/control condition where accounting policy requires.

---

# 147. Invoice without receipt

Supplier invoice without corresponding receipt SHALL follow explicit exception policy.

---

# 148. Payment before matching

Payment SHALL not bypass required matching merely because an API caller requests it.

---

# 149. Period close

Period-close controls SHOULD consider:

```text
unposted receipts
unmatched material receipts
unmatched supplier invoices
landed cost not allocated
inventory valuation issues
```

according to Finance policy.

---

# 150. Landed-cost period integrity

Material landed costs arriving after receipt SHALL follow accounting policy for:

```text
same period
later period
closed period
```

---

# 151. Inventory valuation

Inventory valuation SHALL remain ERP/accounting authority.

---

# 152. Commerce margin

Trade MAY calculate estimated commercial margin.

It SHALL distinguish estimated cost/projection from final accounting cost.

---

# 153. Margin analytics

Analytics MAY combine:

```text
commerce revenue
ERP actual cost
freight
duty
other landed cost
```

to produce realised margin.

The analytical result does not become ERP accounting authority.

---

# 154. Multi-LegalEntity inventory

Inventory SHALL always belong to an explicit accounting/legal context.

---

# 155. Group inventory

A group-level aggregate:

```text
Nabhold Group Inventory
```

MAY be an analytical view.

It SHALL NOT erase independent subsidiary ownership.

---

# 156. Shared warehouse

Multiple LegalEntities MAY physically use the same facility.

Their financial inventory SHALL remain distinct.

---

# 157. Shared facility identity

One physical canonical Location/Warehouse MAY therefore relate to multiple ERP warehouse representations where legal/accounting separation requires it.

---

# 158. Inventory transfer across subsidiaries

A movement from Thamani-owned stock to another independent LegalEntity SHALL not be represented merely as:

```text
warehouse A → warehouse B
```

if ownership changes.

The ERP business flow SHALL capture the intercompany commercial/accounting event.

---

# 159. Group does not imply free stock movement

Corporate ownership SHALL not dissolve LegalEntity inventory boundaries.

---

# 160. Multi-Market inventory

Market availability MAY draw from:

```text
local warehouse
regional warehouse
cross-border warehouse
third-party fulfillment
```

subject to policy.

---

# 161. Market does not own stock

Market is a commercial/contextual construct.

The owning LegalEntity must still be known.

---

# 162. Cross-border fulfillment

Cross-border fulfillment SHALL consider:

```text
customs
tax
duties
export restrictions
import restrictions
residency-independent logistics rules
```

outside simple inventory quantity.

---

# 163. Inventory residency distinction

Physical inventory location and data residency are unrelated concepts.

```text
Warehouse in Uganda
```

does not automatically mean ERP database must be deployed in Uganda.

ResidencyPolicy decides data placement.

---

# 164. Supply-chain attachment records

Supporting records MAY include:

```text
packing list
certificate of origin
inspection certificate
bill of lading
customs document
supplier invoice
delivery note
```

Document/record ownership SHALL follow the later records-management ADR.

---

# 165. No document blobs in canonical events

Large logistics documents SHALL NOT be embedded in canonical events.

Events MAY carry controlled references.

---

# 166. Supplier portal

A future supplier portal SHALL interact through approved procurement APIs.

It SHALL not directly access native ERP database structures.

---

# 167. Warehouse mobile application

A future mobile warehouse app SHALL likewise operate through governed APIs.

---

# 168. Offline warehouse operations

Offline capture MAY be supported where operational conditions require it.

---

# 169. Offline synchronization

Offline receipt/movement SHALL require:

```text
idempotency
conflict detection
trusted device/user Context
reconciliation
```

---

# 170. Offline accounting

Offline client applications SHALL not independently perform authoritative accounting posting.

---

# 171. Barcode

Barcode/GTIN MAY assist Product identification.

It SHALL not universally replace canonical Product identity.

---

# 172. Scan ambiguity

If a barcode resolves ambiguously in the current Context, the operation SHALL fail rather than guess.

---

# 173. Weight-based commodities

For commodities sold/procured by weight, Baobab SHALL preserve exact UOM and measured quantity semantics.

---

# 174. Bag count versus weight

For green coffee, for example:

```text
320 bags
```

and:

```text
19,200 KG
```

are different measures.

One SHALL not silently replace the other.

---

# 175. Moisture/quality measurements

Quality measurements MAY affect:

```text
acceptance
grade
price adjustment
availability
```

but SHALL not necessarily alter Product identity.

---

# 176. Quality authority

If a future Quality Management capability is introduced, its authority over inspection facts SHALL be explicit.

---

# 177. Recall

Baobab SHOULD permit Product/Lot recall workflows where relevant.

---

# 178. Recall state

Recall status SHALL reduce/disable commerce availability through controlled propagation.

---

# 179. Recall is safety critical

Recall SHALL not rely solely on eventual low-priority synchronization.

---

# 180. Inventory confidentiality

Inventory quantities, costs and supplier terms MAY be commercially sensitive.

Access SHALL be Context- and role-controlled.

---

# 181. Cost visibility

Digital Estates SHALL not automatically receive inventory cost.

---

# 182. Supplier price visibility

Commerce storefronts SHALL not receive procurement prices unless a specific business requirement authorises it.

---

# 183. Events and sensitive cost

Inventory events intended broadly for commerce SHALL avoid leaking:

```text
supplier cost
landed cost
internal margin
```

unless required by that consumer.

---

# 184. Reference architecture

```text
                 DIGITAL ESTATES
                       │
                       ▼
               BAOBAB TRADE / MEDUSA
                       │
           ┌───────────┼───────────┐
           │           │           │
           ▼           ▼           ▼
      Commerce      Reservation  Fulfillment
      Catalogue       State       Workflow
           │
           │ canonical IDs /
           │ APIs / events
           ▼
                BAOBAB ERP API
                       │
                       ▼
                    iDempiere
        ┌──────────────┼───────────────┐
        ▼              ▼               ▼
   Procurement     Inventory        Accounting
        │              │               │
        ▼              ▼               ▼
 Purchase Order   Warehouse/       Costing/
 Material Receipt Movements        Valuation
 Supplier Invoice
        │
        └──────────────┬───────────────┘
                       ▼
                 Transactional
                    Outbox
                       │
                       ▼
                 Canonical Events
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
        Trade      Intelligence   Reconciliation
```

---

# 185. Commerce inventory projection

A recommended pattern is:

```text
ERP movement/stock fact
        │
        ▼
Canonical inventory event
        │
        ▼
Trade projection
        │
        ├── stock location
        ├── stocked quantity
        └── commerce policy
                 │
                 ▼
             reservation
                 │
                 ▼
         available-to-sell
```

---

# 186. Inventory correctness hierarchy

When disagreement occurs, Baobab SHALL determine the semantic question first.

For:

> How much stock is financially recorded?

Use ERP.

For:

> How much can this customer buy right now through this commerce channel?

Use Trade's authorised commerce availability model.

For:

> What is physically present at the 3PL right now?

A 3PL/WMS observation may be authoritative.

---

# 187. Inventory reconciliation hierarchy

```text
Physical observation
        │
        ▼
ERP inventory record
        │
        ▼
ERP eligible-commerce projection
        │
        ▼
Trade stocked projection
        │
        ▼
Trade reservations
        │
        ▼
Available-to-sell
```

Each boundary SHALL be reconcilable.

---

# 188. Failure example — ERP event delay

```text
Goods Receipt Completed
         │
         ▼
ERP inventory increased
         │
         ▼
Outbox pending
         │
         X
Broker unavailable
         │
         ▼
Trade still has older projection
```

This is eventual consistency, not ERP corruption.

Baobab SHALL:

```text
observe backlog
retry
publish
update projection
reconcile
```

---

# 189. Failure example — duplicate event

```text
Inventory Event E123
        │
        ├── delivered
        └── delivered again
```

Trade SHALL deduplicate/idempotently apply it.

Quantity MUST NOT double.

---

# 190. Failure example — reservation conflict

```text
Trade says available = 100
Two checkouts reserve 80 + 40
```

Trade SHALL enforce reservation concurrency against its authoritative commerce reservation state.

It SHALL not depend on round trips to ERP for every reservation unless explicitly designed.

---

# 191. Failure example — physical discrepancy

```text
ERP = 100 bags
Physical count = 97 bags
```

Baobab SHALL not modify ERP silently.

Instead:

```text
count
  ↓
variance
  ↓
investigation
  ↓
authorised adjustment
  ↓
ERP movement/accounting
  ↓
event
  ↓
Trade projection
  ↓
reconciliation
```

---

# 192. Failure example — supplier invoice mismatch

```text
PO = USD 50,000

Received = full quantity

Supplier invoice = USD 53,000
```

The difference SHALL be evaluated according to:

```text
approved price change
freight
landed cost
quantity difference
error
tolerance
```

rather than silently accepted.

---

# 193. Core invariants

```text
INV-ERP-SC-001
ERP owns financially consequential inventory.

INV-ERP-SC-002
Trade owns commerce reservation state.

INV-ERP-SC-003
Commerce availability and ERP on-hand inventory are distinct.

INV-ERP-SC-004
Physical stock and financial ownership are distinct.

INV-ERP-SC-005
Warehouse is not LegalEntity.

INV-ERP-SC-006
Warehouse is not Market.

INV-ERP-SC-007
Warehouse is not AD_Org.

INV-ERP-SC-008
Medusa Stock Location and ERP Warehouse require explicit mapping.

INV-ERP-SC-009
Native inventory IDs never become canonical identity.

INV-ERP-SC-010
Lots and serials are preserved where traceability requires them.

INV-ERP-SC-011
Purchase Order and Material Receipt are distinct documents.

INV-ERP-SC-012
Material Receipt and Supplier Invoice are distinct documents.

INV-ERP-SC-013
Receipt date and accounting date remain distinct.

INV-ERP-SC-014
Partial receipts are explicitly represented.

INV-ERP-SC-015
Receipt does not automatically imply commerce sellability.

INV-ERP-SC-016
ERP owns PO/receipt/invoice matching.

INV-ERP-SC-017
Matching exceptions are explicit.

INV-ERP-SC-018
Landed cost is financially governed by ERP.

INV-ERP-SC-019
Estimated and actual landed cost remain distinct.

INV-ERP-SC-020
Landed-cost allocation is auditable.

INV-ERP-SC-021
Purchase currency is not inferred from Market.

INV-ERP-SC-022
Country of origin is not Market.

INV-ERP-SC-023
Goods in transit and goods received remain distinct.

INV-ERP-SC-024
Ownership transfer and physical receipt may occur at different times.

INV-ERP-SC-025
Inter-LegalEntity inventory transfer cannot silently bypass intercompany accounting.

INV-ERP-SC-026
Corporate group ownership does not erase subsidiary inventory ownership.

INV-ERP-SC-027
Inventory adjustments require explicit authorization.

INV-ERP-SC-028
Physical count differences result in controlled adjustment.

INV-ERP-SC-029
ERP inventory tables are never shared with Trade.

INV-ERP-SC-030
Trade does not directly mutate ERP inventory.

INV-ERP-SC-031
ERP does not directly mutate Medusa reservation tables.

INV-ERP-SC-032
Inventory integration uses APIs/events/reconciliation.

INV-ERP-SC-033
Inventory events are idempotently consumed.

INV-ERP-SC-034
Duplicate delivery does not duplicate inventory movement.

INV-ERP-SC-035
Global inventory-event ordering is not required.

INV-ERP-SC-036
Available-to-sell is explicitly defined.

INV-ERP-SC-037
Safety stock may reduce commerce availability without reducing ERP on-hand.

INV-ERP-SC-038
Reservation is not an ERP material movement.

INV-ERP-SC-039
Commerce fulfillment and ERP material shipment remain distinct concepts.

INV-ERP-SC-040
Third-party warehouse execution does not automatically transfer financial authority.

INV-ERP-SC-041
A future WMS may own physical warehouse execution without changing canonical identity.

INV-ERP-SC-042
Supply-chain commands express business intent rather than native-table CRUD.

INV-ERP-SC-043
Quantities include explicit UOM.

INV-ERP-SC-044
Quantity precision is decimal-safe.

INV-ERP-SC-045
Negative-stock policy is explicit.

INV-ERP-SC-046
Commerce projection staleness is measurable.

INV-ERP-SC-047
ERP outage does not promote Trade to financial inventory authority.

INV-ERP-SC-048
Recovery requires inventory reconciliation.

INV-ERP-SC-049
Procurement segregation of duties is supported.

INV-ERP-SC-050
Supplier payment details receive enhanced controls.

INV-ERP-SC-051
Unmatched procurement state is operationally visible.

INV-ERP-SC-052
Inventory valuation remains ERP-owned.

INV-ERP-SC-053
Group inventory totals are analytical aggregation, not merged legal ownership.

INV-ERP-SC-054
Market does not own inventory.

INV-ERP-SC-055
Physical warehouse geography does not determine data residency.

INV-ERP-SC-056
Logistics documents are not embedded wholesale in events.

INV-ERP-SC-057
Offline warehouse operations remain idempotent and reconcilable.

INV-ERP-SC-058
Barcodes do not replace canonical Product identity.

INV-ERP-SC-059
Quality measurements do not automatically change Product identity.

INV-ERP-SC-060
Inventory costs are not exposed to commerce consumers by default.
```

---

# 194. Initial implementation boundary

The first production supply-chain slice SHOULD implement:

```text
Canonical Product
Canonical Party/Supplier
Canonical Warehouse

ERP Purchase Order
ERP Material Receipt
ERP Supplier Invoice
ERP PO/Receipt/Invoice Matching

ERP Inventory Movement
ERP Inventory Position

Trade Stock Location Mapping
Trade Inventory Projection
Trade Reservation

ERP → Trade Inventory Events

Inventory Reconciliation
Procurement Reconciliation
```

---

# 195. Initial import scenario

For the initial imported-goods pattern, Baobab SHOULD prove:

```text
Supplier
   │
   ▼
Purchase Order
   │
   ▼
International Shipment
   │
   ├── freight
   ├── insurance
   ├── customs
   ├── clearing
   └── inland transport
   │
   ▼
Material Receipt
   │
   ▼
Warehouse
   │
   ▼
Supplier / Landed-Cost Invoices
   │
   ▼
Cost Allocation
   │
   ▼
Inventory Valuation
   │
   ▼
Commerce Inventory Projection
   │
   ▼
Customer Availability
```

---

# 196. Definition of done

ADR-ERP-015 SHALL be considered implemented when:

- [ ] ERP inventory authority is explicit.
- [ ] Commerce reservation authority is explicit.
- [ ] Physical, financial, reserved and available quantities are distinct.
- [ ] Canonical Warehouse is defined.
- [ ] ERP Warehouse mapping exists.
- [ ] Medusa Stock Location mapping exists.
- [ ] Locator semantics are defined.
- [ ] Lot/batch support is defined.
- [ ] Serial-number policy is defined where required.
- [ ] Procurement lifecycle is implemented.
- [ ] Supplier canonical mapping exists.
- [ ] Purchase-order lifecycle uses domain commands.
- [ ] Material Receipt is supported.
- [ ] Partial receipt is supported.
- [ ] over/under-receipt policy exists.
- [ ] supplier returns are supported.
- [ ] Supplier Invoice integration is supported.
- [ ] PO/Receipt/Invoice matching exists.
- [ ] matching tolerances are policy-controlled.
- [ ] landed-cost architecture exists.
- [ ] estimated versus actual landed cost is distinguished.
- [ ] import shipment model is defined where required.
- [ ] in-transit inventory policy is defined.
- [ ] ownership-transfer semantics are defined.
- [ ] intercompany inventory movement is governed.
- [ ] inventory adjustments are audited.
- [ ] physical count/cycle-count process is defined.
- [ ] Trade inventory projection exists.
- [ ] reservation lifecycle exists.
- [ ] available-to-sell semantics are documented.
- [ ] ERP-to-Trade inventory events exist.
- [ ] event consumption is idempotent.
- [ ] inventory reconciliation exists.
- [ ] procurement reconciliation exists.
- [ ] projection staleness is observable.
- [ ] ERP outage inventory behaviour is defined.
- [ ] recovery inventory reconciliation exists.
- [ ] procurement SoD controls exist.
- [ ] cost data has restricted visibility.
- [ ] supply-chain observability exists.
- [ ] future WMS/3PL integration is supported without canonical redesign.

---

# 197. Final architectural position

Baobab SHALL reject the simplistic architecture:

```text
ERP quantity
     =
Commerce quantity
     =
Warehouse quantity
     =
Available stock
```

Instead:

```text
                    PHYSICAL WORLD
                         │
                         ▼
                Warehouse / 3PL / WMS
                         │
                         ▼
                     iDempiere
               ┌─────────┼─────────┐
               ▼         ▼         ▼
           Physical   Financial   Cost/
           Record     Inventory   Valuation
               │
               ▼
        Canonical Inventory Facts
               │
               ▼
              Trade
        ┌───────┼────────┐
        ▼       ▼        ▼
    Stocked  Reserved  Channel/
    Projection          Safety Rules
        │       │        │
        └───────┼────────┘
                ▼
         Available-to-Sell
                │
                ▼
          Digital Estate
```

The decisive rules are:

> **iDempiere records the inventory consequences that matter to the enterprise's books; Medusa records the inventory commitments that matter to commerce.**

> **The quantities may converge, but they are not the same concept.**

And:

> **No stock movement, reservation, receipt, shipment or intercompany transfer may erase the distinction between physical location, commercial availability and legal/financial ownership.**

This gives Baobab a supply-chain architecture capable of supporting straightforward retail as well as imported commodities, multi-warehouse operations, B2B/B2C allocation, independent subsidiaries, third-party logistics and future specialist warehouse systems without changing the canonical platform model.