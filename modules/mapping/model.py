from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NativeRecordRef:
    """A pointer to one iDempiere native record. Never used as a cross-engine identifier."""

    table: str
    record_id: int


class MappingNotFoundError(Exception):
    """Raised when no active Mapping/ExternalReference exists for a canonical identity.

    Per ADR-ERP-007, a missing mapping is a business exception; callers must not
    fall back to matching by display name or lazily creating a native record.
    """
