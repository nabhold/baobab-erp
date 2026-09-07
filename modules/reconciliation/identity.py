from dataclasses import dataclass
from typing import Protocol


class MappedEntityStore(Protocol):
    def active_canonical_ids(self, tenant_id: str, canonical_type: str) -> set[str]: ...


@dataclass(frozen=True, slots=True)
class IdentityReconciliationResult:
    canonical_type: str
    missing: frozenset[str]
    unexpected: frozenset[str]

    @property
    def matches(self) -> bool:
        return not self.missing and not self.unexpected


def reconcile_identity(
    tenant_id: str,
    canonical_type: str,
    expected_canonical_ids: set[str],
    store: MappedEntityStore,
) -> IdentityReconciliationResult:
    """Identity reconciliation (ADR-ERP-011 section 64): do the canonical entities
    Baobab expects to have an iDempiere mapping actually have an active one, and are
    there active mappings for canonical entities Baobab no longer expects?

    `expected_canonical_ids` is supplied by the caller (e.g. the canonical registry
    owned by nabhold/baobab-cp) rather than read here -- this module never assumes
    it owns the source of truth for what should exist, only whether the mapping
    table agrees with it.
    """
    mapped = store.active_canonical_ids(tenant_id, canonical_type)
    expected = frozenset(expected_canonical_ids)
    return IdentityReconciliationResult(
        canonical_type=canonical_type,
        missing=expected - mapped,
        unexpected=mapped - expected,
    )
