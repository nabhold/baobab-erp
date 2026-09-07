# Reconciliation

ADR-ERP-011's governing rule: whenever two independently persisted representations
are expected to agree, Baobab defines how disagreement is detected and resolved.
Section 63 lists eight reconciliation dimensions (identity, state, quantity, amount,
currency, status, count, time) and section 69 says reconciliation should proceed from
inexpensive to detailed controls -- count first, entity-level identity comparison
next, then field-level dimensions like state/quantity/amount. `modules/reconciliation`
implements the two cheapest so far.

## Count reconciliation (`modules/reconciliation/record_counts.py`)

Compares two independently maintained counts for a tenant/category and reports
whether they agree -- the cheapest possible check (ADR-ERP-011 section 68), meant to
run before anything more expensive. `reconcile_record_counts(tenant_id, category,
left, right)` takes two `Countable` implementations (anything with a
`count(tenant_id, category) -> int` method) and returns a `ReconciliationResult` with
a `matches` property.

## Identity reconciliation (`modules/reconciliation/identity.py`)

Verifies that the canonical entities Baobab expects to have an iDempiere mapping
actually have an active one, and flags active mappings for entities no longer
expected (ADR-ERP-011 section 64). `reconcile_identity(tenant_id, canonical_type,
expected_canonical_ids, store)` takes the expected set from the caller -- this module
never assumes it owns the source of truth for what should exist (that's the canonical
registry owned by `nabhold/baobab-cp`), only whether `baobab.entity_mapping` agrees
with it -- and a `MappedEntityStore` (`active_canonical_ids(tenant_id, canonical_type)
-> set[str]`, implemented by `PostgresCanonicalMappingStore`). The result's `missing`
set is canonical ids with no active mapping; `unexpected` is active mappings for
canonical ids no longer in the expected set.

## Status

Both dimensions are pure functions over injected stores, tested with in-memory fakes
(`tests/unit/test_record_counts.py`, `tests/unit/test_identity_reconciliation.py`) and
against real Postgres rows (`tests/integration/test_postgres_mapping_store.py`).
Neither is wired to a scheduler or exposed over HTTP yet -- there is no periodic job
that calls them, and no endpoint to trigger or report a run, unlike
`dispatch_worker.py`'s Compose-scheduled loop (`docs/operations.md`). State (section
65), quantity (section 66) and amount (section 67) reconciliation, and everything past
count/identity in the "layered reconciliation" progression (section 69), are not
started. See `architecture/conformance.yaml` against ADR-ERP-011.
