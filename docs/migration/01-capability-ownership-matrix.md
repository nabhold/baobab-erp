# 01 — Capability Ownership Matrix (Phase 2)

Classification key:

- **A** — Core iDempiere ERP authority
- **B** — Initially iDempiere, extractable later behind the same `CapabilityBinding`
- **C** — Already owned by another Baobab engine
- **D** — Platform / Control Plane concern
- **E** — Digital Estate concern
- **F** — Removed entirely (no business need)

| Capability | Class | Notes |
|---|---|---|
| General Ledger | A | iDempiere accounting schema |
| Accounts Payable | A | |
| Accounts Receivable | A | |
| Financial Inventory / Costing | A | |
| Procurement Sourcing | B | Candidate for future Procurement Engine extraction |
| Procurement Accounting | A | Stays with ERP even if sourcing is extracted |
| Warehouse Execution | B | Candidate for future WMS extraction |
| Inventory Accounting | A | |
| Business Partner Master | A | Mapped from canonical `Party` |
| Product Master | A | Mapped from canonical `Product`; catalogue presentation stays with Trade |
| Commerce Catalogue / Checkout / Reservations | C | `nabhold/baobab-trade` (MedusaJS) |
| Commerce Fulfillment State | C | `nabhold/baobab-trade` |
| Market Intelligence / Supplier Research / Risk Signals | C | `nabhold/baobab-pulse` (Headless Haystack) |
| Canonical Identity / Mapping / CapabilityBinding | D | `nabhold/baobab-cp` |
| Tenant / LegalEntity / Market / IsolationProfile definitions | D | `nabhold/baobab-cp` |
| Digital Estate presentation / website UI | E | Not owned by this repository |
| Payment Orchestration | B | Candidate for future Payments Engine; ERP retains payment accounting (A) regardless |
| Document/Attachment storage | B | ERP holds business-record state; binary storage may move to an approved object-storage capability |
| Reporting/Analytics/BI over live ERP tables | F | Replaced by governed exports/events (ADR-ERP-018); no direct warehouse access to iDempiere's database |
| Frappe Desk / ERPNext-specific UI customisation | F | No longer applicable; iDempiere's own client, and Baobab APIs, are the only UIs |
| ERPNext DocType-shaped integration contracts | F | Replaced by canonical contracts (`Party`, `Product`, `PurchaseOrder`, ...) per ADR-ERP-005 |

## Reading this matrix

- Class **A** capabilities are implemented directly against iDempiere by this repository.
- Class **B** capabilities are implemented in iDempiere today but exposed only through
  canonical capability contracts, so a future extraction changes the `CapabilityBinding`
  target, not the consumer.
- Class **C** capabilities are explicitly out of scope for this repository; no code here
  should reimplement them.
- Class **D** capabilities are consumed, never redefined, here.
- Class **F** capabilities are the parts of the old ERPNext-era design (or hypothetical
  ERPNext customisation) that are not carried forward at all.
