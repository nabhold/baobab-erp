# 00 — Target Architecture (Phase 0: Architecture Freeze)

Status: Accepted. This document freezes the target architecture for `nabhold/baobab-erp`
before further implementation. It restates, in one place, the decisions already accepted
across ADR-ERP-001 through ADR-ERP-020.

> **ERPNext is being replaced, not retained.**

This repository previously carried a Frappe/ERPNext foundation-stage scaffold
(`apps/baobab_erp` as a Frappe custom app, a Bench-based Compose topology, MariaDB/Redis).
No tenant, financial, master-data, or transactional records were ever created against it —
the repository never reached a running production or staging site. That scaffold has been
removed in the same change that adds this document. There is no coexistence period for this
repository: it moves directly from the ERPNext scaffold to the iDempiere foundation.

## ERP authority

iDempiere 13 "Orion" LTS is the sole ERP engine of record for Baobab. It owns:

- the general ledger, accounts payable, accounts receivable;
- procurement, sales, and inventory documents and their accounting consequences;
- business-partner, product, and warehouse master records at the engine level.

Frappe and ERPNext have no runtime role. No fallback, dual-write, or compatibility path to
ERPNext exists or will be built.

## Control Plane authority

`nabhold/baobab-cp` (Go) owns canonical platform concepts: `CanonicalEntity`,
`ExternalReference`, `Mapping`, `MappingScope`, `Market`, `DigitalEstate`, `Engine`,
`EngineInstance`, `Capability`, `CapabilityBinding`, `Context`, `IsolationProfile`. This
repository does not redefine or duplicate those concepts; it implements the ERP-side half of
the mapping and consumes Control Plane decisions through the `modules/context` and
`modules/mapping` boundaries.

## Canonical identity

No iDempiere identifier (`AD_Client_ID`, `AD_Org_ID`, `C_BPartner_ID`, `M_Product_ID`, ...) is
ever used as a cross-engine identifier. Every cross-engine business object is a
`CanonicalEntity` with a Baobab UUID; iDempiere's native ID is stored only as an
`ExternalReference` under a `Mapping`. See ADR-ERP-002 and ADR-ERP-007.

## Mapping

```text
CanonicalEntity → Mapping → ExternalReference → iDempiere native record
```

`Tenant`, `LegalEntity`, `Market`, `AD_Client`, and `AD_Org` are related but never assumed
equal. Each relationship is resolved explicitly per `MappingScope`, never hard-coded. See
ADR-ERP-002.

## Capability routing

Consumers (Trade, Pulse, Digital Estates) never call iDempiere directly and never see
iDempiere table or endpoint shapes. They call a canonical capability; the Control Plane
resolves a `CapabilityBinding` to the responsible `EngineInstance`; the ERP application layer
(`modules/application`, `modules/integration`) translates the canonical contract into
iDempiere operations. See ADR-ERP-005.

## Integration boundaries

No engine reads or writes another engine's database. Baobab ERP's Postgres instance may host
Baobab-owned extension schemas (mapping, outbox, inbox, reconciliation state) alongside
iDempiere's own schema in the same physical database for the initial foundation deployment,
but no other engine is granted access to either. Cross-engine interaction is contract-first:
versioned REST APIs and canonical, signed events. See ADR-ERP-005, ADR-ERP-006.

## Event architecture

ERP state changes are recorded in a transactional outbox in the same database transaction as
the operational change, then published at least once as canonical events
(`erp.<noun>.<verb>.v1`). Consumers are required to be idempotent. See ADR-ERP-006.

## Tenant isolation

`Tenant`, `LegalEntity`, `AD_Client`, and `AD_Org` are four different concepts (see
ADR-ERP-002, ADR-ERP-003). Isolation is proportional to legal, regulatory, and commercial
requirements via `IsolationProfile`, not a single hard-coded topology. A missing or ambiguous
mapping fails closed.

## Future capability extraction

iDempiere is the ERP engine today. Specific capabilities (warehouse execution, procurement
sourcing, payment orchestration) may later be delegated to specialist engines behind the same
`CapabilityBinding` contracts without changing consumers. See ADR-ERP-001 §31–33. This
repository is built so that extraction is possible, not so that it is required.

## ERPNext retirement

ERPNext is retired from this repository effective with this change, not staged for later
removal, because no production data, tenant, or integration ever depended on it. Phases 1–28
of the wider migration programme (audit, reconciliation, cutover, stabilisation) apply to a
future migration *from a live ERPNext deployment*, which does not exist for Baobab today. If
one is stood up before this repository reaches production, the migration tooling under
`migration/` is the entry point for that work; until then it remains scaffolding. See
`docs/migration/erpnext-removal-report.md` for exactly what was deleted and why deletion was
safe now rather than deferred.

## What "production-grade" does not mean yet

This document freezes architecture, not completeness. The repository at this change contains:

- a runtime baseline (iDempiere + PostgreSQL via Compose);
- a Baobab OSGi extension skeleton demonstrating the extension pattern;
- application-service modules implementing context, mapping, outbox/inbox, and signing logic
  against the canonical contracts;
- migration tooling scaffolding, empty pending a real source system;
- an honest conformance ledger (`architecture/conformance.yaml`) tracking each ADR against
  Foundation / Partial / Planned status.

It does not yet contain LegalEntity accounting configuration, financial reconciliation,
golden-transaction validation, or a production `EngineInstance`. Those are tracked as open
phases, not silently assumed done.
