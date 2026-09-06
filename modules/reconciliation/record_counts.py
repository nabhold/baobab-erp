from dataclasses import dataclass
from typing import Protocol


class Countable(Protocol):
    def count(self, tenant_id: str, category: str) -> int: ...


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    category: str
    left_count: int
    right_count: int

    @property
    def matches(self) -> bool:
        return self.left_count == self.right_count


def reconcile_record_counts(
    tenant_id: str,
    category: str,
    left: Countable,
    right: Countable,
) -> ReconciliationResult:
    """Layer 1 reconciliation (ADR-ERP-011): do two independently maintained counts agree.

    This deliberately does not attempt Layer 2-4 (control totals, mapping completeness,
    financial equivalence); those require the domain-specific comparators tracked in
    architecture/conformance.yaml against ADR-ERP-011.
    """
    return ReconciliationResult(
        category=category,
        left_count=left.count(tenant_id, category),
        right_count=right.count(tenant_id, category),
    )
