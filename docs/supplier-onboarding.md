# Supplier onboarding (future boundary note)

`nabhold/thamani` is building a supplier registration, vetting and
cross-border sourcing portal (see `nabhold/shared` ADR-0006 and
`nabhold/thamani` ADR-0002). This note records what that means for
`nabhold/baobab-erp` today: **nothing changes here yet.**

## What already applies, unchanged

- `docs/adr/*ADR-ERP-007*` ("Canonical Entity and External Reference
  Mapping") already anticipates the eventual representations this program
  will need: `Party` → `C_BPartner`, `SupplierInvoice` → `C_Invoice`,
  `PurchaseOrder` → `C_Order`. That mapping matrix is a set of potential
  representations, not a commitment this note accelerates.
- `docs/adr/*ADR-ERP-006*`'s transactional outbox/inbox pattern is the
  correct mechanism for any future `supplier.*` consumer here — no new
  event-delivery design is needed when that day comes.
- No Business Partner vendor-role adapter, provisioning logic, or
  supplier-specific fields exist anywhere in `modules/` or
  `idempiere/extensions/` today. This note does not add any.

## What this repository does not do

`nabhold/baobab-erp` does not accept a direct call from `nabhold/thamani`.
Per `nabhold/thamani` ADR-0001 and ADR-0002, Thamani never integrates with
ERP directly — a future consumer of `contracts/supplier-onboarding/v1`'s
events (once a message broker exists anywhere in this ecosystem, which it
does not today) is the mechanism by which an approved supplier application
would eventually become a Business Partner here, not an API this repository
exposes to a digital estate's browser or server.

## Where the actual contract will live

`contracts/erp/v1/system-of-record.yaml`'s `Supplier` concept
(`canonical_owner: erp`, "Business Partner vendor role") remains the
authoritative destination concept. `nabhold/shared`'s
`contracts/supplier-onboarding/v1/system-of-record.yaml` is a separate,
estate-owned, pre-approval domain that references this concept without
redefining it — see that file's own README for the exact boundary. When ERP
provisioning is actually designed, it is a new ADR in this repository, not
a retroactive change to this note.
